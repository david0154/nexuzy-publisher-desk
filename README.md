# Nexuzy Publisher Desk

**AI-Powered News Publishing Platform**

## Features

✅ **RSS Feed Management** - Fetch news from multiple sources  
✅ **David AI 2B** - News similarity matching (80MB)  
✅ **David AI Writer 7B** - Article generation (4.1GB)  
✅ **David AI Translator** - 200+ languages (1.2GB)  
✅ **David AI Vision** - Image watermark detection (2.3GB)  
✅ **WordPress Integration** - Auto-publish to WordPress  
✅ **Modern UI** - Clean, colorful interface  

## Installation

```powershell
# Clone repository
git clone https://github.com/david0154/nexuzy-publisher-desk.git
cd nexuzy-publisher-desk

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## Requirements

- Python 3.8+
- `feedparser` - RSS feed parsing
- `beautifulsoup4` - HTML parsing
- `Pillow` - Image handling for logo/icon
- AI models (optional, will download on first use)

## Usage

### 1. Add RSS Feeds
- Go to **RSS Feeds** tab
- Enter feed name, URL, and category
- Click **Add Feed**

### 2. Fetch News
- Go to **News Queue**
- Click **Fetch Latest News from RSS**
- News articles will be fetched and stored

### 3. Vision AI
- Go to **Vision AI** tab
- Upload news article images
- Detect watermarks automatically

### 4. Translate Articles
- Select article from queue
- Choose target language
- Click **Translate Now**

### 5. Publish to WordPress
- Configure WordPress credentials in **WordPress** tab
- Test connection
- Publish articles directly

## File Structure

```
nexuzy-publisher-desk/
├── main.py              # Main application
├── core/
│   ├── rss_manager.py   # RSS fetching
│   ├── news_matcher.py  # News similarity
│   ├── translator.py    # Translation
│   └── wordpress_api.py # WordPress integration
├── resources/
│   ├── logo.png         # App logo (40x40)
│   └── icon.ico         # Window icon
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## AI Models

All AI models are named **David AI** with NO repository paths shown:

- **David AI 2B** - News matching
- **David AI Writer 7B** - Content generation
- **David AI Translator** - Multi-language
- **David AI Vision** - Image analysis

## License

MIT License
