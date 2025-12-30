# Plan 26: 坊市刷新机制与等级动态匹配 (Market Enhancement)

## 问题描述 (Problem)
目前坊市（Market）的商品可能是一成不变的，或者刷新机制不明确。用户希望每小时可以主动刷新一次，并且商品等级应随人物境界（Layer）动态变化，保证后期能买到高级材料。

## 目标 (Goals)
1.  **主动刷新**: 在坊市 UI 增加“刷新”按钮。
2.  **冷却限制**: 限制每小时只能主动刷新一次（CoolDown）。
3.  **动态等级**: 刷新出的商品 Tier 应围绕玩家当前的境界 Tier 波动（例如：当前筑基[Tier 1]，刷出 Tier 0-2 的物品）。

## 实施步骤 (Implementation Steps)

### 步骤 1: 后端逻辑升级 (`src/services/market_service.py` 或 `MarketWindow`)
*   **记录刷新时间**: 在 `player_status` 表或 `system_metadata` 中记录 `last_market_refresh_time`。
*   **检查冷却**: 点击刷新时，`now - last_refresh_time >= 3600s` ?
    *   Yes: 执行刷新，更新时间，保存 DB。
    *   No: 提示剩余时间。
*   **生成物品算法 (`generate_stock`)**:
    *   获取 `cultivator.layer_index` (Tier)。
    *   定义范围: `min_tier = max(0, current_tier - 1)`, `max_tier = min(MAX_TIER, current_tier + 1)`。
    *   从 `ItemManager` 筛选符合 Tier 范围的物品池。
    *   随机抽取 N 个商品作为本次库存。

### 步骤 2: 数据库支持
*   需要一个地方存储“当前坊市库存”。如果目前是随机生成的暂时数据，建议持久化到数据库的 `market_stock` 表，防止重启后好东西没了，或者利用这个机制刷库存。
*   **方案**:
    *   表 `market_stock (item_id, count, price)`。
    *   每次刷新清空表，插入新数据。
    *   每次购买 `UPDATE` 数量。

### 步骤 3: 前端 UI (`MarketWindow`)
*   添加 `QPushButton("刷新货物")`。
*   添加倒计时 Label (如果 CD 中)。
*   从 `market_stock` DB 读取并展示商品，而不是每次打开都随机生成。

## 执行记录 (Execution Log)
- **2025-12-30**:
    - **数据库**: 新增了 `market_stock` 表用于持久化坊市库存；新增 `player_status.last_market_refresh_time` 字段。
    - **后端**: `Cultivator.refresh_market` 升级为基于 `layer_index` 的动态 Tier 算法 (±1 Tier)；`save_data` / `load_data` 同步更新 DB。
    - **前端**: `MarketWindow` 增加了“进货”按钮和 1小时倒计时逻辑；购买后库存会实时移除。
    - 任务完成。
