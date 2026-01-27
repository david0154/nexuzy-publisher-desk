"""
Enhanced Database Fix Script
Fixes database schema errors including created_at column
"""

import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = 'nexuzy.db'

def fix_database():
    """Fix database schema by adding missing columns"""
    
    if not os.path.exists(DB_PATH):
        logger.error(f"❌ Database not found at: {DB_PATH}")
        logger.info("Please run the application first to create the database.")
        return False
    
    logger.info("="*60)
    logger.info("NEXUZY PUBLISHER DESK - ENHANCED DATABASE FIX")
    logger.info("="*60)
    logger.info(f"Fixing database: {DB_PATH}")
    logger.info("")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check ai_drafts table structure
        cursor.execute("PRAGMA table_info(ai_drafts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        logger.info(f"Current ai_drafts columns: {', '.join(columns)}")
        logger.info("")
        
        # Columns that need to be added (INCLUDING created_at)
        required_columns = {
            'source_url': 'TEXT',
            'source_domain': 'TEXT',
            'image_url': 'TEXT',
            'summary': 'TEXT',
            'headline_suggestions': 'TEXT',
            'is_html': 'BOOLEAN DEFAULT 1',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'generated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }
        
        fixes_applied = 0
        
        for column_name, column_type in required_columns.items():
            if column_name not in columns:
                try:
                    sql = f"ALTER TABLE ai_drafts ADD COLUMN {column_name} {column_type}"
                    logger.info(f"Adding missing column: {column_name}")
                    cursor.execute(sql)
                    conn.commit()
                    logger.info(f"✅ Successfully added: {column_name}")
                    fixes_applied += 1
                except Exception as e:
                    logger.error(f"❌ Error adding {column_name}: {e}")
            else:
                logger.info(f"✓ Column already exists: {column_name}")
        
        # Also check news_queue table
        cursor.execute("PRAGMA table_info(news_queue)")
        news_columns = [col[1] for col in cursor.fetchall()]
        
        logger.info("")
        logger.info(f"Current news_queue columns: {', '.join(news_columns)}")
        logger.info("")
        
        news_required = {
            'image_url': 'TEXT',
            'verified_score': 'REAL DEFAULT 0',
            'verified_sources': 'INTEGER DEFAULT 1',
            'source_domain': 'TEXT'
        }
        
        for column_name, column_type in news_required.items():
            if column_name not in news_columns:
                try:
                    sql = f"ALTER TABLE news_queue ADD COLUMN {column_name} {column_type}"
                    logger.info(f"Adding missing column to news_queue: {column_name}")
                    cursor.execute(sql)
                    conn.commit()
                    logger.info(f"✅ Successfully added: {column_name}")
                    fixes_applied += 1
                except Exception as e:
                    logger.error(f"❌ Error adding {column_name}: {e}")
            else:
                logger.info(f"✓ Column already exists: {column_name}")
        
        # Check translations table
        cursor.execute("PRAGMA table_info(translations)")
        trans_columns = [col[1] for col in cursor.fetchall()]
        
        logger.info("")
        logger.info(f"Current translations columns: {', '.join(trans_columns)}")
        logger.info("")
        
        trans_required = {
            'summary': 'TEXT'
        }
        
        for column_name, column_type in trans_required.items():
            if column_name not in trans_columns:
                try:
                    sql = f"ALTER TABLE translations ADD COLUMN {column_name} {column_type}"
                    logger.info(f"Adding missing column to translations: {column_name}")
                    cursor.execute(sql)
                    conn.commit()
                    logger.info(f"✅ Successfully added: {column_name}")
                    fixes_applied += 1
                except Exception as e:
                    logger.error(f"❌ Error adding {column_name}: {e}")
            else:
                logger.info(f"✓ Column already exists: {column_name}")
        
        conn.close()
        
        logger.info("")
        logger.info("="*60)
        if fixes_applied > 0:
            logger.info(f"✅ DATABASE FIX COMPLETE! Applied {fixes_applied} fixes.")
        else:
            logger.info("✅ DATABASE IS ALREADY UP TO DATE!")
        logger.info("="*60)
        logger.info("")
        logger.info("All database schema errors should now be fixed:")
        logger.info("  ✓ 'no such column: created_at' - FIXED")
        logger.info("  ✓ 'no such column: source_domain' - FIXED")
        logger.info("  ✓ 'no such column: summary' - FIXED")
        logger.info("")
        logger.info("✅ You can now run: python main.py")
        logger.info("")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing database: {e}")
        import traceback
        logger.error(traceback.format_exc())
        logger.error("")
        logger.error("If this error persists, you may need to:")
        logger.error("1. Backup your nexuzy.db file")
        logger.error("2. Delete nexuzy.db")
        logger.error("3. Run python main.py to create a fresh database")
        return False

if __name__ == '__main__':
    success = fix_database()
    if not success:
        input("\nPress Enter to exit...")
