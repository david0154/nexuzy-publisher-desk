"""
WordPress API Module - FIXED Translation Push + Category Support
Proper image upload + Content + Categories + Tags
"""

import requests
import sqlite3
import logging
from typing import Dict, Optional, List
from pathlib import Path
import tempfile
import hashlib
import re

logger = logging.getLogger(__name__)

class WordPressAPI:
    """Handle WordPress API interactions with PROPER image upload + categories"""
    
    def __init__(self, db_path: str = 'nexuzy.db'):
        self.db_path = db_path
        self.session = None
        self.site_url = ''
        self.base_url = ''
        self.media_url = ''
        self.posts_url = ''
        self.categories_url = ''
        self.tags_url = ''
        self._category_cache = {}  # Cache category IDs
        self._tag_cache = {}  # Cache tag IDs
    
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
            self.categories_url = f"{self.base_url}/categories"
            self.tags_url = f"{self.base_url}/tags"
            
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
        """Download image from URL → Upload to WordPress media library"""
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
                content_type = img_response.headers.get('Content-Type', 'image/jpeg')
                ext = content_type.split('/')[-1].split(';')[0]
                filename = f"featured-image.{ext}"
            
            # Ensure valid extension
            if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                filename += '.jpg'
            
            content_type = img_response.headers.get('Content-Type', 'image/jpeg')
            
            logger.info(f"📤 Uploading to WordPress: {filename} ({len(img_response.content)/1024:.1f} KB)")
            
            # Step 3: Upload to WordPress using multipart/form-data
            files = {
                'file': (filename, img_response.content, content_type)
            }
            
            headers = {
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
            
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
            
            if not response.ok:
                logger.error(f"Upload failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                return None
            
            media_data = response.json()
            media_id = media_data.get('id')
            
            if media_id:
                logger.info(f"✅ Image uploaded! Media ID: {media_id}")
                return media_id
            
            return None
        
        except Exception as e:
            logger.error(f"❌ Error uploading image: {e}")
            return None
    
    def get_or_create_category(self, category_name: str) -> Optional[int]:
        """
        Get existing WordPress category ID or create new one
        
        Args:
            category_name: Category name (e.g., 'Technology', 'Sports')
        
        Returns:
            WordPress category ID or None if failed
        """
        if not category_name or not category_name.strip():
            return None
        
        category_name = category_name.strip()
        
        # Check cache first
        if category_name in self._category_cache:
            logger.debug(f"Using cached category: {category_name} (ID: {self._category_cache[category_name]})")
            return self._category_cache[category_name]
        
        try:
            # Search for existing category
            logger.info(f"🔍 Searching for category: {category_name}")
            response = self.session.get(
                self.categories_url,
                params={'search': category_name, 'per_page': 10},
                timeout=10
            )
            
            if response.ok:
                categories = response.json()
                
                # Find exact match (case-insensitive)
                for cat in categories:
                    if cat.get('name', '').lower() == category_name.lower():
                        cat_id = cat.get('id')
                        logger.info(f"✅ Found existing category: {category_name} (ID: {cat_id})")
                        self._category_cache[category_name] = cat_id
                        return cat_id
            
            # Category doesn't exist - create it
            logger.info(f"📝 Creating new category: {category_name}")
            create_response = self.session.post(
                self.categories_url,
                json={'name': category_name},
                timeout=10
            )
            
            if create_response.ok:
                new_cat = create_response.json()
                cat_id = new_cat.get('id')
                logger.info(f"✅ Category created: {category_name} (ID: {cat_id})")
                self._category_cache[category_name] = cat_id
                return cat_id
            else:
                logger.error(f"Failed to create category: HTTP {create_response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error handling category '{category_name}': {e}")
            return None
    
    def get_or_create_tag(self, tag_name: str) -> Optional[int]:
        """Get existing WordPress tag ID or create new one"""
        if not tag_name or not tag_name.strip():
            return None
        
        tag_name = tag_name.strip()
        
        # Check cache
        if tag_name in self._tag_cache:
            return self._tag_cache[tag_name]
        
        try:
            # Search for existing tag
            response = self.session.get(
                self.tags_url,
                params={'search': tag_name, 'per_page': 10},
                timeout=10
            )
            
            if response.ok:
                tags = response.json()
                for tag in tags:
                    if tag.get('name', '').lower() == tag_name.lower():
                        tag_id = tag.get('id')
                        self._tag_cache[tag_name] = tag_id
                        return tag_id
            
            # Create new tag
            create_response = self.session.post(
                self.tags_url,
                json={'name': tag_name},
                timeout=10
            )
            
            if create_response.ok:
                new_tag = create_response.json()
                tag_id = new_tag.get('id')
                self._tag_cache[tag_name] = tag_id
                return tag_id
        
        except Exception as e:
            logger.error(f"Error handling tag '{tag_name}': {e}")
        
        return None
    
    def _extract_categories_from_draft(self, draft_id: int) -> List[str]:
        """Extract category names from news source RSS feed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get categories from news article
            cursor.execute('''
                SELECT n.category, r.category as feed_category
                FROM ai_drafts d
                JOIN news n ON d.news_id = n.id
                LEFT JOIN rss_feeds r ON n.feed_id = r.id
                WHERE d.id = ?
            ''', (draft_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                categories = []
                if result[0]:  # Article category
                    categories.append(result[0])
                if result[1]:  # Feed category
                    categories.append(result[1])
                return [cat.strip() for cat in categories if cat and cat.strip()]
            
            return []
        
        except Exception as e:
            logger.error(f"Error extracting categories: {e}")
            return []
    
    def publish_draft(self, draft_id: int, workspace_id: int, categories: Optional[List[str]] = None, tags: Optional[List[str]] = None) -> Optional[Dict]:
        """
        Publish draft to WordPress with FULL CONTENT + categories + tags
        
        Args:
            draft_id: Draft ID from database
            workspace_id: Workspace ID for credentials
            categories: List of category names (optional, auto-detected if None)
            tags: List of tag names (optional)
        
        Returns:
            Dict with post details or None if failed
        """
        try:
            if not self._initialize_connection(workspace_id):
                return None
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get draft with FULL CONTENT
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
            
            title, body_content, summary, image_url, source_url = result
            
            # CRITICAL: Check if content exists
            if not body_content or not body_content.strip():
                logger.error(f"❌ Draft {draft_id} has NO CONTENT! body_draft is empty!")
                return None
            
            logger.info(f"📝 Preparing to publish: {title}")
            logger.info(f"   Content length: {len(body_content)} characters")
            
            # Upload featured image
            featured_media_id = None
            if image_url:
                logger.info(f"📸 Processing featured image: {image_url}")
                featured_media_id = self.upload_image_from_url(image_url, title)
                if not featured_media_id:
                    logger.warning("⚠️ Featured image upload failed, continuing without image")
            
            # Handle categories
            category_ids = []
            if categories is None:
                # Auto-detect from RSS feed
                categories = self._extract_categories_from_draft(draft_id)
            
            if categories:
                logger.info(f"📂 Processing categories: {', '.join(categories)}")
                for cat_name in categories:
                    cat_id = self.get_or_create_category(cat_name)
                    if cat_id:
                        category_ids.append(cat_id)
                
                if category_ids:
                    logger.info(f"✅ Categories assigned: {len(category_ids)} categories")
                else:
                    logger.warning("⚠️ No categories assigned")
            
            # Handle tags
            tag_ids = []
            if tags:
                logger.info(f"🏷️ Processing tags: {', '.join(tags)}")
                for tag_name in tags:
                    tag_id = self.get_or_create_tag(tag_name)
                    if tag_id:
                        tag_ids.append(tag_id)
            
            # Convert content to Gutenberg blocks
            gutenberg_content = self._convert_to_gutenberg_blocks(body_content, featured_media_id)
            
            # CRITICAL: Verify content conversion
            if not gutenberg_content or not gutenberg_content.strip():
                logger.error(f"❌ Content conversion failed! Gutenberg blocks are empty!")
                logger.error(f"   Original content length: {len(body_content)}")
                return None
            
            logger.info(f"   Gutenberg blocks length: {len(gutenberg_content)} characters")
            
            # Create WordPress post with FULL DATA
            post_data = {
                'title': title,
                'content': gutenberg_content,  # CRITICAL: Full translated content
                'excerpt': summary or '',
                'status': 'draft',  # Create as draft for review
            }
            
            # Add featured image
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
                logger.info(f"✅ Featured image attached: Media ID {featured_media_id}")
            
            # Add categories
            if category_ids:
                post_data['categories'] = category_ids
                logger.info(f"✅ Categories attached: {category_ids}")
            
            # Add tags
            if tag_ids:
                post_data['tags'] = tag_ids
                logger.info(f"✅ Tags attached: {tag_ids}")
            
            logger.info(f"📤 Posting to WordPress...")
            logger.debug(f"   Post data: title={len(title)} chars, content={len(gutenberg_content)} chars")
            
            response = self.session.post(
                self.posts_url,
                json=post_data,
                timeout=60
            )
            
            if not response.ok:
                logger.error(f"❌ Post creation failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text[:1000]}")
                
                if response.status_code == 401:
                    logger.error("❌ AUTHENTICATION FAILED")
                elif response.status_code == 403:
                    logger.error("❌ PERMISSION DENIED")
                
                return None
            
            post = response.json()
            post_id = post.get('id')
            post_url = post.get('link')
            
            if not post_id:
                logger.error("No post ID in response")
                return None
            
            # Verify content was posted
            posted_content = post.get('content', {}).get('rendered', '')
            if not posted_content or len(posted_content) < 50:
                logger.warning(f"⚠️ WARNING: Posted content seems too short!")
                logger.warning(f"   Posted: {len(posted_content)} characters")
                logger.warning(f"   Expected: {len(body_content)} characters")
            
            logger.info(f"\n✅ POST CREATED SUCCESSFULLY!")
            logger.info(f"   Post ID: {post_id}")
            logger.info(f"   URL: {post_url}")
            logger.info(f"   Categories: {len(category_ids)} assigned")
            logger.info(f"   Tags: {len(tag_ids)} assigned")
            logger.info(f"   Content: {len(posted_content)} characters posted")
            
            return {
                'post_id': post_id,
                'url': post_url,
                'status': 'draft',
                'featured_image': featured_media_id,
                'categories': category_ids,
                'tags': tag_ids,
                'content_length': len(posted_content)
            }
        
        except Exception as e:
            logger.error(f"❌ Error publishing to WordPress: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _convert_to_gutenberg_blocks(self, html_content: str, featured_media_id: Optional[int] = None) -> str:
        """
        Convert HTML content to WordPress Gutenberg blocks
        CRITICAL: Must preserve ALL content
        """
        if not html_content or not html_content.strip():
            logger.error("❌ Empty content passed to Gutenberg converter!")
            return ""
        
        blocks = []
        
        # Add featured image block at top if available
        if featured_media_id:
            blocks.append(f'''<!-- wp:image {{"id":{featured_media_id},"sizeSlug":"large","linkDestination":"none"}} -->
<figure class="wp-block-image size-large"><img src="" alt="" class="wp-image-{featured_media_id}"/></figure>
<!-- /wp:image -->''')
        
        # Clean and process content
        content = html_content.strip()
        
        # Split by lines
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect headings
            if line.startswith('<h2>') or line.startswith('<h2 '):
                heading_text = re.sub(r'<.*?>', '', line)
                if heading_text.strip():
                    blocks.append(f'''<!-- wp:heading -->
<h2 class="wp-block-heading">{heading_text}</h2>
<!-- /wp:heading -->''')
            
            elif line.startswith('<h3>') or line.startswith('<h3 '):
                heading_text = re.sub(r'<.*?>', '', line)
                if heading_text.strip():
                    blocks.append(f'''<!-- wp:heading {{"level":3}} -->
<h3 class="wp-block-heading">{heading_text}</h3>
<!-- /wp:heading -->''')
            
            elif line.startswith('<h4>') or line.startswith('<h4 '):
                heading_text = re.sub(r'<.*?>', '', line)
                if heading_text.strip():
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
            elif '<ul>' in line or '<ul ' in line:
                items = re.findall(r'<li>(.*?)</li>', line, re.DOTALL)
                if items:
                    list_html = '\n'.join([f'<li>{item.strip()}</li>' for item in items])
                    blocks.append(f'''<!-- wp:list -->
<ul>{list_html}</ul>
<!-- /wp:list -->''')
            
            elif '<ol>' in line or '<ol ' in line:
                items = re.findall(r'<li>(.*?)</li>', line, re.DOTALL)
                if items:
                    list_html = '\n'.join([f'<li>{item.strip()}</li>' for item in items])
                    blocks.append(f'''<!-- wp:list {{"ordered":true}} -->
<ol>{list_html}</ol>
<!-- /wp:list -->''')
            
            # Plain text - convert to paragraph
            elif line and not line.startswith('<'):
                blocks.append(f'''<!-- wp:paragraph -->
<p>{line}</p>
<!-- /wp:paragraph -->''')
        
        result = '\n\n'.join(blocks)
        
        if not result:
            logger.error(f"❌ Gutenberg conversion produced empty result!")
            logger.error(f"   Original content: {html_content[:200]}...")
        
        return result
    
    def test_connection(self, site_url: str, username: str, password: str) -> bool:
        """Test WordPress connection"""
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
                
                return True
            else:
                logger.error(f"WordPress connection failed: HTTP {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Error during connection test: {e}")
            return False
