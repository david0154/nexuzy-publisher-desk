# -*- mode: python ; coding: utf-8 -*-
"""
Nexuzy Publisher Desk - PyInstaller Spec
Includes ALL AI models with auto-detection

MODELS INCLUDED:
✅ Mistral 7B GGUF (4.4GB) - Article writing
✅ NLLB-200 (600MB) - Translation
✅ all-MiniLM-L6-v2 (90MB) - News matching  
✅ flan-t5-base (Optional) - Sentence improvement

Build command:
    pyinstaller nexuzy.spec

Output:
    dist/Nexuzy Publisher Desk.exe (~5.5-6GB with all models)
"""

import os
import sys
from pathlib import Path
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
    
    # AI/ML - Translation (PyTorch/Transformers)
    'torch',
    'transformers',
    'sentencepiece',
    'sacremoses',
    'tokenizers',
    'huggingface_hub',
    'sentence_transformers',
    
    # AI/ML - Article Writing (llama-cpp)
    'ctransformers',
    'ctransformers.llm',
    
    # Translation model specific (NLLB-200)
    'transformers.models.nllb',
    'transformers.models.nllb.modeling_nllb',
    'transformers.models.nllb.tokenization_nllb',
    'transformers.models.nllb.configuration_nllb',
    'transformers.models.nllb_moe',
    'transformers.modeling_utils',
    'transformers.generation',
    'transformers.generation.utils',
    'transformers.generation.stopping_criteria',
    
    # Sentence transformers models
    'sentence_transformers.models',
    'sentence_transformers.models.Transformer',
    'sentence_transformers.models.Pooling',
    
    # T5 models (flan-t5-base)
    'transformers.models.t5',
    'transformers.models.t5.modeling_t5',
    'transformers.models.t5.tokenization_t5',
    'transformers.models.t5.configuration_t5',
    
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
    
    # OpenCV (for VisionAI)
    'cv2',
    'numpy',
]

# Collect all data files
datas = []

print("\n" + "="*80)
print("📦 COLLECTING DEPENDENCIES")
print("="*80)

# Add transformers data
try:
    print("⏳ Collecting transformers...")
    datas += collect_data_files('transformers', include_py_files=True)
    print("✅ Transformers collected")
except Exception as e:
    print(f"⚠️  Transformers: {e}")

# Add sentencepiece data
try:
    print("⏳ Collecting sentencepiece...")
    datas += collect_data_files('sentencepiece')
    print("✅ Sentencepiece collected")
except Exception as e:
    print(f"⚠️  Sentencepiece: {e}")

# Add tokenizers data
try:
    print("⏳ Collecting tokenizers...")
    datas += collect_data_files('tokenizers')
    print("✅ Tokenizers collected")
except Exception as e:
    print(f"⚠️  Tokenizers: {e}")

# Add sentence_transformers data
try:
    print("⏳ Collecting sentence_transformers...")
    datas += collect_data_files('sentence_transformers')
    print("✅ Sentence_transformers collected")
except Exception as e:
    print(f"⚠️  Sentence_transformers: {e}")

# Add ctransformers data
try:
    print("⏳ Collecting ctransformers...")
    datas += collect_data_files('ctransformers')
    print("✅ Ctransformers collected")
except Exception as e:
    print(f"⚠️  Ctransformers: {e}")

# Add local resources
datas += [
    ('resources', 'resources'),  # UI icons, images
]

# Try to add config.json if exists
if Path('config.json').exists():
    datas.append(('config.json', '.'))
    print("✅ Config.json included")

print("\n" + "="*80)
print("📦 ADDING AI MODELS TO BUILD")
print("="*80 + "\n")

total_size_gb = 0

# ===== MODEL 1: Mistral 7B GGUF (Article Writer) =====
print("🔍 Searching for Mistral 7B GGUF model...")
mistral_search_paths = [
    Path('models/mistral-7b-instruct-v0.2.Q4_K_M.gguf'),
    Path('models/mistral-7b-instruct-v0.2.Q3_K_M.gguf'),
    Path('models/tinyllama-1.1b-chat-v1.0.Q8_0.gguf'),
]

