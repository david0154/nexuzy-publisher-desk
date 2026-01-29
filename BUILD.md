# 📦 Building Nexuzy Publisher Desk with PyInstaller

Complete guide to build a standalone Windows executable with **ALL AI models included**.

---

## 🤖 **AI Models Included**

### **1. Mistral 7B GGUF (4.4GB)** - Article Writing
- **Purpose:** Generate AI articles from headlines
- **Location:** `models/mistral-7b-instruct-v0.2.Q4_K_M.gguf`
- **Size:** 4.4 GB
- **Quantization:** Q4_K_M (4-bit, high quality)

### **2. NLLB-200 (600MB)** - Translation
- **Purpose:** Translate articles to 200+ languages
- **Location:** `~/.cache/huggingface/hub/models--facebook--nllb-200-distilled-600M`
- **Size:** 600 MB
- **Framework:** PyTorch/Transformers

**Total Models Size:** ~5 GB

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

### **3. Download/Place AI Models**

#### **✅ Mistral 7B GGUF Model:**

Place the model file in:
```
models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

**If you don't have it:**
1. Download from HuggingFace: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
2. Download the `mistral-7b-instruct-v0.2.Q4_K_M.gguf` file (4.4GB)
3. Place it in the `models/` folder

#### **✅ NLLB-200 Translation Model:**

Run the application once to download:

```bash
python main.py
```

This will download NLLB-200 (~600MB) to `~/.cache/huggingface/`

Wait for both models to be ready before building!

---

## 🚀 **Building the Executable**

### **Option 1: Using the Spec File (Recommended)**

```bash
git pull origin main
pyinstaller nexuzy.spec
```

During build, you'll see:
```
================================================================================
📦 ADDING AI MODELS TO BUILD
================================================================================
✅ Mistral 7B GGUF: 4.37 GB
✅ NLLB-200 Translation Model: 600 MB
================================================================================

✅ BUILD CONFIGURATION COMPLETE
================================================================================

Expected build size:
  📦 Mistral 7B:        ~4.4 GB
  📦 NLLB-200:          ~0.6 GB
  📦 PyTorch/Deps:      ~0.2 GB
  📦 Other:             ~0.3 GB
  ────────────────────────────────────────
  📦 TOTAL:             ~5.5 GB
```

### **Option 2: Manual Build Command**

```bash
pyinstaller --name="Nexuzy Publisher Desk" \
    --windowed \
    --onedir \
    --icon=resources/icon.ico \
    --add-data="resources;resources" \
    --add-data="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf;models" \
    --add-data="C:/Users/YOUR_USERNAME/.cache/huggingface/hub/models--facebook--nllb-200-distilled-600M;models/nllb-200-distilled-600M" \
    --hidden-import=transformers \
    --hidden-import=torch \
    --hidden-import=llama_cpp \
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
    │   ├── mistral-7b-instruct-v0.2.Q4_K_M.gguf  ← 4.4GB
    │   └── nllb-200-distilled-600M/  ← 600MB
    ├── resources/
    │   └── icon.ico, images, etc.
    ├── _internal/
    │   ├── Python DLLs
    │   ├── transformers/
    │   ├── torch/
    │   ├── llama_cpp/
    │   └── other dependencies
    └── ... other files
```

**Total Size:** ~5.5GB - 6GB (with both models)

---

## ✅ **Verification**

### **1. Check if Models are Included**

```bash
dir "dist\Nexuzy Publisher Desk\models"
```

You should see:
```
mistral-7b-instruct-v0.2.Q4_K_M.gguf    (4.4 GB)
nllb-200-distilled-600M                 (folder)
```

### **2. Test the Executable**

```bash
cd "dist\Nexuzy Publisher Desk"
"Nexuzy Publisher Desk.exe"
```

### **3. Check Logs**

Look for:
```
✅ Mistral 7B model loaded successfully
✅ NLLB-200 model loaded successfully
💾 Translator cached - all future translations will be faster!
```

---

## 🐛 **Troubleshooting**

### **Issue 1: Mistral Model Not Found**

**Error:**
```
FileNotFoundError: Model not found: models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

