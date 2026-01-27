"""
WordPress API Module - Local File Image Upload
Uploads locally downloaded images to WordPress for better reliability
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
    """Handle WordPress API interactions with local file upload"""
    
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

    def upload_image_from_local_file(self, local_path: str, title: str = '') -> Optional[int]:
        """
        Upload image from local file system to WordPress
        Most reliable method - no network dependency for image download
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
            
            logger.info(f"📤 Uploading image to WordPress: {path.name}")
            
            with open(path, 'rb') as f:
                files = {
                    'file': (path.name, f, content_type)
                }
                
                # Add title as metadata
                data = {
                    'title': title or path.stem,
                    'alt_text': title or path.stem
                }
                
                response = self.session.post(
                    self.media_url,
                    files=files,
                    data=data,
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
                
                logger.info(f"✅ Image uploaded to WordPress. Media ID: {media_id}")
                return media_id
            
            except ValueError as e:
                logger.error(f"JSON parsing error: {e}")
                return None
        
        except Exception as e:
            logger.error(f"Error uploading local image: {e}")
            return None
    
    def publish_draft(self, draft_id: int, workspace_id: int) -> Optional[Dict]:
        """
        Publish draft to WordPress with Gutenberg block format
        Uses local downloaded image for better reliability
        """
        try:
            if not self._initialize_connection(workspace_id):
                return None
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT title, body_draft, summary, image_url, source_url, local_image_path
                FROM ai_drafts
                WHERE id = ?
            ''', (draft_id,))
            
            result = cursor.fetchone()
            
            # Handle old schema without local_image_path
            if result and len(result) < 6:
                title, content, summary, image_url, source_url = result
                local_image_path = None
            elif result:
                title, content, summary, image_url, source_url, local_image_path = result
            else:
                conn.close()
                logger.error(f"Draft {draft_id} not found")
                return None
            
            conn.close()
            
            # Upload featured image from local file (preferred) or URL (fallback)
            featured_media_id = None
            
            # PRIORITY 1: Use locally downloaded image
            if local_image_path and Path(local_image_path).exists():
                logger.info(f"Using local image: {local_image_path}")
                featured_media_id = self.upload_image_from_local_file(local_image_path, title)
            
            # FALLBACK: Download from URL if local not available
            elif image_url:
                logger.info(f"Local image not found, downloading from URL: {image_url}")
                local_path = self._download_image(image_url)
                if local_path:
                    featured_media_id = self.upload_image_from_local_file(local_path, title)
            
            if not featured_media_id:
                logger.warning("⚠️ No featured image available")
            
            # Convert HTML to Gutenberg blocks
            gutenberg_content = self._convert_to_gutenberg_blocks(content, featured_media_id)
            
            # Create WordPress post
            post_data = {
                'title': title,
                'content': gutenberg_content,
                'excerpt': summary or '',
                'status': 'draft',  # Create as draft for review
            }
            
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
            
            logger.info(f"📝 Creating WordPress post: {title}")
            
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
    
    def _download_image(self, image_url: str) -> Optional[str]:
        """Download image from URL to temp location"""
        try:
            logger.info(f"Downloading image: {image_url}")
            response = requests.get(image_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code != 200:
                logger.error(f"Failed to download: HTTP {response.status_code}")
                return None
            
            # Save to temp directory
            cache_dir = Path(tempfile.gettempdir()) / "nexuzy_wp_images"
            cache_dir.mkdir(exist_ok=True)
            
            file_hash = hashlib.md5(image_url.encode()).hexdigest()
            ext = Path(image_url.split('?')[0]).suffix or '.jpg'
            local_path = cache_dir / f"{file_hash}{ext}"
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Image downloaded to: {local_path}")
            return str(local_path)
        
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return None
    
    def _convert_to_gutenberg_blocks(self, html_content: str, featured_media_id: Optional[int] = None) -> str:
        """
        Convert HTML content to WordPress Gutenberg blocks
        Ensures proper rendering in WordPress block editor
        """
        import re
        
        blocks = []
        
        # Add featured image block if available
        if featured_media_id:
            blocks.append(f'''<!-- wp:image {{"id":{featured_media_id},"sizeSlug":"large"}} -->
<figure class="wp-block-image size-large"><img src="" alt="" class="wp-image-{featured_media_id}"/></figure>
<!-- /wp:image -->''')
        
        # Split HTML into paragraphs and headings
        lines = html_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for headings
            if line.startswith('<h2>'):
                heading_text = re.sub(r'<.*?>', '', line)
                blocks.append(f'''<!-- wp:heading -->
<h2 class="wp-block-heading">{heading_text}</h2>
<!-- /wp:heading -->''')
            
            elif line.startswith('<h3>'):
                heading_text = re.sub(r'<.*?>', '', line)
                blocks.append(f'''<!-- wp:heading {{"level":3}} -->
<h3 class="wp-block-heading">{heading_text}</h3>
<!-- /wp:heading -->''')
            
            # Paragraphs
            elif line.startswith('<p>'):
                para_text = re.sub(r'<p>|</p>', '', line).strip()
                if para_text:
                    blocks.append(f'''<!-- wp:paragraph -->
<p>{para_text}</p>
<!-- /wp:paragraph -->''')
            
            # Plain text (convert to paragraph)
            elif line and not line.startswith('<'):
                blocks.append(f'''<!-- wp:paragraph -->
<p>{line}</p>
<!-- /wp:paragraph -->''')
        
        return '\n\n'.join(blocks)
    
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
