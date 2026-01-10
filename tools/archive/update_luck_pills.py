#!/usr/bin/env python3
"""
Plan 45: 添加气运丹药到数据库
这些丹药标记为"一面之缘"，一世只能使用一次
"""

import sqlite3
import json
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.path_helper import get_user_data_dir

# 新增的气运丹药定义
LUCK_PILLS = [
    {
        "id": "pill_luck_1",
        "name": "小造化丹",
        "type": "consumable",
        "tier": 1,
        "price": 2000,
        "desc": "夺天地之造化，微量提升本世气运。（一面之缘）",
        "effect": {"affection": 1, "once_per_life": True},
        "recipe": {}
    },
    {
        "id": "pill_luck_3",
        "name": "生生造化丹",
        "type": "consumable",
        "tier": 3,
        "price": 32000,
        "desc": "蕴含天机之力的宝珠，服用可转运。（一面之缘）",
        "effect": {"affection": 3, "once_per_life": True},
        "recipe": {}
    },
    {
        "id": "fruit_karma",
        "name": "春秋大道丹",
        "type": "consumable",
        "tier": 5,
        "price": 200000,
        "desc": "蕴含时间法则的丹药，可以从时间长河中重塑气运。（一面之缘）",
        "effect": {"affection": 5, "once_per_life": True},
        "recipe": {}
    },
    {
        "id": "root_dragon",
        "name": "鸿蒙气运",
        "type": "consumable",
        "tier": 8,
        "price": 1000000,
        "desc": "神秘且强大的气息，拥有逆天改命之效。（一面之缘）",
        "effect": {"affection": 10, "once_per_life": True},
        "recipe": {}
    }
]

def update_items_json():
    """更新 items_v2.json 文件"""
    items_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "src", "data", "items_v2.json")
    
    with open(items_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 将丹药添加到对应的 tier
    for pill in LUCK_PILLS:
        tier_key = f"tier_{pill['tier']}"
        if tier_key in data:
            # 检查是否已存在
            existing_ids = [p['id'] for p in data[tier_key].get('pills', [])]
            if pill['id'] not in existing_ids:
                data[tier_key]['pills'].append(pill)
                print(f"✓ 添加 {pill['name']} 到 {tier_key}")
            else:
                print(f"- {pill['name']} 已存在于 {tier_key}")
        else:
            print(f"✗ 找不到 {tier_key}")
    
    with open(items_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"\n已更新: {items_path}")

def update_database():
    """更新数据库中的 item_definitions 表"""
    db_path = os.path.join(get_user_data_dir(), "user_data.db")
    
    if not os.path.exists(db_path):
        print(f"数据库不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for pill in LUCK_PILLS:
        effect_json = json.dumps(pill['effect'], ensure_ascii=False)
        
        # 使用 INSERT OR REPLACE (根据实际表结构)
        cursor.execute("""
            INSERT OR REPLACE INTO item_definitions 
            (id, name, type, tier, price, description, effect_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            pill['id'],
            pill['name'],
            pill['type'],
            pill['tier'],
            pill['price'],
            pill['desc'],
            effect_json
        ))
        print(f"✓ 数据库添加/更新: {pill['name']}")
    
    conn.commit()
    conn.close()
    print(f"\n数据库已更新: {db_path}")

def create_used_once_table():
    """确保 used_once_items 表存在"""
    db_path = os.path.join(get_user_data_dir(), "user_data.db")
    
    if not os.path.exists(db_path):
        print(f"数据库不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS used_once_items (
            item_id TEXT PRIMARY KEY
        )
    """)
    
    conn.commit()
    conn.close()
    print("✓ used_once_items 表已确保存在")

if __name__ == "__main__":
    print("=" * 50)
    print("Plan 45: 气运丹药更新工具")
    print("=" * 50)
    
    print("\n[1/3] 更新 items_v2.json...")
    update_items_json()
    
    print("\n[2/3] 确保 used_once_items 表存在...")
    create_used_once_table()
    
    print("\n[3/3] 更新数据库...")
    update_database()
    
    print("\n" + "=" * 50)
    print("完成!")
