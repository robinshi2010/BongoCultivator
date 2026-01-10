import sqlite3
import os
import json

DB_PATH = 'user_data.db'

def fix_effects():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    # 定义要修复的数据映射
    # ID -> Effect Dict
    updates = {
        # Tier 0
        "pill_body_basic": {"stat_body": 5},          # 壮骨丸: 体魄+5
        "pill_speed_wind": {"stat_body": 2},          # 疾风散: 体魄+2 (敏捷)
        "pill_detox_0": {"mind_heal": 10},            # 避毒珠: 心魔-10
        
        # Tier 1
        "pill_mind_calm": {"mind_heal": 20},          # 定神丹: 心魔-20
        "pill_strength_bary": {"stat_body": 12},      # 大地金刚丸: 体魄+12
        "pill_vis_night": {"affection": 5},           # 夜视散: 好感+5
        
        # Tier 2
        "pill_beauty_face": {"affection": 30},        # 定颜丹: 好感+30
        "pill_crazy_blood": {"exp_gain": 0.08},       # 燃血丹: 经验+8% (燃血修炼)
        "pill_luck_minor": {"affection": 15},         # 小气运丹: 好感+15 (好运)
        
        # Tier 3
        "pill_soul_protect": {"mind_heal": 50},       # 护神丹
        "pill_teleport": {"stat_body": 5, "affection": 5}, # 缩地成寸: 混合 (代码目前只支持单回显，优先判定谁在前面)
        # InventoryWindow 逻辑是 if-elif，所以只会生效第一个 key
        # 我们只给单一效果
        "pill_teleport": {"stat_body": 8},
        "pill_clone_shadow": {"stat_body": 15},       # 身外化身: 大幅强身
        
        # Tier 4
        "pill_revive_muscle": {"stat_body": 30},
        "pill_clear_heart": {"mind_heal": 80},
    }

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("开始修复丹药效果...")
        for item_id, effect in updates.items():
            effect_json = json.dumps(effect)
            
            cursor.execute("""
                UPDATE item_definitions 
                SET effect_json = ?
                WHERE id = ?
            """, (effect_json, item_id))
            
            if cursor.rowcount > 0:
                print(f" -> 已更新 {item_id}: {effect}")
            else:
                print(f" -> 未找到物品 {item_id} (可能ID不匹配)")

        conn.commit()
        print("所有效果已更新完毕！")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_effects()
