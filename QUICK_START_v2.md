# 🚀 Nexuzy Publisher Desk v2.0 - Quick Start Guide

## 🎯 What's New in v2.0?

Version 2.0 brings **automatic duplicate detection**, **48-hour news cleanup**, and **15 critical bug fixes**.

---

## ⚡ Quick Setup (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements_complete.txt
```

### 2. Run the Application
```bash
python main.py
```

### 3. Create Your First Workspace
- Click **"+ New"** in the header
- Enter workspace name (e.g., "My News Site")
- Click **"Create"**

---

## 📰 Fetching News (Enhanced)

### Step 1: Add RSS Feeds
1. Go to **"📡 RSS Feeds"** in sidebar
2. Enter feed details:
   - **Name:** BBC News
   - **URL:** `http://feeds.bbci.co.uk/news/world/rss.xml`
   - **Category:** World News
3. Click **"Add Feed"**

### Step 2: Fetch News
1. Go to **"📰 News Queue"**
2. Click **"Fetch & Verify News"**

**✨ NEW:** The app now:
- ✅ Removes duplicates automatically
- ✅ Deletes news older than 48 hours
- ✅ Shows statistics (new/skipped/cleaned)

### Example Output:
```
✅ Successfully fetched 15 new articles!
🧹 Cleaned up 23 old news (48h+ old)
⏭️ Skipped 8 duplicates
```

---

## ✍️ Creating Articles (Complete Workflow)

### Method 1: AI Complete Rewrite

1. **Select News:**
   - Go to **"✍️ AI Editor"**
   - Click on a news item in the left panel

2. **Generate Draft:**
   - Click **"🤖 Complete AI Rewrite"**
   - Wait for AI to generate 800-1500 word article
   - ✨ **NEW:** Images auto-checked for watermarks

3. **Edit & Format:**
   - Use WYSIWYG toolbar (Bold, Italic, Headings)
   - Add images, lists, formatting
   - ✨ **NEW:** Formatting is preserved on save!

4. **Save Draft:**
   - Click **"💾 Save Draft"**
   - ✨ **NEW:** Draft can now be edited later!

### Method 2: Edit Existing Draft

1. **Open Saved Drafts:**
   - Go to **"📝 Saved Drafts"**
   - Select any draft

2. **Edit:**
   - Click **"✍️ Edit Selected"** (✨ **NOW WORKS!**)
   - Make changes in WYSIWYG editor

3. **Save Changes:**
   - Click **"💾 Save Draft"** again
   - Changes are updated (not duplicated)

---

## 🌐 Translation (Improved Workflow)

### Old Workflow (Confusing):
```
Translate → Preview → ??? → Lost content
```

### **✨ NEW Workflow (Clear):**
```
Translate → Edit Preview → Save as Draft → Publish
```

### Steps:

1. **Save Original Draft First:**
   - Complete your article in English
   - Click **"💾 Save Draft"**

2. **Translate:**
   - Click **"🌐 Translate"** in editor
   - Select target language (200+ options)
   - Click **"Translate"**

3. **Edit Translation:**
   - ✨ **NEW:** Preview window now has editable fields
   - Make any corrections
   - Title and body are fully editable

4. **Save or Publish:**
   - Click **"💾 Save as Editable Draft"** → Creates new draft
   - OR push directly to WordPress

---

## 🔍 Image Watermark Checking

### Automatic Check:
```python
# Happens during AI draft generation
if watermark detected:
    show warning
else:
    safe to use
```

### Manual Check:
1. Enter image URL in editor
2. Click **"🔍 Check Watermark"**
3. Wait for Vision AI analysis
4. See confidence score and recommendation

**Example Results:**
```
⚠️ WATERMARK DETECTED!
Confidence: 0.89
Recommendation: Replace this image
```

---

## 📤 Publishing to WordPress

### Setup (One-Time):

1. **Go to WordPress Settings:**
   - Click **"🔗 WordPress"** in sidebar

2. **Enter Credentials:**
   - **Site URL:** `https://yoursite.com`
   - **Username:** Your WP username
   - **App Password:** Generate in WP Admin

3. **Test Connection:**
   - Click **"🔌 Test"**
   - Should show "✅ Connection successful!"

### Publishing:

1. **In AI Editor:**
   - Complete and save your draft
   - Click **"📤 Push to WordPress"**

2. **✨ NEW: Progress Dialog:**
   - See real-time status
   - No more frozen UI!

