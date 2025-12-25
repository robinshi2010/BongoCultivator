# Plan 10: 奇遇事件系统 (Structured Event System)

## 目标
建立一个数据驱动的事件引擎，替代目前硬编码的随机对话，使游戏世界具备动态反馈和叙事能力。

## 1. 数据库设计 (`game_events`)
在 `user_data.db` 中新增表结构：

```sql
CREATE TABLE game_events (
    id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,       -- 事件文本，支持 {player} 占位符
    trigger_type TEXT,      -- random/condition/scheduled
    trigger_condition TEXT, -- JSON: {"min_layer": 2, "min_mind": 50, "chance": 0.1}
    outcomes TEXT,          -- JSON: [{"type": "item", "id": "x", "count": 1}, {"type": "stat", "key": "mind", "val": -10}]
    is_unique INTEGER DEFAULT 0 -- 是否为一次性事件
);
```

## 2. 事件引擎 (`src/services/event_engine.py`)
- **加载**: 启动时从 DB 加载所有事件到内存。
- **检查 (`check_triggers`)**: 
    - 每分钟或特定动作后被调用。
    - 遍历事件池，筛选符合条件的事件。
    - 随机权重选择一个触发。
- **执行 (`execute_event`)**:
    - 应用 Outcomes。
    - 写入日志 (`activity_logs` 或 `player_events`).
    - 如果是 `is_unique`，标记为已完成 (不再触发)。

## 3. 奇遇事件库设计 (Event Library)

事件库将包含 **60+** 个精心设计的事件，分为 **Common (日常)**, **Rare (稀有)**, **Unique (唯一/剧情)** 三类。

所有事件均需引用 Plan 9 中定义的物品 ID，以保证世界观一致性。

### Tier 0: 炼气期 (Qi Refining) - *初入仙途*
*主题: 凡人与修仙者的界限模糊，充满对未知的探索。*

| ID | 标题 | 类型 | 触发条件 | 文本 (Text) | 结果 (Outcomes) |
|:---|:---|:---|:---|:---|:---|
| `evt_t0_c1` | **灵气复苏** | Common | Random | "今日晨练时感觉神清气爽，似乎空气中的灵气浓度有所上升。" | `exp +50`, `mind -2` |
| `evt_t0_c2` | **误食野果** | Common | Random | "你在路边发现一颗颜色鲜艳的果实，饥渴难耐下吞服了它。" | 50% `exp +100` / 50% `mind +5` (中毒) |
| `evt_t0_r1` | **兽冢拾荒** | Rare | `state=WORK` | "你误入一处荒废的兽冢，在白骨堆中发现了一颗泛着红光的残齿。" | `gain item: part_wolf_tooth x1` |
| `evt_t0_r2` | **神秘符箓** | Rare | `mind < 20` | "一位路过的云游道士看你骨骼惊奇，随手丢给你一张破旧符纸。" | `gain item: misc_talisman_old x1` |
| `evt_t0_u1` | **洗髓机缘** | Unique | `layer=0` | "你在深山瀑布下冲刷肉身时，意外发现瀑布后的一株幽蓝草药。" | `gain item: herb_marrow_0 x1`, `exp +500` |

### Tier 1: 筑基期 (Foundation) - *大兴土木*
*主题: 构建道基，开始接触五行之力。*

| ID | 标题 | 类型 | 触发条件 | 文本 (Text) | 结果 (Outcomes) |
|:---|:---|:---|:---|:---|:---|
| `evt_t1_c1` | **地脉震动** | Common | Random | "脚下的大地微微颤抖，似有地龙翻身，泄露出一丝精纯土灵气。" | `exp +200` |
| `evt_t1_c2` | **坊市捡漏** | Common | `state=IDLE` | "在坊市角落的摊位上，你发现一块不起眼的矿石竟是赤铜精母。" | `lose money -100`, `gain item: ore_copper_red x1` |
| `evt_t1_r1` | **寒潭奇遇** | Rare | `state=WORK` | "为了躲避仇家，你潜入寒潭深处，却意外发现寒气逼人的晶石。" | `gain item: ore_cold_crystal x1`, `body +1` |
| `evt_t1_u1` | **龙纹觉醒** | Unique | `layer=1` | "你体内的灵力忽然自行运转，与手中的龙纹草产生共鸣，隐约听到了龙吟。" | `gain item: herb_dragon_1 x1`, `exp +2000` |

### Tier 2: 金丹期 (Golden Core) - *内丹大成*
*主题: 炼精化气，炼气化神。*

