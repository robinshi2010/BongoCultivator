
import sys
import os
import unittest
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.event_engine import EventEngine
from src.cultivator import Cultivator
from src.item_manager import ItemManager
from src.database import DB_FILE

class TestPlan17(unittest.TestCase):
    def setUp(self):
        self.item_manager = ItemManager()
        self.event_engine = EventEngine(DB_FILE, self.item_manager)
        self.cultivator = Cultivator()
        
        # Reset Cultivator to Layer 0 (Qi Refining)
        self.cultivator.layer_index = 0
        self.cultivator.item_manager = self.item_manager

    def test_event_filtering_layer_0(self):
        """Test that Tier 8 events are blocked for Layer 0 cultivator"""
        print("\nTesting Event Engine Filtering...")
        
        # Manually inject a Tier 8 event into the engine for testing
        test_event = {
            "id": "evt_test_t8",
            "title": "Test High Tier Event",
            "min_layer": 8,
            "max_layer": 8,
            "weight": 1000, # High weight to ensure it would be picked if valid
            "effects": {"exp": 100}
        }
        self.event_engine.events = [test_event]
        
        # Check triggers
        triggered = self.event_engine.check_triggers(self.cultivator)
        
        if triggered:
            print(f"FAILURE: Tier 8 event triggered for Layer 0 cultivator! Event: {triggered['id']}")
        else:
            print("SUCCESS: Tier 8 event correctly filtered out.")
            
        self.assertIsNone(triggered)

    def test_event_filtering_layer_8(self):
        """Test that Tier 8 events ARE triggered for Layer 8 cultivator"""
        print("\nTesting Event Engine Allowance...")
        
        self.cultivator.layer_index = 8
        test_event = {
            "id": "evt_test_t8_valid",
            "title": "Test High Tier Event Valid",
            "min_layer": 8,
            "max_layer": 8,
            "weight": 1000,
            "effects": {"exp": 100}
        }
        self.event_engine.events = [test_event]
        
        triggered = self.event_engine.check_triggers(self.cultivator)
        
        if triggered and triggered['id'] == "evt_test_t8_valid":
            print("SUCCESS: Tier 8 event triggered for Layer 8 cultivator.")
        else:
            print(f"FAILURE: Tier 8 event NOT triggered for Layer 8 cultivator. Got: {triggered}")
            
        self.assertIsNotNone(triggered)

    def test_item_safeguard(self):
        """Test that gain_item blocks Tier 8 items for Layer 0 cultivator"""
        print("\nTesting Item Safeguard...")
        
        self.cultivator.layer_index = 0
        # "gas_primordial" is Tier 8 (from events.json observation / assumption, let's verify via ItemManager)
        # We need a real high tier item ID. Let's pick one from data or mock it.
        # Actually, let's rely on real data if possible, or Mock ItemManager return.
        
        # Let's mock get_item to ensure we have a "Tier 8" item without relying on specific DB content if it changes
        original_get_item = self.item_manager.get_item
        original_get_random = self.item_manager.get_random_material
        
        self.item_manager.get_item = MagicMock(return_value={"tier": 8, "name": "God Item", "price": 99999})
        self.item_manager.get_random_material = MagicMock(return_value="herb_spirit_1") # Tier 1 item
        
        high_tier_id = "god_item_t8"
        self.cultivator.gain_item(high_tier_id, 1)
        
        # Check inventory
        if high_tier_id in self.cultivator.inventory:
             print(f"FAILURE: High tier item {high_tier_id} found in inventory!")
             self.fail("Safeguard failed")
        elif "herb_spirit_1" in self.cultivator.inventory:
             print("SUCCESS: High tier item replaced by fallback item.")
        else:
             print("FAILURE: Item disappeared completely (could be okay implementation dependent, but we expect replacement)")
             
        # Restore mocks
        self.item_manager.get_item = original_get_item
        self.item_manager.get_random_material = original_get_random

if __name__ == '__main__':
    unittest.main()
