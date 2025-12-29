# 问题分析与调整方案 (Plan 16)

## 1. 缺失数据问题 (Missing Data)
**现象描述**: 打包后的程序运行时，坊市无商品、无随机事件、无炼丹丹方。
**原因分析**:
1.  **数据库初始化不完整**: 也就是 `DatabaseManager._init_db()` 虽然创建了表结构，但没有把初始数据（物品、配方、事件）写入数据库。
2.  **数据导入工具未运行**: 开发环境依赖的手动执行脚本 `tools/import_all_data.py` 并没有被包含在打包后的程序主逻辑中，导致新环境下 `user_data.db` 是空的。
3.  **资源路径问题**: 即使逻辑存在，打包后的资源通过 `_MEIPASS` 访问，需要确保代码使用 `get_resource_path` 正确读取 `src/data` 下的 JSON 文件。

**修复方案**:
1.  **集成数据加载逻辑**: 在 `ItemManager` 或 `DatabaseManager` 初始化时，增加检测逻辑。如果发现 `item_definitions` 表为空，自动触发`DataImporter`。
2.  **实现 `DataImporter`**: 将 `tools/import_all_data.py` 的核心逻辑移植到 `src/services/data_loader.py`，并修改文件读取路径为 `get_resource_path` 兼容打包环境。
3.  **确保资源打包**: 确认 `.spec` 文件已包含 `src/data/*.json` (已确认包含)。

## 2. 升级数值调整 (Leveling Balance)
**需求**: 提升升级速度。
- 炼气期 (LianQi): ~1 小时
- 筑基期 (ZhuJi): ~3 小时
- 金丹期 (JieDan): ~1 天 (24小时)

**当前数值**:
- Tier 0: 200,000 (约 5~10小时)
- Tier 1: 1,400,000
- Tier 2: 6,000,000

**调整方案**:
基于平均每秒获取 8 点经验 (Work/Active Mix) 进行估算：
- 1 小时 = 3600 秒 * 8 = 28,800
- 3 小时 = 10,800 秒 * 8 = 86,400
- 24 小时 = 86,400 秒 * 8 = 691,200

**新经验表建议**:
```python
EXP_TABLE = [
    30000,       # 0: 炼气 (Goal: ~1h)
    120000,      # 1: 筑基 (Goal: ~3h)
    800000,      # 2: 金丹 (Goal: ~24h)
    2500000,     # 3: 元婴 (预估 ~3天)
    8000000,     # 4: 化神 (预估 ~10天)
    20000000,    # 5: 炼虚
    50000000,    # 6: 合体
    100000000,   # 7: 大乘
    999999999    # 8: 渡劫
]
```

## 执行步骤
1.  **重构数据导入**: 创建 `src/services/data_loader.py`，移植 `tools/import_all_data.py` 逻辑。
2.  **更新初始化**: 在 `main.py` 或 `ItemManager` 中调用加载器。
3.  **调整数值**: 修改 `src/cultivator.py` 中的 `EXP_TABLE`。
4.  **验证**:删除本地 `user_data.db` 模拟新用户，运行程序验证数据是否自动写入，并检查升级速度。

## 3. Bug 修复记录 (2025-12-29) - 坊市与丹方缺失
**问题**: 
运行游戏时出现“所有丹方不显示”及“坊市刷新无物品”的现象。

**分析**:
1.  **数据源缺失**: 检查 `src/data/` 目录，发现 `items.json`, `items_v2.json`, `events.json` 等关键数据文件全部缺失。
2.  **加载失败**: `src/services/data_loader.py` 依赖上述 JSON 文件进行数据库初始化。文件缺失导致 `item_definitions`、`recipes` 和 `event_definitions` 表虽然创建了，但数据为空。
3.  **连锁反应**:
    - **坊市**: `MarketWindow` 刷新时调用 `ItemManager` 获取随机物品，因数据库为空返回 None，导致商品列表为空。
    - **丹方**: `AlchemyWindow` 读取 `recipes` 表数据，因表为空，导致列表无显示。

**解决措施**:
1.  **执行数据重建**: 运行了以下维护脚本直接填充数据库：
    - `python3 tools/tools_update_items_v3.py`: 重建了 Tier 0-8 的完整物品 (113个) 和配方 (39个) 数据。
    - `python3 tools/tools_update_events.py`: 重建了事件系统数据 (34个事件)。
2.  **验证结果**: 数据库已成功填充，重启游戏后坊市将正常随机生成商品，炼丹房也能显示对应境界的丹方。

**后续优化建议**:
- 需要将 `tools/tools_update_items_v3.py` 中的数据字典（`TIER_ITEMS` 和 `TIER_PILLS`）导出并固化为 `src/data/items.json`，确保打包时资源完整，避免依赖外部 `tools` 脚本。

## 4. Bug 修复记录 (2025-12-29) - 储物袋物品显示英文
**问题**:
用户报告“储物袋里是英文”，这是因为 `player_inventory` 中存留了旧版本的 Item ID (如 `weed_wash`, `flower_blood`, `ore_iron`, `iron_essence`)，而新版数据库 (`item_definitions`) 中使用了新的 ID 规范 (如 `herb_marrow_0`, `flower_blood_0`, `ore_iron_essence`)。导致 `InventoryWindow` 无法查找到物品详情，fallback 回显为旧 ID 字符串。

**解决措施**:
1.  **编写迁移脚本**: 创建了 `tools/fix_inventory_ids.py`，建立旧 ID 到新 ID 的映射关系。
    -   `weed_wash` -> `herb_marrow_0` (洗髓草)
    -   `flower_blood` -> `flower_blood_0` (凝血花)
    -   `ore_iron` / `iron_essence` -> `ore_iron_essence` (百炼铁精)
2.  **执行迁移**: 运行脚本批量更新了 `user_data.db` 中的 `player_inventory` 表，修复了残留数据。
3.  **验证**: 重启后，所有物品均可正确显示中文名称。