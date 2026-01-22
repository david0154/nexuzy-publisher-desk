"""
RSS Feed Manager Module
Handles RSS feed validation, storage, and fetching
"""

import feedparser
import sqlite3
import logging
from datetime import datetime
from typing import List, Tuple

logger = logging.getLogger(__name__)

class RSSManager:
    """Manage RSS feeds and news fetching"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def validate_rss_url(self, url: str) -> bool:
        """Validate RSS feed URL"""
        try:
            feed = feedparser.parse(url)
            return feed.bozo == False or len(feed.entries) > 0
        except Exception as e:
            logger.error(f"RSS validation error: {e}")
            return False
    
    def fetch_feed_items(self, feed_url: str, max_items: int = 50) -> List[dict]:
        """
        Fetch items from RSS feed
        Returns list of news items with headline, summary, url, etc.
        """
        try:
            feed = feedparser.parse(feed_url)
            items = []
            
            for entry in feed.entries[:max_items]:
                item = {
                    'headline': entry.get('title', 'No title'),
                    'summary': entry.get('summary', '')[:500],  # Truncate
                    'source_url': entry.get('link', feed_url),
                    'source_domain': self._extract_domain(feed_url),
                    'publish_date': self._parse_date(entry),
                    'image': entry.get('media_content', [{}])[0].get('url') if 'media_content' in entry else None
                }
                items.append(item)
            
            return items
        
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
            return []
    
    def fetch_all_workspace_feeds(self, workspace_id: int) -> List[dict]:
        """Fetch all enabled feeds for workspace"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT url FROM rss_feeds 
                WHERE workspace_id = ? AND enabled = 1
            ''', (workspace_id,))
            
            feeds = cursor.fetchall()
            conn.close()
            
            all_items = []
            for (feed_url,) in feeds:
                items = self.fetch_feed_items(feed_url)
                all_items.extend(items)
            
            return all_items
        
        except Exception as e:
            logger.error(f"Error fetching workspace feeds: {e}")
            return []
    
    def store_news_item(self, workspace_id: int, news_item: dict) -> int:
        """Store fetched news item in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO news_queue 
                (workspace_id, headline, summary, source_url, source_domain, publish_date, verified_sources)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (
                workspace_id,
                news_item['headline'],
                news_item['summary'],
                news_item['source_url'],
                news_item['source_domain'],
                news_item.get('publish_date')
            ))
            
            conn.commit()
            news_id = cursor.lastrowid
            conn.close()
            
            return news_id
        
        except Exception as e:
            logger.error(f"Error storing news item: {e}")
            return 0
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc or url
        except:
            return url
    
    @staticmethod
    def _parse_date(entry) -> str:
        """Parse publication date from feed entry"""
        try:
            if 'published_parsed' in entry:
                import time
                return time.strftime('%Y-%m-%d %H:%M:%S', entry['published_parsed'])
            return datetime.now().isoformat()
        except:
            return datetime.now().isoformat()
