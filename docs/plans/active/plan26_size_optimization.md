# Plan 26: 项目体积优化与瘦身计划

## 1. 现状分析
当前项目总占用约为 700MB，主要问题集中在以下几个方面：
- **Dist 打包产物 (481MB)**: 包含了未使用的重型第三方库（如 numpy, cryptography, oracledb, psycopg2 等），且存在文件夹与 .app 包的双重拷贝。
- **Assets 资源文件 (37MB)**: 部分 PNG 图片分辨率过大（如 `cultivator_alchemy_high.png` 为 4.3MB），未进行压缩优化。
- **Build 临时文件 (108MB)**: PyInstaller 构建缓存，可安全清理。

## 2. 目标
- 将 macOS 应用包 (`.app`) 体积从 ~240MB 降低至 **150MB 以下**。
- 清理项目冗余文件，减少磁盘占用。
- 确保清理后应用功能（特别是图像显示和数据库连接）不受影响。

## 3. 执行步骤

### 阶段一：依赖剔除 (Dependency Pruning)
- **动作**: 修改 `BongoCultivator-mac-applesilicon.spec` 文件。
- **细节**: 在 `excludes` 列表中显式排除以下未使用的库：
  - `numpy`
  - `matplotlib`
  - `pandas`
  - `scipy`
  - `PIL` (注意：代码只用到了 Pillow，通常不需要排除 PIL，但需确认是否引入了多余组件，暂且只排除明确不用的)
  - `cryptography` (除非 python-jose 等依赖)
  - `psycopg2` (本项目使用 sqlite/json，不需 postgres)
  - `oracledb`
  - `zmq` (ZeroMQ)
  - `wx`
  - `tkinter`

### 阶段二：资源优化 (Asset Optimization)
- **动作**: 编写脚本批量压缩 `assets/` 目录下的 PNG 图片。
- **细节**:
  - 使用 `Pillow` 对大于 500KB 的图片进行优化。
  - 调整压缩质量 (Quality=85) 并移除无关元数据。
  - 预计可减少 30-50% 的图片体积。

### 阶段三：清理与重构 (Clean & Rebuild)
- **动作**:
  1. 删除 `build/` 和 `dist/` 文件夹。
  2. 运行 PyInstaller 重新打包。
  3. 验证打包后的应用能否正常启动，检查日志是否有 `ModuleNotFoundError`。

### 阶段四：验证
- **检查点**:
  - `dist/BongoCultivator.app` 的最终大小。
  - 游戏内 `cultivator_alchemy_high.png` 等大图是否清晰且加载正常。
  - 数据库读写功能是否正常（排除依赖未误伤 sqlite3）。

## 4. 风险控制
- 排除依赖前先确认 `requirements.txt` 和 `import` 引用，确保不会误删 `sqlmodel` 或 `PyQt6` 必须的底层库。
- 资源压缩前对 `assets` 目录进行备份 (`assets_bak`)。
