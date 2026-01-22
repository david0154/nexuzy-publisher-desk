# 🚀 Nexuzy Publisher Desk - Setup Guide

## Quick Start (5 Minutes)

### Windows Users
1. Download `NexuzyPublisherDesk.exe` 
2. Double-click to launch
3. Wait for models to download (first run only, ~30-40 min)
4. Create workspace
5. Add RSS feeds
6. Start publishing!

### Developer Setup (Build from Source)

#### Prerequisites
- Windows 10/11 or Linux/Mac
- Python 3.9 - 3.11
- 16GB RAM
- 30GB free disk space
- Git

#### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/david0154/nexuzy-publisher-desk.git
cd nexuzy-publisher-desk

# 2. Create virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application (models download automatically)
python main.py
```

#### First Run (Model Download)

On first launch, the app automatically downloads:
- **SentenceTransformer** (80 MB) - for news matching
- **Mistral-7B** (14 GB or 4GB quantized) - for draft generation  
- **NLLB-200** (2.4 GB) - for translation

**Console Output:**
```
2026-01-22 14:30:00 - INFO - Starting Nexuzy Publisher Desk...
2026-01-22 14:30:01 - INFO - Checking AI models...
2026-01-22 14:30:02 - INFO - Downloading SentenceTransformer...
✓ SentenceTransformer downloaded successfully
2026-01-22 14:31:45 - INFO - Downloading Mistral-7B...
... (15-20 minutes)
✓ Mistral-7B downloaded successfully
2026-01-22 14:51:22 - INFO - Downloading NLLB-200...
... (5-10 minutes)
✓ NLLB-200 downloaded successfully
2026-01-22 15:02:15 - INFO - ✓ All AI models ready
2026-01-22 15:02:16 - INFO - Database initialized successfully
```

---

## Building Windows EXE

### Step 1: Prepare Environment
```bash
# From project directory
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
```

### Step 2: Create Logo (Optional)
Place icon file at: `resources/logo.ico`

### Step 3: Build EXE
```bash
pyinstaller build_config.spec
```

**Output**: `dist/NexuzyPublisherDesk.exe`

### Step 4: Test Build
```bash
# Navigate to dist folder
cd dist
NexuzyPublisherDesk.exe
```

**⚠️ Note**: EXE is ~500MB+. First run still downloads models (~30GB total with models).

---

## GPU Acceleration Setup

### NVIDIA CUDA (Recommended for Fast Generation)

```bash
# Install CUDA
# 1. Download from: https://developer.nvidia.com/cuda-downloads
# 2. Install CUDA 11.8 or 12.x
# 3. Verify installation
cuda-samples\1_Utilities\deviceQuery\deviceQuery.exe

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Reinstall other packages
pip install -r requirements.txt
```

### AMD ROCm

```bash
# Install ROCm
# 1. Download from: https://rocmdocs.amd.com/en/docs/deploy/windows/
# 2. Install ROCm

# Install PyTorch with ROCm
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
```

### Apple Silicon (M1/M2/M3)

```bash
# PyTorch with Metal
pip install torch torchvision torchaudio
```

**After GPU setup**, restart application for automatic GPU detection.

---

## Directory Structure After Setup

```
nexuzy-publisher-desk/
├── main.py
├── core/
├── models/                          ← Models downloaded here
├── resources/
├── nexuzy.db                        ← Created on first run
├── nexuzy_publisher.log              ← Created on first run
├── venv/                              ← Virtual environment
├── build/                            ← PyInstaller intermediate
├── dist/                             ← Output EXE
└── README.md
```

---

## Troubleshooting Setup

### Problem: Models Not Downloading

**Solution 1: Manual Download**
```bash
python -c "from main import ModelDownloader; ModelDownloader().check_and_download()"
```

**Solution 2: Check Disk Space**
```bash
# Windows
dir C:\ 

