import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.logger import logger
from src.services.data_loader import DataLoader
from src.services.dialogue_manager import dialogue_manager
from src.database import db_manager

def test_dialogue_system():
    # 1. Force Load Data (Simulate Update)
    print("Forcing Data Load...")
    DataLoader.DATA_VERSION = "999" # Force update
    DataLoader.check_data_update()
    
    # 2. Reload Manager
    print("Reloading Dialogue Manager...")
    dialogue_manager.reload()
    
    # 3. Check Dialogues
    print(f"Loaded {len(dialogue_manager.dialogues)} dialogues.")
    
    # 4. Simulate Context
    class MockCultivator:
        layer_index = 0
        mind = 0
        current_state_name = "IDLE"
        
    cult = MockCultivator()
    print(f"Testing for Layer 0 (Qi Refining)...")
    for _ in range(5):
        print(" -> " + dialogue_manager.get_random_dialogue(cult))
        
    cult.layer_index = 8 
    cult.mind = 90
    print(f"Testing for Layer 8 + Mind 90 (Crazy)...")
    for _ in range(5):
        print(" -> " + dialogue_manager.get_random_dialogue(cult))

if __name__ == "__main__":
    test_dialogue_system()
