# Plan 32: 事件文案差异化与内容丰富 (Event Enrichment)

## 📌 目标 (Objective)

针对 `src/data/events.json` 中自动生成的通用资源事件（采集、挖矿、狩猎）进行文案优化和逻辑差异化。
目前 T0 到 T8 的事件文案完全一致，缺乏代入感。本计划将根据境界（Tier）生成符合修仙背景的独特描述。

---

## 🛠️ 执行步骤 (Implementation Steps)

### Phase 1: 脚本开发 (Scripting)

创建新工具脚本 `tools/enrich_events_content.py`：
1.  **文案库设计**: 定义分层级的文案模板。
    *   **Tier 0-2 (炼气/筑基/金丹)**: 凡人界/低级修真界。关键词：山野、灵气、野兽。
    *   **Tier 3-5 (元婴/化神/炼虚)**: 秘境/险地。关键词：遗迹、虚空、妖王。
    *   **Tier 6-8 (合体/大乘/渡劫)**: 仙界边缘/法则之地。关键词：太古、法则、神兽。
2.  **生成逻辑**:
    *   读取现有的 `src/data/events.json`。
    *   遍历所有 `id` 匹配 `evt_t{tier}_{type}` 的事件。
    *   根据 Tier 替换 `title` 和 `text`。
    *   保留原有的 `effects: { "random_material": 1 }` 核心逻辑。

### Phase 2: 文案示例 (Content Examples)

| Tier | Type | Old Title | New Title | New Text Example |
| :--- | :--- | :--- | :--- | :--- |
| **0** | Gathering | 山野采药 | 山野寻踪 | 在后山悬崖边，你发现了一株沾着露水的止血草。 |
| **4** | Mining | 矿脉探寻 | 虚空掘金 | 你在空间乱流中捕捉到一块漂浮的陨铁，上面还残留着星辰之力。 |
| **8** | Hunting | 狩猎妖兽 | 屠龙证道 | 一头太古魔龙由于年老体衰被你捡漏斩杀，龙血染红了半边天。 |

### Phase 3: 数据更新 (Data Update)

1.  运行脚本更新 `src/data/events.json`。
2.  修改String `src/services/data_loader.py` 中的 `DATA_VERSION` 至 `003`，触发数据库自动同步。

---

## ✅ 验收标准 (Acceptance Criteria)

1.  **文案多样性**: 打开 `events.json`，不同 Tier 的同类事件应有明显不同的标题和描述。
2.  **逻辑保留**: 事件的 `weight`, `min_layer`, `max_layer`, `effects` 等核心数值逻辑保持不变。
3.  **数据库同步**: 运行游戏后，`event_definitions` 表中的数据应更新为新文案。
