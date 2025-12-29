# Plan 20: 完善丹药效果逻辑

## 问题诊断
用户反馈部分丹药（如`疾风散`、`避毒珠`）使用后提示无效果。这是因为 `items_v2.json` 数据中，这些物品的 `effect` 字段是空的（`{}`），且代码层面的“保底逻辑”可能未覆盖或不完善。

**发现的问题物品**:
- `pill_body_basic` (壮骨丸): `effect: {}`. 类型 `stat`.
- `pill_speed_wind` (疾风散): `effect: {}`. 类型 `buff`.
- `pill_detox_0` (避毒珠): `effect: {}`. 类型 `utility`.

其他可能受影响的丹药也需要检查。

## 目标
1.  **数据层修复**: 生成一个新的 SQL 脚本或 Python 脚本，更新数据库中这些物品的 `effect_json` 字段，赋予它们实际效果。
2.  **代码层兜底**: 虽然更新数据库更治本，但代码中对于 `buff`, `utility` 的处理逻辑也需要检查是否健壮。

## 修正方案 (Data Injection)
我们将直接更新数据库中的 `item_definitions` 表。

### 0阶 (Tier 0)
- **pill_body_basic (壮骨丸)**:
    - 效果: 增加体魄。
    - JSON: `{"stat_body": 5}`
- **pill_speed_wind (疾风散)**:
    - 效果: 增加少量掉落率(模拟跑得快捡得多) 或 临时 Buff。目前 Buff 系统较弱，先用直接属性加成代替? 或者实现一个假 Buff。
    - 方案: 既然是“疾风”，不如增加好感度(跑腿快)? 或者直接给个 Buff。
    - 代码逻辑支持 `buff` key。`msg = f"获得了增益 [{buff_name}] ..."`
    - JSON: `{"buff": "风行", "duration": 300}` (持续 300s)
- **pill_detox_0 (避毒珠)**:
    - 效果: 减少心魔 (Clear negative status)。
    - JSON: `{"mind_heal": 10}`

### 1阶 (Tier 1)
- **pill_mind_calm (定神丹)**:
    - 效果: 恢复状态/减少心魔。
    - JSON: `{"mind_heal": 20}`
- **pill_strength_bary (大地金刚丸)**:
    - 效果: 大幅增加体魄。
    - JSON: `{"stat_body": 10}`
- **pill_vis_night (夜视散)**:
    - 效果: 增加掉落率? (Utility is hard to map).
    - 方案: 增加好感度 `affection` (宠物能夜视了开心)。
    - JSON: `{"affection": 5}`

### 2阶 (Tier 2)
- **pill_beauty_face (定颜丹)**:
    - 效果: 增加大量好感度 (cosmetic)。
    - JSON: `{"affection": 20}`
- **pill_crazy_blood (燃血丹)**:
    - 效果: 暂时未实现副作用，先给经验? 或者体魄+心魔+。
    - 方案: 体魄+5, 心魔+10. (Need multiple effects support? Code supports `elif`, so only one triggers. Let's pick one major effect).
    - 修正: 简单点，增益 Buff。
    - JSON: `{"buff": "燃血", "duration": 600}`
- **pill_luck_minor (小气运丹)**:
    - 效果: 增加掉落率。
    - JSON: `{"buff": "小气运", "drop_mult": 0.1, "duration": 600}` (需代码支持 `drop_mult` in Buff logic? `InventoryWindow` just displays buff name).

## 执行步骤

### 步骤 1: 创建修复脚本 `tools/fix_item_effects.py`
编写脚本，针对上述 ID 更新 SQLite 数据库。

### 步骤 2: 执行修复
运行脚本。

### 步骤 3: 验证
重启游戏，再次尝试使用这些丹药。

## 附注：关于 Buff 系统
目前的 `InventoryWindow` 只是显示获得了 Buff 文本，并没有真正把 Buff 挂载到 `Cultivator` 身上。
`Cultivator` 类中目前没有 `active_buffs` 列表。
**为了快速见效，我们暂时把 Buff 类丹药转化为直接属性收益，或者仅仅是文本反馈（如疾风散）。**
**修正**: 用户要求“明确丹药的效果”。如果只是文本提示“获得了增益”但没有实际数值变化，用户会觉得没用。
**策略调整**:
- `pill_speed_wind`: 改为增加 2 点体魄 (锻炼腿脚) 或 2 点好感。-> `{"stat_body": 2}`
- `pill_detox_0`: 减少 5 点心魔。-> `{"mind_heal": 5}`
- `pill_luck_minor`: 增加好感度 (Happy). -> `{"affection": 10}`

尽量映射到 `exp`, `stat_body`, `mind_heal`, `affection` 这四个实装的属性上。

**最终映射表**:
1. `pill_body_basic` -> `{"stat_body": 5}`
2. `pill_speed_wind` -> `{"stat_body": 2}` (敏捷也是身体素质)
3. `pill_detox_0` -> `{"mind_heal": 10}` (排毒清心)
4. `pill_mind_calm` -> `{"mind_heal": 20}`
5. `pill_strength_bary` -> `{"stat_body": 12}`
6. `pill_vis_night` -> `{"affection": 5}` (看清了世界，心情好)
7. `pill_beauty_face` -> `{"affection": 30}` (美美哒)
8. `pill_crazy_blood` -> `{"exp_gain": 0.08}` (燃血修炼，给经验)
9. `pill_luck_minor` -> `{"affection": 15}` (好运)
