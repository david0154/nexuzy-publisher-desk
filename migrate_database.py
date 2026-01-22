"""
Database Migration Script
Adds missing columns to existing database
"""

import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = 'nexuzy.db'

def migrate_database():
    """Migrate existing database to latest schema"""
    
    if not os.path.exists(DB_PATH):
        logger.info("No existing database found. Will be created on first run.")
        return
    
    logger.info(f"Migrating database: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get existing columns in news_queue
    cursor.execute("PRAGMA table_info(news_queue)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    logger.info(f"Existing columns in news_queue: {existing_columns}")
    
    # Add missing columns
    migrations = [
        ("image_url", "ALTER TABLE news_queue ADD COLUMN image_url TEXT"),
        ("verified_score", "ALTER TABLE news_queue ADD COLUMN verified_score REAL DEFAULT 0"),
        ("verified_sources", "ALTER TABLE news_queue ADD COLUMN verified_sources INTEGER DEFAULT 1"),
    ]
    
    for column_name, sql in migrations:
        if column_name not in existing_columns:
            try:
                logger.info(f"Adding column: {column_name}")
                cursor.execute(sql)
                conn.commit()
                logger.info(f"✅ Added: {column_name}")
            except Exception as e:
                logger.error(f"Error adding {column_name}: {e}")
    
    # Check ai_drafts table
    cursor.execute("PRAGMA table_info(ai_drafts)")
    draft_columns = [col[1] for col in cursor.fetchall()]
    
    draft_migrations = [
        ("image_url", "ALTER TABLE ai_drafts ADD COLUMN image_url TEXT"),
        ("headline_suggestions", "ALTER TABLE ai_drafts ADD COLUMN headline_suggestions TEXT"),
        ("summary", "ALTER TABLE ai_drafts ADD COLUMN summary TEXT"),
    ]
    
    for column_name, sql in draft_migrations:
        if column_name not in draft_columns:
            try:
                logger.info(f"Adding column to ai_drafts: {column_name}")
                cursor.execute(sql)
                conn.commit()
                logger.info(f"✅ Added: {column_name}")
            except Exception as e:
                logger.error(f"Error: {e}")
    
    # Check if ads_settings table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ads_settings'")
    if not cursor.fetchone():
        logger.info("Creating ads_settings table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ads_settings (
                id INTEGER PRIMARY KEY,
                workspace_id INTEGER NOT NULL,
                header_code TEXT,
                footer_code TEXT,
                content_code TEXT,
                enabled BOOLEAN DEFAULT 1,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
            )
        ''')
        conn.commit()
        logger.info("✅ Created ads_settings table")
    
    # Check if news_groups table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news_groups'")
    if not cursor.fetchone():
        logger.info("Creating news_groups table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_groups (
                id INTEGER PRIMARY KEY,
                workspace_id INTEGER NOT NULL,
                group_hash TEXT,
                source_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
            )
        ''')
        conn.commit()
        logger.info("✅ Created news_groups table")
    
    # Check if grouped_news table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='grouped_news'")
    if not cursor.fetchone():
        logger.info("Creating grouped_news table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grouped_news (
                id INTEGER PRIMARY KEY,
                group_id INTEGER NOT NULL,
                news_id INTEGER NOT NULL,
                similarity_score REAL,
                FOREIGN KEY (group_id) REFERENCES news_groups(id),
                FOREIGN KEY (news_id) REFERENCES news_queue(id)
            )
        ''')
        conn.commit()
        logger.info("✅ Created grouped_news table")
    
    # Check if scraped_facts table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scraped_facts'")
    if not cursor.fetchone():
        logger.info("Creating scraped_facts table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_facts (
                id INTEGER PRIMARY KEY,
                news_id INTEGER NOT NULL,
                fact_type TEXT,
                content TEXT,
                confidence REAL DEFAULT 0.5,
                source_url TEXT,
                FOREIGN KEY (news_id) REFERENCES news_queue(id)
            )
        ''')
        conn.commit()
        logger.info("✅ Created scraped_facts table")
    
    conn.close()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ DATABASE MIGRATION COMPLETE!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Your database is now up to date with all required columns.")
    logger.info("You can now run: python main.py")
    logger.info("")

if __name__ == '__main__':
    migrate_database()
