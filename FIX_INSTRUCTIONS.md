# 🔧 Fix Instructions for Nexuzy Publisher Desk

## Issues Fixed in This Update

### 1. Database Error: `no such column: source_domain`
**Problem**: The translator module was trying to access a `source_domain` column that doesn't exist in the `ai_drafts` table.

**Solution**: Run the migration script to add missing columns.

### 2. WordPress 401 Authentication Error
**Problem**: WordPress authentication failing with "rest_cannot_create" error.

**Solution**: Properly configure WordPress Application Password.

---

## Quick Fix (5 Minutes)

### Step 1: Run Database Migration

Open terminal in your project directory and run:

```bash
python fix_source_domain_column.py
```

You should see:
```
============================================================
✅ DATABASE MIGRATION COMPLETE!
You can now run the application without errors.
============================================================
```

### Step 2: Fix WordPress Authentication

#### A. Generate WordPress Application Password

1. **Log in to your WordPress admin panel**
   - Go to: `https://yoursite.com/wp-admin`

2. **Navigate to your profile**
   - Click on **Users** → **Profile**
   - Or go directly to: `https://yoursite.com/wp-admin/profile.php`

3. **Scroll down to "Application Passwords" section**
   - If you don't see this section, your WordPress version might be too old (requires WordPress 5.6+)
   - Or application passwords might be disabled

4. **Create new Application Password**
   - Enter a name: `Nexuzy Publisher`
   - Click **Add New Application Password**
   - **IMPORTANT**: Copy the generated password immediately (it looks like: `xxxx xxxx xxxx xxxx xxxx xxxx`)
   - Remove the spaces when pasting into Nexuzy

#### B. Configure in Nexuzy Publisher Desk

1. Open Nexuzy Publisher Desk
2. Go to **WordPress** section in the sidebar
3. Enter your details:
   - **Site URL**: `https://yoursite.com` (without trailing slash)
   - **Username**: Your WordPress username (NOT email)
   - **App Password**: The password you copied (remove spaces)

4. Click **Test** button
5. You should see: ✅ Connection successful!

---

## Troubleshooting

### Database Migration Failed

**Error**: Database not found
```bash
# Make sure you're in the project directory
cd /path/to/nexuzy-publisher-desk
python fix_source_domain_column.py
```

**Error**: Permission denied
```bash
# On Linux/Mac, you might need to make it executable
chmod +x fix_source_domain_column.py
python fix_source_domain_column.py
```

### WordPress Connection Still Failing

#### Check 1: REST API Enabled
Visit: `https://yoursite.com/wp-json/wp/v2/users/me`

- **If you see JSON data or "rest_not_logged_in"**: REST API is working ✅
- **If you see 404 or blank page**: REST API is disabled ❌

**To enable REST API:**
1. Check if any security plugin is blocking it (WordFence, All In One WP Security, etc.)
2. Add this to your `wp-config.php` if needed:
   ```php
   add_filter('rest_authentication_errors', function($result) {
       if (!empty($result)) {
           return $result;
       }
       return true;
   });
   ```

#### Check 2: Application Password Format

❌ **Wrong**: `xxxx xxxx xxxx xxxx` (with spaces)
✅ **Correct**: `xxxxxxxxxxxxxxxx` (no spaces)

#### Check 3: Username vs Email

Make sure you're using your **WordPress username**, not your email address.

To find your username:
1. Go to WordPress admin → Users → All Users
2. Hover over your name
3. Look at the URL: `user_id=1&user=YOUR_USERNAME_HERE`

#### Check 4: SSL/HTTPS Issues

If your site has SSL certificate issues:
```python
# Temporary fix (not recommended for production)
# In wordpress_api.py, add:
self.session.verify = False
```

---

## Verification

### Test Database Fix

1. Open Nexuzy Publisher Desk
2. Go to **Translations** section
3. Try to translate any draft
4. Should work without "source_domain" error

### Test WordPress Fix

1. Open Nexuzy Publisher Desk
2. Go to **AI Editor**
3. Generate or load a draft
4. Click **Push to WordPress**
5. Check your WordPress admin → Posts → All Posts
6. You should see the new draft post

---

## Complete Workflow Test

1. **Fetch News**
   - Go to **RSS Feeds** → Add a feed (e.g., `https://rss.nytimes.com/services/xml/rss/nyt/World.xml`)
   - Go to **News Queue** → Click **Fetch & Verify News**
   - Verify news items appear

2. **Generate Draft**
   - Go to **AI Editor**
   - Select a news item from the left
   - Click **Complete AI Rewrite**
   - Verify generated article appears on the right

3. **Translate**
   - Click **Translate** button
   - Select target language (e.g., Spanish)
   - Verify translation appears
   - Click **Save as Editable Draft**

4. **Publish to WordPress**
   - With the draft loaded in editor
   - Click **Push to WordPress**
   - Check WordPress admin to see the draft post

---

## Need More Help?

### Check Logs

Logs are saved in: `nexuzy_publisher.log`

```bash
# View recent logs
tail -f nexuzy_publisher.log

# Search for errors
grep ERROR nexuzy_publisher.log
```

### Common Log Messages

**Database Issues:**
```
ERROR - no such column: source_domain
→ Solution: Run fix_source_domain_column.py
```

**WordPress Issues:**
```
ERROR - WordPress connection failed: 401
→ Solution: Regenerate Application Password

ERROR - rest_cannot_create
→ Solution: Check user permissions in WordPress
```

**Translation Issues:**
```
WARNING - AI translation failed. Using fallback.
→ Normal: Fallback template will be used
→ To fix: Install transformers: pip install transformers torch
```

---

## Updates Applied

- ✅ Added `source_domain` column to `ai_drafts` table
- ✅ Added `is_html` column to `ai_drafts` table
- ✅ Added `created_at` column to `ai_drafts` table
- ✅ Enhanced WordPress authentication with better error handling
- ✅ Improved image upload process (download → cache → upload)
- ✅ Fixed translation workflow to save as new drafts
- ✅ Added comprehensive logging for debugging

---

## 🚀 You're All Set!

After running the migration script and configuring WordPress credentials properly, your Nexuzy Publisher Desk should work flawlessly.

Happy publishing! 📰✨
