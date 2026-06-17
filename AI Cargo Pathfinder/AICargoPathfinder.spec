# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('icon.ico', '.')]
binaries = []
hiddenimports = ['panda3d', 'panda3d.core', 'panda3d.bullet', 'panda3d.direct', 'panda3d.physics', 'panda3d.egg', 'direct', 'direct.showbase', 'direct.showbase.ShowBase', 'direct.task', 'direct.task.Task', 'direct.gui', 'direct.gui.OnscreenText', 'direct.gui.DirectGui', 'direct.directnotify', 'direct.directnotify.DirectNotify', 'direct.interval', 'direct.showbase.Loader', 'direct.showbase.Audio3DManager', 'direct.particles', 'core', 'core.app', 'core.constants', 'core.environment', 'core.hud', 'core.physics', 'core.procedural_geo', 'core.robot', 'core.sensors']
tmp_ret = collect_all('panda3d')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('direct')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['E:\\Sample Projects of client\\Sample Games to attract the client\\Game maded using the Panda3D\\AI Cargo Pathfinder\\main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='AICargoPathfinder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AICargoPathfinder',
)
