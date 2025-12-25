# BongoCultivation 打包与分发指南

本文档详细说明了如何将《电子修仙》打包为独立可执行程序，以及在不同机器上分发和运行时常见的问题与解决方案。

## 1. 打包指南

本项目使用 PyInstaller 进行打包，所有配置已集成在 `.spec` 配置文件中。

### macOS 打包 (Apple Silicon/Intel)

在 macOS 环境下，使用终端进入项目根目录，运行以下命令：

```bash
# 确保已安装 pyinstaller
pip3 install pyinstaller

# 使用 spec 文件打包
pyinstaller BongoCultivation-mac-applesilicon.spec
```

*   **输出结果**: 打包好的 `.app` 文件将位于 `dist/BongoCultivation.app`。
*   **注意**: 这是一个包含完整运行环境的文件夹（Bundle），看起来像一个单一文件。

### Windows 打包

**注意**: Windows 包必须在 Windows 环境下进行打包。无法在 Mac 上直接打包出 Windows exe。

在 Windows 环境下，使用 PowerShell 或 CMD 进入项目根目录：

```bash
# 使用 spec 文件打包
pyinstaller BongoCultivation-win.spec
```

*   **输出结果**: 打包好的 `.exe` 或文件夹将位于 `dist/` 目录下。

---

## 2. 分发说明

*   **无需环境**: 打包后的程序是**完全自包含的**。目标机器**不需要**安装 Python，也不需要安装任何 pip 依赖库。
*   **直接拷贝**: 你可以直接将 `dist/` 目录下的 `.app` (Mac) 或文件夹 (Windows) 压缩后拷贝给其他用户。

---

## 3. macOS 运行常见问题 ("应用已损坏")

当你将 App（通过 AirDrop、微信、网盘等）发送给朋友，或拷贝到另一台 Mac 上时，macOS 的 Gatekeeper 安全机制可能会拦截运行。

### 问题现象
双击 App 时提示：
> **“BongoCultivation 已损坏，打不开。您应该将它移到废纸篓。”**
> 或
> **“无法打开 BongoCultivation，因为无法验证开发者。”**

这**不是**程序真的坏了，而是 macOS 给从外部接收的文件加上了安全隔离标签（Quarantine）。

### 解决方案
在目标机器上，只需执行一条命令移除隔离属性：

1.  把 App 拖动到「应用程序」文件夹（或桌面）。
2.  打开 **终端 (Terminal)**。
3.  输入以下命令（注意命令最后有一个空格），然后把 App 图标拖进终端窗口，它会自动填入路径：
    ```bash
    sudo xattr -cr /Applications/BongoCultivation.app
    ```
    *(具体路径取决于你放在哪里)*
4.  按下回车，输入电脑密码（输入时看不见），再回车。
5.  现在可以正常双击打开了。

---

## 4. 权限授权说明

本程序核心玩法涉及**键盘鼠标的自动化操作**和**状态检测**，因此必须获取系统相关权限才能正常运行。

### 所需权限
1.  **辅助功能 (Accessibility)**: 用于模拟按键和鼠标点击。
2.  **输入监听 (Input Monitoring)**: (可选) 用于检测用户是否正在忙碌，以实现"上班摸鱼"模式的自动暂停/恢复。

### 授权步骤 (macOS)

首次运行时，系统可能会弹出请求权限的提示，或者程序直接报错/无反应。请按以下步骤手动检查：

1.  打开 **系统设置 (System Settings)** -> **隐私与安全性 (Privacy & Security)**。
2.  点击 **辅助功能 (Accessibility)**。
3.  在列表中找到 **BongoCultivation**。
    *   如果没有，点击 `+` 号手动添加打包好的 App。
4.  **确保开关处于打开状态**。
5.  如果程序仍然无法操作鼠标/键盘：
    *   在列表中选中 `BongoCultivation`。
    *   点击 `-` 号将其删除。
    *   重新添加一次（这通常能解决签名更新后原有权限失效的问题）。
6.  重启 App。

### 授权步骤 (Windows)

Windows 通常不需要特殊授权即可模拟输入，但如果运行在管理员权限运行的游戏或软件之上，可能需要：
*   **以管理员身份运行**: 右键点击 `.exe` -> "以管理员身份运行"。
