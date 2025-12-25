import os
import subprocess
import sqlite3
from src.database import db_manager
from src.item_manager import ItemManager

def main():
    # 1. Generate JSON
    print("Generating Items...")
    subprocess.run(["python3", "tools_generate_items.py"], check=True)

    # 2. Clear DB Tables
    print("Clearing DB Tables...")
    try:
        with db_manager._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM item_definitions")
            cursor.execute("DELETE FROM recipes")
            conn.commit()
    except Exception as e:
        print(f"Error clearing DB: {e}")
        return

    # 3. Trigger Import
    print("Importing to DB...")
    # Reset singleton state if possible or just call methods
    mgr = ItemManager()
    mgr.flat_items = {} 
    mgr.tier_lists = {}
    for i in range(9):
        mgr.tier_lists[i] = {"materials": [], "pills": []}
        
    mgr.import_from_json()
    mgr._load_from_db()

    print(f"Done. Loaded {len(mgr.flat_items)} items.")
    
    # Verify a value
    p0 = mgr.get_item("pill_exp_0")
    if p0:
        print(f"Tier 0 Pill EXP: {p0['effect'].get('exp')}")
        # Expected ~2000 (1% of 200,000)
    
    p2 = mgr.get_item("pill_exp_2")
    if p2:
        print(f"Tier 2 Pill EXP: {p2['effect'].get('exp')}")
        # Expected ~60,000 (1% of 6,000,000)

if __name__ == "__main__":
    main()
