""" 
RSS Manager - IMPROVED IMAGE EXTRACTION (11 Methods!)
Fetches news from RSS feeds with comprehensive image extraction:
- Level 1: 11 RSS image extraction methods (IMPROVED!)
- Level 2: Free stock photos (Unsplash/Pixabay)
- Level 3: PERPLEXITY AI WEB SEARCH
- Level 4: Placeholder

FEATURES:
✅ URL-based duplicate detection
✅ Headline similarity checking  
✅ 48-hour automatic cleanup
✅ AI-powered image discovery
✅ Debug logging for troubleshooting
"""

import sqlite3
import logging
import hashlib
from datetime import datetime, timedelta
from urllib.parse import urlparse, quote, urljoin
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
    """Manage RSS feeds with comprehensive image extraction"""
    
    def __init__(self, db_path='nexuzy.db'):
        self.db_path = db_path
        self.cleanup_hours = 48
        self.max_entries_per_feed = 20
        self.enable_web_search = True
        self.enable_perplexity_search = True
        self.perplexity_api_key = self._load_perplexity_api_key()
        self.debug_mode = False  # Set to True to see detailed RSS entry info
    
    def _load_perplexity_api_key(self):
        """Load Perplexity API key"""
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if api_key:
            logger.info("✅ Loaded Perplexity API key from environment")
            return api_key
        
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
        
        logger.warning("⚠️ Perplexity API key not found")
        return None
    
    def _make_absolute_url(self, base_url, image_url):
        """Convert relative URL to absolute URL"""
        if not image_url:
            return None
        
        # Already absolute
        if image_url.startswith(('http://', 'https://')):
            return image_url
        
        # Protocol-relative URL
        if image_url.startswith('//'):
            return 'https:' + image_url
        
        # Relative URL
        try:
            return urljoin(base_url, image_url)
        except:
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
        
        # Check for image file extensions or image-related paths
        image_indicators = [
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg',
            '/image/', '/images/', '/img/', '/media/', '/photo/', '/photos/',
            'image=', 'img=', 'photo', 'picture', 'thumbnail'
        ]
        
        return any(indicator in url_lower for indicator in image_indicators)
    
    def _extract_search_keywords(self, headline):
        """Extract clean keywords from headline"""
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                      'says', 'announces', 'launches', 'reports', 'reveals']
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', headline.lower())
        keywords = [w for w in words if w not in stop_words]
        
        return ' '.join(keywords[:4])
    
    def _search_perplexity_images(self, headline, category=""):
        """Perplexity AI image search"""
        try:
            if not self.perplexity_api_key:
                return None
            
            logger.info(f"🤖 Perplexity AI searching for: '{headline[:60]}...'")
            
            search_query = f"Find a high quality, copyright-free image URL (direct link to .jpg, .png, or .webp) for this news headline: {headline}"
            if category:
                search_query += f" Category: {category}. "
            search_query += "Return ONLY the image URL from Unsplash, Pexels, Pixabay, or Wikimedia Commons. No explanations."
            
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an image URL finder. Return ONLY a direct image URL (ending in .jpg, .png, .webp, etc.) from free stock photo sites like Unsplash, Pexels, Pixabay, or Wikimedia Commons. Return nothing else - just the URL."
                    },
                    {
                        "role": "user",
                        "content": search_query
                    }
                ],
                "max_tokens": 150,
                "temperature": 0.1,
                "top_p": 0.9,
                "stream": False
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
                    logger.debug(f"Perplexity response: {content[:200]}")
                    
                    # Extract URL
                    url_pattern = r'https?://[^\s<>"\)\]]+?\.(jpg|jpeg|png|gif|webp)(?:\?[^\s<>"\)\]]*)?'
                    urls = re.findall(url_pattern, content, re.IGNORECASE)
                    
                    if urls:
                        for match in urls:
                            start_idx = content.find('http')
                            if start_idx != -1:
                                end_idx = start_idx
                                for char in content[start_idx:]:
                                    if char in [' ', '\n', ')', ']', '"', "'"]:
                                        break
                                    end_idx += 1
                                
                                full_url = content[start_idx:end_idx]
                                if self._is_valid_image_url(full_url):
                                    logger.info(f"✅ Perplexity AI found: {full_url[:80]}")
                                    return full_url
                    
                    simple_urls = re.findall(r'https?://[^\s<>"\)\]]+', content)
                    for url in simple_urls:
                        if self._is_valid_image_url(url):
                            logger.info(f"✅ Perplexity AI found (simple): {url[:80]}")
                            return url
                    
                    logger.warning(f"⚠️ Perplexity returned: {content[:100]}... (no valid image URL)")
                else:
                    logger.warning("⚠️ Perplexity returned empty response")
            else:
                logger.error(f"❌ Perplexity API error: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    logger.error(f"Error details: {error_detail}")
                except:
                    logger.error(f"Response text: {response.text[:300]}")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Perplexity search error: {e}")
            return None
    
    def _search_free_stock_images(self, query, headline_full=""):
        """Search free stock photo sites"""
        try:
            search_query = headline_full[:80] if headline_full else query
            logger.info(f"🔍 Web searching images for: '{search_query}'")
            
            # Try Unsplash
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
            
            # Fallback: keywords
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
            
            logger.warning(f"⚠️ Web image search found nothing for: '{search_query}'")
            return None
            
        except Exception as e:
            logger.error(f"❌ Web search error: {e}")
            return None
    
    def extract_image_from_entry(self, entry, headline="", category="", feed_url=""):
        """
        🔍 IMPROVED: Extract image with 11 methods + debug logging
        """
        image_url = None
        method_used = None
        
        # 🐛 DEBUG: Show what's available in this RSS entry
        if self.debug_mode:
            logger.debug(f"\n{'='*60}")
            logger.debug(f"DEBUG: Entry for '{headline[:50]}...'")
            logger.debug(f"DEBUG: Entry keys: {list(entry.keys())}")
            logger.debug(f"DEBUG: Has media_content: {hasattr(entry, 'media_content')}")
            logger.debug(f"DEBUG: Has media_thumbnail: {hasattr(entry, 'media_thumbnail')}")
            logger.debug(f"DEBUG: Has enclosures: {hasattr(entry, 'enclosures')}")
            logger.debug(f"DEBUG: Has content: {hasattr(entry, 'content')}")
            logger.debug(f"{'='*60}\n")
        
        # Method 1: media:content tags
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if 'image' in media.get('type', '').lower():
                    image_url = media.get('url')
                    if image_url:
                        image_url = self._make_absolute_url(feed_url, image_url)
                        if self._is_valid_image_url(image_url):
                            method_used = "media:content"
                            break
        
        # Method 2: media:thumbnail
        if not image_url and hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
            if isinstance(entry.media_thumbnail, list) and len(entry.media_thumbnail) > 0:
                image_url = entry.media_thumbnail[0].get('url')
                if image_url:
                    image_url = self._make_absolute_url(feed_url, image_url)
                    if self._is_valid_image_url(image_url):
                        method_used = "media:thumbnail"
        
        # Method 3: Enclosures
        if not image_url and hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                enc_type = enclosure.get('type', '').lower()
                enc_url = enclosure.get('href', '')
                if enc_url:
                    enc_url = self._make_absolute_url(feed_url, enc_url)
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
                    image_url = self._make_absolute_url(feed_url, image_url)
                    if self._is_valid_image_url(image_url):
                        method_used = "summary <img>"
        
        # Method 5: Content HTML <img>
        if not image_url and hasattr(entry, 'content') and entry.content:
            for content in entry.content:
                soup = BeautifulSoup(content.get('value', ''), 'html.parser')
                img_tag = soup.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag.get('src')
                    image_url = self._make_absolute_url(feed_url, image_url)
                    if self._is_valid_image_url(image_url):
                        method_used = "content <img>"
                        break
        
        # Method 6: content:encoded (common in WordPress RSS)
        if not image_url and hasattr(entry, 'content_encoded'):
            soup = BeautifulSoup(entry.content_encoded, 'html.parser')
            img_tag = soup.find('img')
            if img_tag and img_tag.get('src'):
                image_url = img_tag.get('src')
                image_url = self._make_absolute_url(feed_url, image_url)
                if self._is_valid_image_url(image_url):
                    method_used = "content:encoded <img>"
        
        # Method 7: Direct 'image' field
        if not image_url and hasattr(entry, 'image'):
            if isinstance(entry.image, dict):
                image_url = entry.image.get('href', entry.image.get('url', ''))
            elif isinstance(entry.image, str):
                image_url = entry.image
            
            if image_url:
                image_url = self._make_absolute_url(feed_url, image_url)
                if self._is_valid_image_url(image_url):
                    method_used = "direct image field"
        
        # Method 8: OpenGraph images
        if not image_url:
            summary = entry.get('summary', entry.get('description', ''))
            if summary:
                soup = BeautifulSoup(summary, 'html.parser')
                og_image = soup.find('meta', property='og:image') or soup.find('meta', attrs={'property': 'og:image'})
                if og_image and og_image.get('content'):
                    image_url = og_image.get('content')
                    image_url = self._make_absolute_url(feed_url, image_url)
                    if self._is_valid_image_url(image_url):
                        method_used = "og:image meta"
        
        # Method 9: Twitter Card images
        if not image_url:
            summary = entry.get('summary', entry.get('description', ''))
            if summary:
                soup = BeautifulSoup(summary, 'html.parser')
                twitter_image = soup.find('meta', attrs={'name': 'twitter:image'}) or soup.find('meta', property='twitter:image')
                if twitter_image and twitter_image.get('content'):
                    image_url = twitter_image.get('content')
                    image_url = self._make_absolute_url(feed_url, image_url)
                    if self._is_valid_image_url(image_url):
                        method_used = "twitter:image meta"
        
        # Method 10: Any <meta> tag with 'image' in name
        if not image_url:
            summary = entry.get('summary', entry.get('description', ''))
            if summary:
                soup = BeautifulSoup(summary, 'html.parser')
                meta_tags = soup.find_all('meta')
                for meta in meta_tags:
                    meta_name = (meta.get('name', '') + meta.get('property', '')).lower()
                    if 'image' in meta_name and meta.get('content'):
                        image_url = meta.get('content')
                        image_url = self._make_absolute_url(feed_url, image_url)
                        if self._is_valid_image_url(image_url):
                            method_used = f"meta tag ({meta.get('name') or meta.get('property')})"
                            break
        
        # Method 11: Link tags with image rel
        if not image_url and hasattr(entry, 'links'):
            for link in entry.links:
                if link.get('rel') == 'image' or 'image' in link.get('type', '').lower():
                    link_url = link.get('href')
                    if link_url:
                        link_url = self._make_absolute_url(feed_url, link_url)
                        if self._is_valid_image_url(link_url):
                            image_url = link_url
                            method_used = "link rel=image"
                            break
        
        # LEVEL 2: Free stock photos
        if not image_url and self.enable_web_search and headline:
            logger.info(f"🌐 No RSS image - trying web search: {headline[:60]}")
            web_image = self._search_free_stock_images(headline, headline_full=headline)
            
            if web_image:
                image_url = web_image
                method_used = "stock photos"
        
        # LEVEL 3: PERPLEXITY AI
        if not image_url and self.enable_perplexity_search and self.perplexity_api_key and headline:
            logger.info(f"🤖 Trying Perplexity AI as final fallback...")
            perplexity_image = self._search_perplexity_images(headline, category)
            
            if perplexity_image:
                image_url = perplexity_image
                method_used = "Perplexity AI"
        
        # Final validation
        if image_url and not self._is_valid_image_url(image_url):
            logger.debug(f"❌ Invalid image URL: {image_url[:80]}")
            image_url = None
            method_used = None
        
        # Logging
        if image_url:
            logger.info(f"✅ Image via [{method_used}]: {image_url[:80]}")
        else:
            logger.warning(f"⚠️ NO IMAGE: {headline[:60]}")
            if self.debug_mode:
                logger.debug("💡 TIP: Set self.debug_mode = True to see available RSS fields")
        
        return image_url
    
    def fetch_news_from_feeds(self, workspace_id, today_only=False):
        """Fetch news with improved image extraction"""
        
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
                        
                        # 11-METHOD IMAGE EXTRACTION
                        image_url = self.extract_image_from_entry(entry, headline, category, feed_url)
                        
                        # Track source
                        if image_url:
                            if 'unsplash' in image_url.lower() or 'pixabay' in image_url.lower() or 'pexels' in image_url.lower():
                                img_stock += 1
                            elif 'perplexity' in str(image_url).lower():
                                img_ai += 1
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
