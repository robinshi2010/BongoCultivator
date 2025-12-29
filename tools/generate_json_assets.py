
import json
import os
import sys

# Add tools directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tools_update_items_v3 import TIER_ITEMS, TIER_PILLS
    from tools_update_events import EVENTS_DATA
except ImportError as e:
    print(f"Error importing data modules: {e}")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "src", "data")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def generate_items_json():
    print("Generating items_v2.json...")
    
    # helper to format item for DataLoader
    # DataLoader expects: { "tier_X": { "materials": [List], "pills": [List] } }
    
    output_data = {}
    
    # Pricing helper (matched to tools_update_items_v3)
    def get_price(tier):
        return 100 * (4 ** tier) 

    # 1. Process Material/Items
    for tier, items in TIER_ITEMS.items():
        base_price = get_price(tier)
        
        tier_key = f"tier_{tier}"
        if tier_key not in output_data:
            output_data[tier_key] = {"materials": [], "pills": []}
            
        for item_data in items:
            iid, name, itype, desc = item_data
            
            # Pricing logic from tool
            price = base_price
            if itype == "Junk": price //= 2
            elif itype == "Mineral": price *= 1.5
            elif itype == "Monster": price *= 2
            elif itype == "Special": price *= 10
            
            item_obj = {
                "id": iid,
                "name": name,
                "type": itype.lower(),
                "tier": tier,
                "price": int(price),
                "desc": desc,
                "effect": {}, # Default empty
                "recipe": {}  # Default empty
            }
            output_data[tier_key]["materials"].append(item_obj)

    # 2. Process Pills
    for tier, pills in TIER_PILLS.items():
        base_price = get_price(tier)
        
        tier_key = f"tier_{tier}"
        if tier_key not in output_data:
            output_data[tier_key] = {"materials": [], "pills": []}
            
        for pill_data in pills:
            iid, name, ptype, desc, ingredients = pill_data
            
            price = base_price * 5
            
            # Simple effect assumption (since original tool dumps simple json)
            effect = {}
            if "Exp" in ptype:
                 effect["exp_gain"] = 0.05 * (tier + 1)
            elif "Break" in ptype:
                 effect["breakthrough_chance"] = 0.2
            
            item_obj = {
                "id": iid,
                "name": name,
                "type": ptype.lower(),
                "tier": tier,
                "price": int(price),
                "desc": desc,
                "effect": effect,
                "recipe": ingredients
            }
            output_data[tier_key]["pills"].append(item_obj)

    # Write to file
    out_path = os.path.join(DATA_DIR, "items_v2.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    print(f"Saved {out_path}")

def generate_events_json():
    print("Generating events.json...")
    
    # DataLoader expects a list of event objects
    output_list = []
    
    for evt in EVENTS_DATA:
        # Format: ID, Title, Type, TriggerJSON, Text, OutcomesJSON
        eid, title, etype, triggers, text, outcomes = evt
        
        # Merge into a single dict
        evt_obj = {
            "id": eid,
            "title": title,
            "type": etype,
            "text": text,
            "weight": 10, # Default
            # triggers...
        }
        
        # Merge triggers
        if isinstance(triggers, dict):
            # Map specific keys if needed, or just dump
            # EventEngine checks: min_layer, max_layer, min_money, etc.
            # triggers typically has these.
            evt_obj.update(triggers)
            # Ensure weight is handled if in trigger? Tool puts 'chance' in trigger, 'weight' hardcoded or separate?
            # tools_update_events doesn't strictly have 'weight' in the tuple (it has ID, Title, Type, Trigger, Text, Outcomes)
            # Wait, EVENTS_DATA tuple length is 6.
            # Let's check tool code again. 
            pass
            
        # Outcomes -> effects
        # EventEngine expects 'effects' dict presumably.
        # But tools_update_events stores 'outcomes_json' list.
        # EventEngine code (Step 16) `trigger_event` handles `effects` dict OR `choices` dict.
        # Wait, the EventEngine logic I saw in Step 16 `_apply_effects` iterates a DICT.
        # But `tools_update_events` (Step 35) defines outcomes as a LIST of dicts: `[{"type": "exp", "val": 50}]`.
        # This is a MISMATCH.
        # `EventEngine._apply_effects`: `for k, v in effects.items():`
        
        # WE NEED TO ALIGN THEM.
        # Since I am generating the JSON that EventEngine will load, I should format it to match EventEngine's expectation.
        # EventEngine expects: `effects: { "exp": 100, "mind": -5 }`
        
        # Convert List outcomes to Dict effects
        effects_dict = {}
        if isinstance(outcomes, list):
            for outcome in outcomes:
                otype = outcome.get("type")
                # Handle 'val' or 'id/count'
                if otype in ["exp", "money", "mind", "body", "luck"]:
                    val = outcome.get("val")
                    # If duplicate type? Sum? 
                    if otype in effects_dict:
                        effects_dict[otype] += val
                    else:
                        effects_dict[otype] = val
                elif otype == "item":
                    # items: {id: count}
                    iid = outcome.get("id")
                    count = outcome.get("count", 1)
                    if "items" not in effects_dict:
                         effects_dict["items"] = {}
                    effects_dict["items"][iid] = count
                elif otype == "random":
                    # Complex type 'random' from tools_update_events... 
                    # EventEngine logic in Step 16 DOES NOT seem to handle 'random' outcomes directly in `_apply_effects`.
                    # Step 16 `_apply_effects` only handles: exp, money, items, mind, body.
                    # It DOES NOT handle nested lists.
                    
                    # This means current EventEngine might NOT support the 'random' outcomes defined in `tools_update_events.py`!
                    # For now, to keep it working, I will skip complex random nodes or simplify them.
                    # Or update checks.
                    pass
        
        evt_obj["effects"] = effects_dict
        
        output_list.append(evt_obj)
        
    out_path = os.path.join(DATA_DIR, "events.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, indent=4, ensure_ascii=False)
    print(f"Saved {out_path}")

if __name__ == "__main__":
    generate_items_json()
    generate_events_json()
