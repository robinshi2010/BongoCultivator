import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import db_manager
from src.models import EventDefinition
from sqlmodel import select, delete

EVENTS_PATH = os.path.join(os.path.dirname(__file__), '../src/data/events.json')

def main():
    print("Starting Event Rebalance...")
    
    with open(EVENTS_PATH, 'r', encoding='utf-8') as f:
        events = json.load(f)
        
    print(f"Loaded {len(events)} existing events.")
    
    new_events = []
    existing_ids = set()
    
    # 1. Rebalance Existing
    for evt in events:
        etype = evt.get("type", "Common")
        
        # New Weights
        if etype == "Common":
            evt["weight"] = 100
        elif etype == "Uncommon":
            evt["weight"] = 40
        elif etype == "Rare":
            evt["weight"] = 10
        elif etype == "Unique":
            evt["weight"] = 2
        else:
            evt["weight"] = 100
            
        # Remove old 'chance' if exists
        evt.pop("chance", None)
        
        new_events.append(evt)
        existing_ids.add(evt['id'])
        
    # 2. Add New Resource Events (Tier 0-8)
    # Define templates
    templates = [
        {
            "suffix": "gathering", "title": "山野采药", "text": "你在野外发现了一丛灵气盎然的草药，小心翼翼地采摘了下来。", 
            "state": "IDLE" 
        },
        {
            "suffix": "mining", "title": "矿脉探寻", "text": "你感应到前方灵气波动，挥镐挖掘，竟是一块不错的灵矿。",
            "state": "WORK"
        },
        {
            "suffix": "hunting", "title": "狩猎妖兽", "text": "一只不开眼的妖兽袭击了你，被你随手斩杀，留下了妖丹材料。",
            "state": "COMBAT"
        }
    ]
    
    generated_count = 0
    for tier in range(9): # 0 to 8
        for tpl in templates:
            evt_id = f"evt_t{tier}_{tpl['suffix']}"
            
            # Check if exists (unlikely but safe)
            if evt_id in existing_ids:
                continue
                
            new_evt = {
                "id": evt_id,
                "title": tpl["title"],
                "type": "Uncommon", # Resource event
                "text": tpl["text"],
                "weight": 40,
                "min_layer": tier,
                "max_layer": tier, # Strict to tier
                "state": tpl["state"],
                "effects": {
                    "random_material": 1
                }
            }
            new_events.append(new_evt)
            generated_count += 1
            
    print(f"Generated {generated_count} new resource events.")
    print(f"Total events: {len(new_events)}")
    
    # 3. Save to JSON
    with open(EVENTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(new_events, f, indent=4, ensure_ascii=False)
        
    # 4. Update Database
    print("Updating Database...")
    try:
        with db_manager.get_session() as session:
            # For simplicity, clear all and re-insert is safest to ensure sync
            # But we must preserve history? History is in event_history table, separate.
            # So event_definitions safe to wipe.
            
            session.exec(delete(EventDefinition))
            
            for evt in new_events:
                db_evt = EventDefinition(
                    id=evt['id'],
                    type=evt['type'],
                    weight=evt['weight'],
                    data_json=json.dumps(evt, ensure_ascii=False)
                )
                session.add(db_evt)
                
            session.commit()
            print("Database updated successfully.")
    except Exception as e:
        print(f"Database update failed: {e}")

if __name__ == "__main__":
    main()
