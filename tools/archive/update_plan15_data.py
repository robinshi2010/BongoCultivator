import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "user_data.db")

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- Phase 2: Fixing Recipes ---")
    
    # 0. Add Sink Item: Spirit Shards
    print("Adding Spirit Shards item...")
    cursor.execute("""
        INSERT OR REPLACE INTO item_definitions (id, name, type, tier, description, price, effect_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("spirit_shards", "灵石碎片", "material", 1, "灵石的碎片，虽无修炼大用，但坊市回收价格稳定。", 10, None))
    
    # 1. Recipe Map
    recipes_to_add = [
        # Material Refinement
        {
            "result_id": "iron_essence",
            "ingredients": {"ore_iron": 5},
            "desc": "提炼凡铁"
        },
        # Recycling
        {
            "result_id": "spirit_shards", # Talisman waste -> Money
            "ingredients": {"talisman_waste": 5}, 
            "desc": "废纸回收"
        },
        # Note: vine_ghost -> spirit_shards? 
        # But PK is result_item_id. We can only have ONE recipe for spirit_shards.
        # So we can't have both "talisman->shards" AND "vine->shards" separately.
        # They must be in the SAME recipe? No, ingredients are AND.
        # This confirms we need unique result items for each recycling path if we want separate recipes.
        # OR we just rely on Market Selling (Phase 3) for most things, and only provide recipes for "Upgrades".
        
        # Plan 15 Phase 3 says: "Allow players to sell inventory items".
        # This renders "Craft to Sell" redundant if we can just "Sell directly".
        # BUT, users might want to craft "Junk" into "Useful" items.
        
        # Let's change strategy:
        # ore_iron -> iron_essence (Upgrade, Good)
        # talisman_waste -> can be sold directly.
        # vine_ghost -> can be sold directly.
        
        # So I will ONLY add the iron_essence recipe.
        # I will SKIP the other recycling recipes because they conflict on 'result_id' or require unique output items.
        # Instead, I'll let Phase 3 (Market Sell) handle the value of talisman_waste.
    ]
    
    # Only keep iron_essence for now to fix the crash and proceed with events
    recipes_to_add = [
        {
            "result_id": "iron_essence",
            "ingredients": {"ore_iron": 5},
            "desc": "提炼凡铁"
        }
    ]

    for r in recipes_to_add:
        print(f"Adding recipe for {r['result_id']}...")
        try:
            cursor.execute("""
                INSERT INTO recipes (result_item_id, ingredients_json, craft_time, success_rate)
                VALUES (?, ?, ?, ?)
            """, (r['result_id'], json.dumps(r['ingredients']), 5, 0.9))
        except sqlite3.IntegrityError:
            print(f"Skipping {r['result_id']} (Recipe already exists)")
        except Exception as e:
            print(f"Error adding {r['result_id']}: {e}")

    print("--- Phase 3: Enriching Events ---")
    
    new_events = [
        {
            "id": "event_beggar_secret",
            "type": "random",
            "weight": 5,
            "text": "路边一个衣衫褴褛的老乞丐拦住你：“少年，我看你骨骼惊奇...”",
            "conditions": {"min_money": 200},
            "choices": [
                {
                    "text": "给他在50灵石",
                    "cost": {"money": 50},
                    "result": {
                        "success_chance": 0.4,
                        "success_effect": {
                            "text": "乞丐大笑三声，塞给你一本破书。",
                            "exp": [100, 300]
                        },
                        "fail_effect": {
                            "text": "乞丐拿了钱转眼就跑没影了。",
                            "mind": [5, 10]
                        }
                    }
                },
                {
                    "text": "无视离开",
                    "result": {
                        "success_chance": 1.0,
                        "success_effect": {
                            "text": "你摇摇头离开了。",
                            "mind": [-1, 0]
                        }
                    }
                }
            ]
        },
        {
            "id": "event_cliff_jump",
            "type": "random",
            "weight": 3, 
            "text": "被仇家追杀至悬崖边，你决定——",
            "conditions": {"min_layer": 1},
            "choices": [
                {
                    "text": "跳下去！",
                    "result": {
                        "success_chance": 0.3,
                        "success_effect": {
                            "text": "挂在树上大难不死，还在山洞发现了前辈遗府！",
                            "exp": [500, 1000],
                            "items": {"iron_essence": 5}
                        },
                        "fail_effect": {
                            "text": "摔了个半死，好久才缓过来。",
                            "body": [-5, -10],
                            "money": [-10, -50]
                        }
                    }
                },
                {
                    "text": "跪地求饶",
                    "result": {
                        "success_chance": 0.1,
                        "success_effect": {
                            "text": "仇家看你可怜，放了你一马。",
                            "mind": [10, 20]
                        },
                        "fail_effect": {
                            "text": "仇家并没有放过你，你被痛打一顿。",
                            "body": [-20, -30]
                        }
                    }
                }
            ]
        },
        {
            "id": "event_weather_thunder",
            "type": "random", 
            "weight": 8,
            "text": "突然雷雨大作，作为修仙者你感觉到这是雷灵气汇聚。",
            "conditions": {},
            "effects": {
                "text": "你大着胆子引雷入体，酥麻中有些许感悟。",
                "exp": [20, 50],
                "body": [0.1, 0.5]
            }
        },
        {
            "id": "event_gambling_stone",
            "type": "market",
            "weight": 5,
            "text": "坊市里的赌石摊位，据说能开出极品灵材。",
            "conditions": {"min_money": 100},
            "choices": [
                {
                    "text": "切一块 (100灵石)",
                    "cost": {"money": 100},
                    "result": {
                        "success_chance": 0.2,
                        "success_effect": {
                            "text": "出绿了！竟然是铁精！",
                            "items": {"iron_essence": 3}
                        },
                        "fail_effect": {
                            "text": "切开全是石头。",
                            "mind": [2, 5]
                        }
                    }
                },
                {
                    "text": "不赌为妙",
                    "result": {
                        "success_chance": 1.0, 
                        "success_effect": {"text": "十赌九输，你克制住了贪念。", "mind": [-2, -5]}
                    }
                }
            ]
        },
        {
            "id": "event_stray_pet",
            "type": "random",
            "weight": 6,
            "text": "一只迷路的小灵兽蹭了蹭你的裤脚。",
            "conditions": {},
            "effects": {
                "text": "你喂了它一点灵食，它开心地围着你转。",
                "luck": [1, 3],
                "items": {"weed_wash": 1}
            }
        },
        {
            "id": "event_sudden_enlightenment",
            "type": "random",
            "weight": 4,
            "text": "观看蚂蚁搬家，忽有感悟。",
            "conditions": {"min_mind": 5},
            "effects": {
                "text": "大道至简，你的心境提升了。",
                "mind": [-10, -20],
                "exp": [10, 30]
            }
        },
        {
            "id": "event_rogue_cultivator",
            "type": "combat",
            "weight": 5,
            "text": "遭遇散修拦路抢劫！",
            "conditions": {"min_layer": 2},
            "choices": [
                {
                    "text": "干他！",
                    "result": {
                        "success_chance": 0.6,
                        "success_effect": {
                            "text": "你技高一筹，反抢了他的储物袋。",
                            "money": [50, 100],
                            "items": {"pill_speed_0": 1}
                        },
                        "fail_effect": {
                            "text": "你被打跑了，丢了一些灵石。",
                            "money": [-20, -50],
                            "body": [-5, -10]
                        }
                    }
                },
                {
                    "text": "破财免灾 (50灵石)",
                    "cost": {"money": 50},
                    "result": {
                        "success_chance": 1.0,
                        "success_effect": { 
                            "text": "散修拿了钱满意的走了。",
                            "mind": [5, 10]
                        }
                    }
                }
            ]
        }
    ]

    for evt in new_events:
        print(f"Adding event: {evt['id']}")
        cursor.execute("""
            INSERT OR REPLACE INTO event_definitions (id, type, weight, data_json)
            VALUES (?, ?, ?, ?)
        """, (evt['id'], evt['type'], evt['weight'], json.dumps(evt)))

    conn.commit()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()
