• 已在 macOS 上把“置顶+鼠标穿透”默认开启，并新增了全局输入权限提示与可持久化的配置开
  关。托盘里切换“锁定/解锁”会同步写回配置，重启后保持。

  - config.json 新增 ghost_mode_on_startup（默认 true），作为功能开关；src/
    app_config.py 负责读取/写入配置。
  - src/tray_icon.py 启动时应用配置并在托盘切换后持久化。
  - src/input_monitor.py 启动监听失败时记录权限错误。
  - src/pet_window.py 在 macOS 下检测到输入监听不可用时弹出权限提示。

  macOS 权限提示说明：请在“系统设置 > 隐私与安全性 > 输入监控”中允许当前应用或 python
  进程；如仍无效，再开启“辅助功能”权限。

  测试未运行（暂无自动化测试）。

  建议的下一步：

  1. 运行 python main.py，确认启动即处于“锁定/鼠标穿透”状态。
  2. 如果键鼠动作不触发动画，按提示在系统设置中授予权限后重启应用。
  3. 如需默认关闭，修改 config.json 将 ghost_mode_on_startup 设为 false。


• 已修复这两个问题：默认不再强制全局穿透（避免“无法操作游戏”），并在 macOS 通过原生窗口
  层级强制置顶，确保穿透时也不会被遮挡。

  - src/pet_window.py 现在在切换穿透时同步设置 macOS 窗口层级（Floating level）并
    raise_()，保证始终置顶。
  - src/pet_window.py 把 macOS 原生设置（忽略鼠标事件 + 置顶层级）合并到一次调用里，避
    免状态不同步。
  - src/app_config.py/config.json 默认关闭启动即穿透，避免启动后无法交互；仍可通过配置
    或托盘切换开启。

  当前配置开关：

  - config.json → ghost_mode_on_startup：false 表示启动可交互，true 表示启动即穿透。

  测试未运行（暂无自动化测试）。

  建议下一步：

  1. 运行 python main.py，确认可交互且置顶稳定。
  2. 如需默认穿透，将 config.json 的 ghost_mode_on_startup 设为 true。


   已修复 macOS 下“解锁后仍无法点击”和“穿透时不置顶”的问题。核心是：在 macOS 只用原生
  NSWindow.ignoresMouseEvents 来做穿透，不再叠加 Qt 的 WindowTransparentForInput/
  WA_TransparentForMouseEvents（这会导致解锁后仍被系统吃掉点击）。同时在窗口重新创建时
  重复应用置顶层级，避免失效。

  变更点：

  - src/pet_window.py：macOS 下不再设置 WindowTransparentForInput 和
    WA_TransparentForMouseEvents，避免“解锁后仍穿透”的锁死状态。
  - src/pet_window.py：在 showEvent + 两次延迟调用中重新应用 NSWindow 的穿透/置顶设置，
    修复切换或重建后置顶失效。

  测试未运行（暂无自动化测试）。

  你可以这样验证：

  1. 启动后托盘里切换“锁定/解锁”，解锁应可拖动/右键小人。
  2. 锁定后依然保持在所有普通窗口之上。

  如果仍偶发点击不恢复，请告诉我具体触发步骤，我会再加一次强制重建/重置输入的修复。


• 已把“锁定后被遮挡”的问题做了 macOS 专项修复：锁定时切到更高的窗口层级并强制置前，同时
  让窗口跨 Space/全屏时也保持可见。

  关键改动：

  - src/pet_window.py：macOS 下锁定时将窗口 level 提升到 kCGStatusWindowLevelKey，解锁
    时回到 kCGFloatingWindowLevelKey。
  - src/pet_window.py：设置 NSWindowCollectionBehavior（All Spaces +
    FullScreenAuxiliary + Stationary）确保跨桌面/全屏不丢层级。
  - src/pet_window.py：调用 orderFrontRegardless 强制前置，避免锁定后被普通窗口遮挡。

  测试未运行（暂无自动化测试）。

  请你验证：

  - 锁定后小人是否始终在最上层（包括切到其他窗口/全屏应用）。
  - 解锁后点击/拖拽是否正常。

  如果你觉得“状态层级过高”影响其他 UI，我可以加一个 config.json 选项（如
  macos_topmost_level: "floating" | "status"）让你自由切换。

  顺带提醒：日志里仍提示 This process is not trusted...，说明“辅助功能”权限还未授权（除
  了“输入监控”外，还需要在“系统设置 > 隐私与安全性 > 辅助功能”里允许该 Python 进程），
  否则全局输入统计会失效。

  已修复“锁定后仍会被遮挡”的问题：在 macOS 锁定状态下会周期性重申窗口置顶，并禁止因失去
  激活而被系统降级层级。新增一个可配置的刷新间隔开关，必要时可调小/关闭。

  变更说明：

  - src/pet_window.py 增加了 macOS 置顶刷新计时器，锁定时按配置间隔重复应用置顶/前置，
    避免点击其他窗口后被遮挡。
  - src/pet_window.py 增加 setHidesOnDeactivate(False)，防止应用失去激活时窗口被系统压
    到后面。
  - src/app_config.py / config.json 新增 macos_topmost_refresh_ms 配置项。

  配置开关：

  - config.json → macos_topmost_refresh_ms（毫秒）。
      - 1000：每秒重申置顶（推荐）。
      - 0：关闭定时重申（若你不需要，可关掉）。

  建议你先这样验证：

  1. 运行 python main.py。
  2. 托盘里锁定后，切换/点击其它窗口，确认小人仍在最上层。
  3. 如仍偶发被遮挡，把 macos_topmost_refresh_ms 调小（如 300）。

  如果你希望我把“锁定时置顶刷新间隔”做成托盘菜单项，也可以继续加。
  