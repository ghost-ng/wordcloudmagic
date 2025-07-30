# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for WordCloud Magic

import sys
from pathlib import Path

block_cipher = None

# Get the directory where the spec file is located
spec_dir = Path(SPECPATH)

a = Analysis(
    ['wordcloud_app.py'],
    pathex=[str(spec_dir)],
    binaries=[],
    datas=[
        # Include configuration files
        ('configs', 'configs'),
        # Include help/template files
        ('templates', 'templates'),
        # Include the icon
        ('icons/icon_256.ico', '.'),
        # Include default config if it exists
        ('configs/default.json', 'configs'),
        ('icons', 'icons'),
        ('icon.png','.')
    ],
    hiddenimports=[
        'ttkbootstrap',
        'ttkbootstrap.themes',
        'ttkbootstrap.themes.standard',
        'wordcloud',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'PIL',
        'PIL._tkinter_finder',
        'numpy',
        'PyPDF2',
        'docx',
        'pptx',
        'markdown2',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.font',
        'tkinter.colorchooser',
        'webbrowser',
        'tempfile',
        'threading',
        'json',
        'os',
        'sys',
        'pathlib',
        'datetime',
        'argparse',
        'logging',
        'traceback',
        'collections',
        're',
        'random',
        'colorsys',
        'ctypes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WordCloudMagic',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon_256.ico',  # Use the icon file
    version_file=None,  # You can add version info later if needed
    clean=True,
)

# Optional: Create a directory distribution instead of single file
# Uncomment the following if you prefer a folder distribution
"""
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WordCloudMagic',
)
"""