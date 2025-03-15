from PyInstaller.building.api import *
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(SPEC))

# 定义数据文件
datas = [
    ('database', 'database'),  # 数据库文件夹
    ('log', 'log'),  # 日志文件夹
]

a = Analysis(
    ['gui/gui.py'],  # 主程序入口
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'pandas',
        'numpy',
        'PyQt5',
        'loguru',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MSI Data Analysis Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 设置为 False 以隐藏控制台窗口
    icon='gui/icon.ico',  # 如果有图标文件的话
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MSI Data Analysis Tool',
) 