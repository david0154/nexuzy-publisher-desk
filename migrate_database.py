"""
Database Migration Script
Adds placeholder_image column to ads_settings table
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database(db_path='nexuzy.db'):
    """Add placeholder_image column to ads_settings if it doesn't exist"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(ads_settings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'placeholder_image' not in columns:
            logger.info("➕ Adding placeholder_image column to ads_settings...")
            cursor.execute('''
                ALTER TABLE ads_settings 
                ADD COLUMN placeholder_image TEXT DEFAULT "https://via.placeholder.com/1200x630/3498db/ffffff?text=Nexuzy+Publisher+Desk"
            ''')
            conn.commit()
            logger.info("✅ Successfully added placeholder_image column")
        else:
            logger.info("✅ placeholder_image column already exists")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("Database Migration: Adding Placeholder Image Support")
    logger.info("="*60)
    
    if migrate_database():
        logger.info("✅ Migration completed successfully!")
    else:
        logger.error("❌ Migration failed!")
