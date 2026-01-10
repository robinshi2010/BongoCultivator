# 📅 Project Plans (项目计划)

此目录包含项目的所有功能开发计划与设计文档。
开发前请查阅相关计划，以确保对齐开发意图，减少错误。

## 📌 目录结构

- **`active/`**: 当前正在进行或待执行的计划。
- **`archive/`**: 已经完成并归档的计划。

---
## 📝 待办计划

~~1. 增加一些默认的挂机收益，目前挂机收益获得的修为太少了。可以加入一些增加修为的特殊事件。~~
~~2. 商店刷新时间缩短，可以 15 分钟刷新一次。~~
~~3. 渡劫期的事件积累心魔太快了，需要平衡一下。~~
~~4. 身外化身丹和幽冥锻体丹消耗的药材一样，没有差异性，重新设计一个合理的。~~

> ✅ 以上问题已整合至 **Plan 48: 游戏平衡性调整**

## 🚀 进行中 (Active)

| Plan ID | 标题 (Title) | 描述 (Description) | 链接 (Link) |
| :--- | :--- | :--- | :--- |
| **Plan 25** | 用户系统 (User System) | 使用 Supabase 完成邮箱验证注册功能，留存用户数据。 | [plan25.md](active/plan25.md) |
| **Plan 49** | GitHub 发布准备 | 清理非必要文件，更新 .gitignore，创建宣传页。 | [plan49_github_release.md](active/plan49_github_release.md) |

---

## 📦 已归档 (Archived)

这些计划已经完成开发。如果需要回溯逻辑或查找最初的设计意图，请查阅以下文档。

### ✅ 已完成 (Completed)
| Plan ID | 标题 (Title) | 描述 (Description) | 链接 (Link) |
| :--- | :--- | :--- | :--- |
| **Plan 48** | 游戏平衡性调整 | 挂机收益+200%、坊市刷新缩短至15分钟、渡劫心魔平衡、丹药配方优化。 | [plan48_balance_tuning_done.md](archive/plan48_balance_tuning_done.md) |
| **Plan 47** | 代码质量修复 | 修复重复代码/死代码/魔法数字，整理工具目录。 | [plan47_code_quality_fix_done.md](archive/plan47_code_quality_fix_done.md) |
| **Plan 46** | 进度迁移系统 | 轮回转世功能：托盘菜单导出/导入 JSON 格式进度备份，版本无关。 | [plan46_progress_migration_done.md](archive/plan46_progress_migration_done.md) |
| **Plan 45** | 气运系统重构 | 重构气运为单世有效属性，影响修炼/掉落/渡劫，新增4种气运丹药。 | [plan45_luck_rework_done.md](archive/plan45_luck_rework_done.md) |
| **Plan 44** | 丹药效果实装 | 为所有丹药配置实际属性效果，支持混合效果。 | [plan44_pills_update.md](archive/plan44_pills_update.md) |
| **Plan 43** | 炼丹 UI 修复 | 修复炼丹按钮连点及 UI 状态同步问题。 | [plan43_fix_alchemy_ui.md](archive/plan43_fix_alchemy_ui.md) |

