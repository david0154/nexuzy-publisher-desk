# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for Nexuzy Publisher Desk
Complete AI-Powered News Publishing Platform

Build Instructions:
1. Install PyInstaller: pip install pyinstaller
2. Run: pyinstaller nexuzy_publisher.spec
3. Executable will be in dist/NexuzyPublisher/

For one-file build, change onefile=True below
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all data files for various packages
datas = []

# Add application resources
datas += [('resources', 'resources')]

# Add AI model directories (if they exist)
if os.path.exists('models'):
    datas += [('models', 'models')]

# Collect data files for sentence-transformers
try:
    datas += collect_data_files('sentence_transformers')
except:
    pass

# Collect data files for transformers
try:
    datas += collect_data_files('transformers')
except:
    pass

# Collect data files for torch
try:
    datas += collect_data_files('torch', include_py_files=True)
except:
    pass

# Collect data files for tokenizers
try:
    datas += collect_data_files('tokenizers')
except:
    pass

# Collect data files for huggingface_hub
try:
    datas += collect_data_files('huggingface_hub')
except:
    pass

# Collect data files for feedparser
try:
    datas += collect_data_files('feedparser')
except:
    pass

# Collect data files for bs4
try:
    datas += collect_data_files('bs4')
except:
    pass

# Collect all submodules
hiddenimports = []

# Core modules
hiddenimports += [
    'tkinter',
    'tkinter.ttk',
    'tkinter.scrolledtext',
    'tkinter.font',
    'tkinter.filedialog',
    'tkinter.messagebox',
]

# Database
hiddenimports += [
    'sqlite3',
]

# Web and RSS
hiddenimports += [
    'feedparser',
    'requests',
    'urllib3',
    'bs4',
    'html.parser',
    'html5lib',
]

# AI/ML Libraries
hiddenimports += [
    'torch',
    'transformers',
    'sentence_transformers',
    'PIL',
    'PIL.Image',
    'numpy',
    'scipy',
    'sklearn',
]

# Transformers submodules
try:
    hiddenimports += collect_submodules('transformers')
except:
    pass

# Sentence transformers submodules
try:
    hiddenimports += collect_submodules('sentence_transformers')
except:
    pass

# Torch submodules
try:
    hiddenimports += collect_submodules('torch')
except:
    pass

# Hugging Face Hub
hiddenimports += [
    'huggingface_hub',
    'huggingface_hub.hf_api',
    'huggingface_hub.utils',
]

# Tokenizers
hiddenimports += [
    'tokenizers',
    'tokenizers.implementations',
]

# LLM support (llama-cpp-python)
try:
    hiddenimports += [
        'llama_cpp',
        'ctypes',
    ]
except:
    pass

# Date parsing
hiddenimports += [
    'dateutil',
    'dateutil.parser',
]

# WordPress API
hiddenimports += [
    'base64',
    'json',
]

# Application core modules
hiddenimports += [
    'core.rss_manager',
    'core.news_matcher',
    'core.ai_draft_generator',
    'core.translator',
    'core.vision_ai',
    'core.wordpress_api',
]

try:
    from core import categories
    hiddenimports += ['core.categories']
except:
    pass

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'pytest',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ONE-FOLDER BUILD (Recommended for AI models)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NexuzyPublisher',
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
    icon='resources/icon.ico' if os.path.exists('resources/icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NexuzyPublisher',
)
