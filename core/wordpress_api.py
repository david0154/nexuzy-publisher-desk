"""
WordPress API Module - Direct URL Image Import
WordPress automatically downloads and hosts images from URLs
"""

import requests
import sqlite3
import logging
from typing import Dict, Optional
from pathlib import Path
import tempfile
import hashlib

logger = logging.getLogger(__name__)

class WordPressAPI:
    """Handle WordPress API interactions with URL-based image upload"""
    
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

    def upload_image_from_url(self, image_url: str, title: str = '') -> Optional[int]:
        """
        Upload image to WordPress directly from URL
        WordPress downloads and hosts the image automatically
        
        Args:
            image_url: Direct URL to image
            title: Optional title for the media item
        
        Returns:
            WordPress media ID or None if failed
        """
        if not image_url or not image_url.startswith('http'):
            logger.warning(f"Invalid image URL: {image_url}")
            return None
        
        try:
            logger.info(f"Uploading image from URL to WordPress: {image_url}")
            
            # WordPress REST API: Upload from URL using wp_handle_sideload
            # We send the image URL and WordPress downloads it
            payload = {
                'url': image_url,
                'title': title or 'Featured Image',
                'caption': '',
                'alt_text': title or ''
            }
            
            # Try WP REST API v2 sideload endpoint (plugin required)
            # If not available, fallback to downloading locally
            response = self.session.post(
                f"{self.base_url}/media/sideload",
                json=payload,
                timeout=60
            )
            
            if response.ok:
                try:
                    media_data = response.json()
                    media_id = media_data.get('id')
                    if media_id:
                        logger.info(f"✅ Image uploaded from URL. Media ID: {media_id}")
                        return media_id
                except ValueError:
                    pass
            
            # FALLBACK: If sideload endpoint not available, download and upload
            logger.info("Sideload endpoint unavailable, downloading image locally...")
            return self._fallback_download_and_upload(image_url)
        
        except Exception as e:
            logger.error(f"Error uploading image from URL: {e}")
            # Try fallback method
            return self._fallback_download_and_upload(image_url)
    
    def _fallback_download_and_upload(self, image_url: str) -> Optional[int]:
        """
        Fallback: Download image locally then upload to WordPress
        Used when direct URL import is not available
        """
        try:
            logger.info(f"Fallback: Downloading {image_url}")
            
            # Download image
            img_response = requests.get(image_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            if img_response.status_code != 200:
                logger.error(f"Failed to download image: HTTP {img_response.status_code}")
                return None
            
            # Get filename and content type
            filename = image_url.split('/')[-1].split('?')[0]
            if not filename or '.' not in filename:
                filename = 'image.jpg'
            
            content_type = img_response.headers.get('Content-Type', 'image/jpeg')
            
            # Upload to WordPress using multipart/form-data
            files = {
                'file': (filename, img_response.content, content_type)
            }
            
            logger.info(f"Uploading downloaded image: {filename}")
            response = self.session.post(
                self.media_url,
                files=files,
                timeout=60
            )
            
            if not response.ok:
                logger.error(f"Upload failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                return None
            
            media_data = response.json()
            media_id = media_data.get('id')
            
            if media_id:
                logger.info(f"✅ Image uploaded successfully. Media ID: {media_id}")
                return media_id
            
            return None
        
        except Exception as e:
            logger.error(f"Fallback upload error: {e}")
            return None

    def download_and_cache_image(self, image_url: str) -> Optional[str]:
        """
        Download an image from a URL and save it to a local cache.
        DEPRECATED: Now using direct URL upload
        """
        if not image_url or not image_url.startswith('http'):
            logger.warning(f"Invalid or empty image URL provided: {image_url}")
            return None

        try:
            cache_dir = Path(tempfile.gettempdir()) / "nexuzy_images"
            cache_dir.mkdir(exist_ok=True)
            file_hash = hashlib.md5(image_url.encode()).hexdigest()
            
            try:
                file_ext = Path(image_url.split('?')[0]).suffix
                if not file_ext or len(file_ext) > 5:
                    file_ext = '.jpg'
            except Exception:
                file_ext = '.jpg'

            local_path = cache_dir / (file_hash + file_ext)

            if local_path.exists():
                logger.info(f"Image already cached: {local_path}")
                return str(local_path)

            logger.info(f"Downloading image from {image_url} to {local_path}")
            response = requests.get(image_url, stream=True, timeout=30)
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info("✅ Image downloaded successfully.")
            return str(local_path)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download image from URL {image_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"An error occurred while caching the image: {e}")
            return None
    
    def upload_image_from_local_file(self, local_path: str) -> Optional[int]:
        """
        Upload image directly from local file system to WordPress
        Uses multipart/form-data format
        """
        try:
            path = Path(local_path)
            if not path.exists():
                logger.error(f"Local image file not found: {local_path}")
                return None
            
            ext = path.suffix.lower()
            content_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            content_type = content_types.get(ext, 'image/jpeg')
            
            logger.info(f"Uploading image from local file: {path.name}")
            
            with open(path, 'rb') as f:
                files = {
                    'file': (path.name, f, content_type)
                }
                
                response = self.session.post(
                    self.media_url,
                    files=files,
                    timeout=60
                )
            
            if not response.ok:
                logger.error(f"Image upload failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                return None
            
            try:
                media_data = response.json()
                media_id = media_data.get('id')
                
                if not media_id:
                    logger.error("No media ID in response")
                    return None
                
                logger.info(f"✅ Image uploaded. Media ID: {media_id}")
                return media_id
            
            except ValueError as e:
                logger.error(f"JSON parsing error: {e}")
                return None
        
        except Exception as e:
            logger.error(f"Error uploading local image: {e}")
            return None
    
    def publish_draft(self, draft_id: int, workspace_id: int) -> Optional[Dict]:
        """
        Publish draft to WordPress with direct URL image upload
        OPTIMIZED: Uses URL upload instead of local caching
        """
        try:
            if not self._initialize_connection(workspace_id):
                return None
            
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
            
            title, content, summary, image_url, source_url = result
            
            # Upload image from URL (WordPress handles download)
            featured_media_id = None
            if image_url:
                logger.info(f"Processing featured image: {image_url}")
                featured_media_id = self.upload_image_from_url(image_url, title)
                
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
            
            if not response.ok:
                logger.error(f"Post creation failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                return None
            
            try:
                post = response.json()
                post_id = post.get('id')
                post_url = post.get('link')
                
                if not post_id:
                    logger.error("No post ID in response")
                    return None
                
                logger.info(f"✅ Post created successfully: {post_url}")
                
                return {
                    'post_id': post_id,
                    'url': post_url,
                    'status': 'draft'
                }
            
            except ValueError as e:
                logger.error(f"JSON parsing error: {e}")
                return None
        
        except Exception as e:
            logger.error(f"Error publishing to WordPress: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def test_connection(self, site_url: str, username: str, password: str) -> bool:
        """
        Test WordPress connection by accessing a protected endpoint
        """
        try:
            test_url = site_url.rstrip('/') + '/wp-json/wp/v2/users/me'
            logger.info(f"Testing WordPress connection to {test_url}")

            session = requests.Session()
            session.auth = (username, password)
            session.headers.update({'User-Agent': 'Nexuzy-Publisher-Test/2.0'})
            
            response = session.get(test_url, timeout=15)

            if response.status_code == 200:
                logger.info("✅ WordPress connection test successful.")
                return True
            else:
                logger.warning(f"WordPress connection test failed: {response.status_code}")
                logger.warning(f"Response: {response.text[:500]}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during WordPress connection test: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection test: {e}")
            return False
