import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.item_manager import ItemManager
# Ensure DB is initialized or let ItemManager handle it
from src.database import db_manager

def main():
    im = ItemManager()
    
    # 1. Get all recipes
    # Access via flat_items for audit
    all_items = im.flat_items
    
    recipes = []
    for iid, info in all_items.items():
        if 'recipe' in info:
            recipes.append(info)
            
    print(f"Found {len(recipes)} items with recipes.")
    
    # 2. Collect all ingredients
    needed_ingredients = set()
    for item in recipes:
        recipe = item['recipe'] # dict {id: count}
        for ing_id in recipe.keys():
            needed_ingredients.add(ing_id)
            
    print(f"Total unique ingredients needed: {len(needed_ingredients)}")
    
    # 3. Check availability
    dropable_items = set()
    for tier, lists in im.tier_lists.items():
        for mid in lists["materials"]:
            dropable_items.add(mid)
        for mid in lists["pills"]:
            dropable_items.add(mid)
            
    missing = []
    for ing_id in needed_ingredients:
        if ing_id in dropable_items:
            continue
        missing.append(ing_id)
        
    if missing:
        print(f"WARNING: {len(missing)} ingredients might be missing from generic drop pools:")
        for m in missing:
            info = all_items.get(m, {})
            print(f" - {m} ({info.get('name')}) Tier: {info.get('tier')} Type: {info.get('type')}")
    else:
        print("SUCCESS: All recipe ingredients are in generic drop/market pools.")

if __name__ == "__main__":
    main()
