# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Nexuzy Publisher Desk
Build with: pyinstaller build_config.spec
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('models', 'models'),
    ],
    hiddenimports=[
        'tkinter',
        'sqlite3',
        'feedparser',
        'requests',
        'bs4',
        'lxml',
        'PIL',
        'torch',
        'transformers',
        'sentence_transformers',
        'numpy',
        'scipy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
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
    name='NexuzyPublisherDesk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/logo.ico',
)
