# Nexuzy Publisher Desk - Complete AI News Platform

## 🚀 Features

- **RSS Feed Management** - Fetch news from multiple sources with images
- **AI News Verification** - Multi-source verification with credibility scoring
- **Complete Article Rewriting** - 800-1500 word professional articles
- **Image Extraction** - Automatic image URLs from RSS feeds
- **News Grouping** - AI-powered similar news detection
- **200+ Language Translation** - NLLB-200 model integration
- **WordPress Publishing** - Direct posting with ads injection
- **Vision AI** - Watermark detection in images
- **Ads Management** - Header, content, footer ads support

## 📦 Installation

1. **Clone repository:**
```bash
git clone https://github.com/david0154/nexuzy-publisher-desk.git
cd nexuzy-publisher-desk
```

2. **Create virtual environment:**
```bash
python -m venv venv
```

3. **Activate virtual environment:**

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## 🗄️ Database Setup

### Fresh Installation:
```bash
# Simply run the application
python main.py
```

### Existing Database Migration:
```bash
# If you have old database, run migration first
python migrate_database.py

# Then run the application
python main.py
```

### Fresh Start (Delete old database):
```bash
# Delete old database
del nexuzy.db  # Windows
rm nexuzy.db   # Linux/Mac

# Run application (creates new DB automatically)
python main.py
```

## 🤖 AI Models

### Required Dependencies:
```bash
# Basic dependencies
pip install feedparser beautifulsoup4 requests

# AI models
pip install sentence-transformers ctransformers transformers torch pillow
```

### Models Used:
1. **David AI 2B** (80MB) - News similarity matching
2. **David AI Writer 7B** (4.1GB) - Article generation (GGUF)
3. **David AI Translator** (1.2GB) - NLLB-200 translation
4. **David AI Vision** (2.3GB) - Watermark detection

## 📝 Usage

1. **Add RSS Feeds** - Configure news sources
2. **Fetch News** - Get latest news with images and verification
3. **AI Rewrite** - Generate complete professional articles
4. **Translate** - Convert to 200+ languages
5. **Publish** - Post to WordPress with ads

## 🔧 Troubleshooting

### "table news_queue has no column named image_url" error:

**Solution 1 - Fresh database (Recommended):**
```bash
del nexuzy.db
python main.py
```

**Solution 2 - Migrate existing:**
```bash
python migrate_database.py
python main.py
```

### Models not loading:
- Ensure all dependencies installed
- Check internet connection (first run downloads models)
- Template mode works without models

## 📄 License

MIT License

## 👨‍💻 Author

Developed by david0154
