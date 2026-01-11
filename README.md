#  BongoCultivator (修仙桌宠)

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-green.svg)]()
[![Version](https://img.shields.io/badge/Version-1.0.0-purple.svg)]()

<p align="center">
  <img src="assets/cultivator_idle.png" alt="BongoCultivator" width="200">
</p>

<p align="center">
  <strong>在敲键盘中历练筋骨，在点鼠标中斩妖除魔，在摸鱼中打坐悟道。</strong><br>
  你的桌面，就是你的修仙洞府。
</p>

---

## 核心特色

### ⌨️ 工作即修行 (Input Driven Growth)

没有所谓的"自动挂机"。你的每一次键盘敲击、鼠标点击都会被系统捕获并转化为修为。

**APM (Actions Per Minute)** 决定了你的修炼效率：

| 状态 | 触发条件 | 修炼效率 |
|------|----------|----------|
| 🧘 **闭关 (Idle)** | 摸鱼/离开电脑 | 基础积累 |
| ⚔️ **历练 (Work)** | 敲键盘（写代码/文档） | 效率提升 |
| 📖 **悟道 (Read)** | 频繁鼠标操作 | 触发顿悟 |
| 🔥 **斗法 (Combat)** | 极高 APM（打游戏） | 灵气潮汐 |

### 桌面陪伴 (Desktop Companion)

一只可爱的修仙小人常驻桌面：
- 始终置顶但不抢占焦点
- 背景透明、可自由拖拽
- 多种状态动画（呼吸、施法、炼丹、睡眠）
- 粒子特效（雷劫、火焰、金光）

### 丹道通神 (Alchemy System)

修仙岂能无丹？收集天材地宝，按照上古丹方开炉炼丹。

- **121 种物品** (Tier 0 - Tier 8)
- **42 种丹方** 可供炼制
- **9 个品阶** 品质系统
- **坊市交易** 每 15 分钟刷新

> ⚠️ 完美品质的筑基丹能让你一步登天，而稍有不慎，炼出的废丹不仅浪费材料，还可能产生不可预知的副作用...

### 🎲 机缘与天命 (Random Encounters)

这是一个"活着"的世界。你可以选择挂机闭关，也可以选择外出历练。

- **66+ 种随机事件** 随时触发
- 根据境界和状态解锁不同事件
- 完整的修仙日志记录

> 你可能在深山遭遇**地龙翻身**，发现灵脉；也可能误入**上古遗阵**，九死一生。

### 🏆 成就系统

- 20+ 成就解锁专属头衔
- 头衔提供永久属性加成

---

## 九重境界

```
炼气期 → 筑基期 → 金丹期 → 元婴期 → 化神期 → 炼虚期 → 合体期 → 大乘期 → 渡劫期 → ✨ 飞升仙界
```


---

## 🚀 快速开始

### 方式一：下载预编译版本（推荐）

前往 [Releases](https://github.com/robinshi2010/BongoCultivator/releases) 页面下载对应平台的安装包：

| 平台 | 文件 | 说明 |
|------|------|------|
| **macOS (Apple Silicon)** | `BongoCultivator.app` | M 芯片 |
| **macOS (Intel)** | `BongoCultivator-intel.app` | Intel 芯片 |
| **Windows** | `BongoCultivator.exe` | Windows 10/11 |

#### ⚠️ macOS 安全提示

由于应用未经 Apple 签名，首次打开时会提示 **"无法验证开发者"**。请按以下步骤操作：

**方法一：右键打开（推荐）**
1. 解压下载的 `.zip` 文件
2. **右键点击**（或 Control + 点击）`BongoCultivator.app`
3. 选择 **"打开"**
4. 在弹出的对话框中点击 **"打开"** 确认

**方法二：终端命令**
```bash
# 移除隔离属性（将路径替换为实际位置）
xattr -cr ~/Downloads/BongoCultivator.app
```

> 这是 macOS Gatekeeper 的安全机制，只需操作一次，之后可正常打开。

### 方式二：源码运行

```bash
# 1. 克隆仓库
git clone https://github.com/robinshi2010/BongoCultivator.git
cd BongoCultivator

# 2. (可选) 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip3 install -r requirements.txt

# 4. 运行
python3 main.py
```

### 方式三：自行打包

如果你想自己打包成可执行文件，可以使用 PyInstaller：

```bash
# 安装 PyInstaller
pip3 install pyinstaller

# macOS (Apple Silicon) 打包
pyinstaller BongoCultivator-mac-applesilicon.spec

# Windows 打包
pyinstaller BongoCultivator-win.spec
```

打包完成后，可执行文件位于 `dist/` 目录下。

---

## 权限设置

### macOS 权限配置（重要！）

由于本应用需要监控键盘和鼠标输入来计算 APM，**必须授予输入监控权限**：

1. 打开 **系统设置** (System Settings)
2. 进入 **隐私与安全性** → **输入监控** (Input Monitoring)
3. 点击 **+** 添加 `BongoCultivator.app`（或终端/IDE，如果是源码运行）
4. 勾选启用
5. **重启应用**使权限生效

> 如果运行后发现 APM 始终为 0，很可能是权限未正确授予。

### Windows 注意事项

- ⚠️ 部分杀毒软件可能误报（因为应用会监控键盘输入）
- 请将 `BongoCultivator.exe` 添加到杀毒软件的**白名单**中
- 如遇到 Windows Defender 拦截，点击 **更多信息** → **仍要运行**

---

## 操作指南

| 操作 | 说明 |
|------|------|
| **左键拖拽** | 移动小人位置 |
| **左键点击** | 对话/互动 |
| **右键点击** | 打开功能菜单 |

### 功能菜单

| 菜单项 | icon | 功能 |
|--------|------|------|
| **状态** | 📊 | 查看详细属性、境界、修为进度 |
| **储物袋** | 🎒 | 查看物品、使用丹药 |
| **炼丹房** | ⚗️ | 合成丹药 |
| **坊市** | 🏪 | 购买材料和丹药 |
| **统计** | 📈 | 工作效率图表 |
| **设置** | ⚙️ | 系统选项 |

---

## 技术栈

| 组件 | 技术 |
|------|------|
| **语言** | Python 3.10+ |
| **GUI** | PyQt6 |
| **数据库** | SQLite + SQLModel |
| **图表** | Matplotlib |
| **输入监听** | Pynput |
| **打包** | PyInstaller |

### 依赖项

```
PyQt6>=6.4.0
pynput>=1.7.6
sqlmodel>=0.0.14
matplotlib>=3.7.0
Pillow>=9.5.0
```

---

## 项目结构

```
BongoCultivator/
├── main.py                 # 程序入口
├── requirements.txt        # 依赖声明
├── LICENSE                 # CC BY-NC-SA 4.0
├── assets/                 # 资源文件
│   ├── cultivator_*.png    # 角色状态图
│   ├── tribulation_*.png   # 渡劫特效图
│   └── icon.icns           # 应用图标
└── src/                    # 源代码
    ├── cultivator.py       # 核心逻辑
    ├── pet_window.py       # 桌宠窗口
    ├── input_monitor.py    # 输入监听
    ├── data/               # 静态数据 (JSON)
    ├── models/             # 数据模型
    ├── services/           # 业务服务
    ├── ui/                 # UI 组件
    └── utils/              # 工具函数
```

---

## 常见问题 (FAQ)

### Q: 为什么我的 APM 一直是 0？
**A:** 请检查是否已授予输入监控权限（见上方"权限设置"章节）。macOS 用户需要在系统设置中明确授权。

### Q: 应用启动后看不到小人？
**A:** 小人默认出现在屏幕右下角。尝试将所有窗口最小化，或者在 Dock/任务栏中找到应用图标（在托盘中有开启对话框和一直保持在最上层的选项）。

### Q: 如何重置游戏进度？
**A:** 删除应用同目录下的 `user_data.db` 文件即可重新开始。

### Q: 炼丹失败率太高怎么办？
**A:** 
1. 减少APM，炼丹是个精细活儿，不要操之过急。

### Q: 应用会占用很多资源吗？
**A:** 正常情况下，CPU 占用 < 1%，内存 < 100MB。如果发现异常，请提交 Issue。

---

## 📜 许可证

本项目采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 协议。

✅ 免费使用和分享  
✅ 可以修改代码  
❌ **禁止商业使用**  
🔄 修改版须使用相同协议

---

## 🤝 贡献

欢迎提交 Issue 或 PR！

如果你有：
- 有趣的修仙事件文案
- 新的丹药点子
- Bug 反馈
- 功能建议

请在 [Issues](https://github.com/robinshi2010/BongoCultivator/issues) 中留言。

---

## 联系

- GitHub: [@robinshi2010](https://github.com/robinshi2010)

---

## 灵感来源

本项目的灵感来源于 [BongoCat](https://github.com/ayangweb/BongoCat) 这个非常受欢迎的桌面键盘猫项目。看到那只可爱的敲键盘的小猫后，作为一个修仙小说爱好者，突发奇想：为何不做一个修仙小人呢？

于是就有了这个**赛博修仙桌宠**——让你在上班摸鱼的同时也能感受修仙的乐趣，在敲代码的间隙积累修为，在 996 的苦海中寻得一丝仙缘。

感谢 BongoCat 项目带来的灵感，也感谢每一位在网文世界中陪伴我们的修仙前辈们。

---

<p align="center">
  <strong>祝各位道友都修炼有成，得证大道</strong>
</p>