| ID | 标题 | 类型 | 触发条件 | 文本 (Text) | 结果 (Outcomes) |
|:---|:---|:---|:---|:---|:---|
| `evt_t2_c1` | **丹火试炼** | Common | `state=ALCHEMY` | "炉温突然升高，你急忙打出几道法诀稳住火候。" | `exp +500`, `mind +1` |
| `evt_t2_r1` | **天雷滚滚** | Rare | Random | "晴空一声霹雳，一道落雷击中了你不远处的竹林！" | `gain item: wood_sky_thunder x1`, `mind +5` (受惊) |
| `evt_t2_r2` | **古修洞府** | Rare | `state=WORK` | "你挖掘到了一座坍塌的洞府，门口散落着几面残破的阵旗。" | `gain item: misc_array_flag x1`, `money +500` |
| `evt_t2_u1` | **金丹异象** | Unique | `layer=2` | "你的金丹表面浮现出九窍玲珑之孔，贪婪地吞噬着周围的星辰之力。" | `gain item: ore_star_sand x2`, `exp +5000` |

### Tier 3: 元婴期 (Nascent Soul) - *身外化身*
*主题: 灵魂出窍，探索幽冥与空间。*

| ID | 标题 | 类型 | 触发条件 | 文本 (Text) | 结果 (Outcomes) |
|:---|:---|:---|:---|:---|:---|
| `evt_t3_c1` | **神游太虚** | Common | `state=IDLE` | "闭关中，你的元婴离体而出，在天地间遨游了一圈。" | `exp +1000`, `mind -5` |
| `evt_t3_r1` | **空间裂隙** | Rare | Random | "面前的空间突然裂开一道细缝，掉落一块形状扭曲的石头。" | `gain item: ore_void_stone x1` |
| `evt_t3_r2` | **九曲灵踪** | Rare | `state=WORK` | "你看见一只白兔钻入土中消失不见，只留下一截红绳。" | `gain item: herb_soul_restore x1` |
| `evt_t3_u1` | **黄泉回响** | Unique | `layer=3` | "你的元婴误入黄泉河畔，被河水沾湿了衣角，却因祸得福凝练了魂体。" | `gain item: water_nether x1`, `mind +10` |

### Tier 4: 化神期 (Soul Formation) - *法则初显*
*主题: 接触天地规则，微观世界。*

| ID | 标题 | 类型 | 触发条件 | 文本 (Text) | 结果 (Outcomes) |
|:---|:---|:---|:---|:---|:---|
| `evt_t4_c1` | **道韵共鸣** | Common | Random | "你观摩落叶飘零，心中忽然对枯荣法则多了一丝明悟。" | `exp +3000` |
| `evt_t4_r1` | **鲲鹏掠影** | Rare | Random | "巨大的阴影遮蔽了天空，一根羽毛如山峰般坠落。" | `gain item: part_kunpeng_feather x1` |
| `evt_t4_u1` | **息壤再生** | Unique | `layer=4` | "你得到的这捧泥土竟然在吞噬周围的岩石自我增殖！" | `gain item: soil_chaos x1` |

### Tier 5: 炼虚期 (Void Refinement) - *破碎虚空*
*主题: 反物质，黑洞，维度跳跃。*

| ID | 标题 | 类型 | 触发条件 | 文本 (Text) | 结果 (Outcomes) |
|:---|:---|:---|:---|:---|:---|
| `evt_t5_c1` | **虚空乱流** | Common | `state=WORK` | "你在虚空穿行时遭遇了能量乱流，不得不消耗修为抵御。" | `exp -5000`, `body +5` (淬体) |
| `evt_t5_r1` | **死星闪耀** | Rare | Random | "远处一颗恒星熄灭了，你冒死捕获了它坍缩后的核心。" | `gain item: core_star x1` |
| `evt_t5_r2` | **彼岸花开** | Rare | `mind > 50` | "在神识恍惚间，你看到了一条满是红花的河流，想起了前世的名字。" | `gain item: flower_other_shore x1`, `mind -20` |

### Tier 6: 合体期 (Fusion) - *圣者降临*
*主题: 神话生物，肉身成圣。*

| ID | 标题 | 类型 | 触发条件 | 文本 (Text) | 结果 (Outcomes) |
|:---|:---|:---|:---|:---|:---|
| `evt_t6_c1` | **万兽朝苍** | Common | Random | "你散发的威压让方圆百里的妖兽匍匐颤抖。" | `exp +8000`, `luck +1` |
| `evt_t6_r1` | **麒麟献瑞** | Rare | `luck > 10` | "一头火麒麟踏云而来，吐出一块臂骨后消失在云端。" | `gain item: bone_kirin_arm x1` |
| `evt_t6_u1` | **三生石畔** | Unique | `layer=6` | "你在梦中看到了自己的过去、未来，以及一块刻着名字的石头。" | `gain item: stone_three_life x1` |