3. **Result:**
   ```
   ✅ Published to WordPress!
   Post ID: 123
   URL: https://yoursite.com/?p=123
   Status: Draft (review in WordPress)
   ```

---

## 🧹 Automatic Cleanup (Background)

### What Gets Cleaned:
- News older than **48 hours**
- Only news with status="new" (not processed)
- Orphaned drafts (news deleted)

### When It Runs:
- ✅ Every time you click **"Fetch & Verify News"**
- ✅ On application startup (if enabled)

### Customize:
Edit `core/rss_manager.py`:
```python
self.cleanup_hours = 48  # Change to 24, 72, etc.
```

---

## 🔍 Duplicate Detection

### Three-Layer Protection:

1. **URL Check:**
   - Same URL = Skip
   - Prevents exact duplicates

2. **Headline Check:**
   - Similar headlines = Skip
   - Handles minor variations

3. **Smart Grouping:**
   - Multiple sources same story = Group
   - Shows "[2 src]" tag in queue

### See Statistics:
```
🎉 Total: 15 new | 8 skipped | 23 cleaned
```

---

## ⚠️ Fixed: Edit Selected Button

### Before v2.0:
```python
Click "Edit Selected" → ERROR: Method not found
```

### ✨ After v2.0:
```python
Click "Edit Selected" → Draft loads in editor → Edit → Save
```

**How It Works:**
1. Double-click any draft OR click "Edit Selected"
2. Draft content loads into editor
3. Make changes
4. Click "Save Draft" (updates existing, doesn't duplicate)

---

## ⚙️ Settings & AI Models

### Check Model Status:
1. Go to **"⚙️ Settings"**
2. See all David AI models:
   - ✅ Available = Green
   - ⚠️ Template Mode = Yellow
   - ❌ Not Available = Red

### If Models Not Loaded:
```bash
# Install missing dependencies
pip install sentence-transformers transformers torch

# Download models (first run)
python main.py  # Models auto-download
```

---

## 🐛 Common Issues (v2.0 Fixes)

### 1. **"Edit Selected" Not Working**
✅ **FIXED** in v2.0 - Method fully implemented

### 2. **Formatting Lost on Save**
✅ **FIXED** - HTML export preserves all formatting

### 3. **Too Many Duplicates**
✅ **FIXED** - Duplicate detection enabled

### 4. **Database Growing Too Large**
✅ **FIXED** - 48-hour auto-cleanup

### 5. **No Error Messages**
✅ **FIXED** - All operations show clear feedback

### 6. **Translation Confusion**
✅ **FIXED** - Clear workflow with editable preview

### 7. **Watermark Check Lambda Error**
✅ **FIXED** - Scope issue resolved

---

## 📈 Performance Tips

### For Best Performance:

1. **Limit RSS Feeds:**
   - Max 10-15 active feeds
   - More = slower fetch

2. **Use Cleanup:**
   - Keep default 48-hour cleanup
   - Prevents database bloat

3. **GPU for AI:**
   - Install CUDA version of PyTorch
   - 10x faster AI generation

4. **SSD Storage:**
   - Place database on SSD
   - Faster queries

---

## 🎯 Pro Tips

### 1. Keyboard Shortcuts:
```
Ctrl+S = Save draft (in editor)
Ctrl+N = New workspace
F5 = Refresh news queue
```

### 2. Bulk Operations:
- Select multiple news items (Ctrl+Click)
- Right-click for context menu
- Delete, group, or export

### 3. Workspace Organization:
- Create workspace per website
- Separate feeds by topic
- Use categories consistently

### 4. Quality Control:
- Always check watermarks before publishing
- Review AI-generated content
- Test WordPress connection regularly

---

## 📞 Need Help?

### Logs:
```bash
# Check application log
tail -f nexuzy_publisher.log

# On Windows
type nexuzy_publisher.log
```

### Common Commands:
```bash
# Reinstall dependencies
pip install -r requirements_complete.txt --force-reinstall

# Reset database (CAUTION)
mv nexuzy.db nexuzy.db.backup
python main.py  # Creates fresh DB

# Check Python version
python --version  # Must be 3.8+
```

---

## 🎉 You're Ready!

You now have a complete AI-powered news publishing platform with:
- ✅ Automatic duplicate removal
- ✅ 48-hour news cleanup
- ✅ Full editing workflow
- ✅ 200+ language translation
- ✅ Watermark detection
- ✅ WordPress integration

**Happy Publishing! 🚀**

---

**Version:** 2.0.0  
**Last Updated:** January 27, 2026  
**Support:** Check GitHub issues or logs
