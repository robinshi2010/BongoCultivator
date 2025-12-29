# Plan 18: 修复物品使用逻辑 (Fix Item Usage Logic)

## 问题诊断 (Problem Diagnosis)
用户反馈炼制的丹药在储物袋（背包）中无法使用。
经调查发现，`items_v2.json`（及数据库）中定义的物品类型与 `InventoryWindow` 识别的类型不匹配。

- **DB 中定义的类型**: `exp` (修为), `stat` (属性), `buff` (增益), `recov` (恢复), `utility` (功能), `break` (突破), `special` (特殊), `cosmetic` (外观)。
- **背包允许使用的类型**: `consumable` (消耗品), `breakthrough` (突破), `buff` (增益)。

这种类型不匹配导致大多数有效丹药的“使用”按钮处于禁用状态。

## 目标 (Goals)
1.  **启用“使用”按钮**: 更新 `InventoryWindow` 以识别所有的消耗品类型。
2.  **统一使用逻辑**: 确保 `use_item` 方法能正确处理这些扩展类型的效果。

## 实施步骤 (Implementation Steps)

### 步骤 1: 更新 `InventoryWindow.show_item_detail`
修改 `src/inventory_window.py`，扩展 `can_use` 的判断条件。

```python
# 旧代码
can_use = item_type in ["consumable", "breakthrough", "buff"]

# 新代码
can_use = item_type in [
    "consumable", "breakthrough", "buff", 
    "exp", "stat", "recov", "break", "utility", "special", "cosmetic"
]
```

### 步骤 2: 更新 `InventoryWindow.use_item`
重构 `use_item` 方法以处理多种类型。不再使用严格的 `if type == ...`，而是检查 `effects` 中的特定键值，这样更健壮，但仍需处理像 `breakthrough` 这样的特殊逻辑。

逻辑映射:
- 类型 `break` -> 逻辑 `breakthrough` (突破)。
- 类型 `exp`, `stat`, `recov`, `buff`, `utility` -> 逻辑 `consumable` (处理效果字典)。

```python
if item_type == "break" or item_type == "breakthrough":
    # 执行突破逻辑
    pass
else:
    # 执行通用消耗品逻辑 (检查 effects 中的 exp, stat, recov 等键)
    pass
```

### 步骤 3: 验证效果键名 (Verify Effect Keys)
确保物品中的 `effects` 字典与 `use_item` 期望的一致。
- `exp`: `{"exp_gain": 0.05}` vs 代码 `effects["exp"]`。代码期望 `exp`（数值）还是 `exp_gain`？
    - **关键问题**: `items_v2.json` 使用的是 `exp_gain`（浮点百分比？），但 `use_item` 似乎期望 `exp`（固定数值？如果不明确的话）。
    - 检查 `inventory_window.py` 第 184 行: `if "exp" in effects: val = effects["exp"]`。
    - 但 `items_v2.json` 中是 `{"exp_gain": 0.05}`。
    - **发现不匹配**: `items_v2.json` 中的键 (`exp_gain`, `breakthrough_chance`) 与 `inventory_window.py` 中的键 (`exp`, `chance`?) 不匹配。
    - `inventory_window.py` 第 233 行: `chance_percent = effects.get("chance", 0)`。
    - `items_v2.json`: `breakthrough_chance`。

**结论**: 我需要修复 `InventoryWindow` 以便同时查找 `items_v2.json` 中的正确键名。

## 详细键名映射计划 (Detailed Key Mapping Plan)
- **修为 (Experience)**:
    - 物品数据: `"exp_gain": 0.05` (百分比) 或 固定值?
    - 现有逻辑: 检查 `"exp"`。
    - 修复: 检查 `"exp_gain"`。如果存在，根据特定逻辑计算数值（最大经验的百分比？或固定数值？）。
    - *修正*: `Cultivator.gain_exp` 接受一个数值。如果 `exp_gain` 是 0.05，它暗示是某事物的 5%（可能是最大经验值或当前等级上限）。
    - 行动: 实现 `exp_gain`（百分比）的逻辑。

- **突破 (Breakthrough)**:
    - 物品数据: `"breakthrough_chance": 0.2`
    - 现有逻辑: 检查 `"chance"` (期望 0-100?)。
    - 修复: 检查 `"breakthrough_chance"`。如果存在 (0.0-1.0)，转换为 `cultivator.attempt_breakthrough` 所需的合适格式。`attempt_breakthrough` 接受 `base_success_rate` (0.0-1.0)。

- **治疗/恢复 (Healing/Recovery)**:
    - 物品类型: `recov`。DB 中通常效果为空？不，让我检查一下。
    - `pill_mind_calm`: `type: recov`, `effect: {}`。（等等，空效果？）
    - 如果效果为空，代码什么也不做。
    - 需要检查是否可以从描述中推断效果，或者数据是否缺失。
    - *观察*: `items_v2.json` 中 `pill_mind_calm` 的 `effect: {}`。这是数据问题，还是硬编码行为？
    - `pill_body_basic`: `effect: {}`。
    - `pill_speed_wind`: `effect: {}`。
    - **主要问题**: JSON 中许多物品的效果为空。
    - *历史检查*: `memory.md` 说“9套标准物品 ... 存入 SQLite”。
    - 如果 JSON 效果为空，即使修复了代码，游戏也不会有任何反应。

**优化后的计划**:
1.  **代码修复**: 允许新类型并映射键名 (`exp_gain` -> `exp`, `breakthrough_chance` -> `chance`)。
2.  **数据/保底修复**: `items_v2.json` 似乎很多物品效果为空。这可能是生成器没有填充它们，或者是占位符。
    - 如果我现在不能轻易用正确效果更新 DB/JSON，我可能需要在代码中根据 Item ID 硬编码一些效果作为保底（Fallback），或者建议更新数据。
    - 不过，`pill_gather_qi` 有 `exp_gain`。`pill_break_found` 有 `breakthrough_chance`。所以部分是有效的。
    - 我应该专注于让那些**有**数据的物品先工作，并可能为 `stat` / `recov` 类型添加保底逻辑（如果效果字典为空但类型暗示了功能，例如 `recov` -> 恢复心魔 10）。

## 执行 (Execution)
1.  编辑 `src/inventory_window.py`。
