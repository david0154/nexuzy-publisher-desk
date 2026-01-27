# Model Download Guide

## Quick Start - Download AI Models

Nexuzy Publisher Desk requires AI models to generate high-quality articles. This guide shows you how to download them.

## 📥 Required Models

### 1. Mistral-7B-Instruct GGUF (Main AI Writer)

**Size:** 4.1 GB  
**Purpose:** Generates news article drafts  
**Format:** GGUF Q4_K_M (Optimized for CPU)

### 2. NLLB-200 Translation Model (Auto-downloads)

**Size:** 800 MB  
**Purpose:** Multi-language translation  
**Status:** Auto-downloads on first use ✅

---

## 💻 Download Methods

### Method 1: Browser Download (Easiest)

1. **Visit HuggingFace:**
   ```
   https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/blob/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
   ```

2. **Click "Download" button** (top right)

3. **Wait for download** (~4.1 GB, may take 10-30 minutes depending on speed)

4. **Move file to models folder:**
   ```
   nexuzy-publisher-desk/
   └── models/
       └── mistral-7b-instruct-v0.2.Q4_K_M.gguf  ← Place here
   ```

### Method 2: Command Line (wget)

```bash
# Create models directory
mkdir -p models
cd models

# Download model
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Verify download
ls -lh mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### Method 3: HuggingFace CLI (Advanced)

```bash
# Install huggingface-cli
pip install huggingface-hub

# Download model
huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF \
  mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  --local-dir models/ \
  --local-dir-use-symlinks False
```

---

## 📁 File Structure After Download

```
nexuzy-publisher-desk/
├── main.py
├── requirements.txt
├── models/
│   ├── mistral-7b-instruct-v0.2.Q4_K_M.gguf  ← 4.1 GB
│   └── (other models auto-downloaded)
├── core/
├── ui/
└── ...
```

---

## ✅ Verify Model Installation

### Run Application Test

```bash
python main.py
```

**Expected Output:**
```
2026-01-27 12:38:34 - __main__ - INFO - Starting Nexuzy Publisher Desk
...
2026-01-27 12:38:59 - core.ai_draft_generator - INFO - Loading GGUF model from: models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
2026-01-27 12:39:02 - core.ai_draft_generator - INFO - ✅ Mistral-7B-GGUF Q4_K_M loaded successfully (4.1GB)
2026-01-27 12:39:02 - core.ai_draft_generator - INFO - ✅ AI Writer LOADED - Full AI generation enabled
```

### If Model Not Found:

```
2026-01-27 12:39:07 - core.ai_draft_generator - WARNING - ⚠️  GGUF model not found. Checked paths:
2026-01-27 12:39:07 - core.ai_draft_generator - WARNING -   - models/TheBloke_Mistral-7B-Instruct-v0.2-GGUF/mistral-7b-instruct-v0.2.Q4_K_M.gguf
2026-01-27 12:39:07 - core.ai_draft_generator - WARNING -   - models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
2026-01-27 12:39:07 - core.ai_draft_generator - WARNING - 📥 Download from: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/...
2026-01-27 12:39:07 - core.ai_draft_generator - WARNING - 💡 Place in: models/ folder
2026-01-27 12:39:07 - core.ai_draft_generator - WARNING - ✅ App continues in SAFE MODE with template generation
```

**Solution:** Download model and place in `models/` folder

---

## 🔒 SAFE MODE (No Model Required)

If the AI model is not available, the app automatically switches to **SAFE MODE**:

### What Works in SAFE MODE:

✅ RSS feed management  
✅ News fetching and matching  
✅ Template-based article generation  
✅ Manual article writing  
✅ WYSIWYG editor  
✅ Translation (NLLB-200 auto-downloads)  
✅ WordPress publishing  

### What Requires AI Model:

❌ Full AI-powered article generation  
❌ Advanced content rewriting  
❌ AI-based sentence improvement (uses fallback)  

### SAFE MODE Article Generation:

Safe mode generates articles using templates:

```
<h2>Introduction</h2>
<p>[Headline] - This [category] development has gained significant attention...</p>

