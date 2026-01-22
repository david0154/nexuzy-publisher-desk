# Deployment Guide - Building EXE with PyInstaller

## 📦 Overview

This guide covers building a standalone Windows executable for Nexuzy Publisher Desk using PyInstaller and creating an installer with Inno Setup.

---

## 🛠️ Prerequisites

### Software Requirements

- **Python 3.9-3.11** (3.13 not fully supported by llama-cpp-python)
- **Visual Studio Build Tools** (for llama-cpp-python compilation)
- **PyInstaller** (installed via requirements.txt)
- **Inno Setup 6** (for installer creation)

### Install Visual Studio Build Tools

**Required for llama-cpp-python compilation on Windows**

**Option 1: Full Visual Studio (Recommended)**
```
1. Download Visual Studio 2022 Community (free)
   https://visualstudio.microsoft.com/downloads/

2. During installation, select:
   ☑️ "Desktop development with C++"
   ☑️ "Windows 10/11 SDK"

3. Install and restart
```

**Option 2: Build Tools Only (Lighter)**
```
1. Download Build Tools for Visual Studio 2022
   https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022

2. Run installer, select:
   ☑️ "C++ build tools"
   ☑️ "Windows 10/11 SDK"

3. Install (2-4GB download)
```

**Verify Installation:**
```bash
# Should show version info
where cl
```

---

## 🔧 Step 1: Install Dependencies

### 1.1 Create Virtual Environment

```bash
# Clone repository
git clone https://github.com/david0154/nexuzy-publisher-desk.git
cd nexuzy-publisher-desk

# Create venv
python -m venv venv

# Activate
venv\Scripts\activate
```

### 1.2 Install llama-cpp-python (Pre-built Wheel)

**Instead of building from source, use pre-built wheels:**

```bash
# For CPU-only (most users)
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# For NVIDIA GPU (CUDA 12.1)
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121

# For AMD GPU (ROCm)
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/rocm
```

### 1.3 Install Other Dependencies

```bash
# Install remaining packages
pip install transformers>=4.36.0
pip install sentence-transformers>=2.2.2
pip install torch>=2.1.0
pip install huggingface_hub>=0.19.4
pip install feedparser>=6.0.10
pip install requests>=2.31.0
pip install beautifulsoup4>=4.12.2
pip install lxml>=4.9.3
pip install pillow>=10.1.0
pip install pyinstaller>=6.1.0
pip install python-dotenv>=1.0.0
pip install colorama>=0.4.6
```

**Or install from requirements (after llama-cpp-python):**
```bash
pip install -r requirements.txt --no-deps
```

---

## 📜 Step 2: Prepare for Build

### 2.1 Create Resources Directory

```bash
mkdir resources
```

Add these files:
- `resources/logo.ico` - Application icon (256x256 ICO)
- `resources/logo.png` - Splash screen logo

### 2.2 Test Application

```bash
# Run to ensure everything works
python main.py
```

---

## 🏗️ Step 3: Build with PyInstaller

### 3.1 PyInstaller Command

**Basic Build (Console):**
```bash
pyinstaller --name="NexuzyPublisher" \
            --onefile \
            --windowed \
            --icon="resources/logo.ico" \
            --add-data="resources;resources" \
            main.py
```

**Advanced Build (With Hidden Imports):**
```bash
pyinstaller --name="NexuzyPublisher" \
            --onefile \
            --windowed \
            --icon="resources/logo.ico" \
            --add-data="resources;resources" \
            --hidden-import="llama_cpp" \
            --hidden-import="transformers" \
            --hidden-import="sentence_transformers" \
            --hidden-import="torch" \
            --hidden-import="sqlite3" \
            --hidden-import="tkinter" \
            --hidden-import="PIL" \
            --collect-all="llama_cpp" \
            --collect-all="sentence_transformers" \
            main.py
```

### 3.2 PyInstaller Spec File

**Create `nexuzy.spec`:**

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
    ],
    hiddenimports=[
        'llama_cpp',
        'transformers',
        'sentence_transformers',
        'torch',
        'sqlite3',
        'tkinter',
        'PIL',
        'feedparser',
        'requests',
        'beautifulsoup4',
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
    name='NexuzyPublisher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/logo.ico',
)
```

**Build using spec:**
```bash
pyinstaller nexuzy.spec
```

### 3.3 Build Output

```
dist/
└── NexuzyPublisher.exe  (50-150MB)
```

**Test the EXE:**
```bash
cd dist
.\NexuzyPublisher.exe
```

---

## 📦 Step 4: Create Installer with Inno Setup

### 4.1 Install Inno Setup

```
Download: https://jrsoftware.org/isdl.php
Version: Inno Setup 6.3.x or later
```

### 4.2 Create Inno Setup Script

**Create `installer.iss`:**

```iss
; Nexuzy Publisher Desk - Inno Setup Script
; Copyright (c) 2026 David & Nexuzy Tech

#define MyAppName "Nexuzy Publisher Desk"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Nexuzy Tech"
#define MyAppURL "https://github.com/david0154/nexuzy-publisher-desk"
#define MyAppExeName "NexuzyPublisher.exe"
#define MyAppIcon "resources\logo.ico"

