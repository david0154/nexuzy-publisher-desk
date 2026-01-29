# -*- mode: python ; coding: utf-8 -*-
"""
Nexuzy Publisher Desk - PyInstaller Spec
Includes ALL AI models and dependencies

MODELS INCLUDED:
✅ NLLB-200 (600MB) - Translation model
✅ Mistral 7B GGUF (4.4GB) - Article writing model

Build command:
    pyinstaller nexuzy.spec

Output:
    dist/Nexuzy Publisher Desk.exe (~5.5GB with both models)
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
    
    # AI/ML models - Translation
    'torch',
    'transformers',
    'sentencepiece',
    'sacremoses',
    'tokenizers',
    'huggingface_hub',
    'sentence_transformers',
    
    # AI/ML models - Article Writing
    'llama_cpp',
    'llama_cpp.llama_cpp',
    
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

# Add llama-cpp-python data
try:
    datas += collect_data_files('llama_cpp')
except:
    pass

# Add local resources
datas += [
    ('resources', 'resources'),  # UI icons, images
    ('config.json', '.'),  # Config file (if exists)
]

# Add AI models
print("\n" + "="*80)
print("📦 ADDING AI MODELS TO BUILD")
print("="*80)

# 1. Mistral 7B GGUF model (Article Writer)
mistral_model_path = 'models/mistral-7b-instruct-v0.2.Q4_K_M.gguf'
if os.path.exists(mistral_model_path):
    file_size = os.path.getsize(mistral_model_path) / (1024**3)  # Convert to GB
    datas.append((mistral_model_path, 'models'))
    print(f"✅ Mistral 7B GGUF: {file_size:.2f} GB")
else:
    print(f"⚠️  Mistral 7B GGUF not found at: {mistral_model_path}")
    print(f"   Model will need to be downloaded on first run")

# 2. NLLB-200 translation model
nllb_paths = [
    # HuggingFace cache location
    (os.path.expanduser('~/.cache/huggingface/hub/models--facebook--nllb-200-distilled-600M'), 
     'models/nllb-200-distilled-600M'),
]

for src, dst in nllb_paths:
    if os.path.exists(src):
        datas.append((src, dst))
        print(f"✅ NLLB-200 Translation Model: 600 MB")
        break
else:
    print(f"⚠️  NLLB-200 model not found in HuggingFace cache")
    print(f"   Run 'python main.py' once to download it")

print("="*80 + "\n")

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

print("\n" + "="*80)
print("✅ BUILD CONFIGURATION COMPLETE")
print("="*80)
print("\nExpected build size:")
print("  📦 Mistral 7B:        ~4.4 GB")
print("  📦 NLLB-200:          ~0.6 GB")
print("  📦 PyTorch/Deps:      ~0.2 GB")
print("  📦 Other:             ~0.3 GB")
print("  " + "─"*40)
print("  📦 TOTAL:             ~5.5 GB")
print("\nStart build with: pyinstaller nexuzy.spec")
print("="*80 + "\n")
