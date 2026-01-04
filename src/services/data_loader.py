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
    
    DATA_VERSION = "005" # 初始版本号，每次修改静态数据(JSON)请递增

    @staticmethod
    def check_data_update():
        """
        检查代码中的数据版本号是否高于数据库中的版本号。
        如果是，则强制执行 load_initial_data 更新静态数据。
        """
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Get current DB version
            cursor.execute("SELECT value FROM system_metadata WHERE key = 'data_version'")
            row = cursor.fetchone()
            db_version = row[0] if row else "000"
            
            logger.info(f"数据版本检查: Code={DataLoader.DATA_VERSION}, DB={db_version}")
            
            if DataLoader.DATA_VERSION > db_version:
                logger.info("检测到数据更新，正在同步静态数据...")
                if DataLoader.load_initial_data():
                    # Update version in DB
                    cursor.execute("INSERT OR REPLACE INTO system_metadata (key, value) VALUES ('data_version', ?)", (DataLoader.DATA_VERSION,))
                    conn.commit()
                    logger.info(f"数据更新完成，版本号更新为 {DataLoader.DATA_VERSION}")
            else:
                logger.debug("数据已是最新，跳过更新。")
                
            conn.close()
        except Exception as e:
            logger.error(f"版本检查失败: {e}")

    @staticmethod
    def load_initial_data():
        """
        从资源文件加载所有初始数据 (Items, Recipes, Events) 并写入数据库。
        """
        logger.info("开始加载数据库数据...")
        
        # 1. 获取资源路径
        # 注意: get_resource_path 会处理打包后的路径映射
        items_v1_path = get_resource_path("src/data/items.json")
        items_v2_path = get_resource_path("src/data/items_v2.json")
        events_path = get_resource_path("src/data/events.json")
        dialogues_path = get_resource_path("src/data/dialogues.json")
        achievements_path = get_resource_path("src/data/achievements.json") # 如果有

        # 2. 加载 JSON
        v1_items = DataLoader.load_json(items_v1_path)
        v2_items = DataLoader.load_json(items_v2_path)

        events_data = DataLoader.load_json(events_path)
        dialogues_data = DataLoader.load_json(dialogues_path)
        
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


            # --- Dialogues ---
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dialogue_definitions (
                    id TEXT PRIMARY KEY,
                    text TEXT,
                    type TEXT,
                    conditions_json TEXT,
                    weight INTEGER
                )
            """)
            
            count_dialogues = 0
            if isinstance(dialogues_data, list):
                for dia in dialogues_data:
                    did = dia.get("id")
                    dtext = dia.get("text")
                    dtype = dia.get("type")
                    dweight = dia.get("weight", 10)
                    dcond = json.dumps(dia.get("conditions", {}))
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO dialogue_definitions (id, text, type, conditions_json, weight)
                        VALUES (?, ?, ?, ?, ?)
                    """, (did, dtext, dtype, dcond, dweight))
                    count_dialogues += 1
            
            # Set initial version if not present
            cursor.execute("INSERT OR IGNORE INTO system_metadata (key, value) VALUES ('data_version', ?)", (DataLoader.DATA_VERSION,))

            conn.commit()
            conn.close()
            
            logger.info(f"数据库数据加载完成: Items={count_items}, Recipes={count_recipes}, Events={count_events}, Dialogues={count_dialogues}")
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
