# -*- mode: python ; coding: utf-8 -*-
"""
Nexuzy Publisher Desk - PyInstaller Spec
Includes ALL AI models and dependencies

Build command:
    pyinstaller nexuzy.spec

Output:
    dist/Nexuzy Publisher Desk.exe
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all hidden imports
hiddenimports = [
    # Core dependencies
    'feedparser',
    'requests',
    'beautifulsoup4',
    'bs4',
    'lxml',
    'sqlite3',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    
    # AI/ML models
    'torch',
    'transformers',
    'sentencepiece',
    'sacremoses',
    'tokenizers',
    'huggingface_hub',
    'sentence_transformers',
    
    # Translation model specific
    'transformers.models.nllb',
    'transformers.models.nllb.modeling_nllb',
    'transformers.models.nllb.tokenization_nllb',
    'transformers.models.nllb.configuration_nllb',
    'transformers.modeling_utils',
    'transformers.generation',
    'transformers.generation.utils',
    
    # Utilities
    'dateutil',
    'dateutil.parser',
    'urllib',
    'urllib.parse',
    'json',
    'logging',
    'hashlib',
    're',
    'pathlib',
    'threading',
    'queue',
    'datetime',
    'time',
    'os',
    'sys',
    'webbrowser',
    
    # WordPress API
    'base64',
    'mimetypes',
]

# Collect all transformers and torch data files
datas = []

# Add transformers data
try:
    datas += collect_data_files('transformers', include_py_files=True)
except:
    pass

# Add sentencepiece data
try:
    datas += collect_data_files('sentencepiece')
except:
    pass

# Add tokenizers data
try:
    datas += collect_data_files('tokenizers')
except:
    pass

# Add sentence_transformers data
try:
    datas += collect_data_files('sentence_transformers')
except:
    pass

# Add local resources
datas += [
    ('resources', 'resources'),  # UI icons, images
    ('config.json', '.'),  # Config file (if exists)
]

# Add AI models from cache directory
model_paths = [
    # NLLB-200 translation model
    (os.path.expanduser('~/.cache/huggingface/hub/models--facebook--nllb-200-distilled-600M'), 
     'models/nllb-200-distilled-600M'),
    
    # Sentence transformers (if used)
    (os.path.expanduser('~/.cache/torch/sentence_transformers'),
     'models/sentence_transformers'),
]

for src, dst in model_paths:
    if os.path.exists(src):
        datas.append((src, dst))
        print(f"✅ Including model: {dst}")
    else:
        print(f"⚠️ Model not found (will download on first run): {dst}")

# Analysis
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
        # Exclude unnecessary packages to reduce size
        'matplotlib',
        'numpy.testing',
        'scipy',
        'pandas',
        'IPython',
        'notebook',
        'jupyter',
        'pytest',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Nexuzy Publisher Desk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window (GUI app)
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
    name='Nexuzy Publisher Desk',
)