**Solution:**
1. Check if model exists:
   ```bash
   dir models\mistral-7b-instruct-v0.2.Q4_K_M.gguf
   ```
2. Download from HuggingFace:
   - https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
   - Get `mistral-7b-instruct-v0.2.Q4_K_M.gguf` (4.4GB)
3. Place in `models/` folder
4. Rebuild: `pyinstaller nexuzy.spec`

---

### **Issue 2: NLLB Model Not Found**

**Error:**
```
OSError: Model not found: facebook/nllb-200-distilled-600M
```

**Solution:**
1. Run app once to download:
   ```bash
   python main.py
   ```
2. Wait for download to complete
3. Verify model exists:
   ```bash
   dir %USERPROFILE%\.cache\huggingface\hub\models--facebook--nllb-200-distilled-600M
   ```
4. Rebuild: `pyinstaller nexuzy.spec`

---

### **Issue 3: DLL Load Failed**

**Error:**
```
ImportError: DLL load failed while importing _C
```

**Solution:**
Install Visual C++ Redistributable:
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Install and reboot

---

### **Issue 4: Build Too Large (>6GB)**

**Solutions:**

**Option A:** Use smaller Mistral model:
- `mistral-7b-instruct-v0.2.Q3_K_M.gguf` (3.5GB instead of 4.4GB)
- Lower quality but 1GB smaller

**Option B:** Don't include models in build:
```python
# In nexuzy.spec, comment out model additions
# Models will download on first run instead
```

**Option C:** Exclude unnecessary packages:
```python
# In nexuzy.spec, add to excludes:
excludes=[
    'matplotlib',
    'scipy',
    'pandas',
    'jupyter',
    'notebook',
    'pytest',
]
```

---

## 📦 **Distribution**

### **Option 1: Folder Distribution (Recommended)**

Zip the entire folder:

```bash
cd dist
tar -a -c -f "Nexuzy-Publisher-Desk-v1.0.zip" "Nexuzy Publisher Desk"
```

**Result:** `Nexuzy-Publisher-Desk-v1.0.zip` (~2-3GB compressed)

**Pros:**
- ✅ Good compression (50% smaller)
- ✅ Easy to update individual files

**Cons:**
- ❌ Large download (2-3GB)
- ❌ Users see multiple files

---

### **Option 2: Split Archive (For Large Files)**

Split into smaller parts for easier download:

```bash
7z a -v1000m "Nexuzy-Publisher-Desk-v1.0.7z" "Nexuzy Publisher Desk"
```

**Result:** 
- `Nexuzy-Publisher-Desk-v1.0.7z.001` (1GB)
- `Nexuzy-Publisher-Desk-v1.0.7z.002` (1GB)
- `Nexuzy-Publisher-Desk-v1.0.7z.003` (500MB)

**Users extract with:** `7z x Nexuzy-Publisher-Desk-v1.0.7z.001`

---

### **Option 3: Installer with Inno Setup**

Create a professional installer:

```inno
[Setup]
AppName=Nexuzy Publisher Desk
AppVersion=1.0
DefaultDirName={autopf}\Nexuzy Publisher Desk
OutputBaseFilename=NexuzyPublisherDeskSetup
Compression=lzma2/ultra64
SolidCompression=yes
DiskSpanning=yes

[Files]
Source: "dist\Nexuzy Publisher Desk\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Nexuzy Publisher Desk"; Filename: "{app}\Nexuzy Publisher Desk.exe"
Name: "{autodesktop}\Nexuzy Publisher Desk"; Filename: "{app}\Nexuzy Publisher Desk.exe"
```

**Result:** `NexuzyPublisherDeskSetup.exe` (~2-2.5GB compressed)

---

## 🎯 **Build Checklist**

