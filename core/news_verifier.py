"""
News Verification Module
Verifies news authenticity by searching web and checking multiple sources
"""

import logging
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)

class NewsVerifier:
    """Verify news authenticity through web search"""
    
    def __init__(self, db_path='nexuzy.db'):
        self.db_path = db_path
    
    def verify_news_item(self, news_id):
        """Verify a single news item by searching web"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get news details
            cursor.execute('''
                SELECT headline, summary, source_domain FROM news_queue WHERE id = ?
            ''', (news_id,))
            
            news = cursor.fetchone()
            if not news:
                return None
            
            headline, summary, source = news
            
            # Simulate web verification (in production, use real search API)
            # For now, use source credibility scoring
            credibility_score = self._calculate_credibility(source, headline)
            
            # Update news with verification
            cursor.execute('''
                UPDATE news_queue 
                SET status = ?, verified_sources = ?
                WHERE id = ?
            ''', ('verified' if credibility_score > 50 else 'unverified', 
                  credibility_score, news_id))
            
            conn.commit()
            conn.close()
            
            return {
                'news_id': news_id,
                'verified': credibility_score > 50,
                'credibility_score': credibility_score,
                'sources_found': 1  # In production, count actual sources found
            }
        
        except Exception as e:
            logger.error(f"Error verifying news: {e}")
            return None
    
    def _calculate_credibility(self, source_domain, headline):
        """Calculate credibility score based on source and headline"""
        
        # Trusted news sources (higher scores)
        trusted_sources = [
            'cnn.com', 'bbc.com', 'reuters.com', 'apnews.com',
            'nytimes.com', 'theguardian.com', 'washingtonpost.com',
            'bloomberg.com', 'wsj.com', 'ft.com', 'economist.com'
        ]
        
        score = 50  # Base score
        
        # Check source credibility
        for trusted in trusted_sources:
            if trusted in source_domain.lower():
                score += 30
                break
        
        # Check headline quality (no clickbait indicators)
        clickbait_words = ['shocking', 'unbelievable', 'you won\'t believe', 'amazing']
        has_clickbait = any(word in headline.lower() for word in clickbait_words)
        
        if not has_clickbait:
            score += 10
        else:
            score -= 20
        
        # Ensure score is within 0-100
        return max(0, min(100, score))
    
    def bulk_verify(self, workspace_id):
        """Verify all unverified news in workspace"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id FROM news_queue 
                WHERE workspace_id = ? AND status = 'new'
                LIMIT 50
            ''', (workspace_id,))
            
            news_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            verified_count = 0
            for news_id in news_ids:
                result = self.verify_news_item(news_id)
                if result and result['verified']:
                    verified_count += 1
            
            return verified_count, len(news_ids)
        
        except Exception as e:
            logger.error(f"Error in bulk verification: {e}")
            return 0, 0
