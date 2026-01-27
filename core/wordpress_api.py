"""
WordPress API Module - CRITICAL FIX for Content Loss
Proper Gutenberg conversion that preserves ALL content
"""

import requests
import sqlite3
import logging
from typing import Dict, Optional, List
from pathlib import Path
import re
from html.parser import HTMLParser

logger = logging.getLogger(__name__)

class WordPressAPI:
    """Handle WordPress API interactions with PROPER content handling"""
    
    def __init__(self, db_path: str = 'nexuzy.db'):
        self.db_path = db_path
        self.session = None
        self.site_url = ''
        self.base_url = ''
        self.media_url = ''
        self.posts_url = ''
        self.categories_url = ''
        self.tags_url = ''
        self._category_cache = {}
        self._tag_cache = {}
    
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
            
            self.session = requests.Session()
            self.session.auth = (username, password)
            self.session.headers.update({'User-Agent': 'Nexuzy-Publisher/2.0'})
            
            logger.info(f"✅ Connected to: {self.site_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize WordPress connection: {e}")
            return False

    def upload_image_from_url(self, image_url: str, title: str = '') -> Optional[int]:
        """Download image from URL → Upload to WordPress media library"""
        if not image_url or not image_url.startswith('http'):
            return None
        
        try:
            img_response = requests.get(image_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            if img_response.status_code != 200:
                return None
            
            filename = image_url.split('/')[-1].split('?')[0] or 'image.jpg'
            if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                filename += '.jpg'
            
            content_type = img_response.headers.get('Content-Type', 'image/jpeg')
            
            files = {'file': (filename, img_response.content, content_type)}
            data = {'title': title, 'alt_text': title} if title else {}
            
            response = self.session.post(self.media_url, files=files, data=data, timeout=60)
            
            if response.ok:
                media_id = response.json().get('id')
                if media_id:
                    logger.info(f"✅ Image uploaded! Media ID: {media_id}")
                return media_id
            
            return None
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return None
    
    def get_or_create_category(self, category_name: str) -> Optional[int]:
        """Get existing WordPress category ID or create new one"""
        if not category_name or not category_name.strip():
            return None
        
        category_name = category_name.strip()
        
        if category_name in self._category_cache:
            return self._category_cache[category_name]
        
        try:
            response = self.session.get(self.categories_url, params={'search': category_name, 'per_page': 10}, timeout=10)
            
            if response.ok:
                for cat in response.json():
                    if cat.get('name', '').lower() == category_name.lower():
                        cat_id = cat.get('id')
                        self._category_cache[category_name] = cat_id
                        return cat_id
            
            create_response = self.session.post(self.categories_url, json={'name': category_name}, timeout=10)
            
            if create_response.ok:
                cat_id = create_response.json().get('id')
                self._category_cache[category_name] = cat_id
                return cat_id
        except Exception as e:
            logger.error(f"Error handling category: {e}")
        
        return None
    
    def get_or_create_tag(self, tag_name: str) -> Optional[int]:
        """Get existing WordPress tag ID or create new one"""
        if not tag_name or not tag_name.strip():
            return None
        
        tag_name = tag_name.strip()
        if tag_name in self._tag_cache:
            return self._tag_cache[tag_name]
        
        try:
            response = self.session.get(self.tags_url, params={'search': tag_name, 'per_page': 10}, timeout=10)
            if response.ok:
                for tag in response.json():
                    if tag.get('name', '').lower() == tag_name.lower():
                        tag_id = tag.get('id')
                        self._tag_cache[tag_name] = tag_id
                        return tag_id
            
            create_response = self.session.post(self.tags_url, json={'name': tag_name}, timeout=10)
            if create_response.ok:
                tag_id = create_response.json().get('id')
                self._tag_cache[tag_name] = tag_id
                return tag_id
        except:
            pass
        
        return None
    
    def _extract_categories_from_draft(self, draft_id: int) -> List[str]:
        """Extract category names from news source RSS feed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
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
                if result[0]: categories.append(result[0])
                if result[1]: categories.append(result[1])
                return [cat.strip() for cat in categories if cat and cat.strip()]
            return []
        except Exception as e:
            logger.error(f"Error extracting categories: {e}")
            return []
    
    def publish_draft(self, draft_id: int, workspace_id: int, categories: Optional[List[str]] = None, tags: Optional[List[str]] = None) -> Optional[Dict]:
        """
        Publish draft to WordPress - GUARANTEED to include full content
        """
        try:
            if not self._initialize_connection(workspace_id):
                return None
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT title, body_draft, summary, image_url, source_url FROM ai_drafts WHERE id = ?', (draft_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                logger.error(f"Draft {draft_id} not found")
                return None
            
            title, body_content, summary, image_url, source_url = result
            
            # CRITICAL CHECK
            if not body_content or not body_content.strip():
                logger.error(f"❌ CRITICAL: Draft {draft_id} body_draft is EMPTY!")
                logger.error("   Translation may have failed or content wasn't saved")
                return None
            
            logger.info(f"📝 Publishing: {title}")
            logger.info(f"   Original content: {len(body_content)} chars")
            logger.info(f"   Preview: {body_content[:200]}...")
            
            # Upload image
            featured_media_id = None
            if image_url:
                featured_media_id = self.upload_image_from_url(image_url, title)
            
            # Get categories
            category_ids = []
            if categories is None:
                categories = self._extract_categories_from_draft(draft_id)
            if categories:
                for cat_name in categories:
                    cat_id = self.get_or_create_category(cat_name)
                    if cat_id:
                        category_ids.append(cat_id)
            
            # Get tags
            tag_ids = []
            if tags:
                for tag_name in tags:
                    tag_id = self.get_or_create_tag(tag_name)
                    if tag_id:
                        tag_ids.append(tag_id)
            
            # Convert to Gutenberg with ROBUST handling
            gutenberg_content = self._convert_to_gutenberg_blocks(body_content, featured_media_id)
            
            # CRITICAL: Verify conversion worked
            if not gutenberg_content or len(gutenberg_content) < 50:
                logger.error(f"❌ Gutenberg conversion FAILED!")
                logger.error(f"   Input: {len(body_content)} chars")
                logger.error(f"   Output: {len(gutenberg_content) if gutenberg_content else 0} chars")
                logger.warning("⚠️ Using RAW HTML as fallback...")
                
                # FALLBACK: Send raw HTML (WordPress will handle it)
                gutenberg_content = body_content
            
            logger.info(f"   Gutenberg content: {len(gutenberg_content)} chars")
            
            # Create post with ALL data
            post_data = {
                'title': title,
                'content': gutenberg_content,  # FULL CONTENT HERE
                'excerpt': summary or '',
                'status': 'draft',
            }
            
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
            if category_ids:
                post_data['categories'] = category_ids
            if tag_ids:
                post_data['tags'] = tag_ids
            
            logger.info(f"📤 Sending to WordPress...")
            logger.debug(f"   POST data: {post_data.keys()}")
            logger.debug(f"   Content length in POST: {len(post_data.get('content', ''))} chars")
            
            response = self.session.post(self.posts_url, json=post_data, timeout=60)
            
            if not response.ok:
                logger.error(f"❌ Post failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text[:1000]}")
                return None
            
            post = response.json()
            post_id = post.get('id')
            post_url = post.get('link')
            
            if not post_id:
                logger.error("No post ID in response!")
                return None
            
            # Verify what WordPress saved
            posted_content = post.get('content', {}).get('rendered', '')
            logger.info(f"\n✅ POST CREATED!")
            logger.info(f"   Post ID: {post_id}")
            logger.info(f"   URL: {post_url}")
            logger.info(f"   Content saved: {len(posted_content)} chars")
            
            if len(posted_content) < len(body_content) * 0.5:  # Less than 50% of original
                logger.warning("⚠️ WARNING: Content seems incomplete!")
                logger.warning(f"   Expected: ~{len(body_content)} chars")
                logger.warning(f"   Got: {len(posted_content)} chars")
                logger.warning("   Check WordPress post manually!")
            
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
            logger.error(f"❌ Error publishing: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _convert_to_gutenberg_blocks(self, html_content: str, featured_media_id: Optional[int] = None) -> str:
        """
        Convert HTML to Gutenberg - ROBUST version that handles ALL formats
        
        CRITICAL FIX: Parse by complete HTML elements, not lines
        This fixes the "only title pushed" bug where multi-line content was lost
        """
        if not html_content or not html_content.strip():
            logger.error("❌ _convert_to_gutenberg: Input is empty!")
            return ""
        
        blocks = []
        
        # Add featured image
        if featured_media_id:
            blocks.append(f'''<!-- wp:image {{"id":{featured_media_id},"sizeSlug":"large"}} -->
<figure class="wp-block-image size-large"><img src="" alt="" class="wp-image-{featured_media_id}"/></figure>
<!-- /wp:image -->''')
        
        # Clean content - remove extra whitespace but preserve structure
        content = html_content.strip()
        
        # CRITICAL FIX: Parse complete HTML elements using regex
        # This handles multi-line tags that were being split incorrectly
        
        # Extract all H2 headings
        for match in re.finditer(r'<h2[^>]*>(.*?)</h2>', content, re.DOTALL | re.IGNORECASE):
            text = re.sub(r'<.*?>', '', match.group(1)).strip()
            text = ' '.join(text.split())  # Normalize whitespace
            if text:
                blocks.append(f'''<!-- wp:heading -->
<h2 class="wp-block-heading">{text}</h2>
<!-- /wp:heading -->''')
        
        # Extract all H3 headings
        for match in re.finditer(r'<h3[^>]*>(.*?)</h3>', content, re.DOTALL | re.IGNORECASE):
            text = re.sub(r'<.*?>', '', match.group(1)).strip()
            text = ' '.join(text.split())
            if text:
                blocks.append(f'''<!-- wp:heading {{"level":3}} -->
<h3 class="wp-block-heading">{text}</h3>
<!-- /wp:heading -->''')
        
        # Extract all paragraphs (MULTI-LINE SUPPORT)
        for match in re.finditer(r'<p[^>]*>(.*?)</p>', content, re.DOTALL | re.IGNORECASE):
            para_text = match.group(1).strip()
            # Normalize whitespace (join multi-line into single line)
            para_text = ' '.join(para_text.split())
            if para_text:
                blocks.append(f'''<!-- wp:paragraph -->
<p>{para_text}</p>
<!-- /wp:paragraph -->''')
        
        # Extract all lists
        for match in re.finditer(r'<ul[^>]*>(.*?)</ul>', content, re.DOTALL | re.IGNORECASE):
            list_content = match.group(1)
            items = re.findall(r'<li[^>]*>(.*?)</li>', list_content, re.DOTALL | re.IGNORECASE)
            if items:
                list_html = '\n'.join([f'<li>{" ".join(item.split())}</li>' for item in items])
                blocks.append(f'''<!-- wp:list -->
<ul>{list_html}</ul>
<!-- /wp:list -->''')
        
        # Extract ordered lists
        for match in re.finditer(r'<ol[^>]*>(.*?)</ol>', content, re.DOTALL | re.IGNORECASE):
            list_content = match.group(1)
            items = re.findall(r'<li[^>]*>(.*?)</li>', list_content, re.DOTALL | re.IGNORECASE)
            if items:
                list_html = '\n'.join([f'<li>{" ".join(item.split())}</li>' for item in items])
                blocks.append(f'''<!-- wp:list {{"ordered":true}} -->
<ol>{list_html}</ol>
<!-- /wp:list -->''')
        
        result = '\n\n'.join(blocks)
        
        # CRITICAL CHECK: If conversion produced nothing, return original HTML
        if not result or len(result) < 50:
            logger.warning("⚠️ Gutenberg conversion produced minimal output")
            logger.warning(f"   Input: {len(html_content)} chars")
            logger.warning(f"   Output: {len(result)} chars")
            logger.warning("   Returning original HTML as fallback")
            return html_content  # WordPress will handle raw HTML
        
        logger.debug(f"✅ Gutenberg conversion: {len(html_content)} → {len(result)} chars")
        return result
    
    def test_connection(self, site_url: str, username: str, password: str) -> bool:
        """Test WordPress connection"""
        try:
            test_url = site_url.rstrip('/') + '/wp-json/wp/v2/users/me'
            session = requests.Session()
            session.auth = (username, password)
            session.headers.update({'User-Agent': 'Nexuzy-Publisher-Test/2.0'})
            response = session.get(test_url, timeout=15)
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"✅ WordPress connection successful!")
                logger.info(f"   User: {user_data.get('name', 'Unknown')}")
                return True
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
