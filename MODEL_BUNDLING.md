# 🤖 MODEL BUNDLING GUIDE

How to bundle AI models with PyInstaller for Nexuzy Publisher Desk

---

## 📚 MODELS USED

### **1. Sentence Transformer: all-MiniLM-L6-v2**

**Purpose:** News similarity, duplicate detection, semantic search

**Size:** ~90 MB

**Required:** YES (app needs this for news matching)

**Download:** Auto-downloaded on first use, or manually prepare

---

### **2. GGUF Model: Mistral 7B**

**Purpose:** AI draft generation (local LLM)

**Size:** ~4.37 GB

**Required:** NO (can use API-based drafts instead)

**Download:** Manual or via build script

---

## 📍 SENTENCE TRANSFORMER LOCATIONS

PyInstaller will auto-detect models in these locations:

### **Your Computer (Current Paths):**

```
C:\Users\Manoj Konark\Downloads\nexuzy-publisher-desk-main\nexuzy-publisher-desk-main\models\
├── models--sentence-transformers--all-MiniLM-L6-v2\     ← HuggingFace format
└── sentence-transformers_all-MiniLM-L6-v2\            ← Alternate format
```

### **Standard Locations (Auto-detected):**

```
Project Structure:
models/
├── sentence-transformers_all-MiniLM-L6-v2/
│   ├── config.json
│   ├── pytorch_model.bin
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   ├── vocab.txt
│   └── ... (other files)
│
├── models--sentence-transformers--all-MiniLM-L6-v2/
│   └── snapshots/
│       └── [hash]/
│           ├── config.json
│           ├── pytorch_model.bin
│           └── ... (other files)
│
└── mistral-7b-instruct-v0.2.Q4_K_M.gguf  ← Optional
```

---

## ⚙️ SETUP METHODS

### **Method 1: Use Preparation Script** (Easiest)

```bash
# This will find, organize, and verify all models
python prepare_models.py
```

**What it does:**
1. ✅ Searches for sentence transformer in all locations
2. ✅ Copies to standard `models/` directory
3. ✅ Verifies all required files
4. ✅ Checks GGUF models
5. ✅ Shows size summary

**Output:**
```
✅ Model preparation complete!

Models ready for PyInstaller:
  Sentence Transformers: 90.2 MB
  GGUF Models: 4.37 GB (optional)
  Total Size: 4.46 GB
```

---

### **Method 2: Copy from Your Location**

```bash
# Your current path:
cd "C:\Users\Manoj Konark\Downloads\nexuzy-publisher-desk-main\nexuzy-publisher-desk-main"

# Copy to standard location (if not already there)
# Both formats work - PyInstaller will find either one

# Format 1: Already in models/ (NO ACTION NEEDED)
dir models\models--sentence-transformers--all-MiniLM-L6-v2

# Format 2: Already in models/ (NO ACTION NEEDED)
dir models\sentence-transformers_all-MiniLM-L6-v2
```

**You already have the models! Just build directly:**
```bash
python build_installer.py
```

---

### **Method 3: Download Fresh Copy**

```python
# Using Python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model.save('models/sentence-transformers_all-MiniLM-L6-v2')
```

---

## 📦 PYINSTALLER INTEGRATION

### **In nexuzy_installer.spec:**

```python
# Auto-detects these patterns:
sentence_transformer_models = [
    'models/models--sentence-transformers--all-MiniLM-L6-v2',
    'models/sentence-transformers_all-MiniLM-L6-v2',
]

# During build, shows:
[BUILD] ✅ Including Sentence Transformer: all-MiniLM-L6-v2
        Files: 23, Size: 90.2 MB
```

### **Hidden Imports Added:**

```python
hiddenimports=[
    'sentence_transformers',
    'sentence_transformers.models',
    'sentence_transformers.util',
    'sentence_transformers.SentenceTransformer',
    # ... other imports
]
```

---

## 🔧 BUILD PROCESS

### **With Your Current Setup:**

```bash
# Your models are already in:
# C:\Users\Manoj Konark\Downloads\nexuzy-publisher-desk-main\nexuzy-publisher-desk-main\models\

# Just run the build:
python build_installer.py

# Or manual:
pyinstaller --clean --noconfirm nexuzy_installer.spec
```

**During build you'll see:**
```
=============================================================
NEXUZY PUBLISHER DESK - BUILD CONFIGURATION
=============================================================
[BUILD] ✅ Including resources/
[BUILD] ✅ Including GGUF models: 1 files (4.37 GB)
        - mistral-7b-instruct-v0.2.Q4_K_M.gguf (4.37 GB)
[BUILD] ✅ Including Sentence Transformer: all-MiniLM-L6-v2
        Files: 23, Size: 90.2 MB
[BUILD] ✅ Including core/
=============================================================
```

