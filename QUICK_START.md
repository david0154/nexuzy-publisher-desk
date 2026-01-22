# ⚡ Nexuzy Publisher Desk - Quick Start (5 Minutes)

## One-Minute Installation

### Windows Users
```
1. Download NexuzyPublisherDesk.exe
2. Double-click → Launch
3. Wait for models (first run: ~30-40 min)
4. Done! (🌟)
```

### Linux/Mac/Developers
```bash
git clone https://github.com/david0154/nexuzy-publisher-desk.git
cd nexuzy-publisher-desk
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt
python main.py
```

---

## First Run Checklist

### ✅ Step 1: Model Download (Auto, ~30-40 min)
Console shows:
```
✓ SentenceTransformer (80MB) - News matching
✓ Mistral-7B (14GB) - Draft generation  
✓ NLLB-200 (2.4GB) - Translation
✓ All models ready
```

### ✅ Step 2: Create Workspace
1. Click **"+ New Workspace"**
2. Name: "My News Desk" (any name)
3. Click **Create**

### ✅ Step 3: Add RSS Feed
1. Click **"RSS Manager"**
2. Click **"+ Add Feed"**
3. Paste RSS URL (e.g., `https://feeds.arstechnica.com/arstechnica/index`)
4. Select category: **Tech**
5. Language: **English**
6. Priority: **5**
7. Click **Save Feed**

### ✅ Step 4: Configure WordPress (Optional)
1. Click **"WordPress"**
2. Enter site URL: `https://yoursite.com`
3. Username: Your WordPress username
4. App Password: Generate in WordPress > Users > Your Profile
5. Click **Test Connection** → "Success"
6. Click **Save**

**Done!** Now publish articles. 🌟

---

## Your First Article (10 Minutes)

### 1. Fetch News (2 min)
```
Click: News Queue → [Fetch Latest News]
→ System fetches from all RSS feeds
→ Headlines appear in list
```

### 2. Verify Event (3 min)
```
Click: Analyze Event
→ System groups same headlines
→ Shows: "Verified (3 sources)" or "Low confidence (1 source)"
→ Displays confirmed facts and conflicts
```

### 3. Generate Draft (2 min)
```
Click: [Generate Draft]
→ AI creates neutral article from facts
→ 3 headline options suggested
→ Full article body generated
→ Draft is READ-ONLY (human must edit)
```

### 4. Edit Article (3 min)
```
Editor Panel:
1. Change headline (mandatory)
2. Rewrite intro (mandatory)
3. Adjust body if needed
4. Check "Edited by human" (mandatory)
5. Click: [Save Draft]
6. NOW "Publish" button enables
```

### 5. Publish to WordPress (2 min)
```
Click: [Send as Draft]
→ Article sent to WordPress as DRAFT
→ Go to WordPress admin
→ Review draft
→ Click Publish (manual)
→ Article LIVE 🌟
```

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New Workspace | `Ctrl + N` |
| Add Feed | `Ctrl + F` |
| Fetch News | `Ctrl + R` |
| Open Editor | `Ctrl + E` |
| Save Draft | `Ctrl + S` |
| Publish | `Ctrl + P` |
| Settings | `Ctrl + ,` |

---

## Common Tasks

### Add Multiple RSS Feeds
```
RSS Manager → + Add Feed → (repeat 5-10 times)

Recommended starters:
- TechCrunch: https://feeds.techcrunch.com/techcrunch/
- BBC News: http://feeds.bbc.co.uk/news/rss.xml
- The Verge: https://www.theverge.com/rss/index.xml
- Hacker News: https://news.ycombinator.com/rss
```

### Generate Article in Another Language
```
1. (Create article as usual in English)
2. Open Translator panel
3. Select language: Hindi / Bengali / Spanish / French
4. Click [Translate Draft]
5. Review translation
6. Publish to separate WordPress post
```

### Connect Multiple WordPress Sites
```
WordPress Config → [+ Add Site]
(repeat for each site with different credentials)

When publishing:
Choose target site from dropdown
```

### Clear Old Articles
```
Settings → [Clean Database]
Select: Delete articles older than 30 days
Click: [Confirm]
```

---

## GPU Setup (Optional, 10x Faster)

### NVIDIA CUDA (Recommended)
```bash
# Install CUDA 11.8 or 12.x from:
# https://developer.nvidia.com/cuda-downloads

# Then reinstall PyTorch:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Restart app - GPU automatically detected
```

### AMD ROCm
```bash
# Install from: https://rocmdocs.amd.com/

# Install PyTorch:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
```

