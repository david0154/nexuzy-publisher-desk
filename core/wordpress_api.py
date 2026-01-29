"""
WordPress API Module with SEO Support
Includes: Keywords, Categories, Tags, Meta Descriptions
"""

import requests
import sqlite3
import logging
import re
from typing import Dict, Optional, List
from collections import Counter

logger = logging.getLogger(__name__)

class WordPressAPI:
    def __init__(self, db_path: str = 'nexuzy.db'):
        self.db_path = db_path
        self.session = None
        self.site_url = ''
        self.base_url = ''
        self._category_cache = {}
        self._tag_cache = {}
    
    def _initialize_connection(self, workspace_id: int) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT site_url, username, app_password FROM wp_credentials WHERE workspace_id = ?', (workspace_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False
            
            site_url, username, password = result
            self.site_url = site_url.rstrip('/')
            self.base_url = f"{self.site_url}/wp-json/wp/v2"
            
            self.session = requests.Session()
            self.session.auth = (username, password)
            self.session.headers.update({'User-Agent': 'Nexuzy-Publisher/3.0'})
            
            logger.info(f"✅ Connected to: {self.site_url}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text for SEO tags"""
        if not text:
            return []
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        # Extract words (3+ characters, alphanumeric)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_text.lower())
        
        # Remove common stop words
        stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'will', 'was', 'were', 'been', 'are', 'not', 'but', 'can', 'all'}
        words = [w for w in words if w not in stop_words]
        
        # Get most common words as keywords
        word_counts = Counter(words)
        keywords = [word for word, count in word_counts.most_common(max_keywords)]
        
        return keywords
    
    def _generate_seo_excerpt(self, content: str, max_length: int = 160) -> str:
        """Generate SEO-optimized excerpt/meta description"""
        if not content:
            return ""
        
        # Remove HTML
        text = re.sub(r'<[^>]+>', '', content)
        text = text.strip()
        
        # Get first sentence or 160 chars
        sentences = re.split(r'[.!?]+', text)
        if sentences and len(sentences[0]) <= max_length:
            return sentences[0].strip() + "."
        
        # Truncate to max_length
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + "..."
        
        return text
    
    def publish_draft(self, draft_id: int, workspace_id: int) -> Optional[Dict]:
        """Publish draft to WordPress with SEO optimization"""
        try:
            if not self._initialize_connection(workspace_id):
                return None
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get draft and category from news
            cursor.execute('''
                SELECT d.title, d.body_draft, d.summary, d.image_url, d.source_url, n.category
                FROM ai_drafts d
                LEFT JOIN news_queue n ON d.news_id = n.id
                WHERE d.id = ?
            ''', (draft_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                logger.error(f"Draft {draft_id} not found")
                return None
            
            title, body, summary, image_url, source_url, news_category = result
            
            if not body or len(body) < 100:
                logger.error(f"Draft {draft_id} has insufficient content")
                return None
            
            logger.info(f"📝 Publishing: {title}")
            logger.info(f"   Content: {len(body)} chars, Category: {news_category}")
            
            # Extract keywords for tags
            keywords = self._extract_keywords(body, max_keywords=10)
            logger.info(f"   Keywords: {', '.join(keywords[:5])}...")
            
            # Generate SEO excerpt
            seo_excerpt = self._generate_seo_excerpt(summary or body, max_length=160)
            logger.info(f"   SEO Excerpt: {seo_excerpt[:80]}...")
            
            # Upload image
            featured_media_id = None
            if image_url:
                featured_media_id = self.upload_image_from_url(image_url, title)
            
            # Handle category
            category_ids = []
            if news_category:
                cat_id = self.get_or_create_category(news_category)
                if cat_id:
                    category_ids.append(cat_id)
                    logger.info(f"   Category: {news_category} (ID: {cat_id})")
            
            # Handle tags from keywords
            tag_ids = []
            for keyword in keywords[:10]:  # Max 10 tags
                tag_id = self.get_or_create_tag(keyword)
                if tag_id:
                    tag_ids.append(tag_id)
            logger.info(f"   Tags: {len(tag_ids)} created")
            
            # Convert to Gutenberg
            gutenberg_content = self._convert_to_gutenberg(body, featured_media_id)
            
            # Create WordPress post with SEO data
            post_data = {
                'title': title,
                'content': gutenberg_content,
                'excerpt': seo_excerpt,
                'status': 'draft',
                'meta': {
                    '_yoast_wpseo_metadesc': seo_excerpt,  # Yoast SEO
                    '_aioseop_description': seo_excerpt,    # All in One SEO
                }
            }
            
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
            if category_ids:
                post_data['categories'] = category_ids
            if tag_ids:
                post_data['tags'] = tag_ids
            
            logger.info(f"📤 Sending to WordPress with SEO...")
            
            response = self.session.post(f"{self.base_url}/posts", json=post_data, timeout=60)
            
            if not response.ok:
                logger.error(f"Failed: HTTP {response.status_code}")
                logger.error(response.text[:500])
                return None
            
            post = response.json()
            
            logger.info(f"✅ Published! ID: {post.get('id')}, URL: {post.get('link')}")
            logger.info(f"   Categories: {len(category_ids)}, Tags: {len(tag_ids)}, Keywords: {len(keywords)}")
            
            return {
                'post_id': post.get('id'),
                'url': post.get('link'),
                'status': 'draft',
                'featured_image': featured_media_id,
                'categories': category_ids,
                'tags': tag_ids,
                'keywords': keywords,
                'seo_excerpt': seo_excerpt
            }
        
        except Exception as e:
            logger.error(f"Error publishing: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def upload_image_from_url(self, image_url: str, title: str = '') -> Optional[int]:
        try:
            img_response = requests.get(image_url, timeout=30)
            if img_response.status_code != 200:
                return None
            filename = image_url.split('/')[-1].split('?')[0] or 'image.jpg'
            files = {'file': (filename, img_response.content, 'image/jpeg')}
            response = self.session.post(f"{self.base_url}/media", files=files, timeout=60)
            if response.ok:
                return response.json().get('id')
            return None
        except:
            return None
    
    def get_or_create_category(self, name: str) -> Optional[int]:
        if name in self._category_cache:
            return self._category_cache[name]
        try:
            resp = self.session.get(f"{self.base_url}/categories", params={'search': name})
            if resp.ok:
                for cat in resp.json():
                    if cat['name'].lower() == name.lower():
                        self._category_cache[name] = cat['id']
                        return cat['id']
            create_resp = self.session.post(f"{self.base_url}/categories", json={'name': name})
            if create_resp.ok:
                cat_id = create_resp.json()['id']
                self._category_cache[name] = cat_id
                return cat_id
        except:
            pass
        return None
    
    def get_or_create_tag(self, name: str) -> Optional[int]:
        if name in self._tag_cache:
            return self._tag_cache[name]
        try:
            resp = self.session.get(f"{self.base_url}/tags", params={'search': name})
            if resp.ok:
                for tag in resp.json():
                    if tag['name'].lower() == name.lower():
                        self._tag_cache[name] = tag['id']
                        return tag['id']
            create_resp = self.session.post(f"{self.base_url}/tags", json={'name': name})
            if create_resp.ok:
                tag_id = create_resp.json()['id']
                self._tag_cache[name] = tag_id
                return tag_id
        except:
            pass
        return None
    
    def _convert_to_gutenberg(self, html: str, media_id: Optional[int] = None) -> str:
        blocks = []
        if media_id:
            blocks.append(f'<!-- wp:image {{"id":{media_id}}} -->\n<figure class="wp-block-image"><img src="" class="wp-image-{media_id}"/></figure>\n<!-- /wp:image -->')
        
        for match in re.finditer(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL):
            text = re.sub(r'<.*?>', '', match.group(1)).strip()
            if text:
                blocks.append(f'<!-- wp:heading -->\n<h2>{text}</h2>\n<!-- /wp:heading -->')
        
        for match in re.finditer(r'<p[^>]*>(.*?)</p>', html, re.DOTALL):
            text = ' '.join(match.group(1).split())
            if text:
                blocks.append(f'<!-- wp:paragraph -->\n<p>{text}</p>\n<!-- /wp:paragraph -->')
        
        result = '\n\n'.join(blocks)
        return result if result else html
    
    def test_connection(self, site_url: str, username: str, password: str) -> bool:
        try:
            url = site_url.rstrip('/') + '/wp-json/wp/v2/users/me'
            session = requests.Session()
            session.auth = (username, password)
            response = session.get(url, timeout=15)
            return response.status_code == 200
        except:
            return False
