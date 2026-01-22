# Nexuzy Publisher Desk

**AI-Powered News Publishing Platform**

## ✅ Complete Feature List

### 🤖 David AI Models (No Repository Paths Shown)

- ✅ **David AI 2B** (80MB) - News Similarity Matching  
- ✅ **David AI Writer 7B** (4.1GB) - Article Generation  
- ✅ **David AI Translator** (1.2GB) - 200+ Languages  
- ✅ **David AI Vision** (2.3GB) - Watermark Detection  

### 📡 RSS Feed Management
- ✅ Add feeds with name, URL, and category
- ✅ Fetch actual news using `feedparser`
- ✅ Parse headlines, summaries, URLs
- ✅ Category-based organization

### 🔍 Vision AI - Watermark Detection
- ✅ Uses CLIP model (openai/clip-vit-large-patch14)
- ✅ Detects watermarks in images
- ✅ Identifies logos and copyright marks
- ✅ Text overlay detection
- ✅ Image quality analysis

### 🌐 Translation (200+ Languages)
- ✅ Powered by NLLB-200 model
- ✅ Major languages: Spanish, French, German, Hindi, Bengali, Chinese, Japanese, Arabic, and 192+ more
- ✅ High-quality neural translation

### 🔗 WordPress Integration
- ✅ Direct publishing to WordPress
- ✅ Connection testing
- ✅ Draft and publish support

### 💾 Database
- ✅ SQLite database
- ✅ Multi-workspace support
- ✅ Clean schema with migrations

## 🚀 Quick Start

### 1. Delete Old Database (IMPORTANT!)

```powershell
# Stop the app if running
# Delete old database
Remove-Item nexuzy.db
```

### 2. Install Dependencies

```powershell
# Core dependencies
pip install -r requirements.txt

# Vision AI (optional but recommended)
pip install torch transformers pillow
```

### 3. Run Application

```powershell
python main.py
```

## 📦 Installation

```powershell
# Clone repository
git clone https://github.com/david0154/nexuzy-publisher-desk.git
cd nexuzy-publisher-desk

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

## 📋 Dependencies

### Required
- `feedparser` - RSS feed parsing
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests
- `Pillow` - Image handling

### Optional (for AI features)
- `torch` - PyTorch (for Vision AI and Translation)
- `transformers` - Hugging Face models
- `sentence-transformers` - News matching
- `sentencepiece` - Translation tokenizer

## 🎯 Usage Guide

### Adding RSS Feeds

1. Click **📡 RSS Feeds** in sidebar
2. Enter:
   - **Feed Name**: `TechCrunch`
   - **RSS URL**: `https://techcrunch.com/feed/`
   - **Category**: `Technology`
3. Click **Add Feed**

### Fetching News

1. Go to **📰 News Queue**
2. Click **Fetch Latest News from RSS**
3. Wait for completion: "Fetched X new articles!"
4. News appears in list

### Using Vision AI

1. Go to **🖼️ Vision AI**
2. Click **📁 Upload & Analyze Image**
3. Select an image
4. View watermark detection results:
   - Watermark detected: Yes/No
   - Confidence: 87.45%
   - Detailed scores for logos, text, copyright marks

### Translation

1. Go to **🌐 Translations**
2. Select target language (200+ options)
3. Click **Translate Now**
4. View translated content in preview

## 🔧 Troubleshooting

### Database Errors

**Error**: `no such column: feed_name`

**Fix**:
```powershell
rm nexuzy.db  # Delete old database
python main.py  # Restart - new DB created automatically
```

### RSS Not Working

**Error**: `RSS Manager module required`

**Fix**:
```powershell
pip install feedparser beautifulsoup4 requests
```

### Vision AI Not Loading

**Error**: `Vision AI requires: pip install torch transformers pillow`

**Fix**:
```powershell
pip install torch transformers pillow
```

First use will download CLIP model (~2.3GB)

### Logo/Icon Not Showing

**Fix**: Create resources folder:
```powershell
mkdir resources
# Add files:
# resources/logo.png (40x40 pixels)
# resources/icon.ico (ICO format)
```

## 📁 Project Structure

```
nexuzy-publisher-desk/
├── main.py                 # Main application
├── core/
│   ├── rss_manager.py      # RSS fetching with feedparser
│   ├── vision_ai.py        # CLIP-based watermark detection
│   ├── news_matcher.py     # News similarity matching
│   ├── translator.py       # NLLB-200 translation
│   ├── ai_draft_generator.py
│   └── wordpress_api.py
├── resources/
│   ├── logo.png           # App logo (40x40)
│   └── icon.ico           # Window icon
├── requirements.txt        # Dependencies
├── fix_database.py        # Database migration tool
├── QUICKSTART.md          # Quick fix guide
├── VISION_AI_SETUP.md     # Vision AI setup guide
└── README.md              # This file
```

## 🎨 Features in Settings

All AI models shown as **David AI** with clean names:

```
✅ David AI 2B - News Similarity Matching (80MB)
✅ David AI Writer 7B - Article Generation (4.1GB)  
✅ David AI Translator - 200+ Languages Translation (1.2GB)
✅ David AI Vision - Image Watermark Detection (2.3GB)
```

**NO repository paths shown!**

## 🌍 Supported Translation Languages

David AI Translator supports 200+ languages including:

- **European**: Spanish, French, German, Italian, Portuguese, Russian, Polish, Dutch, Greek, Swedish, etc.
- **Asian**: Hindi, Bengali, Tamil, Telugu, Chinese (Simplified/Traditional), Japanese, Korean, Thai, Vietnamese, Indonesian, etc.
- **Middle Eastern**: Arabic, Persian, Hebrew, Turkish, Urdu, etc.
- **African**: Swahili, Yoruba, Hausa, Zulu, Afrikaans, Amharic, etc.
- **And 150+ more!**

## 📊 Performance

- **RSS Fetching**: ~2-5 seconds per feed
- **Vision AI Analysis**: ~2-3 seconds per image (after model load)
- **Translation**: ~1-2 seconds per article
- **News Matching**: ~0.5 seconds per article

## 🔐 WordPress Publishing

1. Configure in **🔗 WordPress** tab:
   - Site URL
   - Username
   - Application Password (not regular password!)
2. Click **Test Connection**
3. Click **Publish Sample Article**

## 📝 License

MIT License

## 🤝 Contributing

Pull requests welcome!

## 📧 Support

For issues, please create a GitHub issue.

---

**Made with ❤️ using Python, Tkinter, and AI**
