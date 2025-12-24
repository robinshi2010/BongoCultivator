from src.cultivator import Cultivator
from src.database import db_manager
import time

def main():
    print("Initializing Cultivator...")
    c = Cultivator()
    
    # Manually trigger load with old path to test migration
    old_save = "save_data.json"
    print(f"Loading data (Migration check from {old_save})...")
    c.load_data(old_save)
    
    print("-" * 20)
    print(f"Layer Index: {c.layer_index}")
    print(f"Current Layer: {c.current_layer}")
    print(f"Exp: {c.exp} / {c.max_exp}")
    print(f"Inventory Count: {len(c.inventory)}")
    
    # Check if DB is populated
    with db_manager._get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM player_inventory")
        inv_count = cursor.fetchone()[0]
        print(f"DB Inventory Count: {inv_count}")
        
        cursor.execute("SELECT layer_index FROM player_status WHERE id=1")
        row = cursor.fetchone()
        print(f"DB Layer Index: {row[0]}")

    print("-" * 20)
    print("Testing functionality...")
    # Test market refresh with new tier logic
    c.refresh_market()
    print(f"Market refreshed. Goods: {len(c.market_goods)}")
    if c.market_goods:
        print("Sample good:", c.market_goods[0]['id'], c.market_goods[0]['price'])

if __name__ == "__main__":
    main()
