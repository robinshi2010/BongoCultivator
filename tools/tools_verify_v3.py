import sqlite3
import json

DB_PATH = 'user_data.db'

def verify():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check item count per tier
    print("=== Item Count Per Tier ===")
    cursor.execute("SELECT tier, COUNT(*) from item_definitions GROUP BY tier ORDER BY tier")
    rows = cursor.fetchall()
    for r in rows:
        print(f"Tier {r[0]}: {r[1]} items")
        
    # Check recipe count
    print("\n=== Recipe Check ===")
    cursor.execute("SELECT COUNT(*) from recipes")
    count = cursor.fetchone()[0]
    print(f"Total Recipes: {count}")
    
    # Sample check a complex recipe
    print("\n=== Sample Recipe (Tier 8) ===")
    cursor.execute("SELECT result_item_id, ingredients_json FROM recipes WHERE result_item_id='pill_final_destiny'")
    res = cursor.fetchone()
    if res:
        print(f"Recipe for {res[0]}: {res[1]}")
    else:
        print("Error: pill_final_destiny recipe not found!")
        
    conn.close()

if __name__ == "__main__":
    verify()
