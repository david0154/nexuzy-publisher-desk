"""
WordPress Integration Module
Handles WordPress REST API communication and draft publishing
"""

import sqlite3
import logging
import requests
import json
from typing import Dict, Optional
from base64 import b64encode

logger = logging.getLogger(__name__)

class WordPressAPI:
    """WordPress REST API integration"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def test_connection(self, site_url: str, username: str, app_password: str) -> bool:
        """
        Test WordPress connection
        """
        try:
            # Normalize URL
            if not site_url.endswith('/'):
                site_url += '/'
            
            api_url = f"{site_url}wp-json/wp/v2/posts"
            
            # Create auth header
            credentials = b64encode(f"{username}:{app_password}".encode()).decode()
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            }
            
            # Test request
            response = requests.get(
                api_url,
                headers=headers,
                params={'per_page': 1},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("WordPress connection successful")
                return True
            elif response.status_code == 401:
                logger.error("WordPress authentication failed")
                return False
            else:
                logger.error(f"WordPress connection failed: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Error testing WordPress connection: {e}")
            return False
    
    def save_credentials(self, workspace_id: int, site_url: str, username: str, app_password: str) -> bool:
        """
        Save WordPress credentials to database
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test connection first
            if not self.test_connection(site_url, username, app_password):
                return False
            
            # Store credentials
            cursor.execute('''
                INSERT OR REPLACE INTO wp_credentials 
                (workspace_id, site_url, username, app_password, connected)
                VALUES (?, ?, ?, ?, 1)
            ''', (workspace_id, site_url, username, app_password))
            
            conn.commit()
            conn.close()
            
            logger.info("WordPress credentials saved")
            return True
        
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            return False
    
    def get_credentials(self, workspace_id: int) -> Optional[Dict]:
        """
        Retrieve WordPress credentials for workspace
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT site_url, username, app_password FROM wp_credentials
                WHERE workspace_id = ?
            ''', (workspace_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'site_url': result[0],
                    'username': result[1],
                    'app_password': result[2]
                }
            return None
        
        except Exception as e:
            logger.error(f"Error retrieving credentials: {e}")
            return None
    
    def publish_draft(self, draft_id: int, workspace_id: int) -> Optional[Dict]:
        """
        Publish draft to WordPress as draft post
        Returns: {post_id, url} or None on failure
        """
        try:
            # Get credentials
            creds = self.get_credentials(workspace_id)
            if not creds:
                logger.error("WordPress credentials not found")
                return None
            
            # Get draft content
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT title, body_draft, summary FROM ai_drafts WHERE id = ?
            ''', (draft_id,))
            
            draft = cursor.fetchone()
            conn.close()
            
            if not draft:
                logger.error(f"Draft {draft_id} not found")
                return None
            
            title, body, summary = draft
            
            # Prepare API request
            site_url = creds['site_url']
            if not site_url.endswith('/'):
                site_url += '/'
            
            api_url = f"{site_url}wp-json/wp/v2/posts"
            
            credentials = b64encode(
                f"{creds['username']}:{creds['app_password']}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'title': title,
                'content': body,
                'excerpt': summary,
                'status': 'draft',  # Always save as draft
                'categories': [1],  # Default category
                'tags': ['auto-published']
            }
            
            # Send request
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                post_id = result.get('id')
                post_url = result.get('link')
                
                # Store reference in database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO wordpress_posts 
                    (draft_id, wp_post_id, wp_site_url, status)
                    VALUES (?, ?, ?, 'draft')
                ''', (draft_id, post_id, site_url))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Draft published to WordPress: {post_url}")
                return {
                    'post_id': post_id,
                    'url': post_url,
                    'status': 'draft'
                }
            
            else:
                logger.error(f"WordPress API error: {response.status_code}")
                logger.error(response.text)
                return None
        
        except Exception as e:
            logger.error(f"Error publishing to WordPress: {e}")
            return None
