# Nexuzy Publisher Desk - Implementation Guide v3
## Enhanced Vision AI + Research Writer + Complete WordPress Integration

**Last Updated:** January 28, 2026

---

## Overview of Improvements

This guide covers three major enhancements to Nexuzy Publisher Desk:

### 1. 🔬 Enhanced Vision AI (Multi-Method Watermark Detection)
- **File:** `core/vision_ai.py`
- **Features:**
  - Edge detection for overlays
  - Frequency analysis for repeating patterns (FFT-based)
  - Opacity detection for semi-transparent marks
  - Text detection using edge density
  - Logo detection using corner variance
- **Confidence:** 5-point detection with combined confidence scoring

### 2. 🌟 Research Writer (NEW)
- **File:** `core/research_writer.py`
- **Features:**
  - Web search integration (DuckDuckGo fallback)
  - Article scraping from multiple sources
  - Key point extraction and analysis
  - AI-powered article generation (1000-2000 words)
  - Auto-generated citations and source linking
  - Image finding (Unsplash integration)
  - Save as draft to database

### 3. 🚀 Complete WordPress Integration
- **File:** `core/wordpress_api_enhanced.py`
- **Features:**
  - Push original + ALL translations as separate posts
  - Link translations to original post
  - Inline image processing and upload
  - Featured image handling
  - Gutenberg block conversion (multi-line support)
  - Proper categories and tags management

---

## Installation

### Step 1: Update Dependencies

```bash
# Install new required packages
pip install scipy scikit-image

# Or update all dependencies
pip install -r requirements.txt
```

**New dependencies added:**
- `scipy>=1.11.0` - For frequency analysis and advanced math
- `scikit-image>=0.22.0` - For image processing

### Step 2: Database Migration (Optional but Recommended)

If you have an existing database, ensure the `translations` table exists:

```python
import sqlite3

conn = sqlite3.connect('nexuzy.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS translations (
        id INTEGER PRIMARY KEY,
        draft_id INTEGER,
        language TEXT,
        title TEXT,
        body_draft TEXT,
        summary TEXT,
        created_date TIMESTAMP,
        FOREIGN KEY(draft_id) REFERENCES ai_drafts(id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS research_cache (
        id INTEGER PRIMARY KEY,
        topic TEXT UNIQUE,
        article_content TEXT,
        sources TEXT,
        created_date TIMESTAMP,
        word_count INTEGER
    )
''')

conn.commit()
conn.close()
print("Database tables created successfully!")
```

---

## Usage Guide

### 1. Enhanced Watermark Detection

#### Basic Usage

```python
from core.vision_ai import VisionAI

vision = VisionAI()

# Detect watermarks
result = vision.detect_watermark('path/to/image.jpg')

print(result['status'])
print(f"Watermark Found: {result['watermark_detected']}")
print(f"Confidence: {result['confidence']}")
print(f"Detection Methods: {', '.join(result['methods'])}")

# Detailed breakdown
for method, details in result['details'].items():
    if details['detected']:
        print(f"  ❍ {method}: {details['confidence']:.1%}")
```

#### Detection Methods Explained

| Method | What It Detects | Use Case |
|--------|-----------------|----------|
| **Edge Detection** | Text watermarks via edge density | Logos, text overlays |
| **Frequency Analysis** | Repeating patterns in FFT | Tiled watermarks, patterns |
| **Opacity Detection** | Semi-transparent overlays | Fade/ghost watermarks |
| **Corner Variance** | Logo positions (corners) | Branded watermarks |
| **Color Uniformity** | Uniform color shifts | Colored overlays |

#### Output Example

```
🔴 HIGH CONFIDENCE watermark: text, logo [text(85%) + frequency(72%)]
  ├─ Edge Density: 18.5 (indicates text)
  ├─ Frequency Ratio: 1.45 (repeating pattern)
  ├─ Logo Variance: 1.8 (corner signature)
  └─ Opacity Std: 0.12 (transparent overlay)
```

### 2. Research Writer

#### Basic Article Generation

```python
from core.research_writer import ResearchWriter

writer = ResearchWriter()

# Research and generate article
result = writer.research_and_generate(
    topic="Artificial Intelligence in Healthcare",
    word_count=1500
)

if result['success']:
    print(f"Article generated: {result['word_count']} words")
    print(f"Sources used: {result['sources_used']}")
    print(f"Generated in: {result['generation_time']}")
    
    # Save as draft
    writer.save_as_draft(result['topic'], result['article'])
    print(f"Saved as draft!")
else:
    print(f"Error: {result['error']}")
```

#### With Custom Sources

```python
# Research using specific sources
result = writer.research_and_generate(
    topic="Renewable Energy Trends",
    source_urls=[
        "https://example.com/article1",
        "https://example.com/article2",
        "https://example.com/article3"
    ],
    word_count=2000
)
```

#### Find Images for Article

```python
# Find images for article topic
images = writer.find_images("Artificial Intelligence", count=5)

for img in images:
    print(f"Image: {img['title']}")
    print(f"URL: {img['url']}")
    print(f"By: {img['author']} ({img['source']})")
```

