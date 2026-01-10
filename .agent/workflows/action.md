---
description: 开始执行 plan
---

1. **准备阶段 (Preparation)**
   - 确认当前要执行的计划文件（通常在 `docs/plans/active/` 下）。
   - 阅读 `docs/memory.md` 回顾全局规则。
   - 仔细阅读计划文档，确保完全理解所有步骤。
   - **Check**: 如果有任何不确定的地方，**必须**先向用户询问，确认后再行动。

2. **执行开发循环 (Execution Loop)**
   - 严格按照计划文档的步骤顺序执行。
   - **每完成一个步骤 (Step-by-Step)**:
     1. 编写代码/修改文件。
     2. **自我验证 (Self-Correction)**: 检查代码是否符合需求，是否有明显错误，运行（如果可行）以验证。
     3. **更新计划文档 (Update Plan)**: 在计划文档中对应的步骤前打钩 (将 `- [ ]` 改为 `- [x]`)，或添加简短的执行备注。
   - 避免一次性写完所有代码再检查，要小步快跑，稳扎稳打。

3. **完成与归档 (Completion & Archiving)**
   - 当所有步骤都完成后：
     1. **重命名计划文件**: 将文件从 active 移动到 archive，并添加 `_done` 后缀。
        - 例如: `mv docs/plans/active/plan47_feature.md docs/plans/archive/plan47_feature_done.md`
        // turbo
     2. **更新索引 (Update Index)**: 修改 `docs/plans/PLANS_README.md`。
        - 将该计划从 "🚀 进行中 (Active)" 列表移动到 "📦 已归档 (Archived) -> ✅ 已完成 (Completed)" 列表中。
        - 更新链接指向新的 archive 路径。
     3. **更新记忆 (Update Memory)**:
        - 如果在开发过程中产生了新的重要经验、规则或架构变更，更新 `docs/memory.md`。

4. **总结 (Summary)**
   - 向用户报告任务已完成，并简要总结所做的工作。
