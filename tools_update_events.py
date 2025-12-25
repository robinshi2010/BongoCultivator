import sqlite3
import json
import os

DB_PATH = 'user_data.db'

# Define the full list of events based on Plan 10
# Format: ID, Title, Type, TriggerJSON, Text, OutcomesJSON
# TriggerJSON keys: min_layer, max_layer, state, mind_min, mind_max, luck_min, chance (0.0-1.0), is_unique (bool)
# OutcomesJSON list: {"type": "exp|mind|item|money|body|luck", "val"|"id": ...}

EVENTS_DATA = [
    # --- Tier 0: 炼气期 ---
    ("evt_t0_c1", "灵气复苏", "Common", 
     {"min_layer": 0, "max_layer": 0, "chance": 0.05}, 
     "今日晨练时感觉神清气爽，似乎空气中的灵气浓度有所上升。", 
     [{"type": "exp", "val": 50}, {"type": "mind", "val": -2}]),
     
    ("evt_t0_c2", "误食野果", "Common",
     {"min_layer": 0, "max_layer": 0, "chance": 0.05},
     "你在路边发现一颗颜色鲜艳的果实，饥渴难耐下吞服了它。",
     [{"type": "random", "options": [
         {"weight": 50, "outcomes": [{"type": "exp", "val": 100}]},
         {"weight": 50, "outcomes": [{"type": "mind", "val": 5}]} # Poison/Hallucination
     ]}]),
     
    ("evt_t0_r1", "兽冢拾荒", "Rare",
     {"min_layer": 0, "max_layer": 1, "state": "WORK", "chance": 0.01},
     "你误入一处荒废的兽冢，在白骨堆中发现了一颗泛着红光的残齿。",
     [{"type": "item", "id": "part_wolf_tooth", "count": 1}]),

    ("evt_t0_r2", "神秘符箓", "Rare",
     {"min_layer": 0, "max_layer": 1, "mind_max": 20, "chance": 0.02},
     "一位路过的云游道士看你骨骼惊奇，随手丢给你一张破旧符纸。",
     [{"type": "item", "id": "misc_talisman_old", "count": 1}]),

    ("evt_t0_u1", "洗髓机缘", "Unique",
     {"min_layer": 0, "max_layer": 0, "chance": 0.005, "is_unique": True},
     "你在深山瀑布下冲刷肉身时，意外发现瀑布后的一株幽蓝草药。",
     [{"type": "item", "id": "herb_marrow_0", "count": 1}, {"type": "exp", "val": 500}]),

    # --- Tier 1: 筑基期 ---
    ("evt_t1_c1", "地脉震动", "Common",
     {"min_layer": 1, "max_layer": 1, "chance": 0.05},
     "脚下的大地微微颤抖，似有地龙翻身，泄露出一丝精纯土灵气。",
     [{"type": "exp", "val": 200}]),

    ("evt_t1_c2", "坊市捡漏", "Common",
     {"min_layer": 1, "max_layer": 2, "state": "IDLE", "chance": 0.05},
     "在坊市角落的摊位上，你发现一块不起眼的矿石竟是赤铜精母。",
     [{"type": "money", "val": -100}, {"type": "item", "id": "ore_copper_red", "count": 1}]),

    ("evt_t1_r1", "寒潭奇遇", "Rare",
     {"min_layer": 1, "max_layer": 2, "state": "WORK", "chance": 0.01},
     "为了躲避仇家，你潜入寒潭深处，却意外发现寒气逼人的晶石。",
     [{"type": "item", "id": "ore_cold_crystal", "count": 1}, {"type": "body", "val": 1}]),

    ("evt_t1_u1", "龙纹觉醒", "Unique",
     {"min_layer": 1, "max_layer": 1, "chance": 0.005, "is_unique": True},
     "你体内的灵力忽然自行运转，与手中的龙纹草产生共鸣，隐约听到了龙吟。",
     [{"type": "item", "id": "herb_dragon_1", "count": 1}, {"type": "exp", "val": 2000}]),

    # --- Tier 2: 金丹期 ---
    ("evt_t2_c1", "丹火试炼", "Common",
     {"min_layer": 2, "max_layer": 2, "state": "ALCHEMY", "chance": 0.1},
     "炉温突然升高，你急忙打出几道法诀稳住火候。",
     [{"type": "exp", "val": 500}, {"type": "mind", "val": 1}]),

    ("evt_t2_r1", "天雷滚滚", "Rare",
     {"min_layer": 2, "max_layer": 3, "chance": 0.01},
     "晴空一声霹雳，一道落雷击中了你不远处的竹林！",
     [{"type": "item", "id": "wood_sky_thunder", "count": 1}, {"type": "mind", "val": 5}]),

    ("evt_t2_r2", "古修洞府", "Rare",
     {"min_layer": 2, "max_layer": 3, "state": "WORK", "chance": 0.01},
     "你挖掘到了一座坍塌的洞府，门口散落着几面残破的阵旗。",
     [{"type": "item", "id": "misc_array_flag", "count": 1}, {"type": "money", "val": 500}]),

    ("evt_t2_u1", "金丹异象", "Unique",
     {"min_layer": 2, "max_layer": 2, "chance": 0.005, "is_unique": True},
     "你的金丹表面浮现出九窍玲珑之孔，贪婪地吞噬着周围的星辰之力。",
     [{"type": "item", "id": "ore_star_sand", "count": 2}, {"type": "exp", "val": 5000}]),

    # --- Tier 3: 元婴期 ---
    ("evt_t3_c1", "神游太虚", "Common",
     {"min_layer": 3, "max_layer": 3, "state": "IDLE", "chance": 0.05},
     "闭关中，你的元婴离体而出，在天地间遨游了一圈。",
     [{"type": "exp", "val": 1000}, {"type": "mind", "val": -5}]),

    ("evt_t3_r1", "空间裂隙", "Rare",
     {"min_layer": 3, "max_layer": 4, "chance": 0.01},
     "面前的空间突然裂开一道细缝，掉落一块形状扭曲的石头。",
     [{"type": "item", "id": "ore_void_stone", "count": 1}]),

    ("evt_t3_r2", "九曲灵踪", "Rare",
     {"min_layer": 3, "max_layer": 4, "state": "WORK", "chance": 0.01},
     "你看见一只白兔钻入土中消失不见，只留下一截红绳。",
     [{"type": "item", "id": "herb_soul_restore", "count": 1}]),

    ("evt_t3_u1", "黄泉回响", "Unique",
     {"min_layer": 3, "max_layer": 3, "chance": 0.005, "is_unique": True},
     "你的元婴误入黄泉河畔，被河水沾湿了衣角，却因祸得福凝练了魂体。",
     [{"type": "item", "id": "water_nether", "count": 1}, {"type": "mind", "val": 10}]),

    # --- Tier 4: 化神期 ---
    ("evt_t4_c1", "道韵共鸣", "Common",
     {"min_layer": 4, "max_layer": 4, "chance": 0.05},
     "你观摩落叶飘零，心中忽然对枯荣法则多了一丝明悟。",
     [{"type": "exp", "val": 3000}]),

    ("evt_t4_r1", "鲲鹏掠影", "Rare",
     {"min_layer": 4, "max_layer": 5, "chance": 0.005},
     "巨大的阴影遮蔽了天空，一根羽毛如山峰般坠落。",
     [{"type": "item", "id": "part_kunpeng_feather", "count": 1}]),

    ("evt_t4_u1", "息壤再生", "Unique",
     {"min_layer": 4, "max_layer": 4, "chance": 0.005, "is_unique": True},
     "你得到的这捧泥土竟然在吞噬周围的岩石自我增殖！",
     [{"type": "item", "id": "soil_chaos", "count": 1}]),

    # --- Tier 5: 炼虚期 ---
    ("evt_t5_c1", "虚空乱流", "Common",
     {"min_layer": 5, "max_layer": 5, "state": "WORK", "chance": 0.05},
     "你在虚空穿行时遭遇了能量乱流，不得不消耗修为抵御。",
     [{"type": "exp", "val": -5000}, {"type": "body", "val": 5}]),

    ("evt_t5_r1", "死星闪耀", "Rare",
     {"min_layer": 5, "max_layer": 6, "chance": 0.005},
     "远处一颗恒星熄灭了，你冒死捕获了它坍缩后的核心。",
     [{"type": "item", "id": "core_star", "count": 1}]),

    ("evt_t5_r2", "彼岸花开", "Rare",
     {"min_layer": 5, "max_layer": 6, "mind_min": 50, "chance": 0.01},
     "在神识恍惚间，你看到了一条满是红花的河流，想起了前世的名字。",
     [{"type": "item", "id": "flower_other_shore", "count": 1}, {"type": "mind", "val": -20}]),

    # --- Tier 6: 合体期 ---
    ("evt_t6_c1", "万兽朝苍", "Common",
     {"min_layer": 6, "max_layer": 6, "chance": 0.05},
     "你散发的威压让方圆百里的妖兽匍匐颤抖。",
     [{"type": "exp", "val": 8000}, {"type": "luck", "val": 1}]),

    ("evt_t6_r1", "麒麟献瑞", "Rare",
     {"min_layer": 6, "max_layer": 7, "luck_min": 10, "chance": 0.01},
     "一头火麒麟踏云而来，吐出一块臂骨后消失在云端。",
     [{"type": "item", "id": "bone_kirin_arm", "count": 1}]),

    ("evt_t6_u1", "三生石畔", "Unique",
     {"min_layer": 6, "max_layer": 6, "chance": 0.005, "is_unique": True},
     "你在梦中看到了自己的过去、未来，以及一块刻着名字的石头。",
     [{"type": "item", "id": "stone_three_life", "count": 1}]),

    # --- Tier 7: 大乘期 ---
    ("evt_t7_c1", "时间停滞", "Common",
     {"min_layer": 7, "max_layer": 7, "chance": 0.05},
     "你感觉到周围的时间流动变慢了，落叶悬在空中久久不落。",
     [{"type": "exp", "val": 15000}]),

    ("evt_t7_r1", "因果纠缠", "Rare",
     {"min_layer": 7, "max_layer": 8, "state": "WORK", "chance": 0.01},
     "你随手拨动的一根无形丝线，竟导致千里之外的一个宗门覆灭。",
     [{"type": "item", "id": "thread_karma", "count": 1}, {"type": "mind", "val": 10}]),

    ("evt_t7_u1", "世界树语", "Unique",
     {"min_layer": 7, "max_layer": 7, "chance": 0.005, "is_unique": True},
     "巨大的世界树虚影向你展示了宇宙的生灭，落下一片枯叶。",
     [{"type": "item", "id": "leaf_world_tree", "count": 1}]),

    # --- Tier 8: 渡劫期 ---
    ("evt_t8_c1", "天道窥视", "Common",
     {"min_layer": 8, "max_layer": 8, "chance": 0.05},
     "天空中出现了一只巨大的眼睛，冷漠地注视着你。",
     [{"type": "mind", "val": 20}]),

    ("evt_t8_r1", "鸿蒙初辟", "Rare",
     {"min_layer": 8, "max_layer": 8, "chance": 0.005},
     "你捕捉到了宇宙诞生之初残留的一缕紫气。",
     [{"type": "item", "id": "gas_primordial", "count": 1}]),
     
    ("evt_t8_u1", "定界之锚", "Unique",
     {"min_layer": 8, "max_layer": 8, "chance": 0.005, "is_unique": True},
     "为了在飞升通道中不迷失方向，你炼化了一方小世界为锚点。",
     [{"type": "item", "id": "stone_destiny", "count": 1}]),
     
    # --- Tier 9: 飞升 ---
    ("evt_t9_c1", "屏幕之外", "Common",
     {"min_layer": 9, "max_layer": 10, "chance": 0.05},
     "我仿佛看到屏幕外有一张巨大的脸在盯着我看...是你吗？",
     [{"type": "exp", "val": 50000}]),

    ("evt_t9_u1", "作者的馈赠", "Unique",
     {"min_layer": 9, "max_layer": 10, "chance": 0.01, "is_unique": True},
     "你捡到了一支钢笔，上面刻着几个烫金小字：'Design Idea'。",
     [{"type": "item", "id": "pen_author", "count": 1}])
]

