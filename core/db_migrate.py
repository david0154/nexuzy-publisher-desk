"""
Database Migration Script
Adds missing columns for image support
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)

def migrate_database(db_path='nexuzy.db'):
    """Add image_url columns to tables"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check and add image_url to news_queue
        cursor.execute("PRAGMA table_info(news_queue)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'image_url' not in columns:
            logger.info("Adding image_url column to news_queue...")
            cursor.execute('''ALTER TABLE news_queue ADD COLUMN image_url TEXT''')
            logger.info("[OK] Added image_url to news_queue")
        
        # Check and add image_url to ai_drafts
        cursor.execute("PRAGMA table_info(ai_drafts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'image_url' not in columns:
            logger.info("Adding image_url column to ai_drafts...")
            cursor.execute('''ALTER TABLE ai_drafts ADD COLUMN image_url TEXT''')
            logger.info("[OK] Added image_url to ai_drafts")
        
        if 'source_url' not in columns:
            logger.info("Adding source_url column to ai_drafts...")
            cursor.execute('''ALTER TABLE ai_drafts ADD COLUMN source_url TEXT''')
            logger.info("[OK] Added source_url to ai_drafts")
        
        conn.commit()
        conn.close()
        
        logger.info("[OK] Database migration complete")
        return True
    
    except Exception as e:
        logger.error(f"Database migration error: {e}")
        return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    migrate_database()
