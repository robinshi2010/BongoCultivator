import json
import sqlite3
import os
import sys

# Define file paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS_V1_PATH = os.path.join(BASE_DIR, "src", "data", "items.json")
ITEMS_V2_PATH = os.path.join(BASE_DIR, "src", "data", "items_v2.json")
DB_PATH = os.path.join(BASE_DIR, "user_data.db")

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return {}

def main():
    print("Starting Item Consolidation Tool...")
    
    # 1. Load both JSON files
    v1_data = load_json(ITEMS_V1_PATH)
    v2_data = load_json(ITEMS_V2_PATH)
    
    combined_items = {}
    
    # Helper to process tier data
    def process_tier_data(tier_data, source_name):
        count = 0
        if not tier_data: return 0
        
        # Process materials, pills, etc.
        for category in ["materials", "pills", "equipments", "books"]:
            if category in tier_data:
                for item in tier_data[category]:
                    item_id = item.get("id")
                    if not item_id: continue
                    
                    # If item exists, update it (merge strategy: v1 overrides v2 if partial, or just replace)
                    # Here we simply upsert based on ID. V1 is processed first, V2 second?
                    # Actually, we want a clean list.
                    
                    # Let's ensure 'effect' and 'recipe' are JSON strings for DB
                    effect_val = json.dumps(item.get("effect", {})) if isinstance(item.get("effect"), dict) else item.get("effect", "{}")
                    recipe_val = json.dumps(item.get("recipe", {})) if isinstance(item.get("recipe"), dict) else item.get("recipe", "{}")
                    
                    combined_items[item_id] = {
                        "id": item_id,
                        "name": item.get("name"),
                        "type": item.get("type"),
                        "tier": item.get("tier"),
                        "price": item.get("price"),
                        "description": item.get("desc"),
                        "effect": effect_val,
                        "recipe": recipe_val
                    }
                    count += 1
        return count

    # 2. Process V2 first (Standard items)
    print("Processing items_v2.json...")
    total_v2 = 0
    for tier, data in v2_data.items():
        total_v2 += process_tier_data(data, "v2")
    print(f" Loaded {total_v2} items from V2.")

    # 3. Process V1 second (Handcrafted items, should override or add to V2)
    print("Processing items.json...")
    total_v1 = 0
    for tier, data in v1_data.items():
        total_v1 += process_tier_data(data, "v1")
    print(f" Loaded {total_v1} items from V1 (Merged/Overridden).")
    
    print(f"Total Unique Items to sync: {len(combined_items)}")

    # 4. Sync to Database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create table if not exists (simplified schema match)
        # 4a. Sync Items
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS item_definitions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                tier INTEGER DEFAULT 0,
                description TEXT,
                price INTEGER DEFAULT 0,
                effect_json TEXT
            )
        """)
        
        cursor.execute("DELETE FROM item_definitions")
        print("Cleared existing 'item_definitions' table.")
        
        inserted_items = 0
        for item in combined_items.values():
            cursor.execute("""
                INSERT INTO item_definitions (id, name, type, tier, description, price, effect_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                item["id"], item["name"], item["type"], item["tier"], 
                item["description"], item["price"], item["effect"]
            ))
            inserted_items += 1
            
        # 4b. Sync Recipes (New Logic)
        # Note: Existing schema uses result_item_id as PK and ingredients_json
        cursor.execute("DELETE FROM recipes")
        print("Cleared existing 'recipes' table.")
        
        inserted_recipes = 0
        for item in combined_items.values():
            # If item has a recipe (valid dict string)
            recipe_str = item["recipe"]
            if recipe_str and recipe_str != "{}":
                # Check if recipe already exists for this item (since PK is result_item_id)
                # But we just cleared the table.
                
                cursor.execute("""
                    INSERT INTO recipes (result_item_id, ingredients_json, craft_time, success_rate)
                    VALUES (?, ?, ?, ?)
                """, (item["id"], recipe_str, 5, 1.0)) # Default 5s craft, 100% success
                inserted_recipes += 1

        conn.commit()
        print(f"Successfully inserted {inserted_items} items and {inserted_recipes} recipes into database.")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

    # 5. Backup json files (Renaming them to .bak so system doesn't rely on them anymore, or keeping them as archive?)
    # User said "don't want so many files".
    # We will rename them to .bak to indicate they are deprecated sources.
    # But wait, the game code (item_manager.py) might STILL be trying to load them.
    # We need to CHECK item_manager.py first! 
    # For now, let's just do the DB sync. The code update is a separate step.
    
if __name__ == "__main__":
    main()
