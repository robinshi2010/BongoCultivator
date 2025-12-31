# Plan 30: 探险与经济平衡 (Exploration & Economy Balance)

## 📌 目标 (Objective)

解决玩家反馈 "挂机一天凑不齐丹药" 的问题。
当前 `EventEngine` 仅基于 `weight` (权重) 随机选择事件，且所有事件权重均为默认值 10，导致：
1. **稀有度失效**: 稀有事件和普通事件概率相同。
2. **掉落不稳定**: 缺乏稳定的材料获取来源 (如采药、挖矿事件)。
3. **经济脱节**: 配方所需材料可能没有对应的掉落事件。

本计划旨在重构事件概率模型，并补充缺少的资源获取事件。

---

## 🛠️ 执行步骤 (Implementation Steps)

### Phase 1: 事件概率模型调整 (Event Probability Rebalance)
- [ ] **权重差异化**: 更新 `src/data/events.json` 及数据库，重新分配权重：
    - `Common` (日常/文本): Weight 100
    - `Uncommon` (资源/小额奖励): Weight 40
    - `Rare` (稀有掉落/奇遇): Weight 10
    - `Unique` (唯一/大机缘): Weight 2
- [ ] **迁移数据**: 编写一次性脚本 `tools/rebalance_events.py`，读取 json 并更新 DB 中的权重，同时废弃旧的 `chance` 字段。

### Phase 2: 新增资源型事件 (New Resource Events)
- [ ] **通用采集事件**: 为每个大境界 (Tier 0-8) 增加三个通用资源事件：
    - **采药 (Gathering)**: 产出当前阶级的随机草药 (Weight 30)。
    - **挖矿 (Mining)**: 产出当前阶级的随机矿石 (Weight 30)。
    - **狩猎 (Hunting)**: 产出当前阶级的随机妖丹/材料 (Weight 30)。
    - *注*: 利用 `ItemManager.get_random_material(tier)` 动态生成掉落，无需为每个物品写事件。
- [ ] **扩展 `EventEngine`**: 支持 `effects: {"random_material": 1}` 这种动态效果，以便支持上述通用事件。

### Phase 3: 配方与掉落核对 (Recipe Audit)
- [ ] **核对脚本**: 编写脚本检查所有 `recipes` 中的原料是否都有对应的获取途径 (Market 或 Event Drop)。
- [ ] **填补空缺**: 如果发现断档 (例如某关键草药从未掉落)，则将其加入坊市列表或特定事件。

---

## ✅ 验收标准 (Acceptance Criteria)
1. **挂机收益**: 模拟挂机 1 小时 (约 60 次检测)，应能获得至少 5-10 个当前阶级的制作材料。
2. **概率正常**: 普通文本事件出现频率最高，稀有奇遇偶尔出现，不再是平均分布。
3. **闭环**: 玩家处于任意阶级时，均有概率获得该阶级突破丹/属性丹所需的全部原料。
