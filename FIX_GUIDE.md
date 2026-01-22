# Fix Guide - Dependency Issues

## Problems Fixed

1. **NumPy 2.x Incompatibility** - Torch doesn't work with NumPy 2.x
2. **PyTorch/Transformers Version Mismatch** - Incompatible versions causing AttributeError
3. **Windows Encoding Issues** - Unicode characters causing UnicodeEncodeError
4. **llama-cpp-python dependency** - Replaced with ctransformers

## Solution Steps

### Step 1: Clean Your Virtual Environment

```powershell
# Deactivate current venv
deactivate

# Delete the old venv folder
Remove-Item -Recurse -Force venv

# Create fresh venv
python -m venv venv

# Activate it
.\venv\Scripts\Activate
```

### Step 2: Upgrade pip and Install Dependencies

```powershell
# Upgrade pip, setuptools, wheel
python -m pip install --upgrade pip setuptools wheel

# Install dependencies with proper versions
pip install -r requirements.txt
```

### Step 3: Verify Installation

```powershell
# Check NumPy version (should be <2.0)
pip show numpy

# Check PyTorch version (should be 2.1.0 - 2.4.x)
pip show torch

# Check transformers version
pip show transformers

# Check ctransformers
pip show ctransformers
```

### Step 4: Run the Application

```powershell
python main.py
```

## What Was Changed

### 1. requirements.txt

**Added version constraints:**
```
numpy>=1.24.0,<2.0.0  # CRITICAL: Must be <2.0 for torch compatibility
transformers>=4.36.0,<4.45.0  # Compatible version range
torch>=2.1.0,<2.5.0  # Compatible with numpy<2
ctransformers>=0.2.27  # Replaced llama-cpp-python
```

### 2. main.py

**Fixed Windows encoding:**
```python
# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# UTF-8 logging
logging.basicConfig(
    handlers=[
        logging.FileHandler('nexuzy_publisher.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
```

**Replaced Unicode symbols:**
- `✓` → `[OK]`
- `✗` → `[FAIL]`
- `⚠` → `[WARN]`
- `📰`, `📡`, `✏️`, `🌐`, `⚙️` → Removed

### 3. core/ai_draft_generator.py

**Changed from llama-cpp-python to ctransformers:**
```python
# Old
from llama_cpp import Llama
llm = Llama(model_path=..., n_ctx=4096, n_threads=4)

# New
from ctransformers import AutoModelForCausalLM
llm = AutoModelForCausalLM.from_pretrained(
    str(model_path),
    model_type='mistral',
    context_length=4096,
    threads=4
)
```

## Expected Output

When you run `python main.py`, you should see:

```
2026-01-22 16:XX:XX,XXX - __main__ - INFO - ============================================================
2026-01-22 16:XX:XX,XXX - __main__ - INFO - Starting Nexuzy Publisher Desk (Pure Python)...
2026-01-22 16:XX:XX,XXX - __main__ - INFO - ============================================================
2026-01-22 16:XX:XX,XXX - __main__ - INFO - Checking AI models (Pure Python)...
2026-01-22 16:XX:XX,XXX - __main__ - INFO - [OK] Database initialized successfully
2026-01-22 16:XX:XX,XXX - __main__ - INFO - [OK] Core modules loaded (Pure Python)
```

Then the Tkinter window should open without errors.

## Common Issues

### Issue 1: Still Getting NumPy Error

**Solution:**
```powershell
# Force reinstall NumPy 1.x
pip uninstall numpy -y
pip install "numpy<2.0" --force-reinstall
```

### Issue 2: Torch Import Error

**Solution:**
```powershell
# Reinstall torch with compatible numpy
pip uninstall torch -y
pip install torch==2.1.0 --force-reinstall
```

### Issue 3: Transformers AttributeError

**Solution:**
```powershell
# Downgrade transformers
pip install "transformers<4.45.0" --force-reinstall
```

### Issue 4: ctransformers Not Found

**Solution:**
```powershell
# Install ctransformers
pip install ctransformers>=0.2.27
```

## Dependency Version Reference

| Package | Minimum | Maximum | Current Recommended |
|---------|---------|---------|--------------------|
| numpy | 1.24.0 | 1.26.4 | 1.26.4 |
| torch | 2.1.0 | 2.4.1 | 2.1.0 |
| transformers | 4.36.0 | 4.44.2 | 4.40.0 |
| sentence-transformers | 2.2.2 | 2.7.0 | 2.2.2 |
| ctransformers | 0.2.27 | latest | 0.2.27 |

## Testing Installation

### Test 1: NumPy Version

```python
import numpy as np
print(f"NumPy version: {np.__version__}")
assert np.__version__.startswith('1.'), "NumPy must be 1.x"
print("[OK] NumPy version correct")
```

### Test 2: PyTorch Import

```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print("[OK] PyTorch works")
```

### Test 3: Transformers Import

```python
from transformers import AutoTokenizer
print("[OK] Transformers works")
```

### Test 4: CTransformers Import

```python
from ctransformers import AutoModelForCausalLM
print("[OK] CTransformers works")
```

### Test 5: SentenceTransformers Import

```python
from sentence_transformers import SentenceTransformer
print("[OK] SentenceTransformers works")
```

## Full Test Script

Create `test_deps.py`:

```python
import sys

print("Testing dependencies...\n")

try:
    import numpy as np
    print(f"[OK] NumPy {np.__version__}")
    assert np.__version__.startswith('1.'), "NumPy must be <2.0"
except Exception as e:
    print(f"[FAIL] NumPy: {e}")
    sys.exit(1)

try:
    import torch
    print(f"[OK] PyTorch {torch.__version__}")
except Exception as e:
    print(f"[FAIL] PyTorch: {e}")
    sys.exit(1)

try:
    from transformers import AutoTokenizer
    print("[OK] Transformers")
except Exception as e:
    print(f"[FAIL] Transformers: {e}")
    sys.exit(1)

try:
    from ctransformers import AutoModelForCausalLM
    print("[OK] CTransformers")
except Exception as e:
    print(f"[FAIL] CTransformers: {e}")
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
    print("[OK] SentenceTransformers")
except Exception as e:
    print(f"[FAIL] SentenceTransformers: {e}")
    sys.exit(1)

print("\n[SUCCESS] All dependencies working!")
```

Run it:
```powershell
python test_deps.py
```

## If All Else Fails

### Nuclear Option: Fresh Start

```powershell
# Delete everything
Remove-Item -Recurse -Force venv, models, __pycache__, core\__pycache__
Remove-Item nexuzy.db, nexuzy_publisher.log -ErrorAction SilentlyContinue

# Start fresh
python -m venv venv
.\venv\Scripts\Activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## Quick Fix Command (Copy-Paste)

```powershell
# One-liner to fix everything
deactivate; Remove-Item -Recurse -Force venv; python -m venv venv; .\venv\Scripts\Activate; python -m pip install --upgrade pip; pip install -r requirements.txt; python test_deps.py
```

## Summary

The main issues were:
1. **NumPy 2.x** - Incompatible with PyTorch
2. **Dependency versions** - Mismatched versions
3. **Windows encoding** - Unicode symbols in logs
4. **Wrong GGUF library** - Using llama-cpp-python instead of ctransformers

All fixed now! Just recreate your venv and install from requirements.txt.
