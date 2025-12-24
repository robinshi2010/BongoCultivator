from src.item_manager import ItemManager
from src.database import db_manager

def main():
    print("Initializing ItemManager...")
    mgr = ItemManager()
    
    print(f"Total Items in memory: {len(mgr.flat_items)}")
    
    # Verify DB content
    with db_manager._get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM item_definitions")
        count = cursor.fetchone()[0]
        print(f"Total Items in DB: {count}")
        
    # Check a specific item
    t0_pill = mgr.get_item("pill_exp_0")
    if t0_pill:
        print("Found pill_exp_0:", t0_pill.get("name"))
    else:
        print("ERROR: pill_exp_0 not found!")

if __name__ == "__main__":
    main()
