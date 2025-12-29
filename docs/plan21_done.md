# Plan 21: Improve Item Description & UI Details

## Problem
The user reported that detailed item descriptions are missing or hard to read in both `InventoryWindow` and `MarketWindow`.
- `InventoryWindow`: Description exists but might be plain. Lacks structured info like Tier or Price.
- `MarketWindow`: Completely lacks a description view. Users buy/sell based only on Name/Price.

## Goals
1.  **Enhance `InventoryWindow`**:
    - Replace the simple `QLabel` with a `QTextEdit` (Read-only) to support rich text and scrolling.
    - Display structured info: **Level (Tier)**, **Type**, **Price**, **Description**, and **Effect**.
2.  **Enhance `MarketWindow`**:
    - Add a Detail View (`QTextEdit`) to both "Buy" and "Sell" tabs.
    - When an item is selected, display its full details (Description, Stats) so players know what they are trading.

## Implementation Steps

### Step 1: `InventoryWindow` Refactor
- **File**: `src/inventory_window.py`
- **Change**:
    - Remove `self.detail_label`.
    - Add `self.description_text = QTextEdit()`.
    - Set read-only, transparent background styling.
    - Update `show_item_detail` to format a rich HTML string:
        ```html
        <b>【Name】</b> <span style='color:gold'>[Tier X]</span><br>
        Type: [Type] <br>
        Price: 100 Spirit Stones<br>
        <hr>
        Description...<br>
        <hr>
        <i>Effect: ...</i>
        ```

### Step 2: `MarketWindow` Refactor
- **File**: `src/market_window.py`
- **Change**:
    - In `setup_buy_tab` and `setup_sell_tab`, utilize `QHBoxLayout` or `QVBoxLayout` to allocate space for a Description box.
    - Add `goods_list.itemClicked.connect(self.show_buy_detail)` and similar for sell list.
    - Implement `show_buy_detail` and `show_sell_detail` to populate the text box with `item_manager` data.

### Step 3: Helper Function for Description
- Since formatting item details is now common across two windows, consider a helper method `format_item_html(item_data)` in `ItemManager` or a utility class?
- For simplicity, maybe just duplicate the formatting logic or put it in `ItemManager`. Let's put a helper in `ItemManager`.

## Data Preparation
- `ItemManager.get_item_details_html(item_id)`: Returns a string ready for `QTextEdit.setHtml()`.