### 📜 历史归档 (Historical Archive)
| Plan ID | 标题 (Title) | 关键功能 (Key Features) | 链接 (Link) |
| :--- | :--- | :--- | :--- |
| **Plan 42** | 修复逻辑 Bug (Fix Logic) | 修复炼丹/交易可能导致资源负数的 Bug。 | [plan42_fix_app_logic_done.md](archive/plan42_fix_app_logic_done.md) |
| **Plan 41** | 修复日志窗口报错 | 修复 QTableWidgetItem 作用域问题。 | [plan41_fix_log_error_done.md](archive/plan41_fix_log_error_done.md) |
| **Plan 40** | 界面与交互修复 | 修复重修弹窗及移除 MPL 依赖。 | [plan40_ui_fixes_done.md](archive/plan40_ui_fixes_done.md) |
| **Plan 39** | 制作人彩蛋 | 增加 'robinshi2009' 彩蛋对话。 | [plan39_done.md](archive/plan39_creator_easter_egg_done.md) |
| **Plan 38** | 事件日志修复 | 修复事件触发时结果显示重复的 Bug。 | [plan38_event_log_fix_done.md](archive/plan38_event_log_fix_done.md) |
| **Plan 37** | 托盘与窗口置顶修复 | 修复对话框显示状态同步及 macOS 窗口置顶切换失效问题。 | [plan37_tray_fixes_done.md](archive/plan37_tray_fixes_done.md) |
| **Plan 36** | 项目体积优化 | 剔除冗余依赖，压缩图片资源，使包体 <150MB。 | [plan36_size_optimization_done.md](archive/plan36_size_optimization_done.md) |
| **Plan 35** | UI与体验优化 | 修复Windows输入框、多屏支持、托盘增强及事件日志。 | [plan35_done.md](archive/plan35_done.md) |
| **Plan 34** | 修复废丹显示 (Fix Pill Waste) | 修复废丹显示为英文的问题，并添加物品定义。 | [plan34_done.md](archive/plan34_done.md) |
| **Plan 33** | UI细节修复与图标更新 | 修复 Liquid 显示问题，更新应用图标。 | [plan33_done.md](archive/plan33_done.md) |
| **Plan 32** | 事件文案差异化 | 优化 T0-T8 通用事件文案，使其符合修仙境界。 | [plan32_done.md](archive/plan32_done.md) |
| **Plan 31** | 动态对话系统 | 数据库驱动的上下文敏感对话系统。 | [plan31_done.md](archive/plan31_done.md) |
| **Plan 30** | 探险与经济平衡 | 重构事件概率，增加通用资源掉落。 | [plan30_done.md](archive/plan30_done.md) |
| **Plan 29** | 坊市体验优化 | 统一中文阶级显示，保持列表选中状态。 | [plan29_done.md](archive/plan29_done.md) |
| **Plan 28** | 核心重构与 SQLModel | ORM 数据库层重构与 Bug 修复。 | [plan28_done.md](archive/plan28_done.md) |
| **Plan 27** | 统一窗口拖拽 | 实现所有子窗口的统一拖拽逻辑。 | [plan27_done.md](archive/plan27_done.md) |
| **Plan 26** | 坊市刷新机制 | 坊市物品刷新逻辑与动态梯度。 | [plan26_done.md](archive/plan26_done.md) |
| **Plan 24** | 每日奖励修复 | 修复每日奖励重复领取的问题。 | [plan24_done.md](archive/plan24_done.md) |
| **Plan 23** | 数据自动同步 | 静态数据的版本控制与自动同步。 | [plan23_done.md](archive/plan23_done.md) |
| **Plan 22** | 数据持久化 | 本地 AppData 存储与存档迁移。 | [plan22_done.md](archive/plan22_done.md) |
| **Plan 21** | 物品详情优化 | UI 富文本描述显示优化。 | [plan21_done.md](archive/plan21_done.md) |
| **Plan 20** | 完善丹药效果 | 为空物品注入实际效果逻辑。 | [plan20_done.md](archive/plan20_done.md) |
| **Plan 19** | 物品使用反馈 | 增加物品使用时的视觉反馈。 | [plan19_done.md](archive/plan19_done.md) |
| **Plan 18** | 修复物品使用 | 修复丹药消耗逻辑与类型映射。 | [plan18_done.md](archive/plan18_done.md) |
| **Plan 17** | 经济平衡修复 | 事件逻辑修复与经济安全锁。 | [plan17_done.md](archive/plan17_done.md) |
| **Plan 16** | 游戏进度调整 | 调整升级曲线与初期游戏体验。 | [plan16_done.md](archive/plan16_done.md) |
| **Plan 15** | 物品价值与经济 | 物品效用、市场出售与交互事件。 | [plan15_done.md](archive/plan15_done.md) |
| **Plan 14** | 轮回继承系统 | 死亡/转世逻辑与遗产继承。 | [plan14_done.md](archive/plan14_done.md) |
| **Plan 13** | 渡劫视觉逻辑 | 渡劫动画序列与透明度渲染。 | [plan13_done.md](archive/plan13_done.md) |
| **Plan 12** | 视觉素材扩展 | 扩展渡劫与炼丹的视觉素材。 | [plan12_done.md](archive/plan12_done.md) |
| **Plan 11** | 成就系统 | 成就追踪、头衔与 Buff 加成。 | [plan11_done.md](archive/plan11_done.md) |
| **Plan 10** | 奇遇事件系统 | 数据库驱动的事件引擎。 | [plan10_done.md](archive/plan10_done.md) |
| **Plan 9** | 物品扩充 | 增加 110+ 物品与修仙设定文案。 | [plan9_done.md](archive/plan9_done.md) |
| **Plan 8** | 跨平台打包 | macOS 平台 PyInstaller 打包配置。 | [plan8_done.md](archive/plan8_done.md) |
| **Plan 7** | 数据库迁移 | SQLite 迁移与 Item Tier 0-8 架构。 | [plan7_done.md](archive/plan7_done.md) |
| **Plan 6** | UI与系统优化 | 托盘信息、掉率平衡、炼丹 2.0。 | [plan6_done.md](archive/plan6_done.md) |
| **Plan 5** | 秘籍系统 | Cheat Codes 实现。 | [plan5_done.md](archive/plan5_done.md) |
| **Plan 4** | 数值平衡 | 经验曲线调整与物品平衡。 | [plan4_done.md](archive/plan4_done.md) |
| **Plan 3** | 生产力统计 | 键鼠活动记录与统计 UI。 | [plan3_done.md](archive/plan3_done.md) |
| **Plan 2** | 视觉增强 | 粒子特效与动画增强。 | [plan2_done.md](archive/plan2_done.md) |
| **Plan 1** | 核心重构 | MVC 架构与状态机重构。 | [plan1_done.md](archive/plan1_done.md) |
