"""
News Matching & Verification Module
Groups same-event headlines using AI-powered similarity
"""

import sqlite3
import logging
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, util
import numpy as np

logger = logging.getLogger(__name__)

class NewsMatchEngine:
    """Match and group same-event news items"""
    
    def __init__(self, db_path: str, model_path: str = 'models/all-MiniLM-L6-v2'):
        self.db_path = db_path
        self.model = self._load_model(model_path)
    
    def _load_model(self, model_path: str):
        """Load SentenceTransformer model"""
        try:
            return SentenceTransformer(model_path)
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None
    
    def group_similar_headlines(self, workspace_id: int, threshold: float = 0.7) -> Dict[int, List[int]]:
        """
        Group headlines by similarity
        Returns dict: {group_id: [news_ids]}
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent unprocessed news items
            cursor.execute('''
                SELECT id, headline FROM news_queue
                WHERE workspace_id = ? AND status = 'new'
                ORDER BY fetched_at DESC
                LIMIT 100
            ''', (workspace_id,))
            
            news_items = cursor.fetchall()
            
            if not news_items or not self.model:
                conn.close()
                return {}
            
            # Encode headlines
            headlines = [item[1] for item in news_items]
            embeddings = self.model.encode(headlines, convert_to_tensor=True)
            
            # Calculate similarity
            groups = {}
            processed = set()
            
            for i, (news_id_i, headline_i) in enumerate(news_items):
                if i in processed:
                    continue
                
                group = [news_id_i]
                processed.add(i)
                
                for j, (news_id_j, headline_j) in enumerate(news_items):
                    if j <= i or j in processed:
                        continue
                    
                    # Calculate cosine similarity
                    similarity = util.pytorch_cos_sim(embeddings[i], embeddings[j])[0][0].item()
                    
                    if similarity >= threshold:
                        group.append(news_id_j)
                        processed.add(j)
                
                if len(group) >= 2:  # Only create group if multiple sources
                    # Create news group
                    group_hash = self._generate_group_hash(headlines[i])
                    cursor.execute('''
                        INSERT INTO news_groups (workspace_id, group_hash, source_count)
                        VALUES (?, ?, ?)
                    ''', (workspace_id, group_hash, len(group)))
                    
                    group_id = cursor.lastrowid
                    
                    # Associate news items with group
                    for news_id in group:
                        cursor.execute('''
                            INSERT INTO grouped_news (group_id, news_id, similarity_score)
                            VALUES (?, ?, ?)
                        ''', (group_id, news_id, threshold))
                        
                        # Update news item status
                        cursor.execute('''
                            UPDATE news_queue SET status = 'grouped', verified_sources = ?
                            WHERE id = ?
                        ''', (len(group), news_id))
                    
                    groups[group_id] = group
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created {len(groups)} news groups")
            return groups
        
        except Exception as e:
            logger.error(f"Error grouping news: {e}")
            return {}
    
    def verify_group_authenticity(self, group_id: int) -> Tuple[bool, float]:
        """
        Verify group authenticity by checking source count and consistency
        Returns (verified: bool, confidence: float)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get group info
            cursor.execute('''
                SELECT source_count FROM news_groups WHERE id = ?
            ''', (group_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return (False, 0.0)
            
            source_count = result[0]
            
            # Authenticity rules:
            # 1 source: Low confidence (0.3)
            # 2-3 sources: Medium confidence (0.6)
            # 4+ sources: High confidence (0.9+)
            
            if source_count == 1:
                return (False, 0.3)  # Single source = not verified
            elif source_count <= 3:
                return (True, 0.6)   # Few sources = medium confidence
            else:
                return (True, min(0.99, 0.7 + (source_count * 0.05)))  # Multiple sources = high confidence
        
        except Exception as e:
            logger.error(f"Error verifying group: {e}")
            return (False, 0.0)
    
    def detect_conflicting_claims(self, group_id: int) -> List[Dict]:
        """
        Detect conflicting facts within same news group
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all facts in group
            cursor.execute('''
                SELECT DISTINCT sf.fact_type, sf.content, sf.source_url
                FROM scraped_facts sf
                JOIN grouped_news gn ON sf.news_id = gn.news_id
                WHERE gn.group_id = ?
            ''', (group_id,))
            
            facts = cursor.fetchall()
            conn.close()
            
            conflicts = []
            
            # Simple conflict detection: same fact_type with different content
            fact_types = {}
            for fact_type, content, source in facts:
                if fact_type not in fact_types:
                    fact_types[fact_type] = []
                fact_types[fact_type].append((content, source))
            
            # Find conflicts
            for fact_type, items in fact_types.items():
                if len(set([item[0] for item in items])) > 1:
                    conflicts.append({
                        'fact_type': fact_type,
                        'items': items
                    })
            
            return conflicts
        
        except Exception as e:
            logger.error(f"Error detecting conflicts: {e}")
            return []
    
    @staticmethod
    def _generate_group_hash(headline: str) -> str:
        """Generate hash for news group from headline"""
        import hashlib
        return hashlib.md5(headline.encode()).hexdigest()[:16]
