import json
import sqlite3
import os
from src.logger import logger
from src.utils.path_helper import get_resource_path
from src.database import DB_FILE

class DataLoader:
    """
    负责将静态配置数据 (JSON) 加载到 SQLite 数据库中。
    主要用于初始化或数据迁移。
    """
    
    @staticmethod
    def load_initial_data():
        """
        从资源文件加载所有初始数据 (Items, Recipes, Events) 并写入数据库。
        """
        logger.info("开始初始化数据库数据...")
        
        # 1. 获取资源路径
        # 注意: get_resource_path 会处理打包后的路径映射
        items_v1_path = get_resource_path("src/data/items.json")
        items_v2_path = get_resource_path("src/data/items_v2.json")
        events_path = get_resource_path("src/data/events.json")
        achievements_path = get_resource_path("src/data/achievements.json") # 如果有

        # 2. 加载 JSON
        v1_items = DataLoader.load_json(items_v1_path)
        v2_items = DataLoader.load_json(items_v2_path)
        events_data = DataLoader.load_json(events_path)
        
        # 3. 处理物品数据合并
        combined_items = {}
        
        def process_tier_data(tier_data):
            if not tier_data: return
            for category in ["materials", "pills", "equipments", "books"]:
                if category in tier_data:
                    for item in tier_data[category]:
                        item_id = item.get("id")
                        if not item_id: continue
                        
                        effect_val = json.dumps(item.get("effect", {})) if isinstance(item.get("effect"), dict) else item.get("effect", "{}")
                        recipe_val = json.dumps(item.get("recipe", {})) if isinstance(item.get("recipe"), dict) else item.get("recipe", "{}")
                        
                        combined_items[item_id] = {
                            "id": item_id,
                            "name": item.get("name"),
                            "type": item.get("type"),
                            "tier": item.get("tier"),
                            "price": item.get("price"),
                            "description": item.get("desc"),
                            "effect": effect_val,
                            "recipe": recipe_val
                        }

        # v2 first, then v1
        for data in v2_items.values(): process_tier_data(data)
        for data in v1_items.values(): process_tier_data(data)
        
        logger.info(f"解析到 {len(combined_items)} 个物品定义")

        # 4. 写入数据库
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # --- Items ---
            # 清空旧数据? 既然是初始化，通常是空的，但为了安全可以用 INSERT OR REPLACE
            # 或者先 DELETE ALL
            # 这里我们假设是初始化，使用 REPLACE
            
            # (Re)Create Table just in case, though database.py does this.
            # We rely on existing schema.
            
            count_items = 0
            for item in combined_items.values():
                cursor.execute("""
                    INSERT OR REPLACE INTO item_definitions (id, name, type, tier, description, price, effect_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (item["id"], item["name"], item["type"], item["tier"], item["description"], item["price"], item["effect"]))
                count_items += 1
                
            # --- Recipes ---
            # Clear old recipes to avoid duplicates if re-running
            cursor.execute("DELETE FROM recipes") 
            count_recipes = 0
            for item in combined_items.values():
                recipe_str = item["recipe"]
                if recipe_str and recipe_str != "{}":
                    # Parse to check validity?
                    cursor.execute("""
                        INSERT INTO recipes (result_item_id, ingredients_json, craft_time, success_rate)
                        VALUES (?, ?, ?, ?)
                    """, (item["id"], recipe_str, 5, 1.0))
                    count_recipes += 1

            # --- Events ---
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS event_definitions (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    weight INTEGER,
                    data_json TEXT
                )
            """)
            cursor.execute("DELETE FROM event_definitions")
            
            count_events = 0
            if isinstance(events_data, list):
                for event in events_data:
                    evt_id = event.get("id")
                    evt_type = event.get("type", "random")
                    evt_weight = event.get("weight", 10)
                    evt_json = json.dumps(event)
                    
                    cursor.execute("""
                        INSERT INTO event_definitions (id, type, weight, data_json)
                        VALUES (?, ?, ?, ?)
                    """, (evt_id, evt_type, evt_weight, evt_json))
                    count_events += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"数据库数据加载完成: Items={count_items}, Recipes={count_recipes}, Events={count_events}")
            return True
            
        except Exception as e:
            logger.error(f"数据库数据加载失败: {e}")
            return False

    @staticmethod
    def load_json(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"无法读取数据文件: {filepath} ({e})")
            return {}