[Setup]
; App Information
AppId={{A1B2C3D4-E5F6-7890-ABCD-1234567890AB}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases

; Installation Directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=output
OutputBaseFilename=NexuzyPublisherDesk_v{#MyAppVersion}_Setup

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMADictionarySize=1048576
LZMANumFastBytes=273

; Appearance
SetupIconFile={#MyAppIcon}
WizardStyle=modern
WizardImageFile=installer_banner.bmp
WizardSmallImageFile=installer_small.bmp

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Uninstall
UninstallDisplayIcon={app}\{#MyAppExeName}

; Architecture
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; License
LicenseFile=LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Resources
Source: "resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICK_START.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "WORDPRESS_SETUP.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "AI_MODELS.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop Icon
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Launch after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Custom installation messages
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.Caption := 
    'This will install Nexuzy Publisher Desk on your computer.' + #13#10 + #13#10 +
    'AI-Powered Offline News Publishing Platform' + #13#10 + #13#10 +
    'Features:' + #13#10 +
    '  • RSS Feed Management' + #13#10 +
    '  • AI Draft Generation (Mistral-7B GGUF)' + #13#10 +
    '  • Multi-Language Translation (NLLB-200)' + #13#10 +
    '  • WordPress Integration' + #13#10 + #13#10 +
    'On first run, AI models (~5GB) will download automatically.' + #13#10 + #13#10 +
    'Click Next to continue.';
end;

// Post-installation message
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox(
      'Installation Complete!' + #13#10 + #13#10 +
      'Important Notes:' + #13#10 +
      '1. First run will download AI models (~5GB)' + #13#10 +
      '2. Ensure stable internet connection for first launch' + #13#10 +
      '3. Allow 15-20 minutes for model downloads' + #13#10 + #13#10 +
      'Check README.md for quick start guide.',
      mbInformation, MB_OK
    );
  end;
end;
```

### 4.3 Build Installer

**Compile with Inno Setup:**
```
1. Open Inno Setup Compiler
2. File → Open → Select installer.iss
3. Build → Compile
4. Wait for compilation
```

**Or compile from command line:**
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

**Output:**
```
output/
└── NexuzyPublisherDesk_v1.1.0_Setup.exe  (50-150MB)
```

---

## 📦 Step 5: Distribution Package

### 5.1 Create Release Package

```bash
mkdir release
cd release

# Copy installer
copy ..\output\NexuzyPublisherDesk_v1.1.0_Setup.exe .

# Create portable version (optional)
mkdir NexuzyPublisherDesk_Portable
copy ..\dist\NexuzyPublisher.exe NexuzyPublisherDesk_Portable\
xcopy ..\resources NexuzyPublisherDesk_Portable\resources\ /E /I
copy ..\README.md NexuzyPublisherDesk_Portable\
copy ..\LICENSE NexuzyPublisherDesk_Portable\

# Zip portable version
tar -a -c -f NexuzyPublisherDesk_v1.1.0_Portable.zip NexuzyPublisherDesk_Portable
```

### 5.2 Release Checklist

- [ ] Test installer on clean Windows machine
- [ ] Verify first-run model download
- [ ] Test all features (RSS, Draft, Translate, WordPress)
- [ ] Check uninstaller works correctly
- [ ] Create release notes
- [ ] Upload to GitHub Releases
- [ ] Update download links in README

---

## 🐛 Troubleshooting Build Issues

### Issue 1: llama-cpp-python Build Fails

**Error:** `CMAKE_C_COMPILER not set` or `nmake not found`

**Solution:**
```bash
# Use pre-built wheel instead
pip uninstall llama-cpp-python
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

### Issue 2: PyInstaller Missing Modules

**Error:** `ModuleNotFoundError` when running EXE

**Solution:**
```bash
# Add to spec file hidden imports
hiddenimports=['missing_module_name']

# Or collect entire package
--collect-all=package_name
```

### Issue 3: EXE Too Large

**Solution:**
```bash
# Use UPX compression
pip install pyinstaller[upx]

# Add to spec file
upx=True,
upx_exclude=['vcruntime140.dll'],
```

### Issue 4: Antivirus Flags EXE

**Solution:**
```
1. Code sign the executable
2. Submit to antivirus vendors for whitelisting
3. Add VirusTotal scan results to release notes
```

---

## 📝 Quick Build Script

**Create `build.bat`:**

```batch
@echo off
echo ========================================
echo Nexuzy Publisher Desk - Build Script
echo ========================================
echo.

echo [1/4] Cleaning previous builds...
rmdir /s /q build dist
del /q *.spec

echo [2/4] Building with PyInstaller...
pyinstaller nexuzy.spec

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo [3/4] Compiling installer...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss

if errorlevel 1 (
    echo Installer compilation failed!
    pause
    exit /b 1
)

echo [4/4] Creating release package...
if not exist release mkdir release
copy output\NexuzyPublisherDesk_v1.1.0_Setup.exe release\

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo Installer: release\NexuzyPublisherDesk_v1.1.0_Setup.exe
echo.
pause
```

**Run build:**
```bash
build.bat
```

---

## 📊 Build Size Optimization

### Expected Sizes

| Component | Size |
|-----------|------|
| PyInstaller EXE | 50-150MB |
| Installer (compressed) | 50-100MB |
| After model download | 5-6GB total |

### Optimization Tips

1. **Exclude unnecessary packages:**
   ```python
   excludes=['matplotlib', 'pandas', 'numpy.tests']
   ```

2. **Use UPX compression:**
   ```python
   upx=True
   ```

3. **Strip debug symbols:**
   ```python
   strip=True
   ```

4. **Separate model downloads:**
   - Don't bundle models in EXE
   - Download on first run

---

## 💫 GitHub Release

### Create Release

```bash
# Tag version
git tag -a v1.1.0 -m "Version 1.1.0 - GGUF models"
git push origin v1.1.0

# Create release on GitHub
gh release create v1.1.0 \
  release/NexuzyPublisherDesk_v1.1.0_Setup.exe \
  release/NexuzyPublisherDesk_v1.1.0_Portable.zip \
  --title "Nexuzy Publisher Desk v1.1.0" \
  --notes "See CHANGELOG.md for details"
```

---

**Last Updated:** January 22, 2026

**Author:** David & Nexuzy Tech
