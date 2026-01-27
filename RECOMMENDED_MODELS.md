# Recommended AI Models for Nexuzy Publisher Desk

## Issue: TinyLlama 1.1B Not Working

TinyLlama (1.1B parameters) is **too small** for complex article generation. It works for simple completions but fails for:
- Long-form content (800-1200 words)
- Complex prompts with multiple instructions
- Structured article generation

---

## ✅ Recommended Models (Working)

### 1. **Phi-2 (2.7B) - BEST CHOICE**

**Why**: Perfect balance of quality and speed for CPU-only generation

**Download**:
```bash
cd models
wget https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf
# Or Q5 for better quality:
wget https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q5_K_M.gguf
```

**Specs**:
- Size: Q4_K_M = 1.6GB, Q5_K_M = 1.9GB
- RAM needed: 4-6GB
- Generation speed: 15-30 seconds per article
- Quality: ⭐⭐⭐⭐⭐ Excellent

**Update code**:
```python
# In main.py or wherever DraftGenerator is initialized:
from core.ai_draft_generator import DraftGenerator

draft_generator = DraftGenerator(
    db_path='nexuzy.db',
    model_name='models/phi-2.Q4_K_M.gguf'  # Change this line
)
```

---

### 2. **Mistral-7B-Instruct (7B) - HIGH QUALITY**

**Why**: Best quality for news articles, professional journalism

**Download**:
```bash
cd models
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

**Specs**:
- Size: Q4_K_M = 4.4GB
- RAM needed: 8-12GB
- Generation speed: 30-90 seconds per article
- Quality: ⭐⭐⭐⭐⭐ Professional grade

**Update code**:
```python
draft_generator = DraftGenerator(
    db_path='nexuzy.db',
    model_name='models/mistral-7b-instruct-v0.2.Q4_K_M.gguf'
)
```

---

### 3. **Llama-3-8B-Instruct (8B) - BEST OVERALL**

**Why**: Latest Meta model, excellent instruction following

**Download**:
```bash
cd models
wget https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF/resolve/main/llama-3-8b-instruct.Q4_K_M.gguf
```

**Specs**:
- Size: Q4_K_M = 4.9GB
- RAM needed: 8-12GB  
- Generation speed: 30-90 seconds
- Quality: ⭐⭐⭐⭐⭐ State-of-the-art

---

## ⚠️ NOT Recommended

### TinyLlama 1.1B ❌
- Too small for article generation
- Generates empty or very short output
- Only good for simple completions

---

## Quick Fix Steps

### Step 1: Test Current Model
```bash
python test_model.py
```

This will show if your model generates text at all.

### Step 2: Download Better Model

For **fastest setup** (recommended):
```bash
cd models
wget https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf
```

For **best quality**:
```bash
cd models
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### Step 3: Update Code

**Option A**: Edit `main.py` directly:
```python
# Find this line (around line 50-60):
self.draft_generator = DraftGenerator(self.db_path)

# Change to:
self.draft_generator = DraftGenerator(
    self.db_path,
    model_name='models/phi-2.Q4_K_M.gguf'  # Or mistral-7b-instruct-v0.2.Q4_K_M.gguf
)
```

**Option B**: Just rename the downloaded model:
```bash
cd models
mv phi-2.Q4_K_M.gguf tinyllama-1.1b-chat-v1.0.Q8_0.gguf
```

(App will auto-detect it)

### Step 4: Test Article Generation
```bash
python main.py
```

1. Go to AI Editor
2. Select news
3. Click "🤖 Complete AI Rewrite"
4. Wait 15-30 seconds
5. Should generate 400-800 words

---

## Performance Comparison

| Model | Size | RAM | Speed | Quality | Recommendation |
|-------|------|-----|-------|---------|----------------|
| TinyLlama 1.1B | 700MB | 2GB | 5s | ⭐ | ❌ Too small |
| Phi-2 2.7B | 1.6GB | 4GB | 20s | ⭐⭐⭐⭐⭐ | ✅ **Best choice** |
| Mistral-7B | 4.4GB | 8GB | 45s | ⭐⭐⭐⭐⭐ | ✅ High quality |
| Llama-3-8B | 4.9GB | 8GB | 60s | ⭐⭐⭐⭐⭐ | ✅ Best overall |

---

## Troubleshooting

### Model not generating text?
```bash
python test_model.py
```

If test fails:
1. Model file corrupted → Re-download
2. Not enough RAM → Use smaller quantization (Q3 or Q4)
3. Model too small → Switch to Phi-2 or Mistral

### Generation too slow?
- Use Q4_K_M quantization (faster)
- Reduce `max_new_tokens` to 800
- Use Phi-2 instead of Mistral/Llama

### Quality not good enough?
- Use Mistral-7B or Llama-3-8B
- Use Q5_K_M quantization (better quality)
- Increase `temperature` to 0.8 for more creativity

---

## Manual Model Installation

If wget doesn't work:

1. Go to: https://huggingface.co/TheBloke/phi-2-GGUF/tree/main
2. Click on `phi-2.Q4_K_M.gguf`
3. Click download button
4. Move file to `models/` folder
5. Rename or update code to match filename

---

**Last Updated**: January 27, 2026
**Status**: TinyLlama confirmed NOT WORKING for article generation
**Solution**: Use Phi-2 (2.7B) or larger