<h2>Background</h2>
<p>This story relates to recent developments in [focus]...</p>

<h2>Key Details</h2>
<p>[Summary content]</p>

<h2>Analysis</h2>
<p>Industry experts are closely monitoring this situation...</p>

<em>Note: This article was generated using template-based content generation. 
For full AI-powered drafts, download the Mistral-7B GGUF model.</em>
```

**You can still manually edit and improve these articles in the WYSIWYG editor!**

---

## 🐛 Troubleshooting

### Problem: Download is very slow

**Solution:**
- Use a download manager (IDM, Free Download Manager)
- Try different time of day (less network congestion)
- Use HuggingFace CLI with resume capability

### Problem: "File corrupted" error

**Solution:**
1. Delete partial download
2. Re-download completely
3. Verify file size: Should be exactly **4,368,438,464 bytes** (4.1 GB)

### Problem: "Out of memory" when loading model

**Solution:**
- Close other applications
- Minimum 8GB RAM required (16GB recommended)
- Use Q4_K_M quantization (already optimized)

### Problem: Model loads but generation is very slow

**Solution:**
- Check CPU usage (should use 4 cores)
- Close background applications
- Consider Q3_K_S quantization (smaller, faster, slightly lower quality)

### Problem: ctransformers not installed

**Solution:**
```bash
pip install ctransformers
```

If build fails on Windows:
```bash
pip install ctransformers --no-build-isolation
```

---

## 📦 Alternative Models (Advanced Users)

### Smaller Models (Less RAM, Faster)

**Mistral-7B Q3_K_S** (2.9 GB)
```
https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/blob/main/mistral-7b-instruct-v0.2.Q3_K_S.gguf
```

**Mistral-7B Q2_K** (2.2 GB)
```
https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/blob/main/mistral-7b-instruct-v0.2.Q2_K.gguf
```

### Larger Models (More RAM, Better Quality)

**Mistral-7B Q5_K_M** (5.1 GB)
```
https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/blob/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf
```

**Mistral-7B Q6_K** (5.9 GB)
```
https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/blob/main/mistral-7b-instruct-v0.2.Q6_K.gguf
```

**Note:** Change filename in `core/ai_draft_generator.py` (line 24) if using alternative model.

---

## ❓ FAQ

**Q: Do I need internet after downloading models?**  
A: No! Once downloaded, everything runs 100% offline.

**Q: Can I use GPU instead of CPU?**  
A: Yes, but requires llama-cpp-python with CUDA support. Current version optimized for CPU.

**Q: How long does article generation take?**  
A: 30-60 seconds per article on modern CPU (4+ cores).

**Q: Can I use different AI models?**  
A: Yes, but requires code modifications. Mistral-7B is recommended for news generation.

**Q: Is SAFE MODE good enough?**  
A: For basic workflows, yes! You can manually edit articles. Full AI model recommended for volume.

---

## 👍 Recommended Setup

**For Best Experience:**

1. Download **Mistral-7B Q4_K_M** (4.1 GB) - balanced quality/speed
2. Let NLLB-200 auto-download on first translation
3. 16GB RAM for smooth operation
4. Quad-core CPU or better

**For Limited Resources:**

1. Use **SAFE MODE** (no model download)
2. Manually write/edit articles in WYSIWYG editor
3. Still get full translation and publishing features
4. Works on 8GB RAM, dual-core CPU

---

## 📞 Support

If you encounter issues:

1. Check [GitHub Issues](https://github.com/david0154/nexuzy-publisher-desk/issues)
2. Review `nexuzy_publisher.log` file
3. Open a new issue with error logs

---

**Ready to generate AI-powered articles?** Download the model and start publishing! 🚀
