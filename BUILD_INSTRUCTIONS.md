# 🚀 Build Instructions - Nexuzy Publisher Desk

## 📋 Prerequisites

### Required Software
1. **Python 3.8+**
2. **PyInstaller** - `pip install pyinstaller`
3. **Inno Setup 6.x** - [Download](https://jrsoftware.org/isinfo.php)

### AI Models (~7.6GB)

Download to `models/` directory:

1. **David AI Writer 7B** (4.1GB)
   - File: `models/david-ai-writer-7b.gguf`
   - Download: [Llama-2-7B-Chat GGUF](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF)

2. **David AI Translator** (1.2GB)
   - Dir: `models/nllb-200-distilled-600M/`
   - Download: `git clone https://huggingface.co/facebook/nllb-200-distilled-600M`

3. **David AI Vision** (2.3GB)
   - Dir: `models/vision-watermark-detector/`
   - Download: `git clone https://huggingface.co/openai/clip-vit-base-patch32`

4. **David AI Matcher** (80MB)
   - Dir: `models/all-MiniLM-L6-v2/`
   - Download: `git clone https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2`

## 🔨 Build Steps

### 1. Build Executable
```bash
build_exe.bat
```

Output: `dist/NexuzyPublisher/NexuzyPublisher.exe`

### 2. Create Installer

1. Open **Inno Setup Compiler**
2. Open `setup.iss`
3. Click **Build** → **Compile**
4. Wait 10-20 minutes (7.6GB models)

Output: `Output/NexuzyPublisherSetup.exe` (~7.75GB)

## 📂 Directory Structure

```
nexuzy-publisher-desk/
├── main.py
├── core/
├── resources/
│   ├── icon.ico
│   └── logo.png
├── models/
│   ├── david-ai-writer-7b.gguf (4.1GB)
│   ├── nllb-200-distilled-600M/ (1.2GB)
│   ├── vision-watermark-detector/ (2.3GB)
│   └── all-MiniLM-L6-v2/ (80MB)
├── nexuzy_publisher.spec
├── setup.iss
└── build_exe.bat
```

## 📊 Size Breakdown

| Component | Size |
|-----------|------|
| Application | ~150MB |
| AI Writer 7B | 4.1GB |
| AI Translator | 1.2GB |
| AI Vision | 2.3GB |
| AI Matcher | 80MB |
| **Total** | **~7.75GB** |

## 🐛 Troubleshooting

### Build Fails
- Install dependencies: `pip install -r requirements.txt`
- Update PyInstaller: `pip install --upgrade pyinstaller`

### Models Not Found
- Check `models/` directory structure
- Verify all 4 models downloaded

### Installer Too Large
- Use 7-Zip to split: `7z a -v2g Setup.7z Output/NexuzyPublisherSetup.exe`

## ✅ Checklist

- [ ] Python 3.8+ installed
- [ ] PyInstaller installed
- [ ] Inno Setup installed
- [ ] All 4 AI models downloaded (~7.6GB)
- [ ] Models in correct directories
- [ ] Icon/resources in place
- [ ] Executable built and tested
- [ ] Installer created

---

**Build Time:** ~20-30 minutes total
**Disk Space:** 20GB+ free recommended
