# -*- mode: python ; coding: utf-8 -*-
"""
Nexuzy Publisher Desk - PyInstaller Spec File
Builds standalone Windows executable with bundled AI model

Usage:
    pyinstaller --clean --noconfirm nexuzy_installer.spec

Requirements:
    - All dependencies from requirements.txt
    - GGUF model in models/ directory (optional)
    - Icon file in resources/logo.ico (optional)
"""

import sys
from pathlib import Path

block_cipher = None

# Collect data files
datas = []

# Resources (icons, images, etc.)
if Path('resources').exists():
    datas.append(('resources', 'resources'))
    print("[BUILD] Including resources/")

# AI Models (if available) - OPTIONAL
if Path('models').exists() and any(Path('models').glob('*.gguf')):
    datas.append(('models', 'models'))
    print("[BUILD] Including AI models/")
    
    # Calculate model size
    total_size = sum(f.stat().st_size for f in Path('models').glob('*.gguf'))
    print(f"[BUILD] Model size: {total_size / (1024**3):.2f} GB")
else:
    print("[BUILD] WARNING: No AI models found in models/")
    print("[BUILD] Users will need to download models separately")

# Core modules (if structured as package)
if Path('core').exists():
    datas.append(('core', 'core'))
    print("[BUILD] Including core/")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # ===== GUI =====
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.filedialog',
        
        # ===== DATABASE =====
        'sqlite3',
        
        # ===== WEB & RSS =====
        'feedparser',
        'requests',
        'requests_toolbelt',
        'urllib',
        'urllib.request',
        'urllib.parse',
        'urllib3',
        'bs4',
        'lxml',
        'lxml.etree',
        'lxml._elementpath',
        'html.parser',
        
        # ===== AI/ML CORE =====
        'torch',
        'torch.nn',
        'torch.utils',
        'torch.utils.data',
        'transformers',
        'transformers.models',
        'transformers.models.auto',
        'sentence_transformers',
        'ctransformers',
        'huggingface_hub',
        'huggingface_hub.file_download',
        'safetensors',
        'safetensors.torch',
        'tokenizers',
        
        # ===== IMAGE PROCESSING =====
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'PIL.ImageFilter',
        'PIL.ImageEnhance',
        'PIL.ExifTags',
        'cv2',
        
        # ===== DATA SCIENCE =====
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
        'numpy.random',
        'scipy',
        'scipy.spatial',
        'scipy.spatial.distance',
        
        # ===== UTILITIES =====
        'dateutil',
        'dateutil.parser',
        'colorama',
        'dotenv',
        'sentencepiece',
        'sacremoses',
        'protobuf',
        're',
        'json',
        'logging',
        'logging.handlers',
        'threading',
        'queue',
        'io',
        'base64',
        'hashlib',
        'tempfile',
        'shutil',
        
        # ===== WORDPRESS API =====
        'wptools',
        
        # ===== CORE MODULES (if structured as package) =====
        'core',
        'core.database',
        'core.rss_fetcher',
        'core.ai_draft_generator',
        'core.wordpress_api',
        'core.wordpress_formatter',
        'core.vision_ai',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'matplotlib',
        'matplotlib.pyplot',
        'pandas',
        'jupyter',
        'notebook',
        'IPython',
        'pytest',
        'setuptools',
        'wheel',
        'pip',
        'distutils',
        
        # Exclude unused transformers models
        'transformers.models.bert',
        'transformers.models.gpt2',
        'transformers.models.roberta',
        
        # Exclude unused torch components
        'torch.distributions',
        'torch.autograd',
        'torch.jit',
        
        # Test/dev tools
        'unittest',
        'doctest',
        'pydoc',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NexuzyPublisherDesk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX (disable if UPX not available)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window - GUI only
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/logo.ico' if Path('resources/logo.ico').exists() else None,
)

print("\n" + "="*60)
print("BUILD COMPLETE!")
print("="*60)
print(f"\nExecutable: dist/NexuzyPublisherDesk.exe")
print("\nNext steps:")
print("  1. Test: dist/NexuzyPublisherDesk.exe")
print("  2. Create installer: nexuzy_installer.iss (optional)")
print("  3. Distribute to users")
print("\n" + "="*60 + "\n")
