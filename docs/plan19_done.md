# Plan 19: Visual Feedback for Item Usage

## Problem
User reported that using items (pills) provides no visible feedback, making it unclear if the item worked or what effect it had.

## Solution
Integrate the existing `show_notification` system from `PetWindow` into `InventoryWindow`. When an item is used, a floating notification (toast) should appear on the main Pet character, displaying the effect (e.g., "Cultivation +500", "Breakthrough Failed").

## Steps

### Step 1: Modify `InventoryWindow` Constructor
Update `src/inventory_window.py` to accept a reference to `pet_window`.
- Note: Keep `parent=None` for `QWidget` constructor to ensure the window remains a top-level window (not clipped by the small PetWindow).
- Store `pet_window` as a member variable.

```python
class InventoryWindow(QWidget):
    def __init__(self, cultivator, pet_window=None, parent=None):
        super().__init__(parent)
        self.pet_window = pet_window
        # ...
```

### Step 2: Update `PetWindow.open_inventory`
Update `src/pet_window.py` to pass `self` as `pet_window` when creating `InventoryWindow`.

```python
# src/pet_window.py

def open_inventory(self):
    # ...
    if not hasattr(self, 'inventory_window') or self.inventory_window is None:
        # Pass self as pet_window, parent remains None
        self.inventory_window = InventoryWindow(self.cultivator, pet_window=self) 
    # ...
```

### Step 3: Trigger Notification in `use_item`
Update `src/inventory_window.py` -> `use_item` method.
- Call `self.pet_window.show_notification(msg)` upon successful usage.
- Also consider triggering effects via `pet_window.effect_widget` if possible (e.g. golden flash for breakthrough).

```python
if used_success:
    # ... existing logic ...
    
    # New feedback
    if self.pet_window:
        self.pet_window.show_notification(msg)
        
        # Optional: Trigger VFX based on item type
        if "breakthrough" in item_type or "break" in item_type:
            # Maybe trigger a small flash?
            pass
```

## Verification
- Open Inventory.
- Use a "聚气散" (Exp pill).
- Verify that a green notification text appears above the Pet character.