def update_events():
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create Table if not exists
    print("Creating game_events table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_events (
            id TEXT PRIMARY KEY,
            title TEXT,
            type TEXT,
            trigger_json TEXT, -- JSON
            description TEXT,
            outcomes_json TEXT, -- JSON
            is_unique INTEGER DEFAULT 0,
            has_triggered INTEGER DEFAULT 0 -- For unique events state tracking (though might be better in player_status, putting here for simple toggle in this simple engine or use separate log)
        )
    """)
    # NOTE: In a perfect design, 'has triggered' status for unique events should be in a user-specific table (e.g. event_history), 
    # not in the definitions table. 
    # However, for this single-player embedded DB, we can use a separate table for history or just query logs.
    # Let's create a separate table for event history to be clean.
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_history (
            event_id TEXT PRIMARY KEY,
            triggered_at INTEGER
        )
    """)

    # 2. Insert Data
    print("Inserting events...")
    # Clear old events first to allow updates
    cursor.execute("DELETE FROM game_events")
    
    count = 0
    for evt in EVENTS_DATA:
        eid, title, etype, triggers, text, outcomes = evt
        
        # Serialize JSON
        trig_json = json.dumps(triggers)
        out_json = json.dumps(outcomes)
        is_unique = 1 if triggers.get("is_unique") else 0
        
        cursor.execute(
            "INSERT INTO game_events (id, title, type, trigger_json, description, outcomes_json, is_unique) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (eid, title, etype, trig_json, text, out_json, is_unique)
        )
        count += 1
        
    conn.commit()
    conn.close()
    print(f"Successfully processed {count} events.")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("Error: DB not found.")
    else:
        update_events()
