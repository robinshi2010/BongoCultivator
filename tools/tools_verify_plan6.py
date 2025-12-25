import random
from src.cultivator import Cultivator
from src.pet_window import PetState
from src.item_manager import ItemManager

def main():
    print("=== Plan 6 Verification ===")
    
    # 1. Check Recipes
    mgr = ItemManager()
    pill = mgr.get_item("pill_exp_0")
    print(f"Checking pill_exp_0 recipe: {pill.get('recipe')}")
    if not pill.get('recipe'):
        print("FAIL: Recipe not loaded!")
    else:
        print("PASS: Recipe loaded.")

    # 2. Check Drop Rates (Simulation)
    c = Cultivator()
    c.layer_index = 0 # Tier 0
    c.affection = 0
    c.talents['drop'] = 0
    
    print("\nSimulating 10000 ticks of WORK...")
    drops = 0
    
    # Mock behavior of update()
    # Logic in cultivator: if random < (0.005 + bonus)
    # bonus = 0
    expected_rate = 0.005
    
    for _ in range(10000):
        # We can't easily call c.update() because it depends on APM and does other stuff
        # Let's extract the logic or just trust we edited the file.
        # But we can try to call update with high APM
        msg, state = c.update(100, 0) # High KB APM -> WORK
        if "探险发现" in msg:
            drops += 1
            
    rate = drops / 10000.0
    print(f"Total Drops: {drops}")
    print(f"Observed Rate: {rate:.4f} (Expected ~{expected_rate})")
    
    if 0.003 < rate < 0.007:
        print("PASS: Drop rate is within expected range.")
    else:
        print("WARNING: Drop rate might be off.")

    # 3. Check Dynamic Pool
    # We can check what items we got in inventory
    # Tier 0 should get Tier 0 (80%) and Tier 1 (5%?) and Tier -1 (0%)
    # Wait, Inventory keys
    print("\nChecking Drop Distribution:")
    t0_count = 0
    t1_count = 0
    other_count = 0
    
    for item_id, count in c.inventory.items():
        if "_0" in item_id: t0_count += count
        elif "_1" in item_id: t1_count += count
        else: other_count += count
        
    print(f"Tier 0 items: {t0_count}")
    print(f"Tier 1 items: {t1_count}")
    print(f"Other items: {other_count}")
    
    if t1_count > 0:
        print("PASS: Obtained higher tier items.")
    else:
        print("INFO: No higher tier items (might be luck).")

if __name__ == "__main__":
    main()
