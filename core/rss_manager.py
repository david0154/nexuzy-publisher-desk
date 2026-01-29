"""
RSS Manager - WITH AUTO WEB SEARCH FOR MISSING IMAGES
Fetches news from RSS feeds with intelligent image fallback:
- 8 RSS image extraction methods
- 🆕 Auto web search for related images (Unsplash, Pexels, Pixabay)
- URL-based duplicate detection
- Headline similarity checking  
- 48-hour automatic cleanup
"""

import sqlite3
import logging
import hashlib
from datetime import datetime, timedelta
from urllib.parse import urlparse, quote
import re
import json

try:
    import feedparser
    from bs4 import BeautifulSoup
    import requests
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

logger = logging.getLogger(__name__)


class RSSManager:
    """Manage RSS feeds with auto web search for missing images"""
    
    def __init__(self, db_path='nexuzy.db'):
        self.db_path = db_path
        self.cleanup_hours = 48
        self.max_entries_per_feed = 20
        self.enable_web_search = True  # Enable auto web search for images
    
    def _generate_url_hash(self, url):
        """Generate unique hash for URL deduplication"""
        if not url:
            return None
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
        cursor.execute('''
            SELECT COUNT(*) FROM news_queue 
            WHERE workspace_id = ? AND headline = ?
        ''', (workspace_id, headline))
        
        if cursor.fetchone()[0] > 0:
            return True
        
        headline_prefix = headline[:50].lower()
        cursor.execute('''
            SELECT COUNT(*) FROM news_queue 
            WHERE workspace_id = ? AND LOWER(SUBSTR(headline, 1, 50)) = ?
        ''', (workspace_id, headline_prefix))
        
        return cursor.fetchone()[0] > 0
    
    def get_placeholder_image(self, workspace_id):
        """Get default placeholder image URL from settings"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(ads_settings)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'placeholder_image' in columns:
                cursor.execute('SELECT placeholder_image FROM ads_settings WHERE workspace_id = ?', (workspace_id,))
                result = cursor.fetchone()
                conn.close()
                
                if result and result[0]:
                    return result[0]
            
            conn.close()
            return "https://via.placeholder.com/1200x630/3498db/ffffff?text=Nexuzy+Publisher+Desk"
            
        except Exception as e:
            logger.error(f"Error getting placeholder: {e}")
            return "https://via.placeholder.com/1200x630/3498db/ffffff?text=Nexuzy+Publisher+Desk"
    
    def cleanup_old_news(self, workspace_id, hours=None):
        """Delete news older than specified hours (default 48)"""
        if hours is None:
            hours = self.cleanup_hours
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cutoff_str = cutoff_time.isoformat()
            
            cursor.execute('''
                DELETE FROM news_queue 
                WHERE workspace_id = ? 
                AND fetched_at < ?
                AND status = 'new'
            ''', (workspace_id, cutoff_str))
            
            deleted_count = cursor.rowcount
            
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
            from dateutil import parser
            pub_date = parser.parse(publish_date_str)
            today = datetime.now().date()
            return pub_date.date() == today
        except:
            return True
    
    def _is_valid_image_url(self, url):
        """Validate if URL looks like an image URL"""
        if not url:
            return False
        
        url_lower = url.lower()
        
        if url_lower.startswith('data:image'):
            return False
        
        if not url_lower.startswith(('http://', 'https://')):
            return False
        
        image_indicators = [
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',
            '/image/', '/images/', '/img/', '/media/',
            'image=', 'img=', 'photo', 'picture'
        ]
        
        return any(indicator in url_lower for indicator in image_indicators)
    
    def _extract_search_keywords(self, headline, category=""):
        """
        🆕 Extract keywords from headline for image search
        """
        # Remove common filler words
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                      'says', 'new', 'announces', 'launches', 'reports', 'reveals']
        
        # Clean headline
        words = re.findall(r'\b[a-zA-Z]{3,}\b', headline.lower())
        keywords = [w for w in words if w not in stop_words]
        
        # Take top 3-4 most important words
        search_query = ' '.join(keywords[:4])
        
        # Add category context if available
        if category and category.lower() not in ['general', 'news']:
            search_query = f"{category} {search_query}"
        
        return search_query[:60]  # Limit query length
    
    def _search_free_stock_images(self, query):
        """
        🆕 Search free stock photo sites for related images
        Returns: image_url or None
        """
        try:
            logger.info(f"🔍 Web searching images for: '{query}'")
            
            # Method 1: Unsplash API (No API key needed for basic search)
            try:
                unsplash_url = f"https://source.unsplash.com/1200x630/?{quote(query)}"
                response = requests.head(unsplash_url, timeout=5, allow_redirects=True)
                
                if response.status_code == 200:
                    final_url = response.url
                    logger.info(f"✅ Found Unsplash image: {final_url[:80]}")
                    return final_url
            except Exception as e:
                logger.debug(f"Unsplash search failed: {e}")
            
            # Method 2: Pexels API (Free tier available)
            # Note: Requires API key - users should add their own
            # For now, skip if no key available
            
            # Method 3: Pixabay (Similar to Unsplash)
            try:
                # Pixabay direct image search (no API key needed for basic)
                pixabay_search = f"https://pixabay.com/en/photos/search/{quote(query)}/"
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(pixabay_search, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    img_tags = soup.find_all('img', class_=re.compile('.*?'))
                    
                    for img in img_tags:
                        src = img.get('src') or img.get('data-lazy')
                        if src and self._is_valid_image_url(src) and 'pixabay' in src:
                            # Get full-size version
                            full_url = src.replace('_640', '_1280')
                            logger.info(f"✅ Found Pixabay image: {full_url[:80]}")
                            return full_url
            except Exception as e:
                logger.debug(f"Pixabay search failed: {e}")
            
            logger.warning(f"⚠️ Web image search found nothing for: '{query}'")
            return None
            
        except Exception as e:
            logger.error(f"❌ Web search error: {e}")
            return None
    
    def extract_image_from_entry(self, entry, headline="", category=""):
        """
        Extract image URL from RSS entry with 8 methods + web search fallback
        """
        image_url = None
        method_used = None
        
        # Method 1: media:content tags
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if 'image' in media.get('type', '').lower():
                    image_url = media.get('url')
                    if self._is_valid_image_url(image_url):
                        method_used = "media:content"
                        break
        
        # Method 2: media:thumbnail tags
        if not image_url and hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
            if isinstance(entry.media_thumbnail, list) and len(entry.media_thumbnail) > 0:
                image_url = entry.media_thumbnail[0].get('url')
                if self._is_valid_image_url(image_url):
                    method_used = "media:thumbnail"
        
        # Method 3: Enclosures
        if not image_url and hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                enc_type = enclosure.get('type', '').lower()
                enc_url = enclosure.get('href', '')
                if 'image' in enc_type or self._is_valid_image_url(enc_url):
                    image_url = enc_url
                    method_used = "enclosure"
                    break
        
        # Method 4: Summary/description HTML <img>
        if not image_url:
            summary = entry.get('summary', entry.get('description', ''))
            if summary:
                soup = BeautifulSoup(summary, 'html.parser')
                img_tag = soup.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag.get('src')
                    if self._is_valid_image_url(image_url):
                        method_used = "summary <img>"
        
        # Method 5: Content HTML <img>
        if not image_url and hasattr(entry, 'content') and entry.content:
            for content in entry.content:
                soup = BeautifulSoup(content.get('value', ''), 'html.parser')
                img_tag = soup.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag.get('src')
                    if self._is_valid_image_url(image_url):
                        method_used = "content <img>"
                        break
        
        # Method 6: OpenGraph images
        if not image_url:
            summary = entry.get('summary', entry.get('description', ''))
            if summary:
                soup = BeautifulSoup(summary, 'html.parser')
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    image_url = og_image.get('content')
                    if self._is_valid_image_url(image_url):
                        method_used = "og:image meta"
        
        # Method 7: Twitter Card images
        if not image_url:
            summary = entry.get('summary', entry.get('description', ''))
            if summary:
                soup = BeautifulSoup(summary, 'html.parser')
                twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
                if twitter_image and twitter_image.get('content'):
                    image_url = twitter_image.get('content')
                    if self._is_valid_image_url(image_url):
                        method_used = "twitter:image meta"
        
        # Method 8: Link tags with image rel
        if not image_url and hasattr(entry, 'links'):
            for link in entry.links:
                if link.get('rel') == 'image' or 'image' in link.get('type', '').lower():
                    link_url = link.get('href')
                    if self._is_valid_image_url(link_url):
                        image_url = link_url
                        method_used = "link rel=image"
                        break
        
        # 🆕 Method 9: WEB SEARCH FOR RELATED IMAGES
        if not image_url and self.enable_web_search and headline:
            logger.info(f"🌐 No RSS image - trying web search for: {headline[:50]}")
            search_query = self._extract_search_keywords(headline, category)
            web_image = self._search_free_stock_images(search_query)
            
            if web_image:
                image_url = web_image
                method_used = "web search (Unsplash/Pixabay)"
        
        # Final validation
        if image_url and not self._is_valid_image_url(image_url):
            logger.debug(f"❌ Invalid image URL rejected: {image_url[:80]}")
            image_url = None
            method_used = None
        
        # Logging
        if image_url:
            logger.info(f"✅ Image found via [{method_used}]: {image_url[:80]}... for '{headline[:40]}...'")
        else:
            logger.warning(f"⚠️ NO IMAGE found for: {headline[:60]}... (tried 9 methods including web search)")
        
        return image_url
    
    def fetch_news_from_feeds(self, workspace_id, today_only=False):
        """
        Fetch latest news from all active RSS feeds with auto web search for images
        
        Args:
            workspace_id: Current workspace
            today_only: If True, only fetch today's news
        """
        
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("RSS Manager requires feedparser and beautifulsoup4")
        
        placeholder_image = self.get_placeholder_image(workspace_id)
        
        logger.info("🧹 Running 48-hour cleanup...")
        deleted_count = self.cleanup_old_news(workspace_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
        images_from_rss = 0
        images_from_web = 0
        images_placeholder = 0
        
        for feed_id, feed_name, feed_url, category in feeds:
            try:
                logger.info(f"📰 Fetching from: {feed_name} ({feed_url})")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                try:
                    response = requests.get(feed_url, headers=headers, timeout=10)
                    feed = feedparser.parse(response.content)
                except:
                    feed = feedparser.parse(feed_url)
                
                if not feed.entries:
                    logger.warning(f"⚠️ No entries found in feed: {feed_url}")
                    continue
                
                logger.info(f"✅ Found {len(feed.entries)} entries in {feed_name}")
                
                for entry in feed.entries[:self.max_entries_per_feed]:
                    try:
                        headline = entry.get('title', 'No title').strip()
                        summary = entry.get('summary', entry.get('description', ''))
                        
                        if summary:
                            soup = BeautifulSoup(summary, 'html.parser')
                            summary = soup.get_text(separator=' ', strip=True)[:800]
                        
                        source_url = entry.get('link', '')
                        
                        if not headline or len(headline) < 10:
                            continue
                        
                        publish_date = entry.get('published', entry.get('updated', datetime.now().isoformat()))
                        
                        if today_only and not self._is_today_news(publish_date):
                            total_skipped += 1
                            continue
                        
                        if self._check_duplicate_url(conn, workspace_id, source_url):
                            total_skipped += 1
                            continue
                        
                        if self._check_duplicate_headline(conn, workspace_id, headline):
                            total_skipped += 1
                            continue
                        
                        source_domain = urlparse(source_url).netloc if source_url else feed_name
                        source_domain = source_domain.replace('www.', '')
                        
                        # 🔍 EXTRACT IMAGE (8 RSS methods + web search)
                        image_url = self.extract_image_from_entry(entry, headline, category)
                        
                        # Track image source
                        if image_url:
                            if 'unsplash' in image_url.lower() or 'pixabay' in image_url.lower():
                                images_from_web += 1
                            else:
                                images_from_rss += 1
                        else:
                            images_placeholder += 1
                            image_url = placeholder_image
                            logger.debug(f"📷 Using placeholder for: {headline[:50]}")
                        
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
        result_msg += f"\n📷 Images: {images_from_rss} from RSS, {images_from_web} from web search, {images_placeholder} placeholder"
        if deleted_count > 0:
            result_msg += f"\n🧹 Cleaned up {deleted_count} old news (48h+ old)"
        if total_skipped > 0:
            result_msg += f"\n⏭️ Skipped {total_skipped} duplicates"
        
        logger.info(f"🎉 Total: {total_fetched} new | RSS:{images_from_rss} | Web:{images_from_web} | Placeholder:{images_placeholder}")
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
    
    def delete_feed(self, feed_id):
        """Delete an RSS feed by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT feed_name FROM rss_feeds WHERE id = ?', (feed_id,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, "Feed not found"
            
            feed_name = result[0]
            cursor.execute('DELETE FROM rss_feeds WHERE id = ?', (feed_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"🗑️ Deleted feed: {feed_name}")
            return True, f"Feed '{feed_name}' deleted successfully"
            
        except Exception as e:
            logger.error(f"Error deleting feed: {e}")
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
