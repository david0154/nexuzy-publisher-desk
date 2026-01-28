#!/usr/bin/env python3
"""
Nexuzy Publisher Desk - Windows Installer Builder
Builds standalone Windows executable with bundled AI model

Usage:
    python build_installer.py

Requirements:
    - PyInstaller
    - All dependencies from requirements.txt
    - GGUF model in models/ directory
    - (Optional) Inno Setup for installer creation
"""

import os
import sys
import shutil
import subprocess
import urllib.request
from pathlib import Path
import zipfile

print("""
╔═══════════════════════════════════════════════════════════╗
║  Nexuzy Publisher Desk - Windows Installer Builder       ║
║  Building standalone executable with AI model...          ║
╚═══════════════════════════════════════════════════════════╝
""")

# Configuration
APP_NAME = "Nexuzy Publisher Desk"
APP_VERSION = "2.0.0"
MAIN_SCRIPT = "main.py"
ICON_FILE = "resources/logo.ico"
MODEL_DIR = Path("models")
RECOMMENDED_MODEL = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MODEL_URL = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MODEL_SIZE_GB = 4.37

def check_requirements():
    """Check if all requirements are installed"""
    print("\n[1/8] Checking requirements...")
    
    try:
        import PyInstaller
        print("  ✅ PyInstaller installed")
    except ImportError:
        print("  ❌ PyInstaller not found!")
        print("     Install: pip install pyinstaller")
        return False
    
    if not Path(MAIN_SCRIPT).exists():
        print(f"  ❌ {MAIN_SCRIPT} not found!")
        return False
    print(f"  ✅ {MAIN_SCRIPT} found")
    
    # Check for icon
    if not Path(ICON_FILE).exists():
        print(f"  ⚠️  Icon file {ICON_FILE} not found (will use default)")
    else:
        print(f"  ✅ Icon file found")
    
    return True

def check_model():
    """Check if AI model exists, offer to download if missing"""
    print("\n[2/8] Checking AI model...")
    
    MODEL_DIR.mkdir(exist_ok=True)
    
    model_path = MODEL_DIR / RECOMMENDED_MODEL
    
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ Model found: {RECOMMENDED_MODEL} ({size_mb:.1f} MB)")
        return True
    
    print(f"  ⚠️  Model not found: {RECOMMENDED_MODEL}")
    print(f"     Size: {MODEL_SIZE_GB} GB")
    print(f"     URL: {MODEL_URL}")
    print("\n  Options:")
    print("    1. Download now (automatic)")
    print("    2. Download manually and place in models/")
    print("    3. Continue without model (app will require manual setup)")
    
    choice = input("\n  Choose (1/2/3): ").strip()
    
    if choice == "1":
        return download_model(MODEL_URL, model_path)
    elif choice == "2":
        print("\n  📥 Manual download:")
        print(f"     1. Download: {MODEL_URL}")
        print(f"     2. Save to: {model_path}")
        print("     3. Re-run this script")
        sys.exit(0)
    elif choice == "3":
        print("  ⚠️  Building without model - users will need to download separately")
        return True
    else:
        print("  ❌ Invalid choice")
        return False

