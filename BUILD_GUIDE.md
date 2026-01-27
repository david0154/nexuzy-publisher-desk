# 🚀 BUILD GUIDE - Windows Installer

Complete guide to building standalone Windows executable for Nexuzy Publisher Desk.

---

## 📋 PREREQUISITES

### 1. **Python Environment**
```bash
# Python 3.10 or 3.11 (recommended)
python --version

# Install all dependencies
pip install -r requirements.txt

# Install PyInstaller
pip install pyinstaller
```

### 2. **AI Model** (Required)

**Download Mistral 7B (4.37 GB):**
```bash
# Option 1: Let build script download automatically
python build_installer.py
# Select option 1 when prompted

# Option 2: Manual download
# URL: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
# Save to: models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### 3. **Inno Setup** (Optional - for installer)

**Download:** https://jrsoftware.org/isdl.php

**Install to:** `C:\Program Files (x86)\Inno Setup 6\`

---

## 🔨 BUILD PROCESS

### **Automated Build (Recommended)**

```bash
# Run automated build script
python build_installer.py
```

**What it does:**
1. ✅ Checks requirements
2. ✅ Downloads AI model (if missing)
3. ✅ Cleans previous builds
4. ✅ Creates PyInstaller configuration
5. ✅ Builds standalone executable
6. ✅ Tests the build
7. ✅ Creates installer script
8. ✅ (Optional) Compiles installer

**Build time:** 10-20 minutes (first time)

---

### **Manual Build**

```bash
# 1. Clean previous builds
rmdir /s /q build dist

# 2. Create spec file (already provided)
# Edit nexuzy_installer.spec if needed

# 3. Build with PyInstaller
pyinstaller --clean --noconfirm nexuzy_installer.spec

# 4. Test executable
cd dist
NexuzyPublisherDesk.exe
```

---

## 📦 OUTPUT FILES

### **After Build:**

```
project/
├── dist/
│   └── NexuzyPublisherDesk.exe  ← Standalone executable (200-300 MB)
│
├── build/  ← Build artifacts (can delete)
│
├── nexuzy_installer.spec  ← PyInstaller config
└── nexuzy_installer.iss    ← Inno Setup script
```

### **Executable Details:**

| Property | Value |
|----------|-------|
| **Size** | ~250 MB (without model) |
| **Size with Model** | ~4.6 GB (includes AI model) |
| **Type** | Windows GUI application |
| **Dependencies** | All bundled (no Python needed!) |
| **Console** | Hidden (GUI only) |

---

## 🎁 CREATE INSTALLER

### **Option 1: Inno Setup (Recommended)**

```bash
# If Inno Setup is installed:
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" nexuzy_installer.iss

# Output:
installer/NexuzyPublisherDesk_v2.0.0_Setup.exe
```

**Installer features:**
- ✅ Professional Windows installer
- ✅ Start menu shortcuts
- ✅ Desktop icon (optional)
- ✅ Uninstaller
- ✅ Admin privileges handling
- ✅ Compressed (~4 GB → ~3 GB)

### **Option 2: ZIP Archive (Portable)**

```bash
# Create portable ZIP
powershell Compress-Archive -Path dist\* -DestinationPath NexuzyPublisherDesk_Portable.zip
```

**Portable features:**
- ✅ No installation needed
- ✅ Extract and run
- ✅ Smaller download
- ❌ No shortcuts/uninstaller

---

## 🧪 TESTING

### **Test Checklist:**

```bash
# 1. Run executable
cd dist
NexuzyPublisherDesk.exe

# 2. Check features:
✅ App launches without errors
✅ Database initializes
✅ RSS feeds can be added
✅ News articles fetch correctly
✅ AI draft generation works
✅ WYSIWYG editor opens
✅ WordPress integration works
✅ Vision AI watermark detection works

# 3. Check on clean PC (recommended):
- Windows 10/11 without Python
- Fresh user account
- No development tools
```

---

## 📤 DISTRIBUTION

### **GitHub Releases (Recommended)**

```bash
# 1. Create release on GitHub
# 2. Upload files:
   - NexuzyPublisherDesk_v2.0.0_Setup.exe (installer)
   - NexuzyPublisherDesk_Portable.zip (portable)
   - README.md
   - LICENSE

# 3. Write release notes
```

### **File Sizes:**

| File | Size | Download Time (10 Mbps) |
|------|------|------------------------|
| **Installer (with model)** | ~3-4 GB | ~45-60 min |
| **Portable (with model)** | ~4.5 GB | ~60-90 min |
| **Installer (no model)** | ~200 MB | ~3 min |
| **Portable (no model)** | ~250 MB | ~3-4 min |

**Recommendation:** Distribute WITHOUT model, let users download separately.

---

## ⚠️ COMMON ISSUES

### **Issue: "UPX is not available"**

```bash
# Solution: Disable UPX in spec file
# Edit nexuzy_installer.spec:
upx=False,  # Change from True to False
```

### **Issue: "Module not found" errors**

```bash
# Solution: Add to hiddenimports in spec file
hiddenimports=[
    'missing_module',
    # ...
]
```

### **Issue: Executable is too large**

```bash
# Solutions:
1. Don't bundle the model (users download separately)
2. Use --onefile mode (slower startup)
3. Exclude unnecessary packages:

excludes=[
    'matplotlib',
    'pandas',
    'jupyter',
]
```

### **Issue: Slow startup**

```bash
# This is normal on first run!
# PyInstaller extracts files to temp directory

# To improve:
1. Use --onedir mode (current default)
2. Add splash screen (optional)
3. Preload model cache
```

---

## 🔧 CUSTOMIZATION

### **Change App Icon:**

```bash
# 1. Replace resources/logo.ico
# 2. Rebuild
```

### **Change App Name:**

```bash
# Edit build_installer.py:
APP_NAME = "Your App Name"
APP_VERSION = "1.0.0"
```

### **Bundle Different Model:**

```bash
# Edit build_installer.py:
RECOMMENDED_MODEL = "your-model.gguf"
MODEL_URL = "https://..."
```

---
## 📊 BUILD OPTIMIZATION

### **Reduce Size:**

```python
# In spec file, add:
excludes=[
    'matplotlib',
    'pandas', 
    'jupyter',
    'notebook',
    'IPython',
    'pytest',
]
```

### **Faster Build:**

```bash
# Skip UPX compression (faster but larger)
upx=False

# Use existing build (when testing)
pyinstaller nexuzy_installer.spec
# (without --clean flag)
```

---

## ✅ FINAL CHECKLIST

Before distribution:

- [ ] All dependencies installed
- [ ] AI model downloaded (or excluded)
- [ ] Build completes without errors
- [ ] Executable tested on clean PC
- [ ] Installer tested (if using Inno Setup)
- [ ] Antivirus scan completed
- [ ] README.md updated
- [ ] Version number updated
- [ ] Release notes written
- [ ] GitHub release created

---

## 🆘 SUPPORT

**Issues?**

1. Check error messages in build log
2. Verify all dependencies are installed
3. Test on clean Python environment
4. Check PyInstaller docs: https://pyinstaller.org/
5. Open issue on GitHub

---

## 📝 LICENSE

MIT License - See LICENSE file for details

---

**Happy Building! 🚀**
