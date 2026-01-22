"""
RSS Manager - Enhanced with Image Extraction
Fetches news from RSS feeds using feedparser with image support
"""

import sqlite3
import logging
from datetime import datetime
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
    
    def fetch_news_from_feeds(self, workspace_id):
        """Fetch latest news from all active RSS feeds with images"""
        
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("RSS Manager requires feedparser and beautifulsoup4. Install with: pip install feedparser beautifulsoup4 requests")
        
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
        
        for feed_id, feed_name, feed_url, category in feeds:
            try:
                # Parse RSS feed with timeout
                logger.info(f"Fetching from: {feed_name} ({feed_url})")
                
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
                    logger.warning(f"No entries found in feed: {feed_url}")
                    continue
                
                logger.info(f"Found {len(feed.entries)} entries in {feed_name}")
                
                # Process each entry (limit to 20 latest)
                for entry in feed.entries[:20]:
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
                        
                        # Get domain
                        source_domain = urlparse(source_url).netloc if source_url else feed_name
                        source_domain = source_domain.replace('www.', '')
                        
                        # Get publish date
                        publish_date = entry.get('published', entry.get('updated', datetime.now().isoformat()))
                        
                        # Extract image URL
                        image_url = self.extract_image_from_entry(entry)
                        
                        # Check if already exists (check by headline similarity)
                        cursor.execute('''
                            SELECT COUNT(*) FROM news_queue 
                            WHERE workspace_id = ? AND headline = ?
                        ''', (workspace_id, headline))
                        
                        if cursor.fetchone()[0] > 0:
                            continue  # Already exists
                        
                        # Insert into news_queue
                        cursor.execute('''
                            INSERT INTO news_queue 
                            (workspace_id, headline, summary, source_url, source_domain, 
                             category, publish_date, status, image_url)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 'new', ?)
                        ''', (workspace_id, headline, summary, source_url, source_domain, 
                              category or 'General', publish_date, image_url))
                        
                        total_fetched += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing entry: {e}")
                        continue
                
                logger.info(f"Fetched {total_fetched} articles from {feed_name}")
                
            except Exception as e:
                logger.error(f"Error fetching feed {feed_url}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"Total fetched: {total_fetched} new articles")
        return total_fetched, f"Successfully fetched {total_fetched} new articles with images!"
    
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
