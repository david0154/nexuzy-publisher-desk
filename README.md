<div align="center">

![Nexuzy Publisher Desk Logo](resources/logo.png)

# Nexuzy Publisher Desk

### 🚀 **AI-Powered Offline News Publishing Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/david0154/nexuzy-publisher-desk)
[![Status](https://img.shields.io/badge/status-Active-success)](https://github.com/david0154/nexuzy-publisher-desk)

**Automate your entire news publishing workflow with AI - from RSS feeds to WordPress - completely offline!**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

---

</div>

## 📖 Overview

Nexuzy Publisher Desk is a complete AI-powered news publishing platform that runs entirely **offline on your local machine**. It automates the entire workflow from RSS feed monitoring to WordPress publishing, with human editorial control at every critical step.

### ✨ Why Nexuzy Publisher Desk?

- 🔒 **100% Offline** - All AI models run locally, no data leaves your computer
- 🤖 **AI-Powered** - Uses GGUF quantized models (Mistral-7B, NLLB-200)
- 📰 **Complete Workflow** - RSS → Matching → Scraping → Draft → Edit → Translate → Publish
- ✅ **Human Control** - You verify, edit, and approve everything before publishing
- 🌐 **Multi-Language** - Built-in translation to 200+ languages
- 💾 **Lightweight** - Only ~5GB AI models (GGUF optimized for CPU)
- 🎨 **Simple UI** - Clean Tkinter interface, no complex setup

---

## 🎯 Features

### Core Capabilities

| Phase | Feature | Description |
|-------|---------|-------------|
| 📡 **RSS Management** | Multi-feed monitoring | Add unlimited RSS feeds with categories and priorities |
| 🔍 **News Matching** | AI similarity detection | Groups related news from different sources using embeddings |
| ✅ **Verification** | Multi-source validation | Requires 3+ independent sources for authenticity |
| 🕷️ **Content Scraping** | Safe fact extraction | Extracts verifiable facts while respecting robots.txt |
| ✍️ **AI Draft Generation** | Mistral-7B GGUF | Generates fact-based drafts from scraped content |
| 📝 **Human Editor** | Full editorial control | Edit, verify, and approve before publishing |
| 🌍 **Translation** | 200+ languages | NLLB-200 GGUF model for accurate translations |
| 🚀 **WordPress Publishing** | REST API integration | Direct publishing with categories and tags |

### AI Models (GGUF Format - CPU Optimized)

```
📦 Total Size: ~5GB (70% smaller than standard models)

├── Mistral-7B-Instruct-GGUF (Q4_K_M) - 4.1GB
│   └── Purpose: News article draft generation
│   └── Format: GGUF quantized (llama.cpp compatible)
│
├── NLLB-200-Distilled-GGUF (Q4_K_M) - 800MB  
│   └── Purpose: Multi-language translation
│   └── Languages: 200+ supported
│
└── SentenceTransformer (all-MiniLM-L6-v2) - 80MB
    └── Purpose: News similarity matching
    └── Embeddings: Semantic search
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.9+** (recommended: 3.10 or 3.11)
- **8GB+ RAM** (16GB recommended for smooth operation)
- **~10GB disk space** (5GB models + 5GB workspace)
- **Internet** (first run only - to download AI models)

### Step 1: Clone Repository

```bash
git clone https://github.com/david0154/nexuzy-publisher-desk.git
cd nexuzy-publisher-desk
```

### Step 2: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 3: Run Application

```bash
python main.py
```

**First Run:** Models will auto-download (~5GB, takes 15-20 minutes)

**Subsequent Runs:** Instant startup from cached models

---

## ⚡ Quick Start

### 1️⃣ Create Workspace

```
1. Click "+ New Workspace"
2. Enter name (e.g., "Tech News")
3. Workspace created ✓
```

### 2️⃣ Add RSS Feeds

```
1. Click "📡 RSS Manager"
2. Click "+ Add Feed"
3. Enter RSS URL (e.g., https://feeds.bbci.co.uk/news/rss.xml)
4. Select category and language
5. Save ✓
```

### 3️⃣ Fetch & Process News

```
1. Go to "📰 News Queue"
2. Click "🔄 Fetch Latest News" (imports from all feeds)
3. Click "🔍 Match & Verify" (AI groups similar headlines)
4. Select news item
5. Click "📄 Generate Draft" (AI writes article)
```

### 4️⃣ Edit & Publish

```
1. Go to "✏️ Editor"
2. Review AI-generated draft
3. Edit headline and body
4. Check ✓ "Edited by Human" (required)
5. Click "💾 Save Draft"
6. Click "🌐 Translate" (optional - 200+ languages)
7. Click "📤 Send to WordPress"
```

### 5️⃣ Configure WordPress

```
1. Go to "🌐 WordPress"
2. Enter:
   - Site URL: https://yoursite.com
   - Username: your-wp-username
   - App Password: (generate from WordPress)
3. Click "🔗 Test Connection"
4. Click "💾 Save" when test succeeds
```

**See [QUICK_START.md](QUICK_START.md) for detailed walkthrough**

---

## 📚 Documentation

### User Guides

- 📘 [**QUICK_START.md**](QUICK_START.md) - 5-minute setup guide
- 📗 [**FEATURES.md**](FEATURES.md) - Complete feature documentation
- 📕 [**WORDPRESS_SETUP.md**](WORDPRESS_SETUP.md) - WordPress REST API configuration
- 📙 [**AI_MODELS.md**](AI_MODELS.md) - AI model details and customization

### Developer Guides

- 🔧 [**SETUP.md**](SETUP.md) - Development environment setup
- 🏗️ [**ARCHITECTURE.md**](ARCHITECTURE.md) - System architecture overview
- 📦 [**DEPLOYMENT.md**](DEPLOYMENT.md) - Building EXE and distribution
- 🤝 [**CONTRIBUTING.md**](CONTRIBUTING.md) - Contribution guidelines

---

## 🛠️ Technology Stack

### Backend
- **Python 3.9+** - Core application
- **SQLite** - Local database
- **llama-cpp-python** - GGUF model inference (CPU-optimized)
- **Transformers** - SentenceTransformer embeddings
- **BeautifulSoup4** - Web scraping
- **Feedparser** - RSS parsing

### AI/ML
- **Mistral-7B-GGUF** - Text generation (4.1GB Q4_K_M)
- **NLLB-200-GGUF** - Translation (800MB Q4_K_M)
- **SentenceTransformer** - Semantic similarity (80MB)

### UI/Frontend
- **Tkinter** - Native GUI (no web browser required)

### Integrations
- **WordPress REST API** - Publishing automation

---

## 🔧 Configuration

### Database Location
```
./nexuzy.db
```

### Model Cache Directory
```
./models/
├── TheBloke_Mistral-7B-Instruct-v0.2-GGUF/
├── QuantFactory_nllb-200-distilled-600M-GGUF/
└── sentence-transformers_all-MiniLM-L6-v2/
```

### Logs
```
./nexuzy_publisher.log
```

---

## 🌐 WordPress Integration

Nexuzy Publisher Desk uses **WordPress REST API** for seamless publishing.

### Requirements
- WordPress 5.0+
- Application Password (WordPress 5.6+)
- REST API enabled (default)

### Setup

**Step 1: Generate Application Password**
```
1. WordPress Admin → Users → Your Profile
2. Scroll to "Application Passwords"
3. Enter name: "Nexuzy Publisher"
4. Click "Add New Application Password"
5. Copy the generated password (shown once)
```

**Step 2: Configure in Nexuzy**
```
1. Open Nexuzy Publisher Desk
2. Go to "🌐 WordPress"
3. Enter:
   - Site URL: https://yoursite.com
   - Username: your-username
   - App Password: (paste from Step 1)
4. Test Connection
5. Save
```

**See [WORDPRESS_SETUP.md](WORDPRESS_SETUP.md) for troubleshooting**

---

## 👥 Team

### Lead Developer

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/david0154">
        <img src="https://github.com/david0154.png" width="100px;" alt="David"/><br />
        <sub><b>David</b></sub>
      </a><br />
      <sub>Project Lead & Core Developer</sub>
    </td>
  </tr>
</table>

### Organization

**Nexuzy Tech** - Innovation in AI-powered automation

- 🌐 Website: [Coming Soon]
- 📧 Contact: [136182039+david0154@users.noreply.github.com](mailto:136182039+david0154@users.noreply.github.com)
- 🐙 GitHub: [@david0154](https://github.com/david0154)

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

- 🐛 **Report Bugs** - Open an issue with detailed reproduction steps
- 💡 **Suggest Features** - Share your ideas in GitHub Discussions
- 📝 **Improve Documentation** - Fix typos, add examples
- 🔧 **Submit Code** - Fork, develop, and create pull requests
- 🌍 **Translations** - Help translate UI and documentation

### Development Setup

```bash
# Fork repository
git clone https://github.com/YOUR_USERNAME/nexuzy-publisher-desk.git
cd nexuzy-publisher-desk

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes
# ...

# Commit with conventional commits
git commit -m "feat: add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

**See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines**

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 David & Nexuzy Tech

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

## 🙏 Acknowledgments

### Open Source Projects

- **[llama.cpp](https://github.com/ggerganov/llama.cpp)** - GGUF inference engine
- **[Mistral AI](https://mistral.ai/)** - Mistral-7B base model
- **[Meta AI](https://ai.meta.com/)** - NLLB translation model
- **[HuggingFace](https://huggingface.co/)** - Model hosting and transformers
- **[WordPress](https://wordpress.org/)** - REST API integration

### Model Creators

- **[TheBloke](https://huggingface.co/TheBloke)** - GGUF quantized Mistral models
- **[QuantFactory](https://huggingface.co/QuantFactory)** - GGUF NLLB models
- **[sentence-transformers](https://www.sbert.net/)** - Embedding models

---

## 📊 Project Stats

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/david0154/nexuzy-publisher-desk?style=social)
![GitHub forks](https://img.shields.io/github/forks/david0154/nexuzy-publisher-desk?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/david0154/nexuzy-publisher-desk?style=social)

![GitHub commit activity](https://img.shields.io/github/commit-activity/m/david0154/nexuzy-publisher-desk)
![GitHub last commit](https://img.shields.io/github/last-commit/david0154/nexuzy-publisher-desk)
![GitHub issues](https://img.shields.io/github/issues/david0154/nexuzy-publisher-desk)
![GitHub pull requests](https://img.shields.io/github/issues-pr/david0154/nexuzy-publisher-desk)

</div>

---

## 🗺️ Roadmap

### Version 1.2.0 (Q2 2026)
- [ ] Advanced fact-checking with ClaimBuster API
- [ ] Image AI verification (NSFW, relevance)
- [ ] Database encryption
- [ ] Batch operations
- [ ] Export to PDF/DOCX

### Version 2.0.0 (Q3 2026)
- [ ] Optional cloud backup
- [ ] Real-time collaboration
- [ ] REST API for external integrations
- [ ] Mobile companion app
- [ ] SaaS version (optional)

**See [ROADMAP.md](ROADMAP.md) for detailed planning**

---

## 💬 Support

### Getting Help

- 📖 **Documentation**: Check the [docs folder](docs/)
- 🐛 **Bug Reports**: [Open an issue](https://github.com/david0154/nexuzy-publisher-desk/issues/new?template=bug_report.md)
- 💡 **Feature Requests**: [Open an issue](https://github.com/david0154/nexuzy-publisher-desk/issues/new?template=feature_request.md)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/david0154/nexuzy-publisher-desk/discussions)

### Community

- ⭐ **Star this repo** if you find it useful!
- 🐦 **Follow us** for updates [Coming Soon]
- 📢 **Share** with fellow developers and publishers

---

## ⚠️ Disclaimer

- **AI-Generated Content**: All AI drafts must be reviewed and edited by humans before publishing
- **Content Responsibility**: Users are responsible for verifying facts and ensuring accuracy
- **Copyright**: Respect copyright laws when scraping and publishing content
- **WordPress**: Ensure you have proper permissions to publish to your WordPress site

---

<div align="center">

**Made with ❤️ by [David](https://github.com/david0154) & [Nexuzy Tech](https://github.com/david0154)**

**[⬆ Back to Top](#nexuzy-publisher-desk)**

---

*Last Updated: January 22, 2026*

</div>
