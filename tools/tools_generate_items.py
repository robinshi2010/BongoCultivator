import json
import os

# Plan 4 EXP Table
EXP_TABLE = [
    200000,      # 0: 炼气
    1400000,     # 1: 筑基
    6000000,     # 2: 金丹
    6000000,     # 3: 元婴
    9000000,     # 4: 化神
    13500000,    # 5: 炼虚
    20250000,    # 6: 合体
    30375000,    # 7: 大乘
    999999999    # 8: 渡劫
]

# Tiers: Name, EnName, BasePrice, BaseExp (Calculated later), PillPrice
# We will dynamic calc BaseExp in loop
TIERS_INFO = [
    ("炼气", "Qi Refining", 100),       
    ("筑基", "Foundation", 500),
    ("金丹", "Golden Core", 2000),
    ("元婴", "Nascent Soul", 5000),
    ("化神", "Spirit Severing", 10000),
    ("炼虚", "Void Training", 20000),
    ("合体", "Integration", 50000),
    ("大乘", "Mahayana", 100000),
    ("渡劫", "Tribulation", 500000)
]

def generate_tier_items(tier_idx, tier_info):
    name_cn, name_en, base_price_factor = tier_info
    
    # Calc Values
    max_exp = EXP_TABLE[tier_idx] if tier_idx < len(EXP_TABLE) else EXP_TABLE[-1]
    
    # 丹药经验: 1% 当前等级总经验
    base_exp = int(max_exp * 0.01)
    
    # 丹药价格: 基础因子 * 1.5
    pill_price = int(base_price_factor * 1.5)
    
    base_price = base_price_factor # Material price base
    
    items = []
    pills = []
    
    # Prefix for IDs
    p = f"t{tier_idx}"
    
    # 1. Spirit Item (Herb) - Common
    herb = {
        "id": f"herb_spirit_{tier_idx}",
        "name": f"{name_cn}灵草",
        "type": "consumable", # Or material, but consumable for exp
        "tier": tier_idx,
        "price": int(base_price),
        "desc": f"生长在灵气充裕之地的草药，适合{name_cn}期修士吞服。",
        "effect": {"exp": int(base_exp * 0.1), "mind_dmg": 1} # Herb gives 10% of pill
    }
    items.append(herb)
    
    # 2. Spirit Item (Fruit) - Rare
    fruit = {
        "id": f"fruit_essence_{tier_idx}",
        "name": f"{name_cn}元果",
        "type": "consumable",
        "tier": tier_idx,
        "price": int(base_price * 5),
        "desc": f"凝聚了天地日月的精华，{name_cn}期的大补之物。",
        "effect": {"exp": int(base_exp * 0.5)} # Fruit gives 50% of pill
    }
    items.append(fruit)
    
    # 3. Monster Material
    monster_mat = {
        "id": f"mat_monster_{tier_idx}",
        "name": f"{name_cn}妖丹",
        "type": "material",
        "tier": tier_idx,
        "price": int(base_price * 8),
        "desc": f"{name_cn}期妖兽的内丹，炼丹主材。"
    }
    items.append(monster_mat)
    
    # --- Pills ---
    
    # 1. Exp Pill (Standard)
    pill_exp = {
        "id": f"pill_exp_{tier_idx}",
        "name": f"{name_cn}聚气丹",
        "type": "consumable",
        "tier": tier_idx,
        "price": pill_price,
        "desc": f"大幅精进{name_cn}期修为 (约1%)。",
        "effect": {"exp": base_exp},
        "recipe": {herb["id"]: 3}
    }
    pills.append(pill_exp)
    
    # 2. Heal / Mind Pill
    pill_mind = {
        "id": f"pill_mind_{tier_idx}",
        "name": f"{name_cn}清心丹",
        "type": "consumable",
        "tier": tier_idx,
        "price": int(pill_price * 0.8),
        "desc": "抚平心魔，稳固道心。",
        "effect": {"mind_heal": 10 + tier_idx * 5},
        "recipe": {herb["id"]: 2, fruit["id"]: 1}
    }
    pills.append(pill_mind)
    
    # 3. Buff Speed
    pill_speed = {
        "id": f"pill_speed_{tier_idx}",
        "name": f"{name_cn}神行散",
        "type": "buff",
        "tier": tier_idx,
        "price": int(pill_price * 1.2),
        "desc": "短时间内大幅提升机缘(掉落率)。",
        "effect": {"buff": "drop_boost", "value": 0.2 + (tier_idx * 0.05), "duration": 1800},
        "recipe": {monster_mat["id"]: 1, herb["id"]: 2}
    }
    pills.append(pill_speed)
    
    # 4. Buff Idle
    pill_idle = {
        "id": f"pill_idle_{tier_idx}",
        "name": f"{name_cn}辟谷丹",
        "type": "buff",
        "tier": tier_idx,
        "price": pill_price,
        "desc": "提升闭关挂机收益。",
        "effect": {"buff": "idle_boost", "value": 0.1 + (tier_idx * 0.05), "duration": 3600},
        "recipe": {fruit["id"]: 2}
    }
    pills.append(pill_idle)
    
    # 5. Breakthrough Pill (Next Tier)
    if tier_idx < 8:
        # Use TIERS_INFO for next name
        next_tier_name = TIERS_INFO[tier_idx+1][0]
        pill_break = {
            "id": f"pill_break_{tier_idx}",
            "name": f"{next_tier_name}突破丹", # e.g. 筑基突破丹 (Targeting Next)
            "type": "breakthrough",
            "tier": tier_idx,
            "price": pill_price * 10,
            "desc": f"辅助突破瓶颈，晋升{next_tier_name}。",
            "effect": {"breakthrough": f"tier_{tier_idx+1}", "chance_add": 20 + tier_idx},
            "recipe": {monster_mat["id"]: 5, fruit["id"]: 5, herb["id"]: 10}
        }
        pills.append(pill_break)
        
    return items, pills

def main():
    full_data = {}
    
    for idx, info in enumerate(TIERS_INFO):
        key = f"tier_{idx}"
        mats, pills = generate_tier_items(idx, info)
        full_data[key] = {
            "materials": mats,
            "pills": pills
        }
        
    # Write to file
    out_path = os.path.join("src", "data", "items_v2.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(full_data, f, indent=4, ensure_ascii=False)
    
    print(f"Generated {out_path}")

if __name__ == "__main__":
    main()
