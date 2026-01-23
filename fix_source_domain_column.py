#!/usr/bin/env python3
"""
Database Migration Script - Add source_domain column
Fixes: 'no such column: source_domain' error in translator
"""

import sqlite3
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_database():
    """Add missing source_domain column to ai_drafts table"""
    db_path = 'nexuzy.db'
    
    if not os.path.exists(db_path):
        logger.error(f"❌ Database not found at: {db_path}")
        logger.info("Please run this script from the project root directory.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(ai_drafts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'source_domain' not in columns:
            logger.info("Adding source_domain column to ai_drafts table...")
            cursor.execute("ALTER TABLE ai_drafts ADD COLUMN source_domain TEXT")
            conn.commit()
            logger.info("✅ Column 'source_domain' added successfully!")
        else:
            logger.info("✅ Column 'source_domain' already exists.")
        
        # Also check and add is_html column if missing (for completeness)
        if 'is_html' not in columns:
            logger.info("Adding is_html column to ai_drafts table...")
            cursor.execute("ALTER TABLE ai_drafts ADD COLUMN is_html BOOLEAN DEFAULT 1")
            conn.commit()
            logger.info("✅ Column 'is_html' added successfully!")
        
        # Also check and add created_at column if missing
        if 'created_at' not in columns:
            logger.info("Adding created_at column to ai_drafts table...")
            cursor.execute("ALTER TABLE ai_drafts ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
            logger.info("✅ Column 'created_at' added successfully!")
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(ai_drafts)")
        all_columns = [col[1] for col in cursor.fetchall()]
        logger.info(f"\n📋 Current ai_drafts table columns: {', '.join(all_columns)}")
        
        conn.close()
        
        logger.info("\n" + "="*60)
        logger.info("✅ DATABASE MIGRATION COMPLETE!")
        logger.info("You can now run the application without errors.")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("Database Migration: Fix source_domain Column")
    logger.info("="*60)
    
    success = fix_database()
    
    if success:
        sys.exit(0)
    else:
        logger.error("\nMigration failed! Please check the errors above.")
        sys.exit(1)
