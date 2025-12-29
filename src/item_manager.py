import json
import os
import random
from src.logger import logger

class ItemManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ItemManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        
        self.flat_items = {} 
        # Support Tier 0-8
        self.tier_lists = {}
        for i in range(9):
            self.tier_lists[i] = {"materials": [], "pills": []}
        
        self.load_items()
        self.initialized = True

    def load_items(self):
        from src.database import db_manager
        
        # 1. Load into memory from DB
        try:
            self._load_from_db()
            if not self.flat_items:
                logger.info("检测到数据库为空，尝试加载默认数据...")
                from src.services.data_loader import DataLoader
                if DataLoader.load_initial_data():
                    # Reload from DB after initialization
                    self._load_from_db()
                    
                if not self.flat_items:
                    logger.warning("Item Database is still EMPTY! Please check data files.")
            else:
                logger.info(f"Loaded {len(self.flat_items)} items from Database.")
        except Exception as e:
            logger.error(f"Failed to load items from DB: {e}")

    def _load_from_db(self):
        from src.database import db_manager
        import json
        
        try:
            with db_manager._get_conn() as conn:
                conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM item_definitions")
                rows = cursor.fetchall()
                
                for row in rows:
                    item_id = row['id']
                    tier = row['tier']
                    itype = row['type']
                    
                    # Parse effect
                    if row['effect_json']:
                        row['effect'] = json.loads(row['effect_json'])
                        
                    # Fetch recipe if needed (optional optimization: fetch all recipes once)
                    # For now, let's just make sure item data is robust
                    
                    self.flat_items[item_id] = row
                    
                    # Categorize
                    cat = "pills" if "pill" in item_id or itype == "consumable" else "materials" 
                    # Note: My generator uses "consumable" for herbs too.
                    # Adjust optimization: Check if ID contains 'pill' or type is break/buff
                    if itype in ['breakthrough', 'buff'] or 'pill' in item_id:
                        cat = "pills"
                    else:
                        cat = "materials"
                        
                    if tier in self.tier_lists:
                        self.tier_lists[tier][cat].append(item_id)
            
                # 3. Load Recipes
                cursor.execute("SELECT * FROM recipes")
                recipe_rows = cursor.fetchall()
                for r_row in recipe_rows:
                    res_id = r_row['result_item_id']
                    if res_id in self.flat_items:
                        ing_json = r_row['ingredients_json']
                        if ing_json:
                            self.flat_items[res_id]['recipe'] = json.loads(ing_json)
                        # Could also load usage craft_time, success_rate if needed
                        self.flat_items[res_id]['craft_time'] = r_row['craft_time']
                        self.flat_items[res_id]['success_rate'] = r_row['success_rate']
                        
        except Exception as e:
            logger.error(f"Load from DB failed: {e}")

    def _process_data(self):
        pass # Deprecated

    def get_item(self, item_id):
        return self.flat_items.get(item_id)

    def get_random_material(self, tier):
        """Randomly return a material ID from the specified tier"""
        candidates = self.tier_lists.get(tier, {}).get("materials", [])
        if candidates:
            return random.choice(candidates)
        return None

    def get_item_name(self, item_id):
        info = self.flat_items.get(item_id)
        return info["name"] if info else item_id
