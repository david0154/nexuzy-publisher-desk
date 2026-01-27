#!/usr/bin/env python3
"""
Model Preparation Script for PyInstaller Build
Organizes all AI models into correct structure for bundling

Usage:
    python prepare_models.py

This script will:
1. Detect sentence transformer models
2. Copy from HuggingFace cache if needed
3. Organize in models/ directory
4. Verify all required files
"""

import os
import shutil
from pathlib import Path
import json

print("""
╔════════════════════════════════════════════════════════════╗
║  Nexuzy Publisher Desk - Model Preparation                ║
║  Preparing models for PyInstaller build...                 ║
╚════════════════════════════════════════════════════════════╝
""")

# Configuration
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

# Sentence Transformer model name
SENTENCE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SENTENCE_MODEL_NAME = "all-MiniLM-L6-v2"

# Required files for sentence transformers
REQUIRED_FILES = [
    'config.json',
    'pytorch_model.bin',
    'tokenizer.json',
    'tokenizer_config.json',
    'vocab.txt',
    'special_tokens_map.json',
    'modules.json',
    'config_sentence_transformers.json',
]

def find_sentence_transformer_model():
    """Find sentence transformer model in various locations"""
    print("\n[1/5] 🔍 Searching for sentence transformer models...")
    
    search_paths = [
        # Local models directory
        MODELS_DIR / f"models--sentence-transformers--{SENTENCE_MODEL_NAME}",
        MODELS_DIR / f"sentence-transformers_{SENTENCE_MODEL_NAME}",
        MODELS_DIR / SENTENCE_MODEL_NAME,
        
        # HuggingFace cache
        Path.home() / '.cache' / 'huggingface' / 'hub' / f'models--sentence-transformers--{SENTENCE_MODEL_NAME}',
        Path.home() / '.cache' / 'torch' / 'sentence_transformers' / f'sentence-transformers_{SENTENCE_MODEL_NAME}',
    ]
    
    for path in search_paths:
        if path.exists():
            print(f"  ✅ Found: {path}")
            return path
    
    print("  ⚠️  Sentence transformer model not found")
    return None

def find_model_files(model_path):
    """Find actual model files (they might be in snapshots/)"""
    if not model_path.exists():
        return None
    
    # Check if files are in root
    config_file = model_path / 'config.json'
    if config_file.exists():
        return model_path
    
    # Check in snapshots/ (HuggingFace cache structure)
    snapshots_dir = model_path / 'snapshots'
    if snapshots_dir.exists():
        # Get latest snapshot
        snapshots = [d for d in snapshots_dir.iterdir() if d.is_dir()]
        if snapshots:
            latest = max(snapshots, key=lambda x: x.stat().st_mtime)
            print(f"    Using snapshot: {latest.name}")
            return latest
    
    return None

def copy_model_to_models_dir(source_path):
    """Copy model files to models/ directory for PyInstaller"""
    print("\n[2/5] 📂 Organizing model files...")
    
    # Find actual model files
    files_path = find_model_files(source_path)
    if not files_path:
        print("  ❌ Could not find model files")
        return False
    
    # Target directory
    target_dir = MODELS_DIR / f"sentence-transformers_{SENTENCE_MODEL_NAME}"
    
    # Check if already exists and is complete
    if target_dir.exists():
        missing_files = [f for f in REQUIRED_FILES if not (target_dir / f).exists()]
        if not missing_files:
            print(f"  ✅ Model already organized in: {target_dir}")
            return True
        else:
            print(f"  ⚠️  Incomplete model, re-copying...")
            shutil.rmtree(target_dir)
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy all files
    print(f"  📋 Copying from: {files_path}")
    print(f"  📋 To: {target_dir}")
    
    copied_count = 0
    total_size = 0
    
    for item in files_path.iterdir():
        if item.is_file():
            target_file = target_dir / item.name
            shutil.copy2(item, target_file)
            copied_count += 1
            total_size += item.stat().st_size
            print(f"    ✓ {item.name} ({item.stat().st_size / 1024:.1f} KB)")
        elif item.is_dir():
            # Copy subdirectories (like tokenizer files)
            shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)
    
    print(f"\n  ✅ Copied {copied_count} files ({total_size / (1024*1024):.1f} MB)")
    return True

def verify_model_files(model_dir):
    """Verify all required files are present"""
    print("\n[3/5] ✓ Verifying model files...")
    
    missing_files = []
    present_files = []
    
    for filename in REQUIRED_FILES:
        file_path = model_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            present_files.append((filename, size))
            print(f"  ✅ {filename} ({size / 1024:.1f} KB)")
        else:
            missing_files.append(filename)
            print(f"  ⚠️  {filename} - MISSING")
    
    if missing_files:
        print(f"\n  ⚠️  Warning: {len(missing_files)} files missing")
        print("     Model may still work, but some features might be unavailable")
    else:
        print("\n  ✅ All required files present!")
    
    return len(missing_files) == 0

