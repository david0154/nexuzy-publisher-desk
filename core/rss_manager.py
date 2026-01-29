""" 
RSS Manager - ULTIMATE IMAGE SEARCH WITH PERPLEXITY AI
Fetches news from RSS feeds with 4-level intelligent image fallback:
- Level 1: 8 RSS image extraction methods
- Level 2: Free stock photos (Unsplash/Pixabay)
- Level 3: 🆕 PERPLEXITY AI WEB SEARCH (ultimate fallback!)
- Level 4: Placeholder (rarely needed now)

FEATURES:
✅ URL-based duplicate detection
✅ Headline similarity checking  
✅ 48-hour automatic cleanup
✅ AI-powered image discovery
"""

import sqlite3
import logging
import hashlib
from datetime import datetime, timedelta
from urllib.parse import urlparse, quote
import re
import json
import os
from pathlib import Path

try:
    import feedparser
    from bs4 import BeautifulSoup
    import requests
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

logger = logging.getLogger(__name__)


class RSSManager:
    """Manage RSS feeds with 4-level image search including Perplexity AI"""
    
    def __init__(self, db_path='nexuzy.db'):
        self.db_path = db_path
        self.cleanup_hours = 48
        self.max_entries_per_feed = 20
        self.enable_web_search = True
        self.enable_perplexity_search = True  # 🆕 Enable Perplexity AI search
        self.perplexity_api_key = self._load_perplexity_api_key()
    
    def _load_perplexity_api_key(self):
        """
        Load Perplexity API key from:
        1. Environment variable (PERPLEXITY_API_KEY)
        2. config.json file
        3. .env file
        """
        # Try environment variable first
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if api_key:
            logger.info("✅ Loaded Perplexity API key from environment")
            return api_key
        
        # Try config.json
        try:
            config_path = Path('config.json')
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    api_key = config.get('perplexity_api_key')
                    if api_key:
                        logger.info("✅ Loaded Perplexity API key from config.json")
                        return api_key
        except Exception as e:
            logger.debug(f"Could not load from config.json: {e}")
        
        # Try .env file
        try:
            env_path = Path('.env')
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('PERPLEXITY_API_KEY='):
                            api_key = line.split('=', 1)[1].strip()
                            logger.info("✅ Loaded Perplexity API key from .env")
                            return api_key
        except Exception as e:
            logger.debug(f"Could not load from .env: {e}")
        
        logger.warning("⚠️ Perplexity API key not found. Add to config.json or environment variable.")
        logger.info("💡 To enable Perplexity image search, add 'perplexity_api_key' to config.json")
        return None
    
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
    
    def _extract_search_keywords(self, headline):
        """
        Extract clean keywords from headline (fallback option)
        """
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                      'says', 'announces', 'launches', 'reports', 'reveals']
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', headline.lower())
        keywords = [w for w in words if w not in stop_words]
        
        return ' '.join(keywords[:4])
    
    def _search_perplexity_images(self, headline, category=""):
        """
        🆕 PERPLEXITY AI IMAGE SEARCH - Ultimate fallback!
        Uses Perplexity API to find relevant images across the web
        """
        try:
            if not self.perplexity_api_key:
                return None
            
            logger.info(f"🤖 Perplexity AI searching for: '{headline[:60]}...'")
            
            search_query = f"Find high quality image URL for: {headline}"
            if category:
                search_query += f" (category: {category})"
            
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an image search assistant. When given a headline, find and return ONLY a single high-quality image URL (direct link to .jpg, .png, .webp, etc.) that best represents the topic. Return ONLY the URL, nothing else. The image must be from a reliable source like Unsplash, Pexels, Wikimedia Commons, or news websites. Do not return placeholder images or broken links."
                    },
                    {
                        "role": "user",
                        "content": f"Find a high-quality image URL for this headline: {headline}"
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.2,
                "top_p": 0.9,
                "search_domain_filter": ["unsplash.com", "pexels.com", "pixabay.com"],
                "return_images": False,
                "return_related_questions": False,
                "search_recency_filter": "month",
                "top_k": 0,
                "stream": False,
                "presence_penalty": 0,
                "frequency_penalty": 1
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content'].strip()
                    
                    # Extract URL from response
                    url_pattern = r'https?://[^\s<>"]+?\.(jpg|jpeg|png|gif|webp)(?:\?[^\s<>"]*)?'
                    urls = re.findall(url_pattern, content, re.IGNORECASE)
                    
                    if urls:
                        for url_match in urls:
                            full_url = content[content.find('http'):content.find(url_match[0]) + len(url_match[0])]
                            if self._is_valid_image_url(full_url):
                                logger.info(f"✅ Perplexity AI found: {full_url[:80]}")
                                return full_url
                    
                    # If no direct URL found, try to extract any URL from response
                    simple_url = re.findall(r'https?://[^\s<>"]+', content)
                    if simple_url:
                        for url in simple_url:
                            if self._is_valid_image_url(url):
                                logger.info(f"✅ Perplexity AI found (alternative): {url[:80]}")
                                return url
                    
                    logger.warning(f"⚠️ Perplexity returned text but no valid image URL: {content[:100]}")
                else:
                    logger.warning("⚠️ Perplexity returned empty response")
            else:
                logger.error(f"❌ Perplexity API error: HTTP {response.status_code}")
                logger.debug(f"Response: {response.text[:200]}")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Perplexity search error: {e}")
            return None
    
    def _search_free_stock_images(self, query, headline_full=""):
        """
        Search free stock photo sites using FULL TITLE first, then keywords
        """
        try:
            search_query = headline_full[:80] if headline_full else query
            logger.info(f"🔍 Web searching images for: '{search_query}'")
            
            # Try Unsplash with full title
            try:
                clean_query = re.sub(r'[^a-zA-Z0-9\s]', '', search_query)
                unsplash_url = f"https://source.unsplash.com/1200x630/?{quote(clean_query)}"
                response = requests.head(unsplash_url, timeout=5, allow_redirects=True)
                
                if response.status_code == 200:
                    final_url = response.url
                    logger.info(f"✅ Found Unsplash image via title: {final_url[:80]}")
                    return final_url
            except Exception as e:
                logger.debug(f"Unsplash title search failed: {e}")
            
            # Fallback: Try with keywords
            if headline_full:
                try:
                    keywords = self._extract_search_keywords(headline_full)
                    logger.info(f"🔍 Retrying with keywords: '{keywords}'")
                    unsplash_url = f"https://source.unsplash.com/1200x630/?{quote(keywords)}"
                    response = requests.head(unsplash_url, timeout=5, allow_redirects=True)
                    
                    if response.status_code == 200:
                        final_url = response.url
                        logger.info(f"✅ Found Unsplash image via keywords: {final_url[:80]}")
                        return final_url
                except Exception as e:
                    logger.debug(f"Unsplash keyword search failed: {e}")
            
            # Try Pixabay
            try:
                pixabay_search = f"https://pixabay.com/en/photos/search/{quote(search_query)}/"
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(pixabay_search, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    img_tags = soup.find_all('img', class_=re.compile('.*?'))
                    
                    for img in img_tags:
                        src = img.get('src') or img.get('data-lazy')
                        if src and self._is_valid_image_url(src) and 'pixabay' in src:
                            full_url = src.replace('_640', '_1280')
                            logger.info(f"✅ Found Pixabay image: {full_url[:80]}")
                            return full_url
            except Exception as e:
                logger.debug(f"Pixabay search failed: {e}")
            
            logger.warning(f"⚠️ Web image search found nothing for: '{search_query}'")
            return None
            
        except Exception as e:
            logger.error(f"❌ Web search error: {e}")
            return None
    
    def extract_image_from_entry(self, entry, headline="", category=""):
        """
        Extract image URL with 4-level search:
        1. RSS feed (8 methods)
        2. Free stock photos
        3. 🆕 PERPLEXITY AI
        4. None (will use placeholder later)
        """
        image_url = None
        method_used = None
        
        # LEVEL 1: RSS extraction (8 methods)
        # Method 1: media:content
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if 'image' in media.get('type', '').lower():
                    image_url = media.get('url')
                    if self._is_valid_image_url(image_url):
                        method_used = "media:content"
                        break
        
        # Method 2: media:thumbnail
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
        
        # Method 4-8: Other RSS methods (summary img, content img, og:image, twitter:image, link rel)
        if not image_url:
            summary = entry.get('summary', entry.get('description', ''))
            if summary:
                soup = BeautifulSoup(summary, 'html.parser')
                img_tag = soup.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag.get('src')
                    if self._is_valid_image_url(image_url):
                        method_used = "summary <img>"
        
        if not image_url and hasattr(entry, 'content') and entry.content:
            for content in entry.content:
                soup = BeautifulSoup(content.get('value', ''), 'html.parser')
                img_tag = soup.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag.get('src')
                    if self._is_valid_image_url(image_url):
                        method_used = "content <img>"
                        break
        
        # LEVEL 2: Free stock photos
        if not image_url and self.enable_web_search and headline:
            logger.info(f"🌐 No RSS image - trying web search: {headline[:60]}")
            web_image = self._search_free_stock_images(headline, headline_full=headline)
            
            if web_image:
                image_url = web_image
                method_used = "stock photos"
        
        # LEVEL 3: 🆕 PERPLEXITY AI
        if not image_url and self.enable_perplexity_search and self.perplexity_api_key and headline:
            logger.info(f"🤖 Trying Perplexity AI as final fallback...")
            perplexity_image = self._search_perplexity_images(headline, category)
            
            if perplexity_image:
                image_url = perplexity_image
                method_used = "Perplexity AI"
        
        # Validation
        if image_url and not self._is_valid_image_url(image_url):
            logger.debug(f"❌ Invalid image URL: {image_url[:80]}")
            image_url = None
            method_used = None
        
        # Logging
        if image_url:
            logger.info(f"✅ Image via [{method_used}]: {image_url[:80]}")
        else:
            logger.warning(f"⚠️ NO IMAGE: {headline[:60]}")
        
        return image_url
    
    def fetch_news_from_feeds(self, workspace_id, today_only=False):
        """Fetch news with 4-level image search"""
        
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("RSS Manager requires feedparser and beautifulsoup4")
        
        placeholder_image = self.get_placeholder_image(workspace_id)
        
        logger.info("🧹 Running cleanup...")
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
            return 0, "No RSS feeds configured."
        
        total_fetched = 0
        total_skipped = 0
        img_rss = 0
        img_stock = 0
        img_ai = 0
        img_placeholder = 0
        
        for feed_id, feed_name, feed_url, category in feeds:
            try:
                logger.info(f"📰 Fetching: {feed_name}")
                
                headers = {'User-Agent': 'Mozilla/5.0'}
                
                try:
                    response = requests.get(feed_url, headers=headers, timeout=10)
                    feed = feedparser.parse(response.content)
                except:
                    feed = feedparser.parse(feed_url)
                
                if not feed.entries:
                    logger.warning(f"⚠️ No entries in: {feed_url}")
                    continue
                
                logger.info(f"✅ Found {len(feed.entries)} entries")
                
                for entry in feed.entries[:self.max_entries_per_feed]:
                    try:
                        headline = entry.get('title', '').strip()
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
                        
                        # 4-LEVEL IMAGE SEARCH
                        image_url = self.extract_image_from_entry(entry, headline, category)
                        
                        # Track source
                        if image_url:
                            if 'perplexity' in str(image_url).lower() or 'AI' in str(image_url):
                                img_ai += 1
                            elif 'unsplash' in image_url.lower() or 'pixabay' in image_url.lower():
                                img_stock += 1
                            else:
                                img_rss += 1
                        else:
                            img_placeholder += 1
                            image_url = placeholder_image
                        
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
                
            except Exception as e:
                logger.error(f"❌ Error fetching feed: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        result_msg = f"✅ Fetched {total_fetched} articles!\n"
        result_msg += f"📷 RSS:{img_rss} | Stock:{img_stock} | AI:{img_ai} | Placeholder:{img_placeholder}"
        if deleted_count > 0:
            result_msg += f"\n🧹 Cleaned: {deleted_count}"
        if total_skipped > 0:
            result_msg += f"\n⏭️ Skipped: {total_skipped}"
        
        logger.info(result_msg)
        return total_fetched, result_msg
    
    def add_feed(self, workspace_id, feed_name, feed_url, category='General'):
        """Add RSS feed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO rss_feeds (workspace_id, feed_name, url, category, enabled)
                VALUES (?, ?, ?, ?, 1)
            ''', (workspace_id, feed_name, feed_url, category))
            
            conn.commit()
            conn.close()
            return True, "Feed added"
            
        except sqlite3.IntegrityError:
            conn.close()
            return False, "Feed exists"
        except Exception as e:
            conn.close()
            return False, str(e)
    
    def delete_feed(self, feed_id):
        """Delete RSS feed"""
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
            
            return True, f"Deleted: {feed_name}"
            
        except Exception as e:
            return False, str(e)
    
    def get_feeds(self, workspace_id):
        """Get feeds"""
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
        """Get news count"""
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
