"""
RSS Manager - Enhanced with Duplicate Detection & Auto-Cleanup
Fetches news from RSS feeds with advanced filtering
- URL-based duplicate detection
- Headline similarity checking  
- 48-hour automatic news cleanup
- Today's news only option
"""

import sqlite3
import logging
import hashlib
from datetime import datetime, timedelta
from urllib.parse import urlparse
import re

try:
    import feedparser
    from bs4 import BeautifulSoup
    import requests
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

logger = logging.getLogger(__name__)


class RSSManager:
    """Manage RSS feeds and fetch news articles with images"""
    
    def __init__(self, db_path='nexuzy.db'):
        self.db_path = db_path
        self.cleanup_hours = 48  # Auto-delete news older than 48 hours
        self.max_entries_per_feed = 20
    
    def _generate_url_hash(self, url):
        """Generate unique hash for URL deduplication"""
        if not url:
            return None
        # Normalize URL (remove query params, trailing slash)
        clean_url = url.split('?')[0].rstrip('/')
        return hashlib.md5(clean_url.encode()).hexdigest()
    
    def _check_duplicate_url(self, conn, workspace_id, url):
        """Check if URL already exists in database"""
        if not url:
            return False
        
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM news_queue 
            WHERE workspace_id = ? AND source_url = ?
        ''', (workspace_id, url))
        
        return cursor.fetchone()[0] > 0
    
    def _check_duplicate_headline(self, conn, workspace_id, headline):
        """Check if similar headline already exists"""
        if not headline or len(headline) < 10:
            return False
        
        cursor = conn.cursor()
        # Check exact match first
        cursor.execute('''
            SELECT COUNT(*) FROM news_queue 
            WHERE workspace_id = ? AND headline = ?
        ''', (workspace_id, headline))
        
        if cursor.fetchone()[0] > 0:
            return True
        
        # Check for very similar headlines (first 50 chars)
        headline_prefix = headline[:50].lower()
        cursor.execute('''
            SELECT COUNT(*) FROM news_queue 
            WHERE workspace_id = ? AND LOWER(SUBSTR(headline, 1, 50)) = ?
        ''', (workspace_id, headline_prefix))
        
        return cursor.fetchone()[0] > 0
    
    def cleanup_old_news(self, workspace_id, hours=None):
        """Delete news older than specified hours (default 48)"""
        if hours is None:
            hours = self.cleanup_hours
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate cutoff time
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cutoff_str = cutoff_time.isoformat()
            
            # Delete old news
            cursor.execute('''
                DELETE FROM news_queue 
                WHERE workspace_id = ? 
                AND fetched_at < ?
                AND status = 'new'
            ''', (workspace_id, cutoff_str))
            
            deleted_count = cursor.rowcount
            
            # Also clean up orphaned drafts (news_id no longer exists)
            cursor.execute('''
                DELETE FROM ai_drafts 
                WHERE workspace_id = ? 
                AND news_id NOT IN (SELECT id FROM news_queue)
            ''', (workspace_id,))
            
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                logger.info(f"✅ Cleaned up {deleted_count} old news items (>{hours}h)")
            
            return deleted_count
        
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")
            return 0
    
    def _is_today_news(self, publish_date_str):
        """Check if news is from today"""
        try:
            # Parse various date formats
            from dateutil import parser
            pub_date = parser.parse(publish_date_str)
            today = datetime.now().date()
            return pub_date.date() == today
        except:
            # If can't parse, assume it's recent
            return True
    
    def extract_image_from_entry(self, entry):
        """Extract image URL from RSS entry"""
        image_url = None
        
        # Method 1: Check media content
        if hasattr(entry, 'media_content'):
            for media in entry.media_content:
                if 'image' in media.get('type', ''):
                    image_url = media.get('url')
                    break
        
        # Method 2: Check media thumbnail
        if not image_url and hasattr(entry, 'media_thumbnail'):
            if entry.media_thumbnail:
                image_url = entry.media_thumbnail[0].get('url')
        
        # Method 3: Check enclosures
        if not image_url and hasattr(entry, 'enclosures'):
            for enclosure in entry.enclosures:
                if 'image' in enclosure.get('type', ''):
                    image_url = enclosure.get('href')
                    break
        
        # Method 4: Parse from summary/description HTML
        if not image_url:
            summary = entry.get('summary', entry.get('description', ''))
            if summary:
                soup = BeautifulSoup(summary, 'html.parser')
                img_tag = soup.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag.get('src')
        
        # Method 5: Check for image in content
        if not image_url and hasattr(entry, 'content'):
            for content in entry.content:
                soup = BeautifulSoup(content.get('value', ''), 'html.parser')
                img_tag = soup.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag.get('src')
                    break
        
        return image_url
    
    def fetch_news_from_feeds(self, workspace_id, today_only=False):
        """
        Fetch latest news from all active RSS feeds with images
        
        Args:
            workspace_id: Current workspace
            today_only: If True, only fetch today's news
        """
        
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("RSS Manager requires feedparser and beautifulsoup4. Install with: pip install feedparser beautifulsoup4 requests")
        
        # First, cleanup old news (48-hour auto-delete)
        logger.info("🧹 Running 48-hour cleanup...")
        deleted_count = self.cleanup_old_news(workspace_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all active feeds for this workspace
        cursor.execute('''
            SELECT id, feed_name, url, category 
            FROM rss_feeds 
            WHERE workspace_id = ? AND enabled = 1
        ''', (workspace_id,))
        
        feeds = cursor.fetchall()
        
        if not feeds:
            conn.close()
            return 0, "No RSS feeds configured. Add some feeds first!"
        
        total_fetched = 0
        total_skipped = 0
        
        for feed_id, feed_name, feed_url, category in feeds:
            try:
                # Parse RSS feed with timeout
                logger.info(f"📰 Fetching from: {feed_name} ({feed_url})")
                
                # Use requests with User-Agent to avoid blocks
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                try:
                    response = requests.get(feed_url, headers=headers, timeout=10)
                    feed = feedparser.parse(response.content)
                except:
                    # Fallback to direct feedparser
                    feed = feedparser.parse(feed_url)
                
                if not feed.entries:
                    logger.warning(f"⚠️ No entries found in feed: {feed_url}")
                    continue
                
                logger.info(f"✅ Found {len(feed.entries)} entries in {feed_name}")
                
                # Process each entry (limit to configured max)
                for entry in feed.entries[:self.max_entries_per_feed]:
                    try:
                        # Extract data
                        headline = entry.get('title', 'No title').strip()
                        
                        # Get summary/description
                        summary = entry.get('summary', entry.get('description', ''))
                        
                        # Clean HTML from summary
                        if summary:
                            soup = BeautifulSoup(summary, 'html.parser')
                            summary = soup.get_text(separator=' ', strip=True)[:800]
                        
                        source_url = entry.get('link', '')
                        
                        # Skip if no valid data
                        if not headline or len(headline) < 10:
                            continue
                        
                        # Get publish date
                        publish_date = entry.get('published', entry.get('updated', datetime.now().isoformat()))
                        
                        # Filter: Today only if requested
                        if today_only and not self._is_today_news(publish_date):
                            total_skipped += 1
                            continue
                        
                        # DUPLICATE CHECK #1: URL
                        if self._check_duplicate_url(conn, workspace_id, source_url):
                            total_skipped += 1
                            continue
                        
                        # DUPLICATE CHECK #2: Headline
                        if self._check_duplicate_headline(conn, workspace_id, headline):
                            total_skipped += 1
                            continue
                        
                        # Get domain
                        source_domain = urlparse(source_url).netloc if source_url else feed_name
                        source_domain = source_domain.replace('www.', '')
                        
                        # Extract image URL
                        image_url = self.extract_image_from_entry(entry)
                        
                        # Insert into news_queue
                        cursor.execute('''
                            INSERT INTO news_queue 
                            (workspace_id, headline, summary, source_url, source_domain, 
                             category, publish_date, status, image_url, fetched_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 'new', ?, CURRENT_TIMESTAMP)
                        ''', (workspace_id, headline, summary, source_url, source_domain, 
                              category or 'General', publish_date, image_url))
                        
                        total_fetched += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Error processing entry: {e}")
                        continue
                
                logger.info(f"✅ Fetched {total_fetched} new articles from {feed_name}")
                
            except Exception as e:
                logger.error(f"❌ Error fetching feed {feed_url}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        result_msg = f"✅ Successfully fetched {total_fetched} new articles!"
        if deleted_count > 0:
            result_msg += f"\n🧹 Cleaned up {deleted_count} old news (48h+ old)"
        if total_skipped > 0:
            result_msg += f"\n⏭️ Skipped {total_skipped} duplicates"
        
        logger.info(f"🎉 Total: {total_fetched} new | {total_skipped} skipped | {deleted_count} cleaned")
        return total_fetched, result_msg
    
    def add_feed(self, workspace_id, feed_name, feed_url, category='General'):
        """Add a new RSS feed"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO rss_feeds (workspace_id, feed_name, url, category, enabled)
                VALUES (?, ?, ?, ?, 1)
            ''', (workspace_id, feed_name, feed_url, category))
            
            conn.commit()
            conn.close()
            return True, "Feed added successfully"
            
        except sqlite3.IntegrityError:
            conn.close()
            return False, "Feed already exists"
        except Exception as e:
            conn.close()
            return False, str(e)
    
    def get_feeds(self, workspace_id):
        """Get all feeds for workspace"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, feed_name, url, category, enabled 
            FROM rss_feeds 
            WHERE workspace_id = ?
            ORDER BY added_at DESC
        ''', (workspace_id,))
        
        feeds = cursor.fetchall()
        conn.close()
        
        return feeds
    
    def get_news_count(self, workspace_id, hours=48):
        """Get count of news within specified hours"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cutoff_str = cutoff_time.isoformat()
            
            cursor.execute('''
                SELECT COUNT(*) FROM news_queue 
                WHERE workspace_id = ? AND fetched_at >= ?
            ''', (workspace_id, cutoff_str))
            
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
