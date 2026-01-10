---
description: 制定新功能开发计划 (Create Development Plan)
---

1. **环境与依赖检查 (Context Check)**
   - 充分理解用户当时的需求。
   - 读取 `docs/memory.md` 了解全局规则 (Rules) 和记忆 (Memory)。
   - 读取 `docs/plans/PLANS_README.md` 查看当前计划状态（获取最新的 Plan ID，避免冲突，并了解现有进度）。
   - 根据需求检索 `docs/` 下的相关文档（如 `docs/mechanics/`）以及相关源代码。
   - **Critical**: 拒绝代码浮肿。不要重复造轮子 (Don't Repeat Yourself)。检查现有代码中是否已有类似实现。确保架构简洁。

2. **确认需求 (Clarification)**
   - 如果需求有任何模糊之处，或者你有认为描述不清楚的地方，**必须**先反问用户，确认需求之后再开始执行任务。
   - 如果需求清晰，继续下一步。

3. **制定计划 (Drafting Plan)**
   - 确定下一个可用的 Plan ID (参考 PLANS_README.md 的 Active 和 Archive 列表)。
   - 在 `docs/plans/active/` 目录下创建新文件，命名格式建议为 `planXX_<brief_description>.md` (例如 `plan47_new_feature.md`)。
   - **文档内容必须使用中文**。
   - 计划文档应包含详细的开发步骤，例如：
     - **目标 (Objective)**: 清晰描述要解决的问题或实现的功能。
     - **分析 (Analysis)**: 涉及的文件、现有逻辑分析、需要的改动。
     - **实施步骤 (Implementation Steps)**: 非常详细、可按步骤执行的开发指令。
     - **验证 (Verification)**: 如何验证功能是否正常。

4. **更新索引 (Update Index)**
   - 将新创建的计划添加到 `docs/plans/PLANS_README.md` 的 "🚀 进行中 (Active)" 列表中，包含 Plan ID、标题、描述和链接。

5. **更新记忆 (Update Memory)**
   - 视情况更新 `docs/memory.md`。如果计划涉及全局规则变更、新引入的规范或重要架构调整，务必更新记忆文档。
   - 检查是否有过期的规则需要移除。

6. **用户确认 (User Review)**
   - 向用户展示计划概要或链接，告知已准备就绪。
   - 等待用户确认或使用 `/action` 开始执行。
