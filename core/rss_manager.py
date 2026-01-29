""" 
RSS Manager - ENHANCED IMAGE EXTRACTION (Perplexity disabled temporarily)
Fetches news from RSS feeds with comprehensive image extraction:
- Level 1: 11+ RSS image extraction methods (ENHANCED!)
- Level 2: Free stock photos (Unsplash/Pixabay)
- Level 3: PERPLEXITY AI (temporarily disabled - HTTP 400 errors)
- Level 4: Placeholder

FEATURES:
✅ URL-based duplicate detection
✅ Headline similarity checking  
✅ 48-hour automatic cleanup
✅ Debug logging for troubleshooting
✅ Better extraction from Mint, WordPress feeds
✅ Smart image quality selection
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
        self.enable_perplexity_search = False  # Temporarily disabled (HTTP 400 errors)
        self.perplexity_api_key = self._load_perplexity_api_key()
        self.debug_mode = False
    
    def _load_perplexity_api_key(self):
        """Load Perplexity API key"""
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if api_key:
            logger.debug("✅ Loaded Perplexity API key from environment (currently disabled)")
            return api_key
        
        try:
            config_path = Path('config.json')
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    api_key = config.get('perplexity_api_key')
                    if api_key:
                        logger.debug("✅ Loaded Perplexity API key from config.json (currently disabled)")
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
                            logger.debug("✅ Loaded Perplexity API key from .env (currently disabled)")
                            return api_key
        except Exception as e:
            logger.debug(f"Could not load from .env: {e}")
        
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
    
    def _get_image_quality_score(self, img_url):
        """Calculate quality score for image URL to pick best one"""
        if not img_url:
            return 0
        
        score = 0
        url_lower = img_url.lower()
        
        # Size indicators (higher is better)
        if '1200' in url_lower or '1920' in url_lower:
            score += 100
        elif '800' in url_lower or '1000' in url_lower:
            score += 80
        elif '600' in url_lower:
            score += 60
        elif '400' in url_lower:
            score += 40
        elif '150' in url_lower or '200' in url_lower:
            score += 20
        
        # Avoid tiny images
        if any(x in url_lower for x in ['thumb', 'icon', 'logo', 'avatar', 'emoji', '16x16', '32x32', '50x50']):
            score -= 50
        
        # Prefer certain image formats
        if url_lower.endswith(('.jpg', '.jpeg', '.png', '.webp')):
            score += 10
        
        # Avoid social media icons
        if any(x in url_lower for x in ['facebook', 'twitter', 'linkedin', 'instagram', 'social']):
            score -= 100
        
        return score
    
    def _extract_all_images_from_html(self, html_content, base_url=""):
        """Extract ALL images from HTML and return best one"""
        if not html_content:
            return None
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            img_tags = soup.find_all('img')
            
            if not img_tags:
                return None
            
            # Score all images
            image_candidates = []
            for img in img_tags:
                img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if img_url:
                    img_url = self._make_absolute_url(base_url, img_url)
                    if self._is_valid_image_url(img_url):
                        score = self._get_image_quality_score(img_url)
                        image_candidates.append((img_url, score))
            
            if not image_candidates:
                return None
            
            # Return highest scoring image
            image_candidates.sort(key=lambda x: x[1], reverse=True)
            best_image = image_candidates[0][0]
            
            if self.debug_mode and len(image_candidates) > 1:
                logger.debug(f"📊 Found {len(image_candidates)} images, picked: {best_image[:80]}")
            
            return best_image
            
        except Exception as e:
            logger.debug(f"Error extracting images from HTML: {e}")
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
        
        # Avoid icons and tiny images
        if any(x in url_lower for x in ['icon', 'logo', 'favicon', 'emoji', '16x16', '32x32', '50x50']):
            return False
        
        # Check for image file extensions or image-related paths
        image_indicators = [
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg',
            '/image/', '/images/', '/img/', '/media/', '/photo/', '/photos/',
            'image=', 'img=', 'photo', 'picture', 'thumbnail', '/lm-img/'  # Mint specific
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
        """Perplexity AI image search (currently disabled)"""
        logger.debug("⚠️ Perplexity AI search is currently disabled (HTTP 400 errors)")
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
        🔍 ENHANCED: Extract image with better support for Mint & WordPress feeds
        """
        image_url = None
        method_used = None
        
        # Debug logging
        if self.debug_mode:
            logger.debug(f"\n{'='*60}")
            logger.debug(f"DEBUG: Entry for '{headline[:50]}...'")
            logger.debug(f"DEBUG: Entry keys: {list(entry.keys())}")
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
        
        # Method 4: 🆕 ENHANCED - Extract ALL images from description and pick best
        if not image_url:
            summary = entry.get('summary', entry.get('description', ''))
            if summary:
                best_img = self._extract_all_images_from_html(summary, feed_url)
                if best_img:
                    image_url = best_img
                    method_used = "description <img> (best)"
        
        # Method 5: 🆕 ENHANCED - Extract ALL images from content and pick best
        if not image_url and hasattr(entry, 'content') and entry.content:
            for content in entry.content:
                best_img = self._extract_all_images_from_html(content.get('value', ''), feed_url)
                if best_img:
                    image_url = best_img
                    method_used = "content <img> (best)"
                    break
        
        # Method 6: content:encoded
        if not image_url and hasattr(entry, 'content_encoded'):
            best_img = self._extract_all_images_from_html(entry.content_encoded, feed_url)
            if best_img:
                image_url = best_img
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
        
        # Method 8: OpenGraph/Twitter images from description
        if not image_url:
            summary = entry.get('summary', entry.get('description', ''))
            if summary:
                soup = BeautifulSoup(summary, 'html.parser')
                
                # Try og:image
                og_image = soup.find('meta', property='og:image') or soup.find('meta', attrs={'property': 'og:image'})
                if og_image and og_image.get('content'):
                    image_url = self._make_absolute_url(feed_url, og_image.get('content'))
                    if self._is_valid_image_url(image_url):
                        method_used = "og:image meta"
                
                # Try twitter:image
                if not image_url:
                    twitter_image = soup.find('meta', attrs={'name': 'twitter:image'}) or soup.find('meta', property='twitter:image')
                    if twitter_image and twitter_image.get('content'):
                        image_url = self._make_absolute_url(feed_url, twitter_image.get('content'))
                        if self._is_valid_image_url(image_url):
                            method_used = "twitter:image meta"
        
        # Method 9: Link tags with image rel
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
        
        # LEVEL 3: PERPLEXITY AI (disabled)
        # Perplexity temporarily disabled due to HTTP 400 errors
        
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
        
        return image_url
    
    def fetch_news_from_feeds(self, workspace_id, today_only=False):
        """Fetch news with enhanced image extraction"""
        
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
                        
                        # ENHANCED IMAGE EXTRACTION
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
