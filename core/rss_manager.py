"""
RSS Manager - Fetches news from RSS feeds using feedparser
"""

import sqlite3
import logging
from datetime import datetime
from urllib.parse import urlparse

try:
    import feedparser
    from bs4 import BeautifulSoup
    import requests
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

logger = logging.getLogger(__name__)


class RSSManager:
    """Manage RSS feeds and fetch news articles"""
    
    def __init__(self, db_path='nexuzy.db'):
        self.db_path = db_path
    
    def fetch_news_from_feeds(self, workspace_id):
        """Fetch latest news from all active RSS feeds"""
        
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("RSS Manager requires feedparser and beautifulsoup4. Install with: pip install feedparser beautifulsoup4")
        
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
            return 0, "No RSS feeds configured"
        
        total_fetched = 0
        
        for feed_id, feed_name, feed_url, category in feeds:
            try:
                # Parse RSS feed
                logger.info(f"Fetching from: {feed_name} ({feed_url})")
                feed = feedparser.parse(feed_url)
                
                if feed.bozo and not feed.entries:
                    logger.warning(f"Failed to parse feed: {feed_url}")
                    continue
                
                # Process each entry (limit to 10 latest)
                for entry in feed.entries[:10]:
                    try:
                        # Extract data
                        headline = entry.get('title', 'No title')
                        summary = entry.get('summary', entry.get('description', ''))
                        source_url = entry.get('link', '')
                        
                        # Clean HTML from summary
                        if summary:
                            soup = BeautifulSoup(summary, 'html.parser')
                            summary = soup.get_text(strip=True)[:500]  # Limit length
                        
                        # Get domain
                        source_domain = urlparse(source_url).netloc if source_url else feed_name
                        
                        # Get publish date
                        publish_date = entry.get('published', entry.get('updated', ''))
                        
                        # Check if already exists
                        cursor.execute('''
                            SELECT COUNT(*) FROM news_queue 
                            WHERE workspace_id = ? AND headline = ? AND source_url = ?
                        ''', (workspace_id, headline, source_url))
                        
                        if cursor.fetchone()[0] > 0:
                            continue  # Already exists
                        
                        # Insert into news_queue
                        cursor.execute('''
                            INSERT INTO news_queue 
                            (workspace_id, headline, summary, source_url, source_domain, 
                             category, publish_date, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 'new')
                        ''', (workspace_id, headline, summary, source_url, source_domain, 
                              category or 'General', publish_date))
                        
                        total_fetched += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing entry: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Error fetching feed {feed_url}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"Fetched {total_fetched} new articles")
        return total_fetched, f"Fetched {total_fetched} new articles successfully!"
    
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
