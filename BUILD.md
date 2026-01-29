# 📦 Building Nexuzy Publisher Desk with PyInstaller

Complete guide to build a standalone Windows executable with **ALL AI models included**.

---

## 📋 **Prerequisites**

### **1. Install PyInstaller**
```bash
pip install pyinstaller
```

### **2. Ensure All Dependencies are Installed**
```bash
pip install -r requirements.txt
```

### **3. Download AI Models (Important!)**

Run the application once to download all models:

```bash
python main.py
```

This will download:
- ✅ **NLLB-200 translation model** (~600MB) to `~/.cache/huggingface/`
- ✅ **Sentence transformers** (if used) to `~/.cache/torch/`

Wait for the models to download completely before building!

---

## 🚀 **Building the Executable**

### **Option 1: Using the Spec File (Recommended)**

```bash
git pull origin main
pyinstaller nexuzy.spec
```

### **Option 2: Manual Build Command**

```bash
pyinstaller --name="Nexuzy Publisher Desk" \
    --windowed \
    --onedir \
    --icon=resources/icon.ico \
    --add-data="resources;resources" \
    --add-data="C:/Users/YOUR_USERNAME/.cache/huggingface/hub/models--facebook--nllb-200-distilled-600M;models/nllb-200-distilled-600M" \
    --hidden-import=transformers \
    --hidden-import=torch \
    --hidden-import=sentencepiece \
    --hidden-import=feedparser \
    --hidden-import=beautifulsoup4 \
    --hidden-import=requests \
    --hidden-import=PIL \
    main.py
```

**Note:** Replace `YOUR_USERNAME` with your Windows username!

---

## 📂 **Output Structure**

After building, you'll get:

```
dist/
└── Nexuzy Publisher Desk/
    ├── Nexuzy Publisher Desk.exe  ← Main executable
    ├── models/
    │   └── nllb-200-distilled-600M/  ← Translation model (600MB)
    ├── resources/
    │   └── icon.ico, images, etc.
    ├── _internal/
    │   ├── Python DLLs
    │   ├── transformers/
    │   ├── torch/
    │   └── other dependencies
    └── ... other files
```

**Total Size:** ~800MB - 1.2GB (with all models)

---

## ✅ **Verification**

### **1. Check if Models are Included**

```bash
dir "dist\Nexuzy Publisher Desk\models"
```

You should see:
```
nllb-200-distilled-600M
```

### **2. Test the Executable**

```bash
cd "dist\Nexuzy Publisher Desk"
"Nexuzy Publisher Desk.exe"
```

### **3. Check Logs**

Look for:
```
✅ NLLB-200 model loaded successfully
💾 Translator cached - all future translations will be faster!
```

---

## 🐛 **Troubleshooting**

### **Issue 1: Models Not Found Error**

**Error:**
```
OSError: Model not found: facebook/nllb-200-distilled-600M
```

**Solution:**
Models weren't included. Check:

1. Did you run `python main.py` before building?
2. Check if models exist:
   ```bash
   dir %USERPROFILE%\.cache\huggingface\hub\models--facebook--nllb-200-distilled-600M
   ```
3. Rebuild with correct paths in `nexuzy.spec`

---

### **Issue 2: DLL Load Failed**

**Error:**
```
ImportError: DLL load failed while importing _C
```

**Solution:**
Install Visual C++ Redistributable:
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Install and reboot

---

### **Issue 3: Build Too Large (>2GB)**

**Solution:**
Optimize by excluding unnecessary packages:

```python
# In nexuzy.spec, add to excludes:
excludes=[
    'matplotlib',
    'scipy',
    'pandas',
    'jupyter',
    'notebook',
    'pytest',
    'setuptools',
    'distutils',
]
```

---

### **Issue 4: Translation Not Working in EXE**

**Check:**

1. Model path in code:
   ```python
   # In core/translator.py
   model_path = os.path.join(base_path, 'models', 'nllb-200-distilled-600M')
   ```

2. Verify base_path:
   ```python
   if getattr(sys, 'frozen', False):
       base_path = sys._MEIPASS  # PyInstaller temp folder
   else:
       base_path = os.path.dirname(__file__)
   ```

---

## 📦 **Distribution**

### **Option 1: Folder Distribution**