#### Workflow

```
🔍 Research & Article Generation Workflow:

1. 🌐 Web Search
   └─ Query: "Your Topic"
   └─ Returns: 5 search results

2. 📰 Article Scraping  
   └─ Extract content from each URL
   └─ Clean and validate (minimum 200 chars)

3. 🧠 Content Analysis
   └─ Extract key sentences
   └─ Identify main points

4. ✍️ Article Generation
   └─ AI-powered (GPT-2) or template-based
   └─ Structure: Intro + Sections + Conclusion

5. 📚 Citations
   └─ Add source links
   └─ Format references

6. 💾 Save as Draft
   └─ Store in database
   └─ Ready for editor review
```

### 3. Complete WordPress Integration

#### Push with Translations

```python
from core.wordpress_api_enhanced import WordPressAPIEnhanced

wp = WordPressAPIEnhanced()

# Publish original + all translations
result = wp.publish_draft_with_translations(
    draft_id=42,
    workspace_id=1,
    categories=['Technology', 'AI'],
    tags=['automation', 'future']
)

if result['success']:
    print(f"Published {result['total_posts_published']} posts:")
    
    print(f"Original: {result['original_post']['post_id']}")
    print(f"  URL: {result['original_post']['url']}")
    
    for lang, post in result['translations'].items():
        print(f"{lang.upper()}: {post['post_id']}")
        print(f"  URL: {post['url']}")
else:
    print(f"Error: {result['error']}")
```

#### Complete Workflow

```
📤 WordPress Publishing Workflow:

1. 🔗 Connect to WordPress
   ├─ Retrieve credentials from database
   ├─ Initialize API session
   └─ Test connection

2. 🖼️ Upload Featured Image
   ├─ Download from URL
   ├─ Upload to media library
   └─ Cache for translations

3. 📝 Publish Original Post
   ├─ Process inline images
   ├─ Convert to Gutenberg blocks
   ├─ Add categories & tags
   └─ Create draft post

4. 🌍 Publish Translations
   ├─ Fetch from translations table
   ├─ Process each language
   ├─ Upload with same image
   └─ Link to original

5. 🔗 Link Posts Together
   ├─ Set original_post meta
   ├─ Add language metadata
   └─ Enable translation navigation

Result: Original + N translations all published as separate posts
```

#### Inline Image Processing

Automatically downloads and processes inline images in your article:

```html
<!-- Original HTML with external images -->
<img src="https://example.com/image1.jpg" alt="Description">

<!-- After processing by WordPress -->
<!-- Auto-uploaded to WordPress media library -->
<!-- Image is cached for translation posts -->
```

#### Gutenberg Block Conversion

Heading, paragraphs, lists, and images are converted to proper WordPress Gutenberg blocks:

```
Input HTML:
<h2>Section Title</h2>
<p>Main paragraph content...</p>
<ul><li>Point 1</li><li>Point 2</li></ul>

Output Gutenberg:
<!-- wp:heading -->
<h2>Section Title</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Main paragraph content...</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul><li>Point 1</li><li>Point 2</li></ul>
<!-- /wp:list -->
```

---

## Integration with main.py

### Add Imports

```python
# In main.py
from core.vision_ai import VisionAI
from core.research_writer import ResearchWriter
from core.wordpress_api_enhanced import WordPressAPIEnhanced
```

### Add UI Elements (if using Tkinter)

```python
# Research Writer Tab
research_frame = ttk.LabelFrame(notebook, text="🌟 Research Writer")

topic_label = ttk.Label(research_frame, text="Topic:")
topic_entry = ttk.Entry(research_frame, width=40)

def on_research():
    topic = topic_entry.get()
    if not topic:
        messagebox.showwarning("Input", "Please enter a topic")
        return
    
    progress_label.config(text="🔬 Researching...")
    root.update()
    
    writer = ResearchWriter()
    result = writer.research_and_generate(topic, word_count=1500)
    
    if result['success']:
        progress_label.config(text=f"✅ Complete! {result['word_count']} words")
        writer.save_as_draft(result['topic'], result['article'])
    else:
        progress_label.config(text=f"❌ Error: {result['error']}")

research_btn = ttk.Button(research_frame, text="Generate Article", command=on_research)
research_btn.pack(pady=10)

progress_label = ttk.Label(research_frame, text="Ready")
progress_label.pack()
```

### Add WordPress Publishing with Translations

```python
def publish_to_wordpress():
    draft_id = int(draft_id_entry.get())
    workspace_id = int(workspace_entry.get())
    
    status_label.config(text="📄 Publishing to WordPress...")
    root.update()
    
    wp = WordPressAPIEnhanced()
    result = wp.publish_draft_with_translations(
        draft_id=draft_id,
        workspace_id=workspace_id,
        categories=['Technology'],
        tags=['automation']
    )
    
    if result['success']:
        msg = f"Published {result['total_posts_published']} posts\n"
        msg += f"Original: {result['original_post']['post_id']}\n"
        for lang in result['translations']:
            msg += f"{lang.upper()}: {result['translations'][lang]['post_id']}\n"
        messagebox.showinfo("Success", msg)
    else:
        messagebox.showerror("Error", f"Failed: {result['error']}")
```

