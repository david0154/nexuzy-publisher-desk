"""
WordPress API Module - PROPER Image Upload Method
Downloads images from source then uploads to WordPress media library
"""

import requests
import sqlite3
import logging
from typing import Dict, Optional
from pathlib import Path
import tempfile
import hashlib
import re

logger = logging.getLogger(__name__)

class WordPressAPI:
    """Handle WordPress API interactions with PROPER image upload"""
    
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
            
            logger.info(f"✅ Connected to: {self.site_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize WordPress connection: {e}")
            return False

    def upload_image_from_url(self, image_url: str, title: str = '') -> Optional[int]:
        """
        PROPER METHOD: Download image from URL → Upload to WordPress media library
        
        This is the ONLY reliable way - WordPress REST API does NOT support
        direct URL uploads without custom plugins!
        
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
            logger.info(f"📥 Downloading image from source: {image_url}")
            
            # Step 1: Download image from original source
            img_response = requests.get(
                image_url,
                timeout=30,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; Nexuzy/2.0)'}
            )
            
            if img_response.status_code != 200:
                logger.error(f"Failed to download image: HTTP {img_response.status_code}")
                return None
            
            # Step 2: Detect filename and content type
            filename = image_url.split('/')[-1].split('?')[0]
            if not filename or '.' not in filename:
                # Fallback to content type
                content_type = img_response.headers.get('Content-Type', 'image/jpeg')
                ext = content_type.split('/')[-1].split(';')[0]
                filename = f"featured-image.{ext}"
            
            # Ensure valid extension
            if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                filename += '.jpg'
            
            content_type = img_response.headers.get('Content-Type', 'image/jpeg')
            
            logger.info(f"📤 Uploading to WordPress: {filename} ({len(img_response.content)/1024:.1f} KB)")
            
            # Step 3: Upload to WordPress using multipart/form-data
            # This is the CORE WordPress REST API method - works everywhere!
            files = {
                'file': (filename, img_response.content, content_type)
            }
            
            # Set proper headers (WordPress requirement)
            headers = {
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
            
            # Add title if provided
            data = {}
            if title:
                data['title'] = title
                data['alt_text'] = title
            
            response = self.session.post(
                self.media_url,
                files=files,
                data=data,
                headers=headers,
                timeout=60
            )
            
            # Step 4: Handle response
            if not response.ok:
                logger.error(f"Upload failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                
                # Check for common errors
                if response.status_code == 401:
                    logger.error("❌ AUTHENTICATION FAILED: Check your App Password!")
                elif response.status_code == 403:
                    logger.error("❌ PERMISSION DENIED: User needs 'author' role or higher!")
                elif response.status_code == 413:
                    logger.error("❌ FILE TOO LARGE: Increase upload_max_filesize in PHP!")
                
                return None
            
            media_data = response.json()
            media_id = media_data.get('id')
            
            if not media_id:
                logger.error("No media ID in response")
                return None
            
            logger.info(f"✅ Image uploaded successfully! Media ID: {media_id}")
            logger.info(f"   URL: {media_data.get('source_url', 'N/A')}")
            
            return media_id
        
        except requests.exceptions.Timeout:
            logger.error("❌ Upload timeout - image too large or slow connection")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error uploading image: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def publish_draft(self, draft_id: int, workspace_id: int) -> Optional[Dict]:
        """
        Publish draft to WordPress with proper Gutenberg block format
        Downloads and uploads images correctly
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
            
            # Upload featured image (if available)
            featured_media_id = None
            if image_url:
                logger.info(f"📸 Processing featured image: {image_url}")
                featured_media_id = self.upload_image_from_url(image_url, title)
                
                if not featured_media_id:
                    logger.warning("⚠️ Featured image upload failed, continuing without image")
            
            # Convert content to Gutenberg blocks
            gutenberg_content = self._convert_to_gutenberg_blocks(content, featured_media_id)
            
            # Create WordPress post
            post_data = {
                'title': title,
                'content': gutenberg_content,
                'excerpt': summary or '',
                'status': 'draft',  # Create as draft for review
            }
            
            # Attach featured image (this is how WordPress shows it in editor)
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
                logger.info(f"✅ Featured image attached: Media ID {featured_media_id}")
            
            logger.info(f"📝 Creating WordPress post: {title}")
            
            response = self.session.post(
                self.posts_url,
                json=post_data,
                timeout=60
            )
            
            if not response.ok:
                logger.error(f"Post creation failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                
                # Common errors
                if response.status_code == 401:
                    logger.error("❌ AUTHENTICATION FAILED")
                elif response.status_code == 403:
                    logger.error("❌ PERMISSION DENIED - User needs author/editor role")
                
                return None
            
            try:
                post = response.json()
                post_id = post.get('id')
                post_url = post.get('link')
                
                if not post_id:
                    logger.error("No post ID in response")
                    return None
                
                logger.info(f"✅ Post created successfully!")
                logger.info(f"   Post ID: {post_id}")
                logger.info(f"   URL: {post_url}")
                
                return {
                    'post_id': post_id,
                    'url': post_url,
                    'status': 'draft',
                    'featured_image': featured_media_id
                }
            
            except ValueError as e:
                logger.error(f"JSON parsing error: {e}")
                return None
        
        except Exception as e:
            logger.error(f"Error publishing to WordPress: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _convert_to_gutenberg_blocks(self, html_content: str, featured_media_id: Optional[int] = None) -> str:
        """
        Convert HTML content to WordPress Gutenberg blocks
        Ensures proper rendering in WordPress block editor
        """
        import re
        
        blocks = []
        
        # Add featured image block at top if available
        if featured_media_id:
            blocks.append(f'''<!-- wp:image {{"id":{featured_media_id},"sizeSlug":"large","linkDestination":"none"}} -->
<figure class="wp-block-image size-large"><img src="" alt="" class="wp-image-{featured_media_id}"/></figure>
<!-- /wp:image -->''')
        
        # Clean HTML content
        content = html_content.strip()
        
        # Split by newlines and process each line
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect headings
            if line.startswith('<h2>') or line.startswith('<h2 '):
                heading_text = re.sub(r'<.*?>', '', line)
                blocks.append(f'''<!-- wp:heading -->
<h2 class="wp-block-heading">{heading_text}</h2>
<!-- /wp:heading -->''')
            
            elif line.startswith('<h3>') or line.startswith('<h3 '):
                heading_text = re.sub(r'<.*?>', '', line)
                blocks.append(f'''<!-- wp:heading {{"level":3}} -->
<h3 class="wp-block-heading">{heading_text}</h3>
<!-- /wp:heading -->''')
            
            elif line.startswith('<h4>') or line.startswith('<h4 '):
                heading_text = re.sub(r'<.*?>', '', line)
                blocks.append(f'''<!-- wp:heading {{"level":4}} -->
<h4 class="wp-block-heading">{heading_text}</h4>
<!-- /wp:heading -->''')
            
            # Detect paragraphs
            elif line.startswith('<p>') or line.startswith('<p '):
                para_text = re.sub(r'<p[^>]*>|</p>', '', line).strip()
                if para_text:
                    blocks.append(f'''<!-- wp:paragraph -->
<p>{para_text}</p>
<!-- /wp:paragraph -->''')
            
            # Detect lists
            elif line.startswith('<ul>') or line.startswith('<ul '):
                # Extract list items
                items = re.findall(r'<li>(.*?)</li>', line)
                if items:
                    list_html = '\n'.join([f'<li>{item}</li>' for item in items])
                    blocks.append(f'''<!-- wp:list -->
<ul>{list_html}</ul>
<!-- /wp:list -->''')
            
            # Plain text (no HTML tags) - convert to paragraph
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
                user_data = response.json()
                logger.info(f"✅ WordPress connection successful!")
                logger.info(f"   User: {user_data.get('name', 'Unknown')}")
                logger.info(f"   Roles: {', '.join(user_data.get('roles', []))}")
                
                # Check permissions
                roles = user_data.get('roles', [])
                if not any(role in roles for role in ['administrator', 'editor', 'author']):
                    logger.warning("⚠️ User role may not have media upload permissions!")
                    logger.warning("   Recommended: author, editor, or administrator")
                
                return True
            else:
                logger.warning(f"WordPress connection test failed: {response.status_code}")
                logger.warning(f"Response: {response.text[:500]}")
                
                if response.status_code == 401:
                    logger.error("❌ AUTHENTICATION FAILED!")
                    logger.error("   Check: Username and Application Password are correct")
                elif response.status_code == 403:
                    logger.error("❌ PERMISSION DENIED!")
                    logger.error("   Check: REST API is enabled")
                
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during WordPress connection test: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection test: {e}")
            return False
