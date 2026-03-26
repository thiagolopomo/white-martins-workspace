# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app_version.json', '.'),
        ('logo_wm.png', '.'),
        ('icone.ico', '.'),
    ],
    hiddenimports=[
        'pages.dashboard_page',
        'pages.converter_page',
        'pages.segregar_page',
        'pages.recon_page',
        'pages.overview_page',
        'workers.converter_worker',
        'workers.segregar_worker',
        'workers.recon_worker',
        'workers.overview_worker',
        'logic.converter_logic',
        'logic.segregar_logic',
        'logic.recon_logic',
        'logic.overview_logic',
    ],
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
    name='WhiteMartins',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icone.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WhiteMartins',
)