Zip the entire folder:

```bash
cd dist
tar -a -c -f "Nexuzy-Publisher-Desk-v1.0.zip" "Nexuzy Publisher Desk"
```

**Pros:**
- ✅ Smaller download (can compress to ~400MB)
- ✅ Easy to update individual files

**Cons:**
- ❌ Users see multiple files

---

### **Option 2: Single File (Not Recommended)**

```bash
pyinstaller --onefile nexuzy.spec
```

**Pros:**
- ✅ Single .exe file

**Cons:**
- ❌ Very large file (>1GB)
- ❌ Slower startup (extracts to temp every time)
- ❌ Antivirus may flag it

---

### **Option 3: Installer (Recommended)**

Use **Inno Setup** to create an installer:

1. Download: https://jrsoftware.org/isdl.php
2. Create installer script:

```inno
[Setup]
AppName=Nexuzy Publisher Desk
AppVersion=1.0
DefaultDirName={autopf}\Nexuzy Publisher Desk
OutputBaseFilename=NexuzyPublisherDeskSetup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\Nexuzy Publisher Desk\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Nexuzy Publisher Desk"; Filename: "{app}\Nexuzy Publisher Desk.exe"
Name: "{autodesktop}\Nexuzy Publisher Desk"; Filename: "{app}\Nexuzy Publisher Desk.exe"
```

3. Compile → Output: `NexuzyPublisherDeskSetup.exe` (~400MB compressed)

---

## 🎯 **Build Checklist**

### **Before Building:**

- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] PyInstaller installed (`pip install pyinstaller`)
- [ ] AI models downloaded (run `python main.py` once)
- [ ] Test app works in development mode
- [ ] Update version number in code
- [ ] Create/update app icon (`resources/icon.ico`)

### **Building:**

- [ ] Pull latest code (`git pull origin main`)
- [ ] Clean previous builds (`rm -rf build dist`)
- [ ] Run PyInstaller (`pyinstaller nexuzy.spec`)
- [ ] Check build output for errors

### **After Building:**

- [ ] Verify models folder exists in `dist/`
- [ ] Test executable on clean Windows VM
- [ ] Check translation works
- [ ] Check RSS fetching works
- [ ] Check AI article generation works
- [ ] Verify WordPress publishing works
- [ ] Test on Windows 10 and Windows 11

---

## 📊 **Build Size Breakdown**

```
Total: ~800MB - 1.2GB

📦 NLLB-200 Model:     600MB  (75%)
📦 PyTorch DLLs:       150MB  (19%)
📦 Transformers:        30MB  (4%)
📦 Other Dependencies:  15MB  (2%)
📦 App Code:             5MB  (<1%)
```

---

## 🚀 **Quick Build Commands**

```bash
# 1. Clean previous builds
rm -rf build dist

# 2. Build
pyinstaller nexuzy.spec

# 3. Test
cd "dist/Nexuzy Publisher Desk"
./"Nexuzy Publisher Desk.exe"

# 4. Package
cd ..
tar -a -c -f "Nexuzy-Publisher-Desk-v1.0.zip" "Nexuzy Publisher Desk"
```

---

## 📝 **Notes**

### **Model Download Location:**

Models are cached in:
- **Windows:** `C:\Users\<USERNAME>\.cache\huggingface\hub\`
- **Linux:** `~/.cache/huggingface/hub/`
- **macOS:** `~/.cache/huggingface/hub/`

### **First Run Behavior:**

If models aren't included in build:
1. App will try to download from HuggingFace
2. Requires internet connection
3. Takes ~10 minutes for 600MB model
4. Models cached for future runs

**Recommendation:** Always include models in build!

---

## ✅ **Success!**

You should now have:

✅ `dist/Nexuzy Publisher Desk/Nexuzy Publisher Desk.exe`  
✅ All AI models included  
✅ Ready to distribute!

---

## 🆘 **Need Help?**

If you encounter issues:

1. Check logs in `build/Nexuzy Publisher Desk/warn-Nexuzy Publisher Desk.txt`
2. Run with console enabled:
   ```python
   # In nexuzy.spec, change:
   console=True  # See error messages
   ```
3. Test dependencies:
   ```bash
   python -c "import torch; import transformers; print('OK')"
   ```

Good luck! 🚀
