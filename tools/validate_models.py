from src.database import db_manager
from src.models import PlayerStatus, PlayerInventory
from src.cultivator import Cultivator
from src.services.event_engine import EventEngine
from src.item_manager import ItemManager
from src.config import LAYERS

def test_models():
    print("Testing SQLModel initialization...")
    # Initialize DB (should create tables if not exist)
    db_manager._init_db()
    
    with db_manager.get_session() as session:
        p = session.get(PlayerStatus, 1)
        if p:
            print(f"Player loaded: Layer {p.layer_index} ({LAYERS[p.layer_index]})")
        else:
            print("Player not found (should have been created by init)")

def test_cultivator_save_load():
    print("\nTesting Cultivator Save/Load...")
    c = Cultivator()
    # Modify something
    c.money += 100
    c.exp += 500
    c.save_data()
    print("Saved.")
    
    c2 = Cultivator()
    c2.load_data()
    print(f"Loaded: Money={c2.money}, Exp={c2.exp}")
    
    assert c2.money == c.money
    assert c2.exp == c.exp
    print("Cultivator Persistence Validated.")

if __name__ == "__main__":
    try:
        test_models()
        test_cultivator_save_load()
        print("\nALL TESTS PASSED.")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
