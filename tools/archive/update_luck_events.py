#!/usr/bin/env python3
"""
Plan 45: 添加气运相关的随机事件到数据库
这些事件可以提升或降低玩家的气运
"""

import sqlite3
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.path_helper import get_user_data_dir

# 新增的气运相关事件定义
LUCK_EVENTS = [
    # ============ 正面事件 (提升气运) ============
    {
        "id": "luck_fortune_cat",
        "type": "random",
        "weight": 3,  # 稀有
        "data": {
            "id": "luck_fortune_cat",
            "title": "金猫送福",
            "text": "一只通体金黄的灵猫从虚空中走来，围着你转了三圈后消失不见，留下一股祥瑞之气。",
            "weight": 3,
            "min_layer": 0,
            "max_layer": 8,
            "effects": {
                "affection": 2,
                "text": "气运提升！"
            }
        }
    },
    {
        "id": "luck_shooting_star",
        "type": "random",
        "weight": 3,
        "data": {
            "id": "luck_shooting_star",
            "title": "流星许愿",
            "text": "一颗璀璨的流星划过天际，你下意识地许了一个愿望，似乎真的触动了什么天机。",
            "weight": 5,
            "min_layer": 1,
            "max_layer": 8,
            "effects": {
                "affection": 1,
                "exp": [50, 150],
                "text": "愿望成真！"
            }
        }
    },
    {
        "id": "luck_rainbow_bridge",
        "type": "random", 
        "weight": 2,  # 非常稀有
        "data": {
            "id": "luck_rainbow_bridge",
            "title": "七彩祥云",
            "text": "天边忽然出现瑰丽的七彩祥云，古籍记载这是天道降福的征兆！",
            "weight": 2,
            "min_layer": 2,
            "max_layer": 8,
            "effects": {
                "affection": 3,
                "money": [500, 1000],
                "text": "天道垂青！"
            }
        }
    },
    {
        "id": "luck_deity_blessing",
        "type": "random",
        "weight": 1,  # 极其稀有
        "data": {
            "id": "luck_deity_blessing",
            "title": "仙人抚顶",
            "text": "恍惚间，你似乎看到一位白发仙人对你微微点头，一股温暖的力量涌入识海。",
            "weight": 1,
            "min_layer": 3,
            "max_layer": 8,
            "unique": True,  # 全游戏只触发一次
            "effects": {
                "affection": 5,
                "mind": -10,
                "text": "仙缘降临！"
            }
        }
    },
    {
        "id": "luck_koi_transform",
        "type": "random",
        "weight": 4,
        "data": {
            "id": "luck_koi_transform",
            "title": "锦鲤附体",
            "text": "你在灵泉边看到了传说中的九色锦鲤，它竟然跃出水面撞向你的胸口！",
            "weight": 4,
            "min_layer": 0,
            "max_layer": 5,
            "effects": {
                "affection": 2,
                "text": "锦鲤附体！"
            }
        }
    },
    # ============ 负面事件 (降低气运) ============
    {
        "id": "luck_black_cat",
        "type": "random",
        "weight": 4,
        "data": {
            "id": "luck_black_cat",
            "title": "黑猫横路",
            "text": "一只黑猫忽然从你面前窜过，你心头莫名一紧，总觉得有什么不好的事要发生。",
            "weight": 4,
            "min_layer": 0,
            "max_layer": 8,
            "effects": {
                "affection": -1,
                "text": "晦气缠身..."
            }
        }
    },
    {
        "id": "luck_broken_mirror",
        "type": "random",
        "weight": 3,
        "data": {
            "id": "luck_broken_mirror",
            "title": "碎镜之兆",
            "text": "你洞府中的铜镜忽然无故碎裂，这是大凶之兆！",
            "weight": 3,
            "min_layer": 1,
            "max_layer": 8,
            "effects": {
                "affection": -2,
                "mind": 3,
                "text": "凶兆显现！"
            }
        }
    },
    {
        "id": "luck_karma_debt",
        "type": "random",
        "weight": 2,
        "data": {
            "id": "luck_karma_debt",
            "title": "因果反噬",
            "text": "冥冥中似有天道在审视你过往的业障，一股无形的压力侵入灵台。",
            "weight": 2,
            "min_layer": 2,
            "max_layer": 8,
            "effects": {
                "affection": -3,
                "exp": [-100, -50],
                "text": "业力反噬！"
            }
        }
    },
    # ============ 选择类事件 (玩家可以赌运气) ============
    {
        "id": "luck_gamble_fate",
        "type": "random",
        "weight": 5,
        "data": {
            "id": "luck_gamble_fate",
            "title": "天命赌局",
            "text": "一个神秘的赌徒出现在你面前：「想试试你的运气吗？赢了翻倍，输了归零。」",
            "weight": 5,
            "min_layer": 1,
            "max_layer": 6,
            "choices": [
                {
                    "text": "接受挑战",
                    "result": {
                        "success_chance": 0.5,
                        "success_effect": {
                            "text": "手气爆棚！你赢了！",
                            "affection": 3,
                            "money": [100, 300]
                        },
                        "fail_effect": {
                            "text": "手气太差，输得精光...",
                            "affection": -2,
                            "money": [-150, -50]
                        }
                    }
                },
                {
                    "text": "婉言拒绝",
                    "result": {
                        "success_chance": 1.0,
                        "success_effect": {
                            "text": "你选择了稳妥，赌徒消失了。"
                        }
                    }
                }
            ]
        }
    },
    {
        "id": "luck_wish_well",
        "type": "random",
        "weight": 6,
        "data": {
            "id": "luck_wish_well",
            "title": "许愿古井",
            "text": "你发现了一口传说中的许愿井，据说投入灵石可以转运...",
            "weight": 6,
            "min_layer": 0,
            "max_layer": 8,
            "choices": [
                {
                    "text": "投入100灵石",
                    "result": {
                        "success_chance": 0.6,
                        "success_effect": {
                            "text": "井水泛起金光，你的愿望被接受了！",
                            "affection": 2,
                            "money": -100
                        },
                        "fail_effect": {
                            "text": "井水毫无反应，灵石沉入井底...",
                            "affection": -1,
                            "money": -100
                        }
                    }
                },
                {
                    "text": "默默离开",
                    "result": {
                        "success_chance": 1.0,
                        "success_effect": {
                            "text": "你选择相信自己的实力。"
                        }
                    }
                }
            ]
        }
    }
]

def update_events_database():
    """更新数据库中的 event_definitions 表"""
    db_path = os.path.join(get_user_data_dir(), "user_data.db")
    
    if not os.path.exists(db_path):
        print(f"数据库不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for event in LUCK_EVENTS:
        data_json = json.dumps(event['data'], ensure_ascii=False)
        
        # 使用 INSERT OR REPLACE
        cursor.execute("""
            INSERT OR REPLACE INTO event_definitions 
            (id, type, weight, data_json)
            VALUES (?, ?, ?, ?)
        """, (
            event['id'],
            event['type'],
            event['weight'],
            data_json
        ))
        print(f"✓ 添加事件: {event['data']['title']}")
    
    conn.commit()
    conn.close()
    print(f"\n数据库已更新: {db_path}")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("Plan 45: 气运事件更新工具")
    print("=" * 50)
    
    print(f"\n添加 {len(LUCK_EVENTS)} 个气运相关事件...")
    update_events_database()
    
    print("\n✓ 完成!")
