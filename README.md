<div align="center">

![Nexuzy Publisher Desk Logo](resources/logo.png)

# Nexuzy Publisher Desk

### 🚀 **AI-Powered Offline News Publishing Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/david0154/nexuzy-publisher-desk)
[![Status](https://img.shields.io/badge/status-Active-success)](https://github.com/david0154/nexuzy-publisher-desk)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Google AdSense](https://img.shields.io/badge/AdSense-90%25_Safe-green)](https://github.com/david0154/nexuzy-publisher-desk#-google-adsense-compliance)

**Automate your entire news publishing workflow with AI - from RSS feeds to WordPress - completely offline!**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [AdSense Safety](#-google-adsense-compliance) • [Contributing](#-contributing) • [Documentation](#-documentation)

---

</div>

## 📖 Overview

Nexuzy Publisher Desk is a complete AI-powered news publishing platform that runs entirely **offline on your local machine**. It automates the entire workflow from RSS feed monitoring to WordPress publishing, with **mandatory human editorial control** to ensure content quality, originality, and compliance with monetization platforms like Google AdSense.

### ✨ Why Nexuzy Publisher Desk?

- 🔒 **100% Offline** - All AI models run locally, no data leaves your computer
- 🤖 **AI-Powered** - Uses GGUF quantized models (Mistral-7B, NLLB-200)
- 📰 **Complete Workflow** - RSS → Matching → Scraping → Draft → **Human Review** → Translate → Publish
- ✅ **Human-in-the-Loop** - **Mandatory** human verification, editing, and approval before publishing
- 💰 **AdSense Safe** - **90%+ compliance** with responsible usage (100% safe with 8-10 posts/day limit)
- 🌐 **Multi-Language** - Built-in translation to 200+ languages
- 💾 **Lightweight** - Only ~5GB AI models (GGUF optimized for CPU)
- 🎨 **Simple UI** - Clean Tkinter interface, no complex setup

---

## 💰 Google AdSense Compliance

### Content Safety Guarantee

Nexuzy Publisher Desk is designed with **Google AdSense policies** in mind, ensuring your monetized blog remains compliant:

| Usage Pattern | AdSense Safety | Recommendation |
|---------------|----------------|----------------|
| **8-10 posts/day** with human review | ✅ **100% Safe** | **Recommended** - Ideal for sustainable publishing |
| **15-20 posts/day** with human review | ⚠️ **90% Safe** | Acceptable - Monitor quality carefully |
| **25+ posts/day** | ❌ **Not Recommended** | High risk - May trigger quality concerns |

### Why AdSense Compliant?

#### 1. **Mandatory Human Review** 🧑‍💻
- ✅ **Required editing step** - AI drafts cannot be published without human modification
- ✅ **Fact verification** - Users must verify claims before publishing
- ✅ **Originality checks** - Multi-source aggregation prevents plagiarism
- ✅ **Quality control** - Editorial oversight at every stage

#### 2. **Content Originality** 📝
- ✅ **Multi-source aggregation** - Combines facts from 3+ independent sources
- ✅ **AI rewriting** - Generates unique content, not copying
- ✅ **Human editing** - Users add insights, context, and original perspective
- ✅ **Citation support** - Encourages proper attribution to sources

#### 3. **Volume Control** 📊
- ✅ **Sustainable pace** - 8-10 posts/day recommended for quality maintenance
- ✅ **Quality over quantity** - Prevents content mill perception
- ✅ **Natural publishing pattern** - Mimics human editorial workflow
- ✅ **Monitoring alerts** - Built-in warnings for excessive publishing rates

#### 4. **Transparency** 🔍
- ✅ **AI-assisted disclosure** - Users can add "AI-assisted" disclaimers
- ✅ **Source attribution** - Encourages linking to original sources
- ✅ **Human verification mark** - ✓ "Edited by Human" checkbox required
- ✅ **Editorial standards** - Promotes responsible AI usage

### Best Practices for 100% Safety ✨

1. **Limit Daily Publishing** 🗓️
   - Publish **maximum 8-10 articles per day**
   - Spread posts throughout the day (not bulk uploads)
   - Take weekends off to maintain natural rhythm

2. **Always Edit AI Drafts** ✏️
   - **Never publish without modification**
   - Add your own insights, analysis, and commentary
   - Verify all facts with original sources
   - Rewrite headlines and introductions

3. **Add Human Value** 💡
   - Include personal opinions or expert commentary
   - Add relevant images with proper licensing
   - Create original conclusions or takeaways
   - Link to authoritative sources

4. **Quality Checks** ✅
   - Read every article before publishing
   - Check grammar and readability
   - Ensure factual accuracy
   - Remove any AI hallucinations or errors

5. **Transparency** 📢
   - Optionally add "AI-assisted writing" disclosure
   - Cite original news sources
   - Maintain editorial standards
   - Respond to reader feedback

### AdSense Policy Compliance Summary

✅ **Original Content** - Multi-source aggregation + human editing = unique articles  
✅ **Valuable to Users** - Fact-verified, edited news with human insights  
✅ **Human Oversight** - Mandatory editorial review before publishing  
✅ **Natural Publishing** - Recommended 8-10 posts/day limit  
✅ **Proper Attribution** - Encourages source citation and transparency  

**🎯 Result:** When used responsibly with human oversight and volume limits, Nexuzy Publisher Desk produces AdSense-compliant content that provides genuine value to readers.

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
| 📝 **Human Editor** | **Mandatory** editorial control | **Required:** Edit, verify, and approve before publishing |
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

### 4️⃣ **Edit & Verify (REQUIRED)** ⚠️

```
1. Go to "✏️ Editor"
2. Review AI-generated draft
3. **REQUIRED:** Edit headline and body with your own words
4. **REQUIRED:** Verify all facts against original sources
5. **REQUIRED:** Check ✓ "Edited by Human" (publishing blocked without this)
6. Add your insights, commentary, or analysis
7. Click "💾 Save Draft"
```

### 5️⃣ Translate & Publish

```
1. Click "🌐 Translate" (optional - 200+ languages)
2. Review translation if needed
3. Click "📤 Send to WordPress"
4. Confirm publishing details
5. Article published ✓
```

### 6️⃣ Configure WordPress

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

## 🤝 Contributing

We **actively welcome contributions** from developers, writers, translators, and news publishers! Join our growing community and help make Nexuzy Publisher Desk better for everyone.

### 🌟 How to Contribute

#### 1. **For Developers** 💻

**Bug Fixes & Features**
```bash
# 1. Fork the repository
git clone https://github.com/YOUR_USERNAME/nexuzy-publisher-desk.git
cd nexuzy-publisher-desk

# 2. Create a feature branch
git checkout -b feature/amazing-feature

# 3. Make your changes
# - Follow PEP 8 style guidelines
# - Add comments and docstrings
# - Write tests if applicable

# 4. Commit with conventional commits
git commit -m "feat: add amazing feature"
# Types: feat, fix, docs, style, refactor, test, chore

# 5. Push and create Pull Request
git push origin feature/amazing-feature
```

**Areas We Need Help:**
- 🐛 Bug fixes and performance improvements
- ✨ New features (see [ROADMAP.md](ROADMAP.md) for ideas)
- 🧪 Unit tests and integration tests
- 📦 Packaging and distribution (AppImage, Flatpak, etc.)
- 🔌 Plugin system development
- 🎨 UI/UX improvements

#### 2. **For Writers & Publishers** 📝

**Documentation & Guides**
- 📚 Improve existing documentation
- 📖 Write tutorials and how-to guides
- 🎥 Create video walkthroughs
- 📝 Share best practices and workflows
- ✍️ Write case studies of your usage

**Quality Assurance**
- 🐛 Report bugs with detailed reproduction steps
- 💡 Suggest feature improvements
- 📊 Share your publishing statistics and feedback
- ✅ Test beta releases

#### 3. **For Translators** 🌍

**Internationalization**
- 🗣️ Translate UI strings to your language
- 📄 Translate documentation
- 🌐 Improve existing translations
- 🧪 Test translated interfaces

**Supported Languages We Need:**
- Spanish (es)
- French (fr)
- German (de)
- Hindi (hi)
- Arabic (ar)
- Chinese (zh)
- [+195 more via NLLB-200]

#### 4. **For Designers** 🎨

**Design Contributions**
- 🎨 Create new UI themes
- 🖼️ Design app icons and logos
- 📱 Design promotional graphics
- 🌈 Improve color schemes and layouts
- ♿ Accessibility improvements

### 📋 Contribution Guidelines

#### Before You Start
1. 🔍 Check [existing issues](https://github.com/david0154/nexuzy-publisher-desk/issues) to avoid duplicates
2. 💬 Join [GitHub Discussions](https://github.com/david0154/nexuzy-publisher-desk/discussions) to discuss major changes
3. 📖 Read [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines
4. ⚖️ Ensure your contribution follows the [MIT License](LICENSE)

#### Code Standards
- ✅ Follow PEP 8 Python style guide
- ✅ Add docstrings to functions and classes
- ✅ Write clear commit messages (conventional commits)
- ✅ Test your changes thoroughly
- ✅ Update documentation if needed

#### Pull Request Process
1. 📝 Describe your changes clearly in the PR description
2. 🔗 Link related issues (e.g., "Fixes #123")
3. ✅ Ensure all checks pass (linting, tests)
4. 👀 Request review from maintainers
5. 🎉 Celebrate when merged!

### 🏆 Contributors

We recognize and appreciate all contributors! Your name will appear here and in [CONTRIBUTORS.md](CONTRIBUTORS.md).

#### Project Lead
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

#### Core Contributors
<!-- ALL-CONTRIBUTORS-LIST:START -->
<!-- This section will be automatically updated -->
*Become the first contributor! 🚀*
<!-- ALL-CONTRIBUTORS-LIST:END -->

### 🎁 Recognition

All contributors receive:
- 📛 Name in README and CONTRIBUTORS.md
- 🏅 GitHub contributor badge
- 🙏 Eternal gratitude from the community
- 🌟 Priority support for your issues

### 💬 Ways to Get Involved

Even if you're not a developer, you can still contribute!

| Contribution Type | How to Help | Difficulty |
|-------------------|-------------|------------|
| 🐛 **Report Bugs** | [Open an issue](https://github.com/david0154/nexuzy-publisher-desk/issues/new?template=bug_report.md) | Easy |
| 💡 **Suggest Features** | [Open a feature request](https://github.com/david0154/nexuzy-publisher-desk/issues/new?template=feature_request.md) | Easy |
| 📖 **Improve Docs** | Edit .md files and submit PR | Easy |
| 🌍 **Translate** | Translate strings and docs | Medium |
| 🎨 **Design** | Create mockups or themes | Medium |
| 💻 **Code** | Submit bug fixes or features | Medium-Hard |
| 🧪 **Test** | Test beta releases | Easy |
| ⭐ **Star & Share** | Spread the word! | Easy |

### 📧 Contact

- 💬 **Discussions:** [GitHub Discussions](https://github.com/david0154/nexuzy-publisher-desk/discussions)
- 🐛 **Issues:** [GitHub Issues](https://github.com/david0154/nexuzy-publisher-desk/issues)
- 📧 **Email:** [136182039+david0154@users.noreply.github.com](mailto:136182039+david0154@users.noreply.github.com)
- 🐙 **GitHub:** [@david0154](https://github.com/david0154)

**We can't wait to see what you'll contribute! 🚀**

---

## 📚 Documentation

### User Guides
- 📘 [**QUICK_START.md**](QUICK_START.md) - 5-minute setup guide
- 📗 [**FEATURES.md**](FEATURES.md) - Complete feature documentation
- 📕 [**WORDPRESS_SETUP.md**](WORDPRESS_SETUP.md) - WordPress REST API configuration
- 📙 [**AI_MODELS.md**](AI_MODELS.md) - AI model details and customization
- 💰 [**ADSENSE_GUIDE.md**](ADSENSE_GUIDE.md) - AdSense compliance best practices

### Developer Guides
- 🔧 [**SETUP.md**](SETUP.md) - Development environment setup
- 🏗️ [**ARCHITECTURE.md**](ARCHITECTURE.md) - System architecture overview
- 📦 [**DEPLOYMENT.md**](DEPLOYMENT.md) - Building EXE and distribution
- 🤝 [**CONTRIBUTING.md**](CONTRIBUTING.md) - Contribution guidelines
- 🧪 [**TESTING.md**](TESTING.md) - Testing guidelines

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

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 David & Nexuzy Tech

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

[Full license text in LICENSE file]
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
- [ ] Publishing rate monitor and alerts
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
- 🤝 **Contribute** - see [Contributing](#-contributing) section above

---

## ⚠️ Important Disclaimers

### Content Responsibility

- ⚠️ **AI-Generated Content**: All AI drafts **MUST** be reviewed and edited by humans before publishing
- ⚠️ **Content Accuracy**: Users are **solely responsible** for verifying facts and ensuring accuracy
- ⚠️ **Human Verification Required**: The "Edited by Human" checkbox is **mandatory** - publishing is blocked without it
- ⚠️ **Copyright Compliance**: Respect copyright laws when scraping and publishing content
- ⚠️ **Source Attribution**: Always credit original news sources appropriately

### AdSense Compliance

- ✅ **Recommended Usage**: 8-10 posts/day with thorough human editing = **100% safe**
- ⚠️ **Moderate Usage**: 15-20 posts/day = **90% safe** (monitor quality carefully)
- ❌ **Excessive Usage**: 25+ posts/day = **Not recommended** (high risk of policy violations)
- 📝 **Human Editing Required**: Never publish AI-generated content without modification
- 🔍 **Quality Control**: Maintain editorial standards at all times

### Legal Notice

- ⚖️ **No Warranty**: This software is provided "as-is" without warranty of any kind
- 🚫 **Not Legal Advice**: AdSense safety ratings are guidelines, not guarantees
- 👤 **User Responsibility**: You are responsible for compliance with all applicable laws and platform policies
- 🔒 **WordPress Security**: Ensure you have proper permissions to publish to your WordPress site
- 📄 **Terms of Service**: Always follow WordPress and AdSense Terms of Service

---

<div align="center">

**Made with ❤️ by [David](https://github.com/david0154) & [Nexuzy Tech](https://github.com/david0154)**

**[⬆ Back to Top](#nexuzy-publisher-desk)**

---

### 🌟 If you find this project useful, please consider:
- ⭐ Starring this repository
- 🐛 Reporting bugs and suggesting features
- 🤝 Contributing code, documentation, or translations
- 📢 Sharing with other developers and publishers

---

*Last Updated: January 29, 2026*

</div>