import json
import os
import sys

# Define Rich Content Map
# Key: Tier (int), Value: Dict of Type -> (Title, Text)
CONTENT_MAP = {
    0: {
        "gathering": ("山野寻踪", "在后山悬崖边，你发现了一株沾着露水的止血草。"),
        "mining":    ("矿镐生风", "你在废弃矿坑的角落里，挖出了一块伴生铜矿。"),
        "hunting":   ("驱逐野兽", "一头野狼试图袭击村庄，被你随手一道符箓击杀。")
    },
    1: {
        "gathering": ("灵气探查", "这株灵草生长在灵泉旁，叶片上隐隐有流光转动。"),
        "mining":    ("深层矿脉", "深入地下百米，你终于敲开了坚硬的岩层，露出了灵石矿。"),
        "hunting":   ("斩杀妖兽", "这是一头开启了灵智的妖狐，它的皮毛是制作法袍的好材料。")
    },
    2: {
        "gathering": ("秘境采摘", "这处小型秘境中遍地是宝，你小心翼翼地采下了一株百灵草。"),
        "mining":    ("晶石共鸣", "手中的探灵盘疯狂转动，正如你所料，这里藏着玄铁精髓。"),
        "hunting":   ("兽潮余波", "你解决了一只落单的铁背苍熊，它的妖丹品质上乘。")
    },
    3: {
        "gathering": ("虚空拾遗", "空间裂隙旁生长着一朵虚空花，你冒着被割伤的风险将其摘下。"),
        "mining":    ("星屑提炼", "你从一块巨大的陨石碎片中，提炼出了珍贵的星辰砂。"),
        "hunting":   ("元婴妖修", "这只妖修竟已修出人形，可惜心术不正，被你替天行道。")
    },
    4: {
        "gathering": ("法则凝聚", "这并非普通的草木，而是木属性法则凝聚而成的结晶。"),
        "mining":    ("地心探索", "忍受着地心烈火的炙烤，你终于找到了传说中的炎阳玉。"),
        "hunting":   ("猎杀凶兽", "上古凶兽的血脉后裔极其强悍，一番苦战后你终于将其斩杀。")
    },
    5: {
        "gathering": ("星海采集", "在枯寂的星球表面，顽强生长着一株星灵草。"),
        "mining":    ("破碎星辰", "你直接炼化了一颗破碎的小行星，从中提取了庚金之精。"),
        "hunting":   ("虚空巨兽", "这头游荡在虚空中的巨兽体积堪比山岳，是你不可多得的战利品。")
    },
    6: {
        "gathering": ("神木遗枝", "传闻这是通天建木的残枝，虽生机已断，但主要材料依然珍贵。"),
        "mining":    ("空间晶壁", "你敲碎了位面壁垒，收集了一些掉落的空间晶石。"),
        "hunting":   ("挑战圣兽", "虽不是纯血圣兽，但这头拥有麒麟血脉的异兽也足以让你全力以赴。")
    },
    7: {
        "gathering": ("因果之花", "这朵花生长在因果线上，采摘它让你沾染了一丝莫名的因果。"),
        "mining":    ("时光之沙", "你在时间长河的支流旁，淘到了一把流逝的时光之沙。"),
        "hunting":   ("天魔化身", "域外天魔试图夺舍，你的神识化剑将其斩灭，留下了纯净的神魂结晶。")
    },
    8: {
        "gathering": ("混沌青莲", "在混沌虚无之中，你有幸见到了一株青莲的虚影，截取了一缕气息。"),
        "mining":    ("鸿蒙紫气", "万物初开不仅有紫气，还有伴生的鸿蒙石，是炼制神器的基材。"),
        "hunting":   ("大道之争", "阻道者杀无赦！你斩杀了一名试图阻碍你飞升的强敌，掠夺了他的气运。")
    }
}

def enrich_events():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "src/data/events.json")
    
    print(f"Reading events from: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        events = json.load(f)
        
    updated_count = 0
    
    for event in events:
        evt_id = event.get("id", "")
        
        # Check if it matches generic event pattern: evt_t{tier}_{type}
        # e.g. evt_t0_gathering
        if not evt_id.startswith("evt_t"):
            continue
            
        parts = evt_id.split("_")
        if len(parts) < 3: 
            continue
            
        # parts[0] = evt
        # parts[1] = t0..t8
        # parts[2] = gathering/mining/hunting
        
        try:
            tier_str = parts[1]
            evt_type = parts[2]
            
            if not tier_str.startswith("t") or evt_type not in ["gathering", "mining", "hunting"]:
                continue
                
            tier = int(tier_str[1:])
            
            if tier in CONTENT_MAP and evt_type in CONTENT_MAP[tier]:
                new_title, new_text = CONTENT_MAP[tier][evt_type]
                event["title"] = new_title
                event["text"] = new_text
                updated_count += 1
                
        except ValueError:
            continue
            
    # Save back
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=4)
        
    print(f"Updated {updated_count} events.")

if __name__ == "__main__":
    enrich_events()