### Apple Silicon (M1/M2/M3)
```bash
# Just reinstall PyTorch (Metal auto-enabled)
pip install torch torchvision torchaudio
```

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 12GB | 16GB+ |
| **Storage** | 40GB | 80GB+ |
| **CPU** | 4-core | 8-core |
| **GPU** | Optional | RTX 2060+ |
| **Internet** | 1st run only | 1st run + RSS fetch |

---

## Troubleshooting

### Models Won't Download
```bash
# Manual download
python -c "from main import ModelDownloader; ModelDownloader().check_and_download()"

# Or check:
# - 30GB free disk space?
# - Internet connection working?
# - Check nexuzy_publisher.log for errors
```

### Out of Memory
```
1. Close other apps
2. Install GPU support (CUDA)
3. Reduce batch size (process 1 article at a time)
4. Restart application
```

### WordPress Connection Fails
```
1. Check credentials in WordPress
2. Verify Application Password is enabled
3. Try: curl -u username:password https://yoursite.com/wp-json/
4. Check firewall/proxy settings
```

### Slow Article Generation
```
1. GPU would help (10x faster)
2. Or: Process offline, optimize hardware
3. Check nexuzy_publisher.log for bottlenecks
```

---

## Tips & Tricks

### 🔥 Pro Tips
1. **Verify before publish**: Always check "Verified (3+ sources)" 
2. **Read the draft**: AI assists, YOU approve
3. **Edit the headline**: Custom headlines perform better
4. **Use multiple languages**: Hit different audiences
5. **Set up multiple workspaces**: One per newsroom/language
6. **Regular backups**: Copy `nexuzy.db` regularly
7. **GPU = 10x faster**: Worth setup if you have NVIDIA
8. **Batch process**: Handle 5-10 articles daily, not hourly

### 🙋 Getting Help
```
1. Check: nexuzy_publisher.log (detailed errors)
2. Read: README.md (features guide)
3. See: FEATURES.md (all capabilities)
4. Try: SETUP.md (installation help)
5. GitHub Issues: Report bugs
```

---

## Workflow Overview

```
📡 RSS
   ↓
📋 Fetch News
   ↓
🔍 Match & Verify
   ↓
🗑️ Scrape Facts
   ↓
🤖 Generate Draft (AI)
   ↓
✏️ Edit (HUMAN - mandatory)
   ↓
🖼️ Add Images
   ↓
🌐 Translate (optional)
   ↓
📤 Send to WordPress
   ↓
📁 Publish (Manual in WordPress)
   ↓
🌟 LIVE! 🌟
```

---

## Next Level

**When comfortable, explore:**
- [ ] Advanced filters in News Queue
- [ ] Bulk operations (edit multiple articles)
- [ ] API integration (custom tools)
- [ ] Database backup/restore
- [ ] Custom RSS feed creation
- [ ] Advanced translation options
- [ ] Multi-site coordination

---

## Support & Resources

- **Repository**: https://github.com/david0154/nexuzy-publisher-desk
- **Issues**: Report bugs here
- **Discussions**: Ask questions here  
- **Developer**: David @ Nexuzy Tech
- **Website**: https://imdavid.in

---

## Key Stats

🏆 **Performance**
- News matching: <5 seconds
- Draft generation: 30-120 seconds (CPU), 5-10 seconds (GPU)
- Translation: 5-30 seconds per article
- Database: <1 second queries

🎓 **Features**
- 100+ total features
- 10+ supported languages
- Offline-first architecture
- 0 cloud dependencies
- Private & secure

🌟 **Quality**
- News verification (multiple sources)
- Fact extraction only (no plagiarism)
- Human approval mandatory
- Conflict detection
- AdSense-safe workflow

---

## Frequently Asked Questions

**Q: Can I use without WordPress?**
A: Yes! Publish drafts as files or just use for news research.

**Q: Is it really offline?**
A: Yes! All processing local. Internet only for RSS fetch & WordPress push.

**Q: Can I use multiple languages?**
A: Yes! Generate in 10+ languages automatically.

**Q: How much storage needed?**
A: ~30GB for models, 1-10GB for database (500+ articles).

**Q: Can I run on Mac/Linux?**
A: Yes! Python runs everywhere.

**Q: Is the AI output ready to publish?**
A: No! Human editing mandatory before publish. AI assists only.

**Q: Can I integrate custom tools?**
A: Not yet, but planned for future versions.

**Q: What about my data security?**
A: All local. No cloud. Database encryption available.

---

## One Command to Start

```bash
# If already installed:
python main.py

# Or run EXE directly:
NexuzyPublisherDesk.exe
```

---

**🌟 Ready? Click → New Workspace → Add Feed → Fetch → Generate → Edit → Publish!**

**Questions? Check README.md, SETUP.md, or FEATURES.md** ✨
