"""
Fix Luck Pills Configuration (Plan 46 Supplement)
修复气运丹药配置错误：为小气运丹添加"一面之缘"标记，修正数值。
"""
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import db_manager
from src.models import ItemDefinition
from src.logger import logger
from sqlmodel import select

# Fix Config
UPDATES = {
    # Tier 2: 小气运丹 (修复数值过高且无限制的 Bug)
    "pill_luck_minor": {
        "name": "中造化丹", # 改名避免混淆
        "effect": {"affection": 2, "once_per_life": True},
        "desc": "比小造化丹稍强，微量提升本世气运。（一面之缘）"
    },
    
    # Tier 1: 小造化丹 (确认配置)
    "pill_luck_1": {
        "effect": {"affection": 1, "once_per_life": True},
        # desc is already fine
    },
    
    # Tier 3: 生生造化丹 (确认配置)
    "pill_luck_3": {
        "effect": {"affection": 3, "once_per_life": True}, # Plan 45 said 3, JSON had 3 but check flag
    },
    
    # Tier 5: 春秋大道丹
    "fruit_karma": {
        "effect": {"affection": 5, "once_per_life": True}
    },
    
    # Tier 8: 鸿蒙气运
    "root_dragon": {
        "effect": {"affection": 10, "once_per_life": True}
    }
}

def fix_items():
    json_path = os.path.join("src", "data", "items_v2.json")
    
    # 1. Update JSON file
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    updated_count = 0
    
    for tier, content in data.items():
        # Check both materials and pills lists
        for category in ["materials", "pills"]:
            items = content.get(category, [])
            for item in items:
                iid = item.get("id")
                if iid in UPDATES:
                    update_cfg = UPDATES[iid]
                    # Partial update
                    if "name" in update_cfg:
                        item["name"] = update_cfg["name"]
                    if "desc" in update_cfg:
                        item["desc"] = update_cfg["desc"]
                    if "effect" in update_cfg:
                        item["effect"] = update_cfg["effect"]
                    updated_count += 1
                    logger.info(f"Updated JSON for item: {iid}")
                    
    # Save JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.info(f"JSON file updated. {updated_count} items modified.")

    # 2. Update Database
    with db_manager.get_session() as session:
        for iid, cfg in UPDATES.items():
            item_def = session.get(ItemDefinition, iid)
            if item_def:
                if "name" in cfg:
                    item_def.name = cfg["name"]
                if "desc" in cfg:
                    item_def.description = cfg["desc"]
                if "effect" in cfg:
                    item_def.effect_json = json.dumps(cfg["effect"])
                
                session.add(item_def)
                logger.info(f"Updated Database for item: {iid}")
            else:
                logger.warning(f"Item {iid} not found in database.")
        
        session.commit()
    logger.info("Database updated.")

if __name__ == "__main__":
    fix_items()
