from src.services.event_engine import EventEngine
from src.database import DB_FILE
from src.item_manager import ItemManager
import os

class MockCultivator:
    def __init__(self, layer=0, mind=0, luck=0, body=10):
        self.layer_index = layer
        self.mind = mind
        self.affection = luck
        self.body = body
        self.money = 0
        self.inventory = {}
        
    def gain_exp(self, val):
        print(f"  [Cultivator] Gain Exp: {val}")
        
    def gain_item(self, iid, count):
        print(f"  [Cultivator] Gain Item: {iid} x{count}")

def verify():
    if not os.path.exists(DB_FILE):
        print(f"DB not found at {DB_FILE}")
        return

    item_mgr = ItemManager()
    engine = EventEngine(DB_FILE, item_mgr)
    
    print(f"Loaded {len(engine.events)} events.")
    
    # Test Tier 0
    print("\n--- Testing Tier 0 (Qi Refining) ---")
    c0 = MockCultivator(layer=0, mind=0)
    # Try multiple ticks
    for _ in range(200): # High count to ensure hits
        evt = engine.check_triggers(c0, "IDLE")
        if evt:
            print(f"Triggered: {evt['title']}")
            res = engine.trigger_event(evt, c0)
            print(f"Result: {res}")
            break
            
    # Test Tier 5 (Void) - Unique
    print("\n--- Testing Tier 5 (Void) - Unique / Rare ---")
    c5 = MockCultivator(layer=5, mind=60) # High mind for '彼岸花开'
    start_history_len = len(engine.history)
    
    hit = False
    for _ in range(500):
        evt = engine.check_triggers(c5, "WORK") # Some envt requires WORK
        if evt:
            if evt['is_unique']:
                print(f"UNIQUE HIT: {evt['title']}")
                res = engine.trigger_event(evt, c5)
                print(f"Result: {res}")
                hit = True
                break
            elif evt['type'] == 'Rare':
                print(f"Rare HIT: {evt['title']}")
                
    if not hit:
        print("No Unique/Rare event triggered in samples.")

if __name__ == "__main__":
    verify()
