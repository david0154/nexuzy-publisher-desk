# Setup Guide - Development Environment

## 🛠️ Quick Setup (5 Minutes)

### Prerequisites

- **Python 3.9 - 3.11** (⚠️ **NOT 3.13** - llama-cpp-python compatibility issues)
- **Git** - For cloning repository
- **8GB+ RAM** - Recommended for AI models
- **~10GB disk space** - 5GB models + workspace

---

## 🚀 Installation Steps

### Step 1: Clone Repository

```bash
git clone https://github.com/david0154/nexuzy-publisher-desk.git
cd nexuzy-publisher-desk
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install llama-cpp-python (Pre-Built Wheel)

⚠️ **IMPORTANT:** Install this FIRST before requirements.txt

**Windows (CPU-only - Recommended):**
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

**Windows (NVIDIA GPU - CUDA 12.1):**
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

**Linux (CPU-only):**
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

**Linux (NVIDIA GPU - CUDA 12.1):**
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

**macOS (CPU-only):**
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

**macOS (Metal GPU Acceleration):**
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/metal
```

### Step 4: Install Other Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Collecting transformers>=4.36.0...
Collecting sentence-transformers>=2.2.2...
Collecting torch>=2.1.0...
...
Successfully installed transformers-4.57.6 torch-2.10.0 ...
```

### Step 5: Verify Installation

```bash
python -c "import llama_cpp; print('llama-cpp-python:', llama_cpp.__version__)"
python -c "import transformers; print('transformers:', transformers.__version__)"
python -c "import torch; print('torch:', torch.__version__)"
```

**Expected output:**
```
llama-cpp-python: 0.3.x
transformers: 4.57.x
torch: 2.10.x
```

---

## 🏃 Run Application

```bash
python main.py
```

**First Run:**
- Models will auto-download (~5GB)
- Takes 15-20 minutes
- Internet connection required

**Subsequent Runs:**
- Instant startup from cached models

---

## 🐛 Troubleshooting

### Issue 1: Python 3.13 Compatibility

**Error:** `llama-cpp-python` not available for Python 3.13

**Solution:**
```bash
# Uninstall Python 3.13
# Install Python 3.11 from python.org
python --version  # Should show 3.11.x

# Recreate venv
rmdir /s /q venv  # Windows
rm -rf venv       # Linux/Mac

python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
pip install -r requirements.txt
```

### Issue 2: llama-cpp-python Build Fails

**Error:** `CMAKE_C_COMPILER not set` or `nmake not found`

**Solution:** Use pre-built wheel (see Step 3)

```bash
# DO NOT use pip install llama-cpp-python
# ALWAYS use pre-built wheel:
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

### Issue 3: torch Version Conflict

**Error:** `No matching distribution found for torch==2.1.1`

**Solution:** Already fixed in requirements.txt (uses `>=2.1.0`)

```bash
git pull origin main
pip install -r requirements.txt
```

### Issue 4: Import Error After Installation

**Error:** `ModuleNotFoundError: No module named 'llama_cpp'`

**Solution:**
```bash
# Verify venv is activated
where python  # Should point to venv\Scripts\python.exe

# Reinstall llama-cpp-python
pip uninstall llama-cpp-python
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

### Issue 5: Models Not Downloading

**Error:** Application starts but models don't download

**Solution:**
```bash
# Check internet connection
ping huggingface.co

# Manually download models
python -c "from huggingface_hub import hf_hub_download; hf_hub_download('TheBloke/Mistral-7B-Instruct-v0.2-GGUF', 'mistral-7b-instruct-v0.2.Q4_K_M.gguf', cache_dir='models')"
```

---

## 📚 Additional Resources

### Documentation

- [QUICK_START.md](QUICK_START.md) - 5-minute usage guide
- [FEATURES.md](FEATURES.md) - Complete feature list
- [WORDPRESS_SETUP.md](WORDPRESS_SETUP.md) - WordPress integration
- [AI_MODELS.md](AI_MODELS.md) - AI model details
- [DEPLOYMENT.md](DEPLOYMENT.md) - Building EXE

### Python Version Compatibility

| Python Version | Status | Notes |
|----------------|--------|-------|
| 3.9 | ✅ Fully Supported | Recommended |
| 3.10 | ✅ Fully Supported | Recommended |
| 3.11 | ✅ Fully Supported | **Best Choice** |
| 3.12 | ⚠️ Limited | Some packages may have issues |
| 3.13 | ❌ Not Supported | llama-cpp-python unavailable |

### GPU Acceleration

**NVIDIA GPU (CUDA):**
```bash
# Install CUDA-enabled torch
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Install CUDA-enabled llama-cpp-python
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

**AMD GPU (ROCm - Linux only):**
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/rocm
```

**Apple Silicon (Metal):**
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/metal
```

---

## 🔧 Development Setup

### Install Development Dependencies

```bash
# Install all dependencies including dev tools
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
pip install -r requirements.txt

# Install dev tools
pip install black flake8 pytest
```

### Code Formatting

```bash
# Format code
black .

# Check linting
flake8 .
```

### Testing

```bash
# Run tests (when available)
pytest tests/
```

---

## 💻 IDE Setup

### Visual Studio Code

1. Install Python extension
2. Select venv interpreter:
   - `Ctrl+Shift+P` → "Python: Select Interpreter"
   - Choose `./venv/Scripts/python.exe`

3. Recommended extensions:
   - Python (Microsoft)
   - Pylance
   - autopep8

### PyCharm

1. Open project folder
2. File → Settings → Project → Python Interpreter
3. Add interpreter → Existing environment
4. Select `venv\Scripts\python.exe`

---

## 🚀 Quick Start Commands

```bash
# Full setup from scratch
git clone https://github.com/david0154/nexuzy-publisher-desk.git
cd nexuzy-publisher-desk
python -m venv venv
venv\Scripts\activate
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
pip install -r requirements.txt
python main.py
```

**Copy-paste this entire block!** ✅

---

## 💬 Support

If you encounter issues:

1. Check [Troubleshooting](#-troubleshooting) above
2. Search [GitHub Issues](https://github.com/david0154/nexuzy-publisher-desk/issues)
3. Open new issue with:
   - Python version: `python --version`
   - OS: Windows/Linux/Mac
   - Error message
   - Full traceback

---

**Last Updated:** January 22, 2026

**Author:** David & Nexuzy Tech
