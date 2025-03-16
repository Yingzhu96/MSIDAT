# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui\\gui.py'],
    pathex=[],
    binaries=[],
    datas=[('database', 'database'), ('log', 'log')],
    hiddenimports=['pandas', 'numpy', 'PyQt5', 'loguru', 'msidat', 'msidat.match.compound_match', 'msidat.molar_mass.cal_molar_mass', 'msidat.annotator.make_annotator', 'openpyxl'],
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
    name='MSI Data Analysis Tool',
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
)
