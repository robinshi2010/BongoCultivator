# Plan 49: GitHub 发布准备 (GitHub Release Preparation)

## 目标 (Goals)

将项目发布到 GitHub，只保留必要的源代码，排除开发工具、缓存、构建产物等非必要文件。

## 需要排除的目录/文件

| 目录/文件 | 原因 | 处理方式 |
|-----------|------|----------|
| `.agent/` | AI Agent 工作目录 | 添加到 .gitignore |
| `__pycache__/` | Python 缓存 | 已在 .gitignore |
| `build/` | PyInstaller 构建中间文件 | 已在 .gitignore |
| `dist/` | 打包输出 | 已在 .gitignore |
| `logs/` | 运行日志 | 已在 .gitignore |
| `tools/` | 开发/迁移工具脚本 | 添加到 .gitignore |
| `pages/` | 其他页面 | 添加到 .gitignore |
| `docs/plans/` | 开发计划文档 | 添加到 .gitignore |
| `data/` | 运行时数据 | 添加到 .gitignore |
| `user_data.db` | 用户存档 | 已在 .gitignore |
| `AGENTS.md` | Agent 配置 | 添加到 .gitignore |
| `*.spec` | PyInstaller 配置 | 可选保留/排除 |

## 需要保留的核心文件

```
BongoCultivator/
├── main.py                 # 程序入口
├── requirements.txt        # 依赖声明
├── README.md               # 项目说明
├── LICENSE                 # 开源协议 ✅ 已创建
├── index.html              # 宣传页 ✅ 已创建
├── .gitignore              # Git 忽略配置
├── assets/                 # 资源文件
│   ├── *.png               # 图片素材
│   └── *.icns              # 图标
└── src/                    # 源代码
    ├── *.py                # 核心代码
    ├── data/               # 静态数据 (items.json, events.json, dialogues.json)
    ├── models/             # 数据模型
    ├── services/           # 业务服务
    ├── ui/                 # UI 组件
    └── utils/              # 工具函数
```

---

## 实施步骤 (Implementation Steps)

### ✅ 步骤 1: 添加 LICENSE 文件

- **已完成** (2026-01-11 00:01)
- 选择 **CC BY-NC-SA 4.0** 协议（署名-非商业-相同方式共享）
- 文件位置: `LICENSE`
- 特点: 允许使用和修改，**禁止商业盈利**

### ✅ 步骤 2: 创建宣传页

- **已完成** (2026-01-10 23:57)
- 文件位置: `index.html`
- 特点:
  - 使用项目实际图片资源
  - ZCOOL KuaiLe 字体（易读的手写风格）
  - 浮动光球 + 网格背景 + 旋转法阵环
  - 6 大核心特性展示
  - 响应式设计

### ⏳ 步骤 3: 更新 .gitignore

需要添加以下规则：

```gitignore
# Development Files
.agent/
tools/
pages/
data/
AGENTS.md

# Documentation (keep README only)
docs/plans/
docs/mechanics/
docs/memory.md
docs/STRUCTURE.md
docs/distribution_guide.md

# PyInstaller
*.spec
```

### ⏳ 步骤 4: 清理 Git 缓存

```bash
# 从版本控制中移除（但不删除本地文件）
git rm -r --cached .agent/ tools/ pages/ data/ docs/plans/ AGENTS.md
git rm --cached *.spec
```

### ⏳ 步骤 5: 优化 README.md

更新 README 使其更适合开源发布：
- [ ] 添加 Badge (License, Python Version)
- [ ] 添加安装说明
- [ ] 添加截图/GIF 演示
- [ ] 添加贡献指南

### ⏳ 步骤 6: 初始化/推送到 GitHub

```bash
# 如果是新仓库
git remote add origin https://github.com/YOUR_USERNAME/BongoCultivator.git

# 提交更改
git add .
git commit -m "chore: 准备 GitHub 发布"

# 推送
git push -u origin main
```

---

## 文件变更清单

| 文件 | 操作 | 状态 | 说明 |
|------|------|------|------|
| `LICENSE` | 新增 | ✅ | CC BY-NC-SA 4.0 协议 |
| `index.html` | 新增 | ✅ | 精美宣传页 |
| `.gitignore` | 修改 | ⏳ | 添加排除规则 |
| `README.md` | 修改 | ⏳ | 优化为开源风格 |
| `.agent/` | 排除 | ⏳ | 从版本控制移除 |
| `tools/` | 排除 | ⏳ | 从版本控制移除 |
| `pages/` | 排除 | ⏳ | 从版本控制移除 |
| `docs/plans/` | 排除 | ⏳ | 从版本控制移除 |

---

## 验证清单

- [ ] 克隆新仓库可以正常运行 `python main.py`
- [ ] 所有依赖在 requirements.txt 中声明
- [ ] 静态数据文件存在 (src/data/)
- [ ] 资源文件完整 (assets/)
- [ ] README 包含完整的安装说明
- [ ] LICENSE 文件存在
- [ ] 宣传页可正常访问

---

## 进度

| 步骤 | 状态 | 完成时间 |
|------|------|----------|
| LICENSE | ✅ 完成 | 2026-01-11 00:01 |
| 宣传页 | ✅ 完成 | 2026-01-10 23:57 |
| .gitignore | ⏳ 待执行 | - |
| Git 清理 | ⏳ 待执行 | - |
| README | ⏳ 待执行 | - |
| 推送 GitHub | ⏳ 待执行 | - |

---

**预计工作量**: 30 分钟 (剩余约 15 分钟)
**优先级**: 高
**状态**: 进行中 (2/6 完成)