### Tier 7: 大乘期 (Mahayana) - *因果循环*
*主题: 时间线操作，因果律。*

| ID | 标题 | 类型 | 触发条件 | 文本 (Text) | 结果 (Outcomes) |
|:---|:---|:---|:---|:---|:---|
| `evt_t7_c1` | **时间停滞** | Common | Random | "你感觉到周围的时间流动变慢了，落叶悬在空中久久不落。" | `exp +15000` |
| `evt_t7_r1` | **因果纠缠** | Rare | `state=WORK` | "你随手拨动的一根无形丝线，竟导致千里之外的一个宗门覆灭。" | `gain item: thread_karma x1`, `mind +10` |
| `evt_t7_u1` | **世界树语** | Unique | `layer=7` | "巨大的世界树虚影向你展示了宇宙的生灭，落下一片枯叶。" | `gain item: leaf_world_tree x1` |

### Tier 8: 渡劫期 (Tribulation) - *直面天道*
*主题: 毁灭与终焉。*

| ID | 标题 | 类型 | 触发条件 | 文本 (Text) | 结果 (Outcomes) |
|:---|:---|:---|:---|:---|:---|
| `evt_t8_c1` | **天道窥视** | Common | Random | "天空中出现了一只巨大的眼睛，冷漠地注视着你。" | `mind +20` |
| `evt_t8_r1` | **鸿蒙初辟** | Rare | Random | "你捕捉到了宇宙诞生之初残留的一缕紫气。" | `gain item: gas_primordial x1` |
| `evt_t8_u1` | **定界之锚** | Unique | `layer=8` | "为了在飞升通道中不迷失方向，你炼化了一方小世界为锚点。" | `gain item: stone_destiny x1` |

### Tier 9: 飞升 (Ascension) - *打破次元壁*
*主题: Meta 游戏，意识到玩家的存在。*

| ID | 标题 | 类型 | 触发条件 | 文本 (Text) | 结果 (Outcomes) |
|:---|:---|:---|:---|:---|:---|
| `evt_t9_c1` | **屏幕之外** | Common | Random | "我仿佛看到屏幕外有一张巨大的脸在盯着我看...是你吗？" | `exp +50000` |
| `evt_t9_u1` | **作者的馈赠** | Unique | `layer=9` | "你捡到了一支钢笔，上面刻着几个烫金小字：'Design Idea'。" | `gain item: pen_author x1` |

---

## 4. 执行步骤 (Execution Steps)

1.  **数据库更新** (`tools/update_events.py`):
    *   创建 `game_events` 表。
    *   编写脚本将上述 60+ 个事件注入数据库。
2.  **引擎开发** (`src/services/event_engine.py`):
    *   实现 `check_condition(trigger)` 函数，解析 JSON 格式的触发条件。
    *   实现 `execute_outcome(outcome)` 函数，解析 JSON 格式的奖励/惩罚。
    *   **集成点**: 在 `PetWindow.game_loop` 中每分钟调用一次 `engine.tick()`。
3.  **UI 适配**:
    *   事件触发时，使用改进后的 `show_notification` (支持长文本) 显示事件描述。
    *   如果获得物品，额外显示一个小图标或特殊音效。
4.  **测试**:
    *   使用 `tools/verify_events.py` 模拟属性，测试事件触发频率和条件判断是否准确。
5.  **文档**:
    *   更新 `memory.md` 和 `plan10.md` 状态。

---
**Status**: Completed

## 完成情况 (Completion Log)
*Date: 2025-12-25*

### 1. 数据库与数据
- 创建了 `game_events` 表。
- 编写并执行了 `tools_update_events.py`，注入了 34+ 个初始事件（覆盖 Common, Rare, Unique 类型，Tier 0-9）。
- 事件内容与 Plan 9 物品系统深度联动。

### 2. 引擎实现
- 创建了 `src/services/event_engine.py`，实现了基于 Layer, State, Stats, Chance 的触发器检查逻辑。
- 实现了 Outcomes 执行逻辑 (Exp, Mind, Luck, Item)。
- 实现了 Unique 事件的历史记录去重。

### 3. 集成与测试
- 更新了 `src/cultivator.py`，集成了 `EventEngine`。
- 修改了 `update` 循环，每 5 分钟 (300 ticks) 尝试触发一次事件。
- 确保事件文本追加到 `gain_msg`，从而在 UI 气泡中显示。
- 编写了 `tools_verify_events.py` 并验证通过。