### **Before Building:**

- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] PyInstaller installed (`pip install pyinstaller`)
- [ ] **Mistral 7B model** in `models/mistral-7b-instruct-v0.2.Q4_K_M.gguf`
- [ ] **NLLB-200 model** downloaded (run `python main.py` once)
- [ ] Test app works in development mode
- [ ] Update version number in code
- [ ] Create/update app icon (`resources/icon.ico`)
- [ ] **Have 10GB+ free disk space** for build

### **Building:**

- [ ] Pull latest code (`git pull origin main`)
- [ ] Clean previous builds (`rm -rf build dist`)
- [ ] Run PyInstaller (`pyinstaller nexuzy.spec`)
- [ ] Watch for model confirmation messages
- [ ] Check build output for errors
- [ ] **Build will take 10-20 minutes** (large models)

### **After Building:**

- [ ] Verify both models in `dist/Nexuzy Publisher Desk/models/`
- [ ] Check total folder size (~5.5GB)
- [ ] Test executable on clean Windows VM
- [ ] Check Mistral AI article generation works
- [ ] Check NLLB translation works
- [ ] Check RSS fetching works
- [ ] Verify WordPress publishing works
- [ ] Test on Windows 10 and Windows 11

---

## 📊 **Build Size Breakdown**

```
Total: ~5.5GB - 6GB

📦 Mistral 7B Model:   4.4 GB  (78%)
📦 NLLB-200 Model:     600 MB  (11%)
📦 PyTorch DLLs:       200 MB  (4%)
📦 llama-cpp DLLs:     150 MB  (3%)
📦 Transformers:        80 MB  (1%)
📦 Other Dependencies:  50 MB  (1%)
📦 App Code:            20 MB  (<1%)
```

**Compressed (ZIP):** ~2-3GB (50% compression)

---

## 🚀 **Quick Build Commands**

```bash
# 1. Ensure models are in place
ls models/mistral-7b-instruct-v0.2.Q4_K_M.gguf  # Should exist
python main.py  # Download NLLB-200

# 2. Clean previous builds
rm -rf build dist

# 3. Build (will take 10-20 minutes)
pyinstaller nexuzy.spec

# 4. Verify models included
ls "dist/Nexuzy Publisher Desk/models/"

# 5. Test
cd "dist/Nexuzy Publisher Desk"
./"Nexuzy Publisher Desk.exe"

# 6. Package
cd ..
tar -a -c -f "Nexuzy-Publisher-Desk-v1.0.zip" "Nexuzy Publisher Desk"
```

---

## 📝 **Important Notes**

### **Model Locations:**

**Mistral 7B:**
```
Source:  models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
In EXE:  dist/Nexuzy Publisher Desk/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

**NLLB-200:**
```
Source:  ~/.cache/huggingface/hub/models--facebook--nllb-200-distilled-600M
In EXE:  dist/Nexuzy Publisher Desk/models/nllb-200-distilled-600M/
```

### **First Run Behavior:**

✅ **With models included (recommended):**
- App starts immediately
- No internet required
- Models load from local files
- Fast startup

❌ **Without models:**
- App tries to download from internet
- Mistral: 4.4GB download (~30-60 min)
- NLLB: 600MB download (~5-10 min)
- Requires stable internet connection

**Recommendation:** Always include models in build!

---

## ✅ **Success!**

You should now have:

✅ `dist/Nexuzy Publisher Desk/Nexuzy Publisher Desk.exe`  
✅ Mistral 7B model included (4.4GB)  
✅ NLLB-200 model included (600MB)  
✅ All dependencies included  
✅ Ready to distribute!  

**Total build size:** ~5.5GB

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
   python -c "import torch; import transformers; import llama_cpp; print('OK')"
   ```
4. Verify both models exist:
   ```bash
   ls models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
   ls ~/.cache/huggingface/hub/models--facebook--nllb-200-distilled-600M
   ```

Good luck! 🚀
