# 🚀 SPEED FIX: Switch to Faster Model

## Problem
If article generation takes **10-15 minutes**, your CPU is too slow for Mistral-7B (4GB model).

## Solution: Use TinyLlama (1.1GB - 10x Faster!)

### Step 1: Download TinyLlama

**Option A: Direct Download**
```bash
# Download from browser:
https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q8_0.gguf

# Move to models folder:
mv tinyllama-1.1b-chat-v1.0.Q8_0.gguf models/
```

**Option B: Use wget/curl**
```bash
cd models
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q8_0.gguf
```

### Step 2: Update Settings

Edit `main.py` or wherever DraftGenerator is created:

**Before:**
```python
self.draft_generator = DraftGenerator(
    db_path=self.db_path,
    model_name='models/mistral-7b-instruct-v0.2.Q4_K_M.gguf'  # SLOW!
)
```

**After:**
```python
self.draft_generator = DraftGenerator(
    db_path=self.db_path,
    model_name='models/tinyllama-1.1b-chat-v1.0.Q8_0.gguf'  # FAST!
)
```

### Step 3: Restart App

```bash
python main.py
```

## Expected Results

| Model | Size | Generation Time | Quality |
|-------|------|----------------|----------|
| **Mistral-7B** | 4GB | 10-15 min (slow CPU) | Excellent |
| **TinyLlama** | 1.1GB | **30-40 seconds** | Very Good |

## Performance Comparison

**Mistral-7B (4GB):**
- ❌ 10-15 minutes on slow CPU
- ✅ Excellent writing quality
- ❌ High CPU/RAM usage

**TinyLlama (1.1GB):**
- ✅ **30-40 seconds** even on slow CPU
- ✅ Very good writing quality
- ✅ Low CPU/RAM usage
- ✅ Perfect for news articles

## Why TinyLlama?

1. **10x smaller** (1.1GB vs 4GB)
2. **10x faster** on CPU
3. **Same article structure** (600 words)
4. **Still professional** quality
5. **Works on any laptop**

## Alternative: Reduce max_new_tokens

If you want to keep Mistral but make it faster:

Edit `core/ai_draft_generator.py` line 414:

**Before:**
```python
max_new_tokens=600,  # 10-15 minutes
```

**After:**
```python
max_new_tokens=300,  # 5-7 minutes (shorter articles)
```

## Need Help?

Check your CPU specs:
```bash
# Windows
wmic cpu get name

# Linux/Mac
lscpu | grep "Model name"
```

**Recommended minimum:**
- Intel i5 or AMD Ryzen 5 (or better)
- 8GB RAM
- For older CPUs: Use TinyLlama!