def download_model(url, destination):
    """Download AI model with progress bar"""
    print(f"\n  📥 Downloading model: {MODEL_SIZE_GB} GB")
    print("     This may take 10-30 minutes depending on your internet speed...")
    print("     You can cancel (Ctrl+C) and download manually instead.\n")
    
    try:
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            bar_length = 40
            filled = int(bar_length * percent / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r     [{bar}] {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end='', flush=True)
        
        urllib.request.urlretrieve(url, destination, progress_hook)
        print("\n  ✅ Model downloaded successfully!")
        return True
    
    except KeyboardInterrupt:
        print("\n\n  ⚠️  Download cancelled")
        if destination.exists():
            destination.unlink()
        return False
    except Exception as e:
        print(f"\n  ❌ Download failed: {e}")
        print("\n  📥 Please download manually:")
        print(f"     URL: {url}")
        print(f"     Save to: {destination}")
        return False

def clean_build():
    """Clean previous build artifacts"""
    print("\n[3/8] Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec~', '*.pyc']
    
    for d in dirs_to_clean:
        if Path(d).exists():
            shutil.rmtree(d)
            print(f"  🗑️  Removed {d}/")
    
    print("  ✅ Clean completed")

def create_spec_file():
    """Create PyInstaller spec file with all configurations - FIXED FOR LARGE MODELS"""
    print("\n[4/8] Creating PyInstaller configuration...")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Configuration for {APP_NAME}
Auto-generated - FIXED: Using onedir mode to avoid struct.error with large GGUF models
"""

import sys
from pathlib import Path

block_cipher = None

# Collect all data files
datas = []

# Resources (icons, images)
if Path('resources').exists():
    datas.append(('resources', 'resources'))

# AI Models (if available)
if Path('models').exists():
    datas.append(('models', 'models'))

# Core modules
if Path('core').exists():
    datas.append(('core', 'core'))

a = Analysis(
    ['{MAIN_SCRIPT}'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # GUI
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.filedialog',
        
        # Database
        'sqlite3',
        
        # Web & RSS
        'feedparser',
        'requests',
        'requests_toolbelt',
        'urllib3',
        'bs4',
        'lxml',
        'lxml.etree',
        'lxml._elementpath',
        
        # AI/ML
        'torch',
        'torch.nn',
        'torch.utils',
        'transformers',
        'transformers.models',
        'transformers.models.auto',
        'sentence_transformers',
        'sentence_transformers.models',
        'sentence_transformers.util',
        'ctransformers',
        'huggingface_hub',
        'huggingface_hub.file_download',
        'safetensors',
        'safetensors.torch',
        'tokenizers',
        
        # Image Processing
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'PIL.ImageFilter',
        'cv2',
        
        # Data Science
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
        'scipy',
        'scipy.spatial',
        'scipy.spatial.distance',
        'sklearn',
        'sklearn.metrics',
        'sklearn.metrics.pairwise',
        
        # Utilities
        'dateutil',
        'dateutil.parser',
        'colorama',
        'dotenv',
        'sentencepiece',
        'sacremoses',
        'protobuf',
        'logging',
        'logging.handlers',
        'threading',
        'queue',
        
        # WordPress API
        'wptools',
        
        # Core modules
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
    hooksconfig={{}},
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
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# CRITICAL FIX: Use onedir mode instead of onefile to avoid struct.error with large models
# This creates a directory with the executable and all dependencies separate
exe = EXE(
    pyz,
    a.scripts,
    [],  # Empty - don't bundle binaries in EXE
    exclude_binaries=True,  # CRITICAL: Keep binaries separate from executable
    name='{APP_NAME.replace(" ", "")}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    icon="{ICON_FILE}" if Path("{ICON_FILE}").exists() else None,
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
    name='{APP_NAME.replace(" ", "")}',
)
'''
    
    spec_file = Path("nexuzy_installer.spec")
    spec_file.write_text(spec_content)
    print(f"  ✅ Created {spec_file} (ONEDIR mode - fixes struct.error)")
    return spec_file

def run_pyinstaller(spec_file):
    """Run PyInstaller to build executable"""
    print("\n[5/8] Building executable with PyInstaller...")
    print("     This may take 5-15 minutes...\n")
    
    try:
        result = subprocess.run(
            ['pyinstaller', '--clean', '--noconfirm', str(spec_file)],
            check=True,
            capture_output=False
        )
        print("\n  ✅ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n  ❌ Build failed: {e}")
        return False
    except FileNotFoundError:
        print("\n  ❌ PyInstaller not found!")
        print("     Install: pip install pyinstaller")
        return False

def test_executable():
    """Test if the built executable exists and is valid"""
    print("\n[6/8] Testing executable...")
    
    exe_name = APP_NAME.replace(" ", "") + ".exe"
    # UPDATED: Check in directory instead of root dist folder
    exe_dir = Path("dist") / APP_NAME.replace(" ", "")
    exe_path = exe_dir / exe_name
    
    if not exe_path.exists():
        print(f"  ❌ Executable not found: {exe_path}")
        return False
    
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"  ✅ Executable created: {exe_path}")
    print(f"     Size: {size_mb:.1f} MB")
    print(f"     Directory structure: dist/{APP_NAME.replace(' ', '')}/")
    
    return True

def create_installer_script():
    """Create Inno Setup script for Windows installer - UPDATED FOR ONEDIR"""
    print("\n[7/8] Creating installer script...")
    
    app_dir_name = APP_NAME.replace(" ", "")
    
    iss_content = f'''; Inno Setup Script for {APP_NAME}
; Generated automatically - UPDATED FOR ONEDIR BUILD

#define MyAppName "{APP_NAME}"
#define MyAppVersion "{APP_VERSION}"
#define MyAppPublisher "Nexuzy"
#define MyAppURL "https://github.com/david0154/nexuzy-publisher-desk"
#define MyAppExeName "{APP_NAME.replace(" ", "")}.exe"
#define MyAppDirName "{app_dir_name}"

[Setup]
AppId={{{{B7E9D8C4-5A3F-4B2E-8F1D-9C6E7A4B5D3C}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer
OutputBaseFilename=NexuzyPublisherDesk_v{APP_VERSION}_Setup
SetupIconFile=resources\\logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"

[Files]
; UPDATED: Install entire directory structure from onedir build
Source: "dist\\{{#MyAppDirName}}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{group}}\\{{cm:UninstallProgram,{{#MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent
'''
    
    iss_file = Path("nexuzy_installer.iss")
    iss_file.write_text(iss_content)
    print(f"  ✅ Created {iss_file}")
    
    # Check if Inno Setup is installed
    inno_setup_path = Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe")
    
    if inno_setup_path.exists():
        print("  ℹ️  Inno Setup detected")
        choice = input("     Build installer now? (y/n): ").strip().lower()
        
        if choice == 'y':
            try:
                print("\n  🔨 Building installer...")
                subprocess.run([str(inno_setup_path), str(iss_file)], check=True)
                print("  ✅ Installer created in installer/ directory")
            except subprocess.CalledProcessError:
                print("  ❌ Installer build failed")
    else:
        print("  ℹ️  Inno Setup not found (optional)")
        print("     Download: https://jrsoftware.org/isdl.php")
        print(f"     Then compile: {iss_file}")
    
    return True

def print_summary():
    """Print build summary"""
    print("\n[8/8] Build Summary")
    print("═" * 60)
    
    exe_name = APP_NAME.replace(" ", "") + ".exe"
    app_dir_name = APP_NAME.replace(" ", "")
    exe_dir = Path("dist") / app_dir_name
    exe_path = exe_dir / exe_name
    
    if exe_path.exists():
        print("\n✅ BUILD SUCCESSFUL!\n")
        print(f"📦 Output Directory: {exe_dir}")
        print(f"📦 Executable: {exe_path}")
        
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"📊 Executable Size: {size_mb:.1f} MB")
        
        # Calculate total directory size
        total_size = sum(f.stat().st_size for f in exe_dir.rglob('*') if f.is_file())
        total_size_mb = total_size / (1024 * 1024)
        print(f"📊 Total Directory Size: {total_size_mb:.1f} MB")
        
        # Check if model is included
        model_path = MODEL_DIR / RECOMMENDED_MODEL
        if model_path.exists():
            print(f"\n🤖 AI Model: Bundled")
            model_size = model_path.stat().st_size / (1024 * 1024 * 1024)
            print(f"   Size: {model_size:.2f} GB")
        else:
            print(f"\n⚠️  AI Model: NOT included")
            print(f"   Users will need to download separately")
        
        print("\n⚠️  IMPORTANT: DIRECTORY BUILD")
        print(f"   The ENTIRE {exe_dir} directory must be distributed together.")
        print(f"   Users run: {exe_name} from that directory.")
        print(f"   This avoids the struct.error with large AI models.")
        
        print("\n📋 Next Steps:")
        print(f"   1. Test the executable: {exe_path}")
        print(f"   2. Create installer: nexuzy_installer.iss (packages the directory)")
        print(f"   3. OR zip the entire dist/{app_dir_name}/ folder for distribution")
        
        print("\n💡 Distribution Options:")
        print("   • ZIP the dist/{app_dir_name}/ directory (portable)")
        print("   • Inno Setup installer (recommended - auto-installs directory)")
        print("   • GitHub Releases")
        
    else:
        print("\n❌ BUILD FAILED")
        print("\nCheck the error messages above for details.")
    
    print("\n" + "═" * 60)

def main():
    """Main build process"""
    try:
        if not check_requirements():
            sys.exit(1)
        
        if not check_model():
            sys.exit(1)
        
        clean_build()
        
        spec_file = create_spec_file()
        
        if not run_pyinstaller(spec_file):
            sys.exit(1)
        
        if not test_executable():
            sys.exit(1)
        
        create_installer_script()
        
        print_summary()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
