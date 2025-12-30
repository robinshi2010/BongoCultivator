# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('src/data', 'src/data')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BongoCultivation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
# icon=['assets/icon.icns'],
)
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='BongoCultivation',
# )
# app = BUNDLE(
#     coll,
#     name='BongoCultivation.app',
#     icon='assets/icon.icns',
#     bundle_identifier='com.robin.bongo',
#     info_plist={
#         'NSHighResolutionCapable': 'True',
#         'NSAppleEventsUsageDescription': '需要控制事件以模拟操作。',
#         'NSAccessibilityUsageDescription': '需要辅助功能权限以监控键盘鼠标活动。',
#         'NSInputMonitoringUsageDescription': '需要输入监听权限以检测忙碌状态。'
#     },
# )
