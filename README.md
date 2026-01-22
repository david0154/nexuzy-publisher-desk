# 📰 Nexuzy Publisher Desk

**Complete offline AI-powered news publishing desktop application**

A professional-grade newsroom desktop tool that combines RSS aggregation, AI-assisted content creation, fact verification, and WordPress integration—all running locally without internet dependency.

---

## 🎯 Features

### 1. **RSS Feed Management**
- Add unlimited RSS feeds
- Categorize by topic (Tech, Business, World, etc.)
- Multi-language support
- Priority-based fetching
- Enable/disable feeds dynamically

### 2. **Intelligent News Matching**
- AI-powered headline similarity detection (SentenceTransformer)
- Group same-event stories from multiple sources
- Authenticity verification by source count
- Conflict detection in facts
- Confidence scoring (single source = unverified, 3+ sources = verified)

### 3. **Safe Content Scraping**
- Extract facts, dates, names, quotes from articles
- **No full article copying** - facts-only mode
- Proper URL handling and error recovery
- Source attribution for every fact

### 4. **AI Draft Generation**
- Mistral-7B model for neutral, fact-based article generation
- Guided by extracted facts and verified information
- Multiple headline suggestions
- Read-only initial drafts (human control mandatory)

### 5. **Editorial Control (Human First)**
- Manual headline editing required
- Human-edited checkboxes
- Word count minimum enforcement
- Similarity threshold validation
- Publish buttons disabled until fully approved

### 6. **Multi-Language Translation**
- NLLB-200 for 10+ languages
- Supported: English, Hindi, Bengali, Spanish, French, German, Arabic, Chinese, Japanese, Portuguese
- Chunk-based translation for long articles
- Per-language approval workflow

### 7. **WordPress Integration**
- Secure REST API connection
- Application password authentication
- Draft-only publishing (manual final publish in WordPress)
- Connection testing before save
- Credential encryption

### 8. **Offline-First Architecture**
- Runs completely offline after first setup
- SQLite local database
- Models cached in `./models/` directory
- No cloud dependencies
- Minimal RAM footprint

---

## 📋 System Requirements

- **OS**: Windows 10/11 (Linux/Mac support via Python)
- **Python**: 3.9 - 3.11
- **RAM**: 16GB recommended (12GB minimum)
- **Storage**: 30GB for models + database
- **GPU**: Optional (CUDA/ROCm for faster processing)
- **Processor**: Multi-core CPU (4+ cores recommended)

---

## 🚀 Installation

### Option 1: Pre-built Executable (Windows)