# Linux/Mac
df -h
```
Need at least 30GB free.

**Solution 3: Network Issues**
- Check internet connection
- Try VPN if HuggingFace is blocked
- Download manually from HuggingFace:
  - https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
  - https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1
  - https://huggingface.co/facebook/nllb-200-distilled-600M

### Problem: Out of Memory

**Solutions:**
1. Close other applications
2. Install GPU support (CUDA/ROCm)
3. Use lighter models (already using distilled versions)
4. Process fewer articles at once
5. Increase virtual memory (Windows):
   - Settings > System > Advanced system settings > Performance > Virtual memory

### Problem: ModuleNotFoundError

```bash
# Reinstall all dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Problem: Tkinter Not Found (Linux)

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

### Problem: PyInstaller Build Fails

```bash
# Clean and rebuild
rmdir /s build
rmdir /s dist
pyinstaller --clean build_config.spec
```

---

## Initial Configuration

### 1. First Launch
```bash
python main.py
```

### 2. Create Workspace
- Click "+ New Workspace"
- Name: e.g., "Tech News Desk"
- Click Create

### 3. Add RSS Feeds
- Click "RSS Manager"
- Click "+ Add Feed"
- Paste RSS URL
- Select category, language, priority
- Click "Save Feed"

### 4. Configure WordPress (Optional)
- Click "WordPress"
- Enter site URL (e.g., `https://myblog.com`)
- Enter username
- Enter application password (generate in WordPress)
- Click "Test Connection"
- Click "Save"

---

## Performance Optimization

### Low-End Hardware (8GB RAM)

1. **Disable translation** initially
2. **Process one article at a time**
3. **Install GPU acceleration**
4. **Clear old articles** periodically

### Recommended Hardware (16GB RAM)

1. **Process 5-10 articles** simultaneously
2. **Enable all features**
3. **Run smooth operation**

### High-End Hardware (32GB+ RAM, GPU)

1. **Batch process 50+ articles**
2. **Enable real-time translation**
3. **Run multiple workspaces**

---

## Logs & Debugging

### View Logs
```bash
# Console output during run
python main.py

# Persistent log file
type nexuzy_publisher.log  # Windows
cat nexuzy_publisher.log   # Linux/Mac

# Real-time log follow
tail -f nexuzy_publisher.log
```

### Debug Mode
```bash
# Modify main.py logging level
# Line ~18, change from logging.INFO to logging.DEBUG
logging.basicConfig(level=logging.DEBUG, ...)

# Run again
python main.py
```

---

## Environment Variables

### Create `.env` file in project root:

```
# Model Configuration
MODEL_CACHE_DIR=./models
GPU_ENABLED=true

# Database
DB_PATH=./nexuzy.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=nexuzy_publisher.log

# Appearance
THEME=dark
WINDOW_WIDTH=1200
WINDOW_HEIGHT=700
```

---

## Security Setup

### Database Encryption (Optional)
```python
# Install SQLCipher
pip install sqlcipher3-binary

# Modify main.py database initialization to use encryption
```

### WordPress Credentials Security
- Never commit `.env` with credentials
- Use WordPress application passwords (not main password)
- Application passwords are safer and revocable

---

## Uninstallation

### Windows
1. Delete EXE file
2. Optional: Delete `models/` folder to free 30GB
3. Optional: Delete `nexuzy.db` to clear database

### Source Installation
```bash
# Remove virtual environment
rmdir /s venv  # Windows
rm -rf venv    # Linux/Mac

# Remove project folder
rmdir /s nexuzy-publisher-desk
rm -rf nexuzy-publisher-desk
```

---

## Next Steps

1. **Read**: [README.md](README.md) for complete feature guide
2. **Try**: Add RSS feeds and fetch news
3. **Explore**: Test news matching and grouping
4. **Configure**: Set up WordPress connection
5. **Generate**: Create first AI draft
6. **Publish**: Push to WordPress

---

## Support

- **Issues**: https://github.com/david0154/nexuzy-publisher-desk/issues
- **Discussions**: https://github.com/david0154/nexuzy-publisher-desk/discussions
- **Logs**: Check `nexuzy_publisher.log` for detailed errors

---

**Ready to launch? Start with `python main.py` or run the EXE!**
