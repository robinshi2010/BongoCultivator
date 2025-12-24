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
        
        # 1. Check if DB needs population
        count = 0
        try:
            with db_manager._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM item_definitions")
                row = cursor.fetchone()
                if row:
                    count = row[0]
        except Exception as e:
            logger.error(f"Failed to check item DB: {e}")

        if count == 0:
            self.import_from_json()
            
        # 2. Load into memory
        self._load_from_db()
        logger.info(f"Loaded {len(self.flat_items)} items from Database.")

    def import_from_json(self):
        import json
        from src.database import db_manager
        
        # Try v2 first
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'items_v2.json')
        if not os.path.exists(json_path):
             logger.warning("items_v2.json not found, skipping import.")
             return

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            with db_manager._get_conn() as conn:
                cursor = conn.cursor()
                
                for tier_key, content in data.items():
                    # tier_0 -> 0
                    tier_idx = int(tier_key.split('_')[1])
                    
                    all_items = content.get("materials", []) + content.get("pills", [])
                    
                    for item in all_items:
                        # Insert Item
                        effect_val = item.get("effect")
                        effect_json = json.dumps(effect_val) if effect_val else None
                        
                        cursor.execute("""
                            INSERT OR REPLACE INTO item_definitions 
                            (id, name, type, tier, description, price, effect_json)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            item["id"], item["name"], item["type"], item["tier"],
                            item["desc"], item["price"], effect_json
                        ))
                        
                        # Insert Recipe if exists
                        if "recipe" in item:
                            recipe_json = json.dumps(item["recipe"])
                            cursor.execute("""
                                INSERT OR REPLACE INTO recipes
                                (result_item_id, ingredients_json, craft_time, success_rate)
                                VALUES (?, ?, ?, ?)
                            """, (item["id"], recipe_json, 10, 0.8)) # Default 10s, 80% success
                            
            logger.info("Successfully imported items from JSON to DB.")
        except Exception as e:
            logger.error(f"Import failed: {e}")

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
