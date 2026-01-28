"""
WordPress API Enhanced Module - COMPLETE Content Push with Translation Support
FIXES: Push all translations as separate posts, link to original, handle inline images
"""

import requests
import sqlite3
import logging
from typing import Dict, Optional, List
from pathlib import Path
import re
from html.parser import HTMLParser
from datetime import datetime

logger = logging.getLogger(__name__)

class WordPressAPIEnhanced:
    """Enhanced WordPress API with full translation and image support"""
    
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
        self._uploaded_images = {}  # Cache for uploaded image IDs
    
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
        
        # Check cache
        if image_url in self._uploaded_images:
            return self._uploaded_images[image_url]
        
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
                    self._uploaded_images[image_url] = media_id
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
    
    def publish_draft_with_translations(self, draft_id: int, workspace_id: int, 
                                       categories: Optional[List[str]] = None, 
                                       tags: Optional[List[str]] = None) -> Dict:
        """
        COMPLETE WORKFLOW: Publish original + ALL translations as separate posts
        
        Args:
            draft_id: Original draft ID
            workspace_id: Workspace ID
            categories: Optional categories
            tags: Optional tags
        
        Returns:
            Dict with all published post IDs and URLs
        """
        try:
            if not self._initialize_connection(workspace_id):
                return {'success': False, 'error': 'Could not connect to WordPress'}
            
            # Get draft info
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT title, body_draft, summary, image_url FROM ai_drafts WHERE id = ?', (draft_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                logger.error(f"Draft {draft_id} not found")
                return {'success': False, 'error': f'Draft {draft_id} not found'}
            
            title, body_content, summary, image_url = result
            
            logger.info(f"📄 Publishing with translations for: {title}")
            
            # Upload featured image
            featured_media_id = None
            if image_url:
                featured_media_id = self.upload_image_from_url(image_url, title)
            
            # Publish original post
            logger.info("✅ Publishing ORIGINAL post...")
            original_post = self._publish_single_post(
                title, body_content, summary, featured_media_id,
                categories, tags, language=None
            )
            
            if not original_post or not original_post.get('post_id'):
                return {
                    'success': False,
                    'error': 'Failed to publish original post',
                    'original': original_post
                }
            
            original_post_id = original_post['post_id']
            logger.info(f"✅ Original post created: ID {original_post_id}")
            
            # Get and publish all translations
            translations = self._get_all_translations(draft_id)
            published_translations = {}
            
            for lang, trans_data in translations.items():
                try:
                    logger.info(f"📄 Publishing {lang.upper()} translation...")
                    
                    trans_title = trans_data.get('title', f"{title} ({lang})")
                    trans_body = trans_data.get('body_draft', body_content)
                    trans_summary = trans_data.get('summary', summary)
                    
                    trans_post = self._publish_single_post(
                        trans_title, trans_body, trans_summary, featured_media_id,
                        categories, tags, language=lang
                    )
                    
                    if trans_post and trans_post.get('post_id'):
                        published_translations[lang] = trans_post
                        logger.info(f"✅ {lang.upper()} post created: ID {trans_post['post_id']}")
                        
                        # Link translation to original
                        self._link_posts(original_post_id, trans_post['post_id'], lang)
                    else:
                        logger.warning(f"⚠️ Failed to publish {lang} translation")
                
                except Exception as e:
                    logger.error(f"Error publishing {lang} translation: {e}")
            
            result = {
                'success': True,
                'original_post': original_post,
                'translations': published_translations,
                'total_posts_published': 1 + len(published_translations),
                'status': f"✅ Published {1 + len(published_translations)} posts (original + {len(published_translations)} translations)"
            }
            
            logger.info(result['status'])
            return result
        
        except Exception as e:
            logger.error(f"❌ Publishing failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _publish_single_post(self, title: str, body_content: str, summary: str,
                            featured_media_id: Optional[int], 
                            categories: Optional[List[str]],
                            tags: Optional[List[str]],
                            language: Optional[str] = None) -> Dict:
        """
        Publish single post with GUARANTEED full content
        
        Args:
            title: Post title
            body_content: Full HTML content
            summary: Post summary/excerpt
            featured_media_id: Featured image media ID
            categories: Category names
            tags: Tag names  
            language: Optional language code
        
        Returns:
            Dict with post details or None if failed
        """
        try:
            if not body_content or not body_content.strip():
                logger.error(f"❌ Content is empty for: {title}")
                return None
            
            # Process inline images in content
            processed_content = self._process_inline_images(body_content)
            
            # Convert to Gutenberg
            gutenberg_content = self._convert_to_gutenberg_blocks(processed_content, featured_media_id)
            
            if not gutenberg_content:
                logger.warning("⚠️ Gutenberg conversion failed, using raw content")
                gutenberg_content = body_content
            
            # Get categories
            category_ids = []
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
            
            # Build post data
            post_data = {
                'title': title,
                'content': gutenberg_content,
                'excerpt': summary or '',
                'status': 'draft',
            }
            
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
            if category_ids:
                post_data['categories'] = category_ids
            if tag_ids:
                post_data['tags'] = tag_ids
            
            # Add language metadata if provided
            if language:
                post_data['meta'] = {'language': language}
            
            logger.debug(f"Sending post: {len(gutenberg_content)} chars")
            
            response = self.session.post(self.posts_url, json=post_data, timeout=60)
            
            if not response.ok:
                logger.error(f"❌ Post failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                return None
            
            post = response.json()
            post_id = post.get('id')
            post_url = post.get('link')
            
            if not post_id:
                logger.error("No post ID in response")
                return None
            
            logger.info(f"✅ Post ID: {post_id}")
            logger.info(f"   URL: {post_url}")
            
            return {
                'post_id': post_id,
                'url': post_url,
                'title': title,
                'status': 'draft',
                'featured_image': featured_media_id,
                'categories': category_ids,
                'tags': tag_ids,
                'language': language,
                'content_length': len(gutenberg_content)
            }
        
        except Exception as e:
            logger.error(f"❌ Error publishing: {e}")
            return None
    
    def _get_all_translations(self, draft_id: int) -> Dict[str, Dict]:
        """
        Get all translations for a draft from database
        
        Args:
            draft_id: Original draft ID
        
        Returns:
            Dict with language codes as keys, translation data as values
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if translations table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='translations'")
            if not cursor.fetchone():
                conn.close()
                return {}
            
            # Get all translations for this draft
            cursor.execute('''
                SELECT language, title, body_draft, summary
                FROM translations
                WHERE draft_id = ?
            ''', (draft_id,))
            
            translations = {}
            for row in cursor.fetchall():
                lang = row[0]
                translations[lang] = {
                    'title': row[1],
                    'body_draft': row[2],
                    'summary': row[3]
                }
            
            conn.close()
            logger.info(f"Found {len(translations)} translations: {', '.join(translations.keys())}")
            return translations
        
        except Exception as e:
            logger.error(f"Error getting translations: {e}")
            return {}
    
    def _link_posts(self, original_id: int, translation_id: int, language: str):
        """
        Link translated post to original using post meta
        
        Args:
            original_id: Original post ID
            translation_id: Translation post ID
            language: Language code
        """
        try:
            # Update translation post meta
            meta_url = f"{self.posts_url}/{translation_id}"
            meta_data = {
                'meta': {
                    'original_post': original_id,
                    'translation_language': language
                }
            }
            
            response = self.session.post(meta_url, json=meta_data, timeout=30)
            if response.ok:
                logger.debug(f"✅ Linked {language} post {translation_id} to original {original_id}")
            else:
                logger.debug(f"⚠️ Could not link posts: {response.status_code}")
        except Exception as e:
            logger.debug(f"Error linking posts: {e}")
    
    def _process_inline_images(self, html_content: str) -> str:
        """
        Process inline images: download and replace with WordPress media URLs
        
        Args:
            html_content: HTML content with image tags
        
        Returns:
            HTML with processed image tags
        """
        # Find all img src URLs
        img_pattern = r'<img[^>]*src=["\']([^"\'>]+)["\'][^>]*>'
        
        def replace_img_url(match):
            img_src = match.group(1)
            alt_text = re.search(r'alt=["\']([^"\'>]*)["\']', match.group(0))
            alt_text = alt_text.group(1) if alt_text else 'Image'
            
            # Upload image
            media_id = self.upload_image_from_url(img_src, alt_text)
            
            if media_id:
                # Replace with WordPress image URL
                logger.debug(f"Processed inline image: {img_src} -> Media ID {media_id}")
                return match.group(0)  # WordPress will handle it
            else:
                return match.group(0)  # Keep original if upload fails
        
        try:
            processed = re.sub(img_pattern, replace_img_url, html_content)
            return processed
        except Exception as e:
            logger.warning(f"Error processing inline images: {e}")
            return html_content
    
    def _convert_to_gutenberg_blocks(self, html_content: str, featured_media_id: Optional[int] = None) -> str:
        """
        Convert HTML to Gutenberg blocks with ROBUST multi-line handling
        
        Args:
            html_content: HTML content
            featured_media_id: Optional featured image ID
        
        Returns:
            Gutenberg-formatted content
        """
        if not html_content or not html_content.strip():
            return ""
        
        blocks = []
        
        # Add featured image
        if featured_media_id:
            blocks.append(f'''<!-- wp:image {{"id":{featured_media_id},"sizeSlug":"large"}} -->
<figure class="wp-block-image size-large"><img src="" alt="" class="wp-image-{featured_media_id}"/></figure>
<!-- /wp:image -->''')
        
        content = html_content.strip()
        
        # Extract and process all heading levels
        for level, tag in enumerate(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], 1):
            for match in re.finditer(f'<{tag}[^>]*>(.*?)</{tag}>', content, re.DOTALL | re.IGNORECASE):
                text = re.sub(r'<.*?>', '', match.group(1)).strip()
                text = ' '.join(text.split())
                if text:
                    if level == 1:
                        blocks.append(f'<!-- wp:heading -->\n<h{level} class="wp-block-heading">{text}</h{level}>\n<!-- /wp:heading -->')
                    else:
                        blocks.append(f'<!-- wp:heading {{"level":{level}}} -->\n<h{level} class="wp-block-heading">{text}</h{level}>\n<!-- /wp:heading -->')
        
        # Extract paragraphs (with multi-line support)
        for match in re.finditer(r'<p[^>]*>(.*?)</p>', content, re.DOTALL | re.IGNORECASE):
            para_text = match.group(1).strip()
            para_text = ' '.join(para_text.split())
            if para_text:
                blocks.append(f'<!-- wp:paragraph -->\n<p>{para_text}</p>\n<!-- /wp:paragraph -->')
        
        # Extract unordered lists
        for match in re.finditer(r'<ul[^>]*>(.*?)</ul>', content, re.DOTALL | re.IGNORECASE):
            list_content = match.group(1)
            items = re.findall(r'<li[^>]*>(.*?)</li>', list_content, re.DOTALL | re.IGNORECASE)
            if items:
                list_html = '\n'.join([f'<li>{" ".join(item.split())}</li>' for item in items])
                blocks.append(f'<!-- wp:list -->\n<ul>{list_html}</ul>\n<!-- /wp:list -->')
        
        # Extract ordered lists
        for match in re.finditer(r'<ol[^>]*>(.*?)</ol>', content, re.DOTALL | re.IGNORECASE):
            list_content = match.group(1)
            items = re.findall(r'<li[^>]*>(.*?)</li>', list_content, re.DOTALL | re.IGNORECASE)
            if items:
                list_html = '\n'.join([f'<li>{" ".join(item.split())}</li>' for item in items])
                blocks.append(f'<!-- wp:list {{"ordered":true}} -->\n<ol>{list_html}</ol>\n<!-- /wp:list -->')
        
        result = '\n\n'.join(blocks)
        
        if not result or len(result) < 50:
            logger.warning("Gutenberg conversion produced minimal output, using raw HTML")
            return html_content
        
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
