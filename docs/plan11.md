# Plan 11: 天道功德榜 (Heavenly Merit System)

## 1. 核心理念 (Core Concept)

> **"凡有所相，皆是虚妄；唯有因果，真实不虚。"**

将传统的 "Achievements" 包装为 **"天道功德 (Heavenly Merit)"** 系统。
用户的每一次敲击、每一分钟挂机、每一个触发的奇遇，都会在冥冥之中积累"因果"。
当因果达到临界点，天道会降下**"功德碑" (Merit Stele)** 赐予封号与宝物。

**设计原则**:
1.  **沉浸感**: 不弹 "Achievement Unlocked"，而是弹 "天道感应 (Heavenly Resonance)"。
2.  **物质奖励**: 强关联 `docs/plan9.md` 的物品系统，成就即是获取稀有资源的途径。
3.  **高性能**: 拒绝每帧检查。基于 `ActivityRecorder` 的聚合数据 + 事件驱动触发。

---

## 2. 数据库设计 (`achievements`)

在 `user_data.db` 中新建表。结构设计支持"隐藏成就"与"进度追踪"。

```sql
CREATE TABLE achievements (
    id TEXT PRIMARY KEY,        -- e.g., 'ach_kb_10k'
    category TEXT,              -- 'action'(行道), 'time'(岁月), 'chance'(机缘), 'fortune'(财阀)
    name TEXT,                  -- 显示名称, e.g. "剑意初成"
    desc TEXT,                  -- 描述 (未解锁时可能显示 "???")
    condition_type TEXT,        -- 'stat_total', 'action_count', 'item_count', 'event_trigger'
    condition_target TEXT,      -- 目标键值, e.g. 'keyboard_clicks'
    threshold INTEGER,          -- 目标数值
    reward_type TEXT,           -- 'title', 'item', 'buff'
    reward_value TEXT,          -- 物品ID 或 称号文本, e.g. 'ore_iron_essence:1'
    is_hidden INTEGER DEFAULT 0,-- 是否为隐藏成就
    status INTEGER DEFAULT 0,   -- 0: Locked, 1: Completed, 2: Claimed
    unlocked_at INTEGER         -- Timestamp
);
```

---

## 3. 成就图谱 (The Merit Roll)

结合 `docs/plan9.md` (物品) 和 `docs/mechanics.md` (数值) 进行设计。

### 3.1 行道 (Dao of Action) - 键鼠操作
*奖励主要关联战斗与炼器材料。*

| ID | 名称 | 条件 | 奖励 (Resonance) | 备注 |
|:---|:---|:---|:---|:---|
| `ach_kb_1w` | **剑意初成** | Keyboard Total > 10,000 | Item: `ore_iron_essence` x1 | 凡铁化精 |
| `ach_kb_10w` | **万剑归宗** | Keyboard Total > 100,000 | Title: **[剑仙]** (攻击特效) | - |
| `ach_mouse_1w`| **一指禅** | Mouse Total > 10,000 | Item: `part_wolf_tooth` x5 | - |
| `ach_apm_high`| **触手怪** | Max APM (1min) > 400 | Item: `part_spider_silk` x10 | 奖励"人面蛛丝"很合理 |

### 3.2 岁月 (Dao of Time) - 挂机与时长
*奖励主要关联心性与悟性。*

| ID | 名称 | 条件 | 奖励 (Resonance) | 备注 |
|:---|:---|:---|:---|:---|
| `ach_time_24h`| **闭关锁国** | Uptime > 24 Hours | Item: `pill_detox_0` x1 | 排毒 |
| `ach_time_100h`| **沧海桑田** | Uptime > 100 Hours | Item: `stone_three_life` x1 | 三生石 (Tier 6 稀有) |
| `ach_work_late`| **守夜人** | 在凌晨 3:00-4:00 仍有操作 | Item: `part_bat_wing` x2 | 隐藏成就 |

### 3.3 机缘 (Dao of Chance) - 事件与掉落
*关联 `docs/plan10.md` 的事件系统。*

| ID | 名称 | 条件 | 奖励 (Resonance) | 备注 |
|:---|:---|:---|:---|:---|
| `ach_evt_50` | **气运之子** | Triggered Events > 50 | Item: `pill_luck_minor` x1 | 小气运丹 |
| `ach_fail_break`| **道心弥坚** | 突破境界失败 > 3次 | Title: **[百折不挠]** (心魔增长-10%) | 安慰奖 |
| `ach_die_1` | **兵解重修** | 渡劫失败/心魔爆炸 x1 | Item: `pill_reborn_heaven` x1 | 回天再造丸 (Tier 5) |

### 3.4 财阀 (Dao of Wealth) - 灵石与其消耗
| ID | 名称 | 条件 | 奖励 (Resonance) | 备注 |
|:---|:---|:---|:---|:---|
| `ach_rich_1w` | **腰缠万贯** | 拥有灵石 > 10,000 | Title: **[多宝道人]** | - |
| `ach_poor_0` | **身无分文** | 拥有灵石 < 5 (且Total>1000) | Item: `misc_broken_sword` x1 | 此时应有断剑 |

---

## 4. 系统实现 (Architecture)

为了性能，我们**不**在每次击键时检查成就。

### 4.1 Check 时机
1.  **定时检查 (Cron)**: 每 5 分钟 (`Slow Loop`) 检查一次基于累积数据 (`total_keys`, `uptime`) 的成就。
2.  **事件触发 (Event-Driven)**: 
    *   当 `check_event` 触发特定结果时，顺便检查相关成就。
    *   当 `level_up` 或 `breakthrough` 发生时，检查相关成就。

### 4.2 `AchievementManager` 伪代码
```python
class AchievementManager:
    def check_all(self, stats: ActivityStats, user_state: UserState):
        # 1. 读取未解锁成就
        locked_achs = self.db.get_locked()
        
        for ach in locked_achs:
            if ach.type == 'stat_total':
                 current_val = stats.get(ach.target)
                 if current_val >= ach.threshold:
                     self.unlock(ach, user_state)
            
            elif ach.type == 'one_off_condition':
                 # 复杂逻辑由专门的 handler 处理
                 pass

    def unlock(self, ach, user_state):
        # 1. DB Update
        self.db.mark_unlocked(ach.id)
        # 2. Grant Reward
        if ach.reward_type == 'item':
            ItemManager.add_item(user_state, ach.reward_value)
        # 3. Notify
        NotificationSystem.show(
            title="天道感应", 
            msg=f"达成成就 [{ach.name}]\n获得奖励: {ach.reward_desc}",
            style="GOLD"
        )
```

## 5. 执行步骤

1.  **Schema**: 创建 `achievements` 表。
2.  **Data Injection**: 编写 `tools/init_achievements.py`，将上述 3.1-3.4 的配置写入 DB。
    *   *依赖*: 需确保 Plan 9 的物品 ID 已存在。
3.  **Backend**: 实现 `src/services/achievement_manager.py`。
4.  **Integration**:
    *   在 `ActivityRecorder.flush()` 后调用检查。
    *   在 `EventEngine` 中埋点。
5.  **Frontend**:
    *   `StatsWindow`: 增加 `Merit` (功德) Tab，显示列表。
    *   已解锁显示金色，未解锁显示灰色与进度条。

---
**Status**: Pending Design
