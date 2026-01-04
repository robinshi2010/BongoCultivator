# Plan 38: 修复事件日志重复显示 Bug

## 1. 问题描述
用户反馈 Trigger 事件（如“坊市捡漏”、“地龙翻身”）时，UI 上会连续显示两次收益结果。
- 现象：日志中出现重复的 `> 灵石 -50` `获得: ...` `> 灵石 -50` `获得: ...`。
- 疑虑：用户担心实际收益/扣除是否也执行了两次。

## 2. 原因分析
经过对 `src/cultivator.py` 的代码审查，发现 `update` 方法在处理随机事件触发时存在**代码重复粘贴错误**。

```python
# src/cultivator.py lines 526-529 (approx)
if result_msg:
    event_msg += f"\n> {result_msg}"
if result_msg:
    event_msg += f"\n> {result_msg}"  <-- 重复块
```

`trigger_event` 方法仅被调用一次，意味着**逻辑上的数值变更只发生了一次**。但由于显式日志（`result_msg`）被拼接了两次到 `event_msg` 字符串中，导致 UI 显示了两份结果。

## 3. 解决方案
- 删除 `src/cultivator.py` 中重复的日志拼接代码块。

## 4. 执行步骤
1.  **编辑文件**: `src/cultivator.py`
2.  **删除**: 移除多余的 `if result_msg:` 块。

## 5. 验证
- 修复后，事件日志应呈现简洁的单次结果显示。
- 确认逻辑执行次数保持为 1 次。

## 5. 执行结果 (Execution Result)
- **修复重复日志**: 已删除 `src/cultivator.py` 中重复拼接 `result_msg` 的代码块。
- **验证**: 现在的代码只会将事件结果追加一次到日志消息中。