---

## Configuration

### Vision AI Settings

```python
from core.vision_ai import VisionAI

vision = VisionAI()

# Adjust detection threshold if needed
vision.detection_threshold = 0.5  # 0-1 scale

# Run detection
result = vision.detect_watermark('image.jpg')
```

### Research Writer Settings

```python
from core.research_writer import ResearchWriter

writer = ResearchWriter(
    db_path='nexuzy.db',      # Database path
    cache_articles=True       # Cache generated articles
)

# Generate with custom word count
result = writer.research_and_generate(
    topic="Your Topic",
    word_count=2000           # 1000-2000 recommended
)
```

### WordPress Settings

```python
from core.wordpress_api_enhanced import WordPressAPIEnhanced

wp = WordPressAPIEnhanced('nexuzy.db')

# Publish with specific settings
result = wp.publish_draft_with_translations(
    draft_id=42,
    workspace_id=1,
    categories=['News', 'Tech'],
    tags=['important', 'update']
)
```

---

## Troubleshooting

### Vision AI Issues

**Problem:** "Vision AI dependencies missing"
```bash
pip install pillow numpy scipy scikit-image
```

**Problem:** Watermarks not detected
- Try image with known watermark first
- Check multiple detection methods output
- Increase `detection_threshold` if too many false positives

### Research Writer Issues

**Problem:** "No sources found"
- Check internet connection
- Try simpler search terms
- Use custom `source_urls` parameter

**Problem:** "BeautifulSoup not available"
```bash
pip install beautifulsoup4 lxml
```

### WordPress Issues

**Problem:** "Content is empty for post"
- Ensure draft body_draft field is populated
- Check translation content exists in database
- Verify HTML formatting

**Problem:** "Image upload failed"
- Check WordPress media permissions
- Verify image URL is accessible
- Check file size (WordPress limit usually 100MB)

**Problem:** "Could not connect to WordPress"
- Verify credentials in database
- Test with: `wp.test_connection(site_url, username, password)`
- Enable REST API in WordPress settings

---

## Performance Notes

### Vision AI
- Edge detection: **~100ms** per image
- Frequency analysis (FFT): **~500ms** per image
- Total detection: **~1-2 seconds** for typical images

### Research Writer
- Web search: **~3 seconds**
- Article scraping: **~10-15 seconds** (5 articles)
- AI generation: **~30-60 seconds** (depends on model)
- Total: **~1-2 minutes** per article

### WordPress Integration
- Image upload: **~5-10 seconds** per image
- Post creation: **~5 seconds** per post
- N translations: **~5 + (5×N) seconds**

---

## Database Schema

### translations table
```sql
CREATE TABLE translations (
    id INTEGER PRIMARY KEY,
    draft_id INTEGER NOT NULL,
    language TEXT NOT NULL,        -- en, es, fr, etc.
    title TEXT,
    body_draft TEXT,
    summary TEXT,
    created_date TIMESTAMP,
    FOREIGN KEY(draft_id) REFERENCES ai_drafts(id)
);
```

### research_cache table
```sql
CREATE TABLE research_cache (
    id INTEGER PRIMARY KEY,
    topic TEXT UNIQUE,
    article_content TEXT,
    sources TEXT,                 -- JSON array of URLs
    created_date TIMESTAMP,
    word_count INTEGER
);
```

---

## API Reference

### VisionAI Methods

| Method | Returns | Purpose |
|--------|---------|----------|
| `detect_watermark(path)` | Dict | Multi-method watermark detection |
| `check_image_quality(path)` | Dict | Quality metrics and recommendations |
| `get_detection_summary(path)` | str | Human-readable report |

### ResearchWriter Methods

| Method | Returns | Purpose |
|--------|---------|----------|
| `research_and_generate(topic, word_count)` | Dict | Full research workflow |
| `find_images(topic, count)` | List[Dict] | Find relevant images |
| `save_as_draft(topic, article)` | bool | Save to database |
| `clear_cache()` | None | Clear article cache |

### WordPressAPIEnhanced Methods

| Method | Returns | Purpose |
|--------|---------|----------|
| `publish_draft_with_translations(id, workspace)` | Dict | Publish original + translations |
| `upload_image_from_url(url, title)` | int | Upload image, return media ID |
| `test_connection(url, user, pass)` | bool | Test WordPress connection |

---

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Update database if needed (run migration script)
3. ✅ Test each component individually
4. ✅ Integrate into main.py UI
5. ✅ Configure WordPress credentials
6. ✅ Test end-to-end workflows

---

## Support & Issues

For issues or questions:
1. Check troubleshooting section above
2. Review GitHub issues
3. Check logs in `nexuzy.log`

---

**Version:** 3.0  
**Status:** Production Ready ✅  
**Last Updated:** January 28, 2026
