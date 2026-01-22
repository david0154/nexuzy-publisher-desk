# Quick Fix Guide

## Database Schema Errors

If you see errors like:
- `no such column: feed_name`
- `no such column: category`
- `table rss_feeds has no column named name`

### Solution: Delete Old Database

```powershell
# Stop the application if running

# Delete old database
rm nexuzy.db

# OR use the fix script
python fix_database.py

# Then restart
python main.py
```

The application will automatically create a new database with the correct schema.

## Missing Dependencies

If RSS fetching doesn't work:

```powershell
pip install feedparser beautifulsoup4 requests Pillow
```

## Translation Not Working

Translation requires the NLLB model:

```powershell
pip install transformers torch sentencepiece sacremoses
```

First translation will download the model (~1.2GB).

## Logo/Icon Not Showing

Create the resources folder:

```powershell
mkdir resources
# Add your files:
# resources/logo.png (40x40 pixels)
# resources/icon.ico (Windows icon format)
```

## Complete Fresh Install

```powershell
# Pull latest
git pull

# Delete old database
rm nexuzy.db

# Install all dependencies
pip install -r requirements.txt

# Run
python main.py
```