1. Download `NexuzyPublisherDesk.exe` from [Releases](#)
2. Double-click to run
3. Models download automatically on first launch (~30-40 minutes depending on internet speed)
4. Ready to use!

### Option 2: From Source (Development)

```bash
# Clone repository
git clone https://github.com/david0154/nexuzy-publisher-desk.git
cd nexuzy-publisher-desk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Option 3: Build Your Own EXE

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller build_config.spec

# Output: dist/NexuzyPublisherDesk.exe
```

---

## 📁 Project Structure

```
nexuzy-publisher-desk/
├── main.py                      # Application entry point + auto-downloader
├── core/
│   ├── rss_manager.py          # RSS feed handling
│   ├── news_matcher.py         # AI-powered news grouping
│   ├── content_scraper.py      # Safe fact extraction
│   ├── ai_draft_generator.py   # Mistral-7B integration
│   ├── translator.py           # NLLB-200 translations
│   └── wordpress_api.py        # WordPress REST API
├── models/                      # AI models (auto-downloaded)
│   ├── all-MiniLM-L6-v2/       # SentenceTransformer for matching
│   ├── Mistral-7B-Instruct/    # Draft generation model
│   ├── nllb-200-distilled/     # Translation model
│   └── models_config.json      # Downloaded models registry
├── resources/                   # Icons and images
│   └── logo.ico
├── nexuzy.db                    # SQLite database (auto-created)
├── nexuzy_publisher.log         # Application logs
├── requirements.txt             # Python dependencies
├── build_config.spec            # PyInstaller configuration
├── .gitignore                   # Git ignore patterns
└── README.md                    # This file
```

---

## 🔄 Complete Workflow

### Phase 1: News Collection
1. **Add RSS Feeds**: `RSS Manager` → `Add Feed` → Select category & language
2. **Fetch News**: `Fetch Latest News` button → System reads all enabled feeds
3. **Database Storage**: Headlines, summaries, URLs stored locally

### Phase 2: Verification
1. **Match Headlines**: SentenceTransformer groups similar headlines
2. **Verify Authenticity**: System counts sources
   - 1 source = "Low confidence" (unverified)
   - 2-3 sources = "Medium confidence"
   - 4+ sources = "High confidence" (verified)
3. **Detect Conflicts**: Compare facts across sources

### Phase 3: Scraping
1. **Open News Group**: Click verified news event
2. **Extract Facts**: System scrapes dates, names, quotes, facts
3. **Store Reference Data**: No full article text, only reference facts

### Phase 4: AI Analysis
1. **Click "Analyze Event"**: AI reads all facts from multiple sources
2. **Generate Timeline**: Events ordered chronologically
3. **Build Fact List**: Consolidated verified information
4. **Detect Contradictions**: Flag conflicting claims

### Phase 5: Draft Generation
1. **Click "Generate Draft"**: Mistral-7B creates neutral article
2. **AI Output**:
   - Suggested headlines (multiple options)
   - Full article body
   - Summary box
3. **Draft Locked**: Read-only until manual editing

### Phase 6: Editorial Review (MANDATORY)
1. **Open Editor Panel**
2. **Edit Headline**: Must change/approve manually
3. **Rewrite Intro**: Personal editorial touch
4. **Adjust Body**: Add context, fix tone
5. **Check "Edited by Human"**: Checkbox required
6. **Verify Word Count**: Minimum enforced
7. **Publish button enables** only after all checks

### Phase 7: Images & Translation
1. **Select Images**: System suggests from RSS enclosures
2. **Approve Images**: Manual image verification
3. **Translate (Optional)**: Select language → Generate translations → Review each

### Phase 8: WordPress Publishing
1. **Configure WordPress**: Site URL + credentials
2. **Test Connection**: Verify credentials work
3. **Send as Draft**: Article appears as draft in WordPress
4. **User Publishes**: Manual final publish in WordPress admin

---

## 🤖 AI Models Used

### 1. **SentenceTransformer** (all-MiniLM-L6-v2)
- **Purpose**: News matching & similarity detection
- **Size**: 80MB
- **Speed**: Fast CPU processing
- **Function**: Groups same-event headlines, calculates confidence

### 2. **Mistral-7B-Instruct**
- **Purpose**: Article draft generation
- **Size**: 14GB (quantized: 4GB with GGUF)
- **Speed**: 2-5 tokens/sec on CPU (faster with GPU)
- **Function**: Generates neutral, fact-based articles from extracted facts

### 3. **NLLB-200-Distilled**
- **Purpose**: Multi-language translation
- **Size**: 2.4GB
- **Languages**: 200+ language pairs
- **Function**: Translates articles preserving meaning and context

### Auto-Download on First Run

Models automatically download from HuggingFace on first application launch:
```
✓ Downloading SentenceTransformer... (80MB)
✓ Downloading Mistral-7B... (14GB or 4GB quantized)
✓ Downloading NLLB-200... (2.4GB)
✓ All models ready
```

**Progress**: Terminal shows download percentage and ETA

---

## 🔐 Privacy & Security

✅ **Complete Privacy**
- No data sent to cloud
- All processing local
- SQLite database encrypted option available
- WordPress credentials stored locally (can be encrypted)

✅ **Content Safety**
- No full article copying
- Facts-based only
- Human approval mandatory before publish
- Conflict detection prevents misinformation

✅ **AdSense Safe**
- Human-edited mandatory
- Conflict detection
- Source verification
- No scraped content publication

---

## 📊 Database Schema

Key tables:
- `workspaces` - Separate newsrooms
- `rss_feeds` - Managed feed sources
- `news_queue` - Fetched news items
- `news_groups` - Grouped same-event stories
- `scraped_facts` - Extracted information
- `ai_drafts` - Generated articles
- `translations` - Multi-language versions
- `wordpress_posts` - Published articles
- `wp_credentials` - WordPress configuration

---

## ⚡ Performance Tips

1. **GPU Acceleration**: Install CUDA/ROCm for 10x faster processing
2. **Limit Feeds**: 50-100 feeds recommended, 200+ max
3. **Weekly Cleanup**: Archive old news items
4. **Model Selection**: Use distilled versions for faster performance on low-end hardware
5. **Batch Processing**: Process multiple articles before publishing

---

## 🐛 Troubleshooting

### Models Not Downloading
```bash
# Manual download
python -c "from main import ModelDownloader; ModelDownloader().check_and_download()"
```

### Out of Memory
- Close other applications
- Install GPU support (CUDA)
- Use quantized models
- Process fewer articles at once

### WordPress Connection Failed
- Verify credentials in WordPress
- Check application password is enabled
- Ensure REST API not disabled
- Test with curl: `curl -u username:password https://yoursite.com/wp-json/wp/v2/posts`

### Slow Translation
- GPU significantly speeds up translations
- Translate shorter articles first
- Consider translating only key languages

---

## 📝 Usage Examples

### Example 1: Tech News Aggregation
1. Add TechCrunch, Hacker News, The Verge RSS feeds
2. Fetch latest → System finds 5 articles about "AI Breakthrough"
3. AI matches them → Groups as same event
4. Generate draft → AI writes neutral article comparing all sources
5. Edit manually → Add your analysis
6. Publish to WordPress as draft → Review before final publish

### Example 2: Multi-Language Publishing
1. Generate English article (as above)
2. Translate to Hindi, Bengali
3. Publish 3 WordPress drafts (one per language)
4. Share across regional audiences

---

## 🎓 Learning Resources

- **SentenceTransformer Docs**: https://www.sbert.net/
- **Mistral AI**: https://mistral.ai/
- **NLLB Translation**: https://huggingface.co/facebook/nllb-200
- **WordPress REST API**: https://developer.wordpress.com/docs/api/

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Advanced image verification
- Database encryption
- Export to multiple formats
- Cloud backup integration
- Advanced analytics

---

## 📄 License

MIT License - See LICENSE file

---

## 🙋 Support

**Issues?** 
- Check [GitHub Issues](https://github.com/david0154/nexuzy-publisher-desk/issues)
- Review logs in `nexuzy_publisher.log`
- Test models manually in Python REPL

**Feature Requests?**
- Open GitHub Discussion
- Describe use case
- Provide examples

---

## 📞 Contact

**Developed by**: [Nexuzy Tech](https://imdavid.in)
**GitHub**: [david0154](https://github.com/david0154)
**Email**: contact@nexuzy.in

---

## 🚀 Roadmap

- [ ] Cloud storage sync (optional)
- [ ] Advanced fact verification (Claim Buster API)
- [ ] Image NSFW detection improvement
- [ ] Video content support
- [ ] Real-time collaboration
- [ ] API for external integrations
- [ ] Mobile companion app
- [ ] Voice input for quick notes

---

**Built with ❤️ for modern newsrooms. Offline. Private. Powerful.**
