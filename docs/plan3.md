# Plan 3: 生产力与统计扩展 (Productivity & Statistics Expansion)

本计划旨在将桌宠升级为生产力辅助工具，通过 `pynput` 监听并记录用户行为，使用 SQLite 本地存储数据，并提供多维度的统计分析（日/周/月/年）和可视化报表。

## 核心目标
1.  **数据采集**: 低功耗、隐私安全地记录键盘敲击和鼠标操作。
2.  **数据持久化**: 使用 SQLite 存储历史数据，支持按天、周、月、年查询。
3.  **统计分析**:
    - 周期统计：日、周、月、年的总操作量。
    - 忙碌分析：分析每个周期内最忙碌的时段（如一天中哪一小时最忙，一周中哪天最忙）。
4.  **可视化**: 图表展示趋势与分布。
5.  **游戏化联动**: 努力工作（高 APM）换取游戏资源。

---

## 详细实施计划

### Phase 1: 数据层 (Data Persistence Layer)
**目标**: 建立可靠的本地存储机制。
1.  **数据库设计 (`src/database.py`)**:
    -   使用 `sqlite3`。
    -   **Table `activity_logs_minute`**:
        -   `timestamp` (INTEGER/DATETIME): 记录时间戳 (精确到分钟)。
        -   `keys_count` (INTEGER): 该分钟内的键盘敲击数。
        -   `mouse_count` (INTEGER): 该分钟内的鼠标操作数(点击+滚动)。
        -   *(Index on timestamp for fast queries)*
2.  **数据聚合策略**:
    -   前端监听器按秒采集。
    -   后台线程每 **1 分钟** 将内存中的计数写入数据库。
    -   如果 1 分钟内无操作，则不写入（节省空间）。
3.  **数据清理**:
    -   (可选) 超过 1 年的分钟级数据可以聚合成小时级或天级数据 (Data Rolling)，本阶段暂不强制，但在设计上预留接口。

### Phase 2: 采集与录入 (Collection & Recording)
**目标**: 改造现有的 `InputMonitor` 以支持持久化记录。
1.  **改造 `src/input_monitor.py`**:
    -   分离 "实时 APM 计算" (用于 UI展示) 和 "累计计数" (用于存库)。
    -   增加 `pop_accumulated_counts()` 接口，取出自上次取出后的所有计数， atomic 操作，确保不丢数据。
2.  **创建记录器服务 (`src/services/activity_recorder.py`)**:
    -   后台线程/定时器。
    -   每 60 秒调用 `InputMonitor` 获取累计数据。
    -   调用 `DatabaseManager` 写入 SQLite。

### Phase 3: 统计引擎 (Statistics Engine)
**目标**: 提供业务层所需的统计数据。
1.  **创建 `src/services/stats_analyzer.py`**:
    -   **`get_summary(start_time, end_time)`**: 返回该时间段的总键鼠数。
    -   **`get_trend(start_time, end_time, bucket_size)`**: 返回时间序列数据，用于画折线图。
    -   **`get_busy_analysis(start_time, end_time)`**:
        -   对于“一天”视图：返回 0-23 点每小时的活跃度，找出最忙小时。
        -   对于“一周”视图：返回 周一~周日 每天的总活跃度，找出最忙的一天。
        -   对于“一月/一年”视图：返回每日/每月的趋势。

### Phase 4: 可视化 UI (Visualization)
**目标**: 让用户直观看到数据。
1.  **统计面板 (`src/ui/stats_window.py`)**:
    -   **Tab 1: 今日 (Daily)**
        -   大字显示：今日总键入、总点击、今日专注时长（活跃分钟数）。
        -   图表：24小时活跃度柱状图。
        -   分析结论：“今天 14:00-15:00 是你最‘修仙’的时刻”。
    -   **Tab 2: 历史 (History - Week/Month/Year)**
        -   切换按钮：近7天 / 本月 / 今年。
        -   图表：趋势折线图。
        -   热力图 (可选)：类似 GitHub Contribution 的日历热力图。
2.  **技术选型**:
    -   使用 `matplotlib` 生成静态图 (`FigureCanvasQTAgg`) 嵌入 PyQt 界面（简单、兼容性好）。

### Phase 5: 游戏化联动 (Gamification)
1.  **修炼系统接入**:
    -   每日结算：基于今日总操作量，发放“灵石”或“修为”。
    -   实时反馈：APM 爆表时，桌宠头顶冒出特殊特效（如“燃烧”）。

---

## 执行步骤 (Step-by-Step Execution)
*执行规则：每完成一步，检查功能，更新 memory/plan，再进行下一步。*

#### Step 1: 数据库与基础结构
- [x] 创建 `src/database.py`，实现 `init_db` 和 `insert_activity`。
- [x] 编写简单的测试脚本，验证数据库写入和读取。

#### Step 2: 改造监听与录入
- [x] 修改 `src/input_monitor.py`，支持累积计数导出。
- [x] 创建 `src/services/activity_recorder.py`，实现每分钟自动落库逻辑。
- [x] 在 `main.py` 或 `PetWindow` 中启动 `ActivityRecorder`。
- [x] **验证**: 运行程序 5 分钟，操作键盘鼠标，检查数据库是否有 5 条记录。

#### Step 3: 统计分析逻辑
- [x] 创建 `src/services/stats_analyzer.py`。
- [x] 实现 `get_daily_stats` (今日概览 & 24h趋势)。
- [x] 实现 `get_period_stats` (指定日期范围的统计 & 最忙时段分析)。
- [x] **验证**: 编写单元测试，模拟数据库数据，验证统计函数输出准确。

#### Step 4: UI 原型与今日视图
- [x] 创建 `src/ui/stats_window.py` 基础窗口。
- [x] 实现 "今日" 标签页布局。
- [x] 接入 `stats_analyzer` 数据，显示今日总数。
- [x] 集成 `matplotlib` 绘制今日每小时柱状图。
- [x] **验证**: 启动应用，打开统计面板，能看到基于 Step 2 录入的数据的图表。

#### Step 5: 历史视图与多周期支持
- [x] 在 `stats_window.py` 增加 周/月/年 切换逻辑。
- [x] 完善 `stats_analyzer` 的长周期查询优化。
- [x] 显示“最忙分析”结论文本。

#### Step 6: 游戏化与收尾
- [x] 将活跃度换算为游戏资源 (在 `cultivator.py` 中增加接口)。
- [x] 代码清理与注释完善。
- [x] 全局测试。

---
**Privacy Note**: 所有数据存储在本地 `user_data.db` (或类似文件)，不上传。