---

## 📦 DISTRIBUTION SIZES

### **With Both Models:**

```
Executable Bundle:
  - NexuzyPublisherDesk.exe: 250 MB
  - models/
    ├── sentence-transformers/: 90 MB
    └── mistral-7b-*.gguf: 4.37 GB
  
Total: ~4.7 GB
```

### **Minimal (Recommended):**

```
Executable Bundle:
  - NexuzyPublisherDesk.exe: 250 MB
  - models/
    └── sentence-transformers/: 90 MB
  
Total: ~340 MB

(GGUF model downloaded separately by users)
```

---

## ✅ VERIFICATION

### **Check Model Files:**

```bash
# Your current location:
dir "C:\Users\Manoj Konark\Downloads\nexuzy-publisher-desk-main\nexuzy-publisher-desk-main\models"

# Should show:
# - models--sentence-transformers--all-MiniLM-L6-v2 (folder)
# - sentence-transformers_all-MiniLM-L6-v2 (folder)
# - mistral-7b-instruct-v0.2.Q4_K_M.gguf (file, optional)
```

### **Verify Sentence Transformer:**

```bash
# Check either format (both work):
dir models\sentence-transformers_all-MiniLM-L6-v2

# Required files:
✅ config.json
✅ pytorch_model.bin (largest file, ~90 MB)
✅ tokenizer.json
✅ tokenizer_config.json
✅ vocab.txt
✅ special_tokens_map.json
```

### **Test After Build:**

```bash
cd dist
NexuzyPublisherDesk.exe

# Check console/logs:
✅ "Sentence transformer loaded successfully"
✅ News matching works
✅ Duplicate detection works
```

---

## ⚠️ TROUBLESHOOTING

### **Issue: "Model not found" during runtime**

**Cause:** Model not bundled or wrong path

**Solution:**
```bash
# 1. Check if model was included in build
dir dist\models

# 2. Re-run preparation
python prepare_models.py

# 3. Rebuild
pyinstaller --clean --noconfirm nexuzy_installer.spec
```

---

### **Issue: "sentence_transformers module not found"**

**Cause:** Missing hidden import

**Solution:**
```python
# Already added in nexuzy_installer.spec:
hiddenimports=[
    'sentence_transformers',
    'sentence_transformers.models',
    'sentence_transformers.util',
]
```

---

### **Issue: Build size too large**

**Options:**

**1. Exclude GGUF model:**
```bash
# Don't include mistral-7b-*.gguf
# Users download separately
# Reduces from 4.7 GB to 340 MB
```

**2. Keep only sentence transformer:**
```bash
# Sentence transformer is REQUIRED (90 MB)
# Can't exclude this one
```

---

### **Issue: Slow model loading**

**This is NORMAL:**
- Sentence Transformer: 5-10 seconds first load
- GGUF Model: 10-30 seconds every load
- Models are cached after first load

---

## 📊 SIZE COMPARISON

| Component | Size | Required | Load Time |
|-----------|------|----------|------------|
| **Executable** | 250 MB | YES | Instant |
| **Sentence Transformer** | 90 MB | YES | 5-10 sec (first) |
| **GGUF Model** | 4.37 GB | NO | 10-30 sec |
| **Total (Minimal)** | 340 MB | - | - |
| **Total (Full)** | 4.7 GB | - | - |

---

## 🎯 RECOMMENDATIONS

### **For Distribution:**

✅ **DO include:** Sentence Transformer (required, only 90 MB)

❌ **DON'T include:** GGUF model (optional, 4.37 GB)

**Why?**
- Smaller download (340 MB vs 4.7 GB)
- Faster distribution
- Users who want local AI drafts can download GGUF separately
- Most users can use API-based drafts instead

---

### **For Development:**

✅ **DO include:** Both models for full testing

---

## 🚀 QUICK START

```bash
# You already have the models in the right place!
# Just build:

# Step 1: Verify models
python prepare_models.py

# Step 2: Build
python build_installer.py

# Done! Your models are bundled.
```

---

## 📝 SUMMARY

**Your Current Setup:**
```
✅ Sentence Transformer: Already in models/
✅ GGUF Model: Already in models/ (optional)
✅ PyInstaller spec: Configured to include both
✅ Hidden imports: All added

🎯 Ready to build!
```

**Just run:**
```bash
python build_installer.py
```

**Your models will be automatically bundled!**

---

**Questions? Check BUILD_GUIDE.md or open an issue on GitHub**