mistral_found = False
for model_path in mistral_search_paths:
    if model_path.exists():
        file_size_gb = model_path.stat().st_size / (1024**3)
        datas.append((str(model_path), 'models'))
        print(f"✅ Mistral GGUF: {model_path.name} ({file_size_gb:.2f} GB)")
        total_size_gb += file_size_gb
        mistral_found = True
        break

if not mistral_found:
    print("⚠️  Mistral GGUF model not found in models/ folder")
    print("   Download from: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF")
    print("   Place in: models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    print("   Model will download on first run if missing")

print()

# ===== MODEL 2: NLLB-200 Translation Model =====
print("🔍 Searching for NLLB-200 translation model...")
nllb_cache_paths = [
    Path.home() / '.cache' / 'huggingface' / 'hub' / 'models--facebook--nllb-200-distilled-600M',
    Path.home() / '.cache' / 'huggingface' / 'transformers' / 'models--facebook--nllb-200-distilled-600M',
]

nllb_found = False
for cache_path in nllb_cache_paths:
    if cache_path.exists():
        datas.append((str(cache_path), 'models/nllb-200-distilled-600M'))
        print(f"✅ NLLB-200: Translation model (~600 MB)")
        total_size_gb += 0.6
        nllb_found = True
        break

if not nllb_found:
    print("⚠️  NLLB-200 model not found in HuggingFace cache")
    print("   Run 'python main.py' once to download it")
    print("   Model will download on first run if missing")

print()

# ===== MODEL 3: Sentence Transformers (News Matching) =====
print("🔍 Searching for sentence-transformers/all-MiniLM-L6-v2...")
st_cache_paths = [
    Path.home() / '.cache' / 'torch' / 'sentence_transformers' / 'sentence-transformers_all-MiniLM-L6-v2',
    Path.home() / '.cache' / 'huggingface' / 'hub' / 'models--sentence-transformers--all-MiniLM-L6-v2',
]

st_found = False
for cache_path in st_cache_paths:
    if cache_path.exists():
        datas.append((str(cache_path), 'models/sentence-transformers_all-MiniLM-L6-v2'))
        print(f"✅ Sentence-Transformers: all-MiniLM-L6-v2 (~90 MB)")
        total_size_gb += 0.09
        st_found = True
        break

if not st_found:
    print("⚠️  sentence-transformers model not found")
    print("   Model will download on first run")

print()

# ===== MODEL 4: Flan-T5-Base (Optional - Sentence Improvement) =====
print("🔍 Searching for google/flan-t5-base (optional)...")
t5_cache_paths = [
    Path.home() / '.cache' / 'huggingface' / 'hub' / 'models--google--flan-t5-base',
]

t5_found = False
for cache_path in t5_cache_paths:
    if cache_path.exists():
        datas.append((str(cache_path), 'models/flan-t5-base'))
        print(f"✅ Flan-T5-Base: Sentence improvement (~1 GB)")
        total_size_gb += 1.0
        t5_found = True
        break

if not t5_found:
    print("⚠️  flan-t5-base model not found (optional)")
    print("   App will work without it")

print("\n" + "="*80)
print("✅ MODEL COLLECTION COMPLETE")
print("="*80)
print(f"\nTotal models size: {total_size_gb:.2f} GB")
print(f"\nExpected build size breakdown:")
print(f"  📦 AI Models:          ~{total_size_gb:.1f} GB")
print(f"  📦 PyTorch/Deps:       ~0.3 GB")
print(f"  📦 Other Libraries:    ~0.2 GB")
print(f"  " + "─"*40)
print(f"  📦 TOTAL:              ~{total_size_gb + 0.5:.1f} GB")
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
        'matplotlib.pyplot',
        'numpy.testing',
        'scipy',
        'pandas',
        'IPython',
        'notebook',
        'jupyter',
        'pytest',
        'setuptools',
        'distutils',
        'test',
        'tests',
        'testing',
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
print("✅ BUILD CONFIGURATION READY")
print("="*80)
print("\nNext steps:")
print("  1. Ensure all models are downloaded (run: python main.py)")
print("  2. Start build with: pyinstaller nexuzy.spec")
print("  3. Build will take 10-20 minutes (copying models)")
print("  4. Output: dist/Nexuzy Publisher Desk/")
print("="*80 + "\n")
