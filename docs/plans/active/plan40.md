# Plan 40: 界面与交互修复 (UI & Interaction Fixes)

## 🎯 目标 (Goals)
修复用户反馈的两个主要交互问题，并确保界面风格统一且符合项目“极致美学”的要求。

1.  **修复兵解重修弹窗异常**: 替换原生 `QMessageBox`，使用自定义风格的对话框，解决 Windows 下显示异常问题，并提升视觉体验。
2.  **修复修仙记录无法打开**: 解决因移除 `matplotlib` (Plan 36) 导致的 `StatsWindow` 导入失败问题，使用原生 `QPainter` 或 CSS 重写图表绘制逻辑。

## 📋 任务描述 (Tasks)

### 1. 兵解重修弹窗重构 (Reincarnation Dialog)
- [ ] **创建/复用自定义对话框**:
  - 检查现有的 `src/ui/custom_input.py` 或创建通用的 `ConfirmationDialog`。
  - 确保支持自定义标题、内容及“确定/取消”按钮文案。
  - 样式需符合“修仙风格”（深色背景、金色边框/文字）。
- [ ] **替换调用逻辑**:
  - 修改 `src/pet_window.py` 中的 `on_voluntary_rebirth` 方法。
  - 移除 `QMessageBox.question`，改为调用自定义对话框。

### 2. 修仙记录窗口修复 (Stats Window Fix)
- [ ] **移除 Matplotlib 依赖**:
  - 修改 `src/ui/stats_window.py`。
  - 删除所有 `matplotlib` 相关的 import。
- [ ] **重写图表组件**:
  - **今日趋势图 (Today Chart)**: 使用 `QPainter` 绘制简单的柱状图或折线图。
  - **历史趋势图 (History Chart)**:同样使用自定义 Widget 绘制简易折线图。
  - 保持图表风格为金色/半透明，与现有 UI 融合。
- [ ] **验证**:
  - 确保点击“修仙记录”能正常打开窗口。
  - 确保数据正常显示，图表无报错。

## 📝 验收标准 (Acceptance Criteria)
1.  **兵解重修**: 在 Windows 环境下，点击“兵解重修”能弹出风格统一的对话框，文字显示正常，按钮功能可用。
2.  **修仙记录**: 点击菜单中的“修仙记录”能秒开窗口，且程序不报错；图表虽然简化但仍能直观展示趋势。
3.  **依赖检查**: 全局搜索确认不再包含 `matplotlib` 引用（除了已隔离的旧代码或注释）。
