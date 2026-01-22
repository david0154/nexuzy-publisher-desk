# Vision AI Setup Guide

## What is Vision AI?

David AI Vision uses the **CLIP model** (2.3GB) to detect:
- ✅ Watermarks in news images
- ✅ Logos and brand marks
- ✅ Copyright overlays
- ✅ Text on images
- ✅ Image quality assessment

## Installation

```powershell
# Install Vision AI dependencies
pip install torch transformers pillow
```

## First Time Usage

When you first use Vision AI, it will automatically download the CLIP model (~2.3GB):

```
Loading Vision AI model: openai/clip-vit-large-patch14
Downloading model... (2.3GB)
[OK] Vision AI model loaded successfully
```

## How to Use

### 1. Open Vision AI Tab
- Click "🖼️ Vision AI" in the sidebar

### 2. Upload Image
- Click "📁 Upload & Analyze Image"
- Select any image (PNG, JPG, JPEG, BMP, GIF)

### 3. Scan for Watermarks
- Click "🔍 Scan for Watermarks"
- Results show:
  - **Watermark Detected**: Yes/No
  - **Confidence**: 85.3%
  - **Detailed Scores**: Individual detection scores

## Example Results

```json
{
  "watermark_detected": true,
  "confidence": "87.45%",
  "watermark_score": "87.45%",
  "clean_score": "12.55%",
  "status": "Watermark detected",
  "detailed_scores": {
    "watermark": "87.45%",
    "logo": "65.32%",
    "text_overlay": "45.21%",
    "copyright_mark": "34.12%"
  }
}
```

## Features

### Watermark Detection
- Detects Getty Images watermarks
- Detects Shutterstock watermarks
- Detects custom logo overlays
- Detects text watermarks

### Image Quality Analysis
- Professional vs amateur photo
- Sharp vs blurry
- Proper exposure check
- Composition quality

## Model Details

- **Model**: CLIP ViT-Large-Patch14
- **Size**: 2.3GB
- **Provider**: OpenAI
- **Repository**: `openai/clip-vit-large-patch14`
- **Capabilities**: Zero-shot image classification

## Troubleshooting

### Model not downloading?

```powershell
# Manual download
python -c "from transformers import CLIPModel; CLIPModel.from_pretrained('openai/clip-vit-large-patch14')"
```

### Out of memory?

CLIP requires ~4GB RAM. If you have limited memory:
- Close other applications
- Use smaller images (resize to 1024x1024 max)
- Consider using CPU mode

### Slow performance?

First analysis takes longer (~10-15 seconds):
- Model loads into memory
- Subsequent analyses are faster (~2-3 seconds)

## Use Cases

1. **News Article Images**
   - Check if scraped images have watermarks
   - Filter out copyrighted stock photos
   - Ensure clean images for publishing

2. **Quality Control**
   - Verify image quality before publishing
   - Detect low-quality or blurry images
   - Check for proper composition

3. **Copyright Compliance**
   - Detect Getty Images watermarks
   - Identify Shutterstock logos
   - Find copyright notices

## Performance

- **First load**: 15-20 seconds (model download)
- **Model loading**: 5-10 seconds
- **Per image analysis**: 2-3 seconds
- **Batch processing**: ~2 seconds per image

## Storage Requirements

- Model cache: `~/.cache/huggingface/`
- CLIP model: 2.3GB
- Total: ~2.5GB with cache
