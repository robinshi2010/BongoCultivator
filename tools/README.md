# 工具目录说明

## 活跃工具 (Active Tools)

这些工具是项目维护中仍在使用的：

| 文件名 | 用途 |
|--------|------|
| `generate_json_assets.py` | 从代码重建 `src/data/` 下缺失的 items/events JSON 文件 |
| `generate_icns.py` | 生成 macOS 图标文件 (.icns) |
| `generate_icon.py` | 生成应用图标 |
| `import_all_data.py` | 导入所有游戏数据到数据库 |
| `import_events.py` | 导入事件数据 |
| `init_achievements.py` | 初始化成就系统数据 |
| `optimize_assets.py` | 压缩和优化资源文件 |
| `process_images.py` | 图片预处理工具 |
| `remove_bg_tool.py` | 移除图片背景工具 |
| `analyze_recipes.py` | 分析丹方配置 |
| `audit_recipes.py` | 审计丹方数据 |
| `validate_models.py` | 验证数据模型 |

## 验证工具 (Verification Tools)

用于验证各个系统的测试脚本：

| 文件名 | 用途 |
|--------|------|
| `tools_verify_*.py` | 各种验证脚本 |
| `test_*.py` | 测试脚本 |
| `check_res.py` | 资源检查 |

## 归档工具 (Archived Tools in `archive/`)

一次性使用过的迁移/修复脚本，保留用于参考：

- `fix_*.py` - 历史修复脚本
- `update_*.py` - 历史更新脚本
- `inject_*.py` - 数据注入脚本
- `consolidate_*.py` - 数据整合脚本
- `enrich_*.py` - 数据丰富脚本
- `rebalance_*.py` - 数值平衡脚本

## Shell 脚本

| 文件名 | 用途 |
|--------|------|
| `tools_make_icon.sh` | 图标制作脚本 |

---
*最后更新: 2026-01-10*
