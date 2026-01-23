# Update wordpress_api.py with enhanced image handling from local files
# Key changes:
# 1. Add upload_image_from_local_file method
# 2. Update publish_draft to handle local image paths
# 3. Ensure no external image links in posts

import requests
import sqlite3
import logging
from typing import Dict, List, Optional
from datetime import datetime
import base64
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class WordPressAPI:
    """Handle WordPress API interactions with enhanced image handling"""
    
    def __init__(self, db_path: str = 'nexuzy.db'):
        self.db_path = db_path
        self.session = None
        self.site_url = ''
        self.base_url = ''
        self.media_url = ''
        self.posts_url = ''
    
    def _initialize_connection(self, workspace_id: int) -> bool:
        """Initialize WordPress connection from workspace credentials"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT site_url, username, app_password FROM wp_credentials WHERE workspace_id = ?', (workspace_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                logger.error("WordPress credentials not configured")
                return False
            
            site_url, username, password = result
            self.site_url = site_url.rstrip('/')
            self.base_url = f"{self.site_url}/wp-json/wp/v2"
            self.media_url = f"{self.base_url}/media"
            self.posts_url = f"{self.base_url}/posts"
            
            # Create authenticated session
            self.session = requests.Session()
            self.session.auth = (username, password)
            self.session.headers.update({
                'User-Agent': 'Nexuzy-Publisher/2.0',
            })
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize WordPress connection: {e}")
            return False
    
    def upload_image_from_local_file(self, local_path: str) -> Optional[int]:
        """
        Upload image directly from local file system to WordPress
        No external image URLs - direct upload to WP media library
        
        Args:
            local_path: Path to local image file
        
        Returns:
            WordPress media ID or None if failed
        """
        try:
            path = Path(local_path)
            if not path.exists():
                logger.error(f"Local image file not found: {local_path}")
                return None
            
            # Read image file
            with open(path, 'rb') as f:
                image_data = f.read()
            
            # Determine content type
            ext = path.suffix.lower()
            content_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            content_type = content_types.get(ext, 'image/jpeg')
            
            # Prepare upload
            headers = {
                'Content-Disposition': f'attachment; filename="{path.name}"',
                'Content-Type': content_type
            }
            
            logger.info(f"Uploading image from local file: {path.name}")
            
            # Upload to WordPress
            response = self.session.post(
                self.media_url,
                data=image_data,
                headers=headers,
                timeout=60
            )
            
            if response.status_code in (200, 201):
                media_data = response.json()
                media_id = media_data.get('id')
                logger.info(f"✅ Image uploaded to WordPress Media Library. Media ID: {media_id}")
                return media_id
            else:
                logger.error(f"Image upload failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error uploading local image: {e}")
            return None
    
    def publish_draft(self, draft_id: int, workspace_id: int) -> Optional[Dict]:
        """
        Publish draft to WordPress with proper image handling
        Images are uploaded from local storage, not linked externally
        
        Args:
            draft_id: Draft ID from ai_drafts table
            workspace_id: Workspace ID for credentials
        
        Returns:
            dict with post_id and url, or None if failed
        """
        try:
            # Initialize connection
            if not self._initialize_connection(workspace_id):
                return None
            
            # Get draft data
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT title, body_draft, summary, image_url, source_url
                FROM ai_drafts
                WHERE id = ?
            ''', (draft_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                logger.error(f"Draft {draft_id} not found")
                return None
            
            title, content, summary, image_path, source_url = result
            
            # Upload featured image from local file (NOT from URL)
            featured_media_id = None
            if image_path:
                logger.info(f"Uploading featured image from local storage: {image_path}")
                featured_media_id = self.upload_image_from_local_file(image_path)
                
                if not featured_media_id:
                    logger.warning("Featured image upload failed, continuing without image")
            
            # Create WordPress post
            post_data = {
                'title': title,
                'content': content,
                'excerpt': summary or '',
                'status': 'draft',  # Create as draft for review
            }
            
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
            
            logger.info(f"Creating WordPress post: {title}")
            
            response = self.session.post(
                self.posts_url,
                json=post_data,
                timeout=60
            )
            
            if response.status_code in (200, 201):
                post = response.json()
                post_id = post.get('id')
                post_url = post.get('link')
                
                logger.info(f"✅ Post created successfully: {post_url}")
                
                return {
                    'post_id': post_id,
                    'url': post_url,
                    'status': 'draft'
                }
            else:
                logger.error(f"Post creation failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error publishing to WordPress: {e}")
            return None
    
    def test_connection(self, site_url: str, username: str, password: str) -> bool:
        """Test WordPress connection"""
        try:
            base_url = site_url.rstrip('/') + '/wp-json/wp/v2'
            session = requests.Session()
            session.auth = (username, password)
            
            response = session.get(base_url, timeout=10)
            return response.status_code == 200
        except:
            return False
