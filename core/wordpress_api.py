"""
WordPress API Integration - Enhanced with Proper Image Handling
Publishes articles and manages media on WordPress sites
"""

import requests
import sqlite3
import logging
from typing import Dict, List, Optional
from datetime import datetime
import base64
import time

logger = logging.getLogger(__name__)

class WordPressAPI:
    """Handle WordPress API interactions with enhanced reliability"""
    
    def __init__(self, site_url: str, username: str, password: str, db_path: str = 'nexuzy.db'):
        """
        Initialize WordPress API client
        
        Args:
            site_url: WordPress site URL (e.g., https://example.com)
            username: WordPress username
            password: WordPress password or app-specific password
            db_path: Database path for tracking
        """
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.password = password
        self.db_path = db_path
        self.base_url = f"{self.site_url}/wp-json/wp/v2"
        self.media_url = f"{self.base_url}/media"
        self.posts_url = f"{self.base_url}/posts"
        self.categories_url = f"{self.base_url}/categories"
        self.tags_url = f"{self.base_url}/tags"
        self.session = self._create_session()
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    def _create_session(self) -> requests.Session:
        """Create authenticated session"""
        session = requests.Session()
        session.auth = (self.username, self.password)
        session.headers.update({
            'User-Agent': 'Nexuzy-Publisher/1.0',
            'Content-Type': 'application/json'
        })
        return session
    
    def test_connection(self) -> bool:
        """Test WordPress API connectivity"""
        try:
            response = self.session.get(
                f"{self.base_url}",
                timeout=10
            )
            if response.status_code == 200:
                logger.info("[OK] WordPress API connection successful")
                return True
            else:
                logger.error(f"WordPress API returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"WordPress connection failed: {e}")
            return False
    
    def upload_image_from_base64(self, image_base64: str, filename: str) -> Optional[int]:
        """
        Upload image directly from base64 encoded data
        
        Args:
            image_base64: Base64 encoded image data
            filename: Image filename
        
        Returns:
            WordPress media ID or None if failed
        """
        try:
            # Decode base64
            image_binary = base64.b64decode(image_base64)
            
            # Prepare upload
            headers = {
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'image/jpeg'  # Adjust based on actual format
            }
            
            logger.info(f"Uploading image: {filename}")
            
            # Upload with retry
            response = self._retry_request(
                'post',
                self.media_url,
                data=image_binary,
                headers=headers
            )
            
            if response and response.status_code in (200, 201):
                media_data = response.json()
                media_id = media_data.get('id')
                logger.info(f"Image uploaded successfully. Media ID: {media_id}")
                return media_id
            else:
                logger.error(f"Image upload failed: {response.status_code if response else 'No response'}")
                return None
        
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return None
    
    def upload_image_from_url(self, image_url: str) -> Optional[int]:
        """
        Upload image from URL
        
        Args:
            image_url: Direct image URL
        
        Returns:
            WordPress media ID or None if failed
        """
        try:
            # Download image
            logger.info(f"Downloading image from: {image_url}")
            img_response = requests.get(image_url, timeout=30)
            
            if img_response.status_code != 200:
                logger.error(f"Failed to download image: {img_response.status_code}")
                return None
            
            # Extract filename
            filename = image_url.split('/')[-1].split('?')[0] or 'image.jpg'
            
            # Convert to base64 and upload
            image_base64 = base64.b64encode(img_response.content).decode('utf-8')
            return self.upload_image_from_base64(image_base64, filename)
        
        except Exception as e:
            logger.error(f"Error uploading image from URL: {e}")
            return None
    
    def create_post(
        self,
        title: str,
        content: str,
        featured_media_id: Optional[int] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        status: str = 'draft',
        excerpt: str = ''
    ) -> Optional[Dict]:
        """
        Create WordPress post with full support
        
        Args:
            title: Post title
            content: Post content (HTML)
            featured_media_id: WordPress media ID for featured image
            categories: List of category names
            tags: List of tag names
            status: 'draft', 'publish', or 'pending'
            excerpt: Post excerpt
        
        Returns:
            Post data dict or None if failed
        """
        try:
            # Resolve categories and tags
            category_ids = []
            if categories:
                for cat in categories:
                    cat_id = self.get_or_create_category(cat)
                    if cat_id:
                        category_ids.append(cat_id)
            
            tag_ids = []
            if tags:
                for tag in tags:
                    tag_id = self.get_or_create_tag(tag)
                    if tag_id:
                        tag_ids.append(tag_id)
            
            # Build post data
            post_data = {
                'title': title,
                'content': content,
                'excerpt': excerpt,
                'status': status,
                'categories': category_ids,
                'tags': tag_ids
            }
            
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
            
            logger.info(f"Creating post: {title}")
            
            # Create post with retry
            response = self._retry_request(
                'post',
                self.posts_url,
                json=post_data
            )
            
            if response and response.status_code in (200, 201):
                post = response.json()
                logger.info(f"Post created successfully. Post ID: {post['id']}")
                return post
            else:
                logger.error(f"Post creation failed: {response.status_code if response else 'No response'}")
                if response:
                    logger.error(f"Response: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            return None
    
    def publish_draft(
        self,
        draft_id: int,
        image_base64: Optional[str] = None,
        image_filename: str = 'featured-image.jpg',
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Publish a draft to WordPress with complete setup
        
        Args:
            draft_id: Nexuzy draft ID
            image_base64: Base64 encoded featured image
            image_filename: Image filename
            categories: WordPress categories
            tags: WordPress tags
        
        Returns:
            WordPress post data or None
        """
        try:
            # Get draft from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT title, body_draft, summary
                FROM ai_drafts
                WHERE id = ?
            ''', (draft_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                logger.error(f"Draft {draft_id} not found")
                return None
            
            title, content, summary = result
            
            # Upload featured image if provided
            featured_media_id = None
            if image_base64:
                featured_media_id = self.upload_image_from_base64(
                    image_base64,
                    image_filename
                )
            
            # Create post
            post = self.create_post(
                title=title,
                content=content,
                featured_media_id=featured_media_id,
                excerpt=summary,
                categories=categories,
                tags=tags,
                status='publish'
            )
            
            if post:
                # Track in database
                self._track_published_post(draft_id, post['id'], post['link'])
            
            return post
        
        except Exception as e:
            logger.error(f"Error publishing draft: {e}")
            return None
    
    def get_or_create_category(self, category_name: str) -> Optional[int]:
        """Get category ID or create if doesn't exist"""
        try:
            # Search for existing category
            response = self._retry_request(
                'get',
                self.categories_url,
                params={'search': category_name}
            )
            
            if response and response.status_code == 200:
                categories = response.json()
                if categories and len(categories) > 0:
                    return categories[0]['id']
            
            # Create new category
            logger.info(f"Creating category: {category_name}")
            response = self._retry_request(
                'post',
                self.categories_url,
                json={'name': category_name}
            )
            
            if response and response.status_code in (200, 201):
                return response.json()['id']
            
            logger.warning(f"Could not create category: {category_name}")
            return None
        
        except Exception as e:
            logger.error(f"Error with category: {e}")
            return None
    
    def get_or_create_tag(self, tag_name: str) -> Optional[int]:
        """Get tag ID or create if doesn't exist"""
        try:
            # Search for existing tag
            response = self._retry_request(
                'get',
                self.tags_url,
                params={'search': tag_name}
            )
            
            if response and response.status_code == 200:
                tags = response.json()
                if tags and len(tags) > 0:
                    return tags[0]['id']
            
            # Create new tag
            logger.info(f"Creating tag: {tag_name}")
            response = self._retry_request(
                'post',
                self.tags_url,
                json={'name': tag_name}
            )
            
            if response and response.status_code in (200, 201):
                return response.json()['id']
            
            logger.warning(f"Could not create tag: {tag_name}")
            return None
        
        except Exception as e:
            logger.error(f"Error with tag: {e}")
            return None
    
    def _retry_request(self, method: str, url: str, max_retries: int = None, **kwargs):
        """Make HTTP request with automatic retry"""
        max_retries = max_retries or self.max_retries
        
        for attempt in range(max_retries):
            try:
                if method == 'get':
                    response = self.session.get(url, timeout=30, **kwargs)
                elif method == 'post':
                    response = self.session.post(url, timeout=30, **kwargs)
                elif method == 'put':
                    response = self.session.put(url, timeout=30, **kwargs)
                else:
                    response = self.session.request(method, url, timeout=30, **kwargs)
                
                return response
            
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    logger.warning(f"Request timeout, retrying ({attempt + 1}/{max_retries})...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Request failed after {max_retries} attempts")
                    return None
            
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Request failed: {e}. Retrying ({attempt + 1}/{max_retries})...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Request failed after {max_retries} attempts: {e}")
                    return None
        
        return None
    
    def _track_published_post(self, draft_id: int, post_id: int, post_url: str):
        """Track published post in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE ai_drafts
                SET wordpress_post_id = ?, wordpress_url = ?, published_at = ?, status = 'published'
                WHERE id = ?
            ''', (post_id, post_url, datetime.now().isoformat(), draft_id))
            
            conn.commit()
            conn.close()
            logger.info(f"Published post tracked: Draft {draft_id} -> Post {post_id}")
        
        except Exception as e:
            logger.error(f"Error tracking published post: {e}")
    
    def get_published_posts(self, workspace_id: int) -> List[Dict]:
        """Get all published posts for a workspace"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, wordpress_post_id, wordpress_url, published_at
                FROM ai_drafts
                WHERE workspace_id = ? AND status = 'published'
                ORDER BY published_at DESC
                LIMIT 50
            ''', (workspace_id,))
            
            posts = cursor.fetchall()
            conn.close()
            
            return [{
                'draft_id': p[0],
                'title': p[1],
                'post_id': p[2],
                'url': p[3],
                'published_at': p[4]
            } for p in posts]
        
        except Exception as e:
            logger.error(f"Error getting published posts: {e}")
            return []
