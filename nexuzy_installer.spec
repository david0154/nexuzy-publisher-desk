# -*- mode: python ; coding: utf-8 -*-
"""
Nexuzy Publisher Desk - PyInstaller Spec File
Builds standalone Windows executable with:
- GGUF models (Mistral 7B)
- Sentence Transformer models (all-MiniLM-L6-v2)
- All Python dependencies

Usage:
    pyinstaller --clean --noconfirm nexuzy_installer.spec

FIX: Changed from onefile to onedir mode to avoid struct.error with large models
"""

import sys
from pathlib import Path
import os

block_cipher = None

# Collect data files
datas = []

print("\n" + "="*60)
print("NEXUZY PUBLISHER DESK - BUILD CONFIGURATION")
print("="*60)

# Resources (icons, images, etc.)
if Path('resources').exists():
    datas.append(('resources', 'resources'))
    print("[BUILD] ✅ Including resources/")

# ===== AI MODELS =====

# 1. GGUF Models (Mistral 7B for draft generation)
if Path('models').exists():
    gguf_files = list(Path('models').glob('*.gguf'))
    if gguf_files:
        datas.append(('models', 'models'))
        total_size = sum(f.stat().st_size for f in gguf_files)
        print(f"[BUILD] ✅ Including GGUF models: {len(gguf_files)} files ({total_size / (1024**3):.2f} GB)")
        for f in gguf_files:
            print(f"        - {f.name} ({f.stat().st_size / (1024**3):.2f} GB)")
    else:
        print("[BUILD] ⚠️  No GGUF models found in models/")
else:
    print("[BUILD] ⚠️  models/ directory not found")

# 2. Sentence Transformer Models (for embeddings/similarity)
sentence_transformer_models = [
    'models/models--sentence-transformers--all-MiniLM-L6-v2',
    'models/sentence-transformers_all-MiniLM-L6-v2',
    'models/sentence-transformers',  # Any other sentence transformers
]

for model_path in sentence_transformer_models:
    if Path(model_path).exists():
        # Include the entire model directory
        model_name = Path(model_path).name
        datas.append((model_path, f'models/{model_name}'))
        
        # Calculate size
        total_files = sum(1 for _ in Path(model_path).rglob('*') if _.is_file())
        total_size = sum(f.stat().st_size for f in Path(model_path).rglob('*') if f.is_file())
        
        print(f"[BUILD] ✅ Including Sentence Transformer: {model_name}")
        print(f"        Files: {total_files}, Size: {total_size / (1024**2):.1f} MB")

# 3. Hugging Face Cache (if models are in cache)
cache_paths = [
    Path.home() / '.cache' / 'huggingface' / 'hub' / 'models--sentence-transformers--all-MiniLM-L6-v2',
    Path.home() / '.cache' / 'torch' / 'sentence_transformers',
]

for cache_path in cache_paths:
    if cache_path.exists():
        # Only include if not already in local models/
        if not any(Path(model_path).exists() for model_path in sentence_transformer_models):
            model_name = cache_path.name
            datas.append((str(cache_path), f'models/{model_name}'))
            total_size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
            print(f"[BUILD] ✅ Including from cache: {model_name} ({total_size / (1024**2):.1f} MB)")

# Core modules (if structured as package)
if Path('core').exists():
    datas.append(('core', 'core'))
    print("[BUILD] ✅ Including core/")

print("="*60 + "\n")

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
        
        # ===== SENTENCE TRANSFORMERS (for embeddings) =====
        'sentence_transformers',
        'sentence_transformers.models',
        'sentence_transformers.util',
        'sentence_transformers.SentenceTransformer',
        
        # CTRANSFORMERS (for GGUF models)
        'ctransformers',
        
        # HuggingFace Hub
        'huggingface_hub',
        'huggingface_hub.file_download',
        'huggingface_hub.constants',
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
        'sklearn',
        'sklearn.metrics',
        'sklearn.metrics.pairwise',
        
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
        
        # ===== CORE MODULES =====
        'core',
        'core.database',
        'core.rss_fetcher',
        'core.ai_draft_generator',
        'core.wordpress_api',
        'core.wordpress_formatter',
        'core.vision_ai',
        'core.translator',
        'core.news_matcher',
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

# FIXED: Changed to directory-based build (onedir) to avoid struct.error with large models
# Instead of bundling everything into one executable, we create a directory with:
# - NexuzyPublisherDesk.exe (small launcher)
# - _internal/ directory (contains all dependencies and models)

exe = EXE(
    pyz,
    a.scripts,
    [],  # Empty - don't bundle binaries here
    exclude_binaries=True,  # CRITICAL FIX: Don't bundle in EXE, keep separate
    name='NexuzyPublisherDesk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX (disable if UPX not available)
    console=False,  # No console window - GUI only
    disable_windowed_traceback=False,
    icon='resources/logo.ico' if Path('resources/logo.ico').exists() else None,
)

# COLLECT creates the directory structure
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NexuzyPublisherDesk',
)

print("\n" + "="*60)
print("BUILD SUMMARY")
print("="*60)
print(f"Output: dist/NexuzyPublisherDesk/ (directory)")
print(f"Executable: dist/NexuzyPublisherDesk/NexuzyPublisherDesk.exe")
print(f"Data files included: {len(datas)} directories")
print("\nModels bundled:")
print("  - GGUF models (if in models/)")
print("  - Sentence Transformer models")
print("  - Tokenizers and configs")
print("\nBuild mode: ONEDIR (fixes struct.error with large models)")
print("The entire dist/NexuzyPublisherDesk/ directory must be distributed together.")
print("\nNext steps:")
print("  1. Test: dist/NexuzyPublisherDesk/NexuzyPublisherDesk.exe")
print("  2. Create installer: Use Inno Setup to package the directory")
print("  3. Distribute to users")
print("="*60 + "\n")
