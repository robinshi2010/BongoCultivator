
import sqlite3
import os

DB_PATH = "user_data.db"

def fix_inventory():
    print("Fixing inventory IDs...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Map Old -> New
    mapping = {
        "flower_blood": "flower_blood_0",
        "weed_wash": "herb_marrow_0",
        "ore_iron": "ore_iron_essence",
        "iron_essence": "ore_iron_essence",
        # Add more if found
        "pill_speed_0": "pill_speed_wind",
        "herb_spirit": "herb_marrow_0"
    }
    
    # Get current inventory
    cursor.execute("SELECT item_id, count FROM player_inventory")
    rows = cursor.fetchall()
    
    for item_id, count in rows:
        if item_id in mapping:
            new_id = mapping[item_id]
            print(f"Migrating {item_id} -> {new_id} ({count})")
            
            # Check if new_id already exists to merge count
            cursor.execute("SELECT count FROM player_inventory WHERE item_id = ?", (new_id,))
            res = cursor.fetchone()
            if res:
                # Merge
                new_count = res[0] + count
                cursor.execute("UPDATE player_inventory SET count = ? WHERE item_id = ?", (new_count, new_id))
                cursor.execute("DELETE FROM player_inventory WHERE item_id = ?", (item_id,))
            else:
                # Rename
                cursor.execute("UPDATE player_inventory SET item_id = ? WHERE item_id = ?", (new_id, item_id))
                
    conn.commit()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    fix_inventory()
