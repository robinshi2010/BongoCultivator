# Plan 24: 修复修仙记录重复领取灵石Bug (Fix Record Reward Bug)

## 问题描述 (Problem)
用户反馈：“关闭游戏再打开之后，还能重复领取修仙记录里的灵石奖励。”
这意味着领取奖励的状态（`claimed` 或 `rewarded`）没有正确持久化到数据库，或者读取时未能正确加载该状态。每次重启应用，内存中的状态被重置，导致可以重复领取。

## 目标 (Goals)
1.  **定位问题**: 确认“修仙记录”对应的是哪一部分代码（可能是成就系统 `AchievementManager` 或其他记录系统）。
2.  **修复持久化**: 确保领取奖励后，立即更新数据库中对应的标志位。
3.  **修复加载**: 确保启动时正确从数据库读取已领奖状态。
4.  **验证**: 重启游戏后，已领取的奖励应显示为“已领取”或不可交互状态。

## 实施步骤 (Implementation Steps)

### 步骤 1: 代码审计与定位
*   检查 `src/services/achievement_manager.py` (如果是成就)。
*   或者检查 `src/ui/stats_window.py` (如果修仙记录在这里)。
*   查找“领取奖励”按钮的信号连接槽函数，追踪数据流向。
*   确认数据库表结构（如 `achievements` 表）是否有 `is_rewarded` 字段。

### 步骤 2: 修复逻辑
*   **数据库**: 如果缺少状态字段，需在 `src/database.py` 中添加字段迁移逻辑（或修改表结构）。
*   **后端**: 在领取奖励的函数中，执行 SQL `UPDATE` 语句将状态写入 DB。
*   **前端**: 在窗口初始化/刷新时，根据从 DB 加载的状态设置按钮的 Enable/Disable 状态。

### 步骤 3: 测试
*   启动游戏 -> 达成条件 -> 领取奖励 -> 获得灵石。
*   关闭游戏 -> 重新启动。
*   打开修仙记录 -> 确认按钮不可再次点击。

## 执行记录 (Execution Log)
- **2025-12-30**: 
    - 修改 `src/database.py`: 为 `player_status` 表增加了 `daily_reward_claimed` 字段。
    - 修改 `src/cultivator.py`: 在 `save_data` 和 `load_data` 中增加了该字段的读写逻辑。
    - 修改 `src/ui/stats_window.py`: 在 `refresh_data` 中增加了状态检查，如果已领取则禁用按钮。
    - 任务完成。