def check_gguf_models():
    """Check for GGUF models (Mistral, etc.)"""
    print("\n[4/5] 🤖 Checking GGUF models (for draft generation)...")
    
    gguf_files = list(MODELS_DIR.glob('*.gguf'))
    
    if gguf_files:
        print(f"  ✅ Found {len(gguf_files)} GGUF model(s):")
        total_size = 0
        for f in gguf_files:
            size = f.stat().st_size
            total_size += size
            print(f"    - {f.name} ({size / (1024**3):.2f} GB)")
        print(f"\n  📊 Total GGUF size: {total_size / (1024**3):.2f} GB")
    else:
        print("  ⚠️  No GGUF models found")
        print("     Download manually:")
        print("     https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF")
        print("     Save to: models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")

def download_sentence_transformer():
    """Download sentence transformer model if missing"""
    print("\n💡 Download sentence transformer model? (y/n): ", end='')
    choice = input().strip().lower()
    
    if choice == 'y':
        print("\n  📥 Downloading all-MiniLM-L6-v2 (~90 MB)...")
        print("     This will take 1-2 minutes...\n")
        
        try:
            from sentence_transformers import SentenceTransformer
            
            # This will download to cache
            model = SentenceTransformer(SENTENCE_MODEL)
            
            # Save to local directory
            target_dir = MODELS_DIR / f"sentence-transformers_{SENTENCE_MODEL_NAME}"
            model.save(str(target_dir))
            
            print("\n  ✅ Model downloaded and saved!")
            return target_dir
        
        except ImportError:
            print("\n  ❌ sentence-transformers not installed!")
            print("     Install: pip install sentence-transformers")
            return None
        except Exception as e:
            print(f"\n  ❌ Download failed: {e}")
            return None
    else:
        print("\n  ⚠️  Skipping download")
        return None

def show_summary():
    """Show summary of all models"""
    print("\n[5/5] 📊 Build Summary")
    print("═" * 60)
    
    # Count files and sizes
    total_size = 0
    total_files = 0
    
    # GGUF models
    gguf_files = list(MODELS_DIR.glob('*.gguf'))
    gguf_size = sum(f.stat().st_size for f in gguf_files)
    
    # Sentence transformer models
    st_dirs = [
        MODELS_DIR / f"sentence-transformers_{SENTENCE_MODEL_NAME}",
        MODELS_DIR / f"models--sentence-transformers--{SENTENCE_MODEL_NAME}",
    ]
    st_size = 0
    for st_dir in st_dirs:
        if st_dir.exists():
            st_size += sum(f.stat().st_size for f in st_dir.rglob('*') if f.is_file())
    
    total_size = gguf_size + st_size
    
    print(f"\n📦 Models ready for PyInstaller:")
    print(f"\n  GGUF Models (Draft Generation):")
    if gguf_files:
        print(f"    ✅ {len(gguf_files)} model(s) - {gguf_size / (1024**3):.2f} GB")
    else:
        print(f"    ⚠️  None (download recommended)")
    
    print(f"\n  Sentence Transformers (Embeddings):")
    if st_size > 0:
        print(f"    ✅ all-MiniLM-L6-v2 - {st_size / (1024**2):.1f} MB")
    else:
        print(f"    ⚠️  None (will be downloaded on first run)")
    
    print(f"\n  Total Size: {total_size / (1024**3):.2f} GB")
    
    print("\n═" * 60)
    print("\n✅ Model preparation complete!")
    print("\nNext steps:")
    print("  1. Run: python build_installer.py")
    print("  2. Or: pyinstaller --clean nexuzy_installer.spec")
    print("\n")

def main():
    try:
        # Step 1: Find sentence transformer model
        model_path = find_sentence_transformer_model()
        
        if model_path:
            # Step 2: Copy to models/ directory
            if copy_model_to_models_dir(model_path):
                # Step 3: Verify files
                target_dir = MODELS_DIR / f"sentence-transformers_{SENTENCE_MODEL_NAME}"
                verify_model_files(target_dir)
        else:
            # Offer to download
            downloaded_path = download_sentence_transformer()
            if downloaded_path:
                verify_model_files(downloaded_path)
        
        # Step 4: Check GGUF models
        check_gguf_models()
        
        # Step 5: Show summary
        show_summary()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
