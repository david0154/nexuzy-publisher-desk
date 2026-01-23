# 🚀 Quick Fix Guide - Apply in 3 Minutes

## Your Errors:

```
❌ Error translating draft: no such column: source_domain
❌ WordPress connection test failed with status code: 401
⚠️ GGUF model not found (optional - app still works)
```

---

## 🔧 Fix It Now (3 Steps)

### Step 1: Update Code (30 seconds)

```bash
cd nexuzy-publisher-desk
git pull origin main
```

You should see:
```
Updating files:
  migrate_database.py
  fix_database.py
  core/translator.py
  + new documentation files
```

---

### Step 2: Fix Database (1 minute)

```bash
python fix_database.py
```

**Expected output:**
```
============================================================
NEXUZY PUBLISHER DESK - DATABASE FIX
============================================================
Fixing database: nexuzy.db

✅ Successfully added: source_url
✅ Successfully added: source_domain

============================================================
✅ DATABASE FIX COMPLETE! Applied 2 fixes.
============================================================
```

**If you see "already exists":** Your database is up to date! ✅

---

### Step 3: Fix WordPress Auth (2 minutes)

#### A. Generate New Password

**Go to WordPress:**
- Dashboard → Users → Profile
- Scroll to **Application Passwords**
- Name: "Nexuzy"
- Click **Add New**
- Copy the password (looks like: `xxxx xxxx xxxx xxxx xxxx xxxx`)

#### B. Update in App

**In Nexuzy Publisher Desk:**
1. Open the app: `python main.py`
2. Go to **WordPress API** tab
3. Enter:
   - **Site URL:** `https://jiveglow.xyz`
   - **Username:** (your WordPress username)
   - **Password:** (paste the app password, remove spaces)
4. Click **Test Connection**

**Expected:** ✅ **Connected successfully**

---

## ✅ Done!

Test translation:
1. Go to **AI Drafts** tab
2. Select a draft
3. Click **Translate**
4. Choose language
5. Should work without errors ✅

Push to WordPress:
1. Select translated draft
2. Click **Push to WordPress**
3. Should upload successfully ✅

---

## ❌ Still Having Issues?

### Database Error Still Appears:

```bash
# Check if columns exist
sqlite3 nexuzy.db "PRAGMA table_info(ai_drafts);" | grep source
```

Should show:
```
8|source_url|TEXT|0||0
9|source_domain|TEXT|0||0
```

If not, run:
```bash
python migrate_database.py
```

### WordPress Still 401:

1. Check if REST API works:
   ```bash
   curl https://jiveglow.xyz/wp-json/wp/v2/posts
   ```
   Should return JSON, not 404

2. Test credentials:
   ```bash
   curl -u "username:apppassword" https://jiveglow.xyz/wp-json/wp/v2/users/me
   ```
   Should return your user info

3. Read detailed guide: [`WORDPRESS_AUTH_FIX.md`](WORDPRESS_AUTH_FIX.md)

---

## 📚 Full Documentation

- [`FIX_SUMMARY.md`](FIX_SUMMARY.md) - Complete technical details
- [`WORDPRESS_AUTH_FIX.md`](WORDPRESS_AUTH_FIX.md) - WordPress troubleshooting
- [`QUICK_START.md`](QUICK_START.md) - Getting started guide

---

## 📝 Changelog

**What was fixed:**

✅ **Database:**
- Added `source_url` column to ai_drafts
- Added `source_domain` column to ai_drafts  
- Made translator.py check for columns dynamically
- Better error messages with fix instructions

✅ **Documentation:**
- Complete WordPress auth troubleshooting
- Step-by-step fix guides
- Verification commands

✅ **Error Handling:**
- Graceful fallbacks for missing columns
- Helpful error messages
- Automatic detection of schema issues

---

**Total time to fix: ~3 minutes** ⏱️

**After fixes, you can:**
- ✅ Translate drafts to 200+ languages
- ✅ Push directly to WordPress
- ✅ No more database errors
- ✅ Full app functionality restored

🎉 **Enjoy your fixed Nexuzy Publisher Desk!**
