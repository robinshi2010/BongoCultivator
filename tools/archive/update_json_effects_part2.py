
import json

UPDATES = {
    # Corrections
    "pill_dimension_step": {"affection": 15}, # 界游丹
    "pill_reborn_heaven": {"stat_body": 20, "mind_heal": 20}, # 回天再造丸
    "water_creation": {"stat_body": 10, "affection": 10}, # 造化神泉
    "pill_long_life": {"stat_body": 50}, # 长生丹
    "pill_time_back": {"mind_heal": 100}, # 回溯丹
    "liquid_thunder": {"stat_body": 20, "exp_gain": 0.20}, # 天劫雷液
}

def update_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    count = 0
    # Data is structured as: "tier_0": { "materials": [], "pills": [] }
    for tier, content in data.items():
        if isinstance(content, dict):
            for category in ["materials", "pills"]:
                if category in content:
                    for item in content[category]:
                        item_id = item["id"]
                        if item_id in UPDATES:
                            item["effect"] = UPDATES[item_id]
                            count += 1
                            print(f"Updated JSON: {item['name']} ({item_id})")
                            
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Updated {count} items in JSON.")

if __name__ == "__main__":
    update_json_file("src/data/items_v2.json")
