#!/usr/bin/env python3
"""
Database Schema Migration - Fix research_cache table
Run once to add missing columns
"""

import sqlite3
import sys
from pathlib import Path

print("="*60)
print("🔧 DATABASE SCHEMA FIX")
print("="*60)

db_path = 'nexuzy.db'

if not Path(db_path).exists():
    print(f"❌ Database not found: {db_path}")
    print("Creating new database...")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='research_cache'
    """)
    
    if not cursor.fetchone():
        print("\nℹ️ research_cache table doesn't exist, creating...")
        cursor.execute('''
            CREATE TABLE research_cache (
                id INTEGER PRIMARY KEY,
                topic TEXT,
                topic_hash TEXT UNIQUE,
                article_content TEXT,
                sources TEXT,
                created_date TIMESTAMP,
                word_count INTEGER,
                quality_score REAL
            )
        ''')
        print("✅ Table created successfully")
        conn.commit()
        conn.close()
        print("\n✅ Database ready!")
        sys.exit(0)
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(research_cache)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    print(f"\n🔍 Existing columns: {', '.join(existing_columns)}")
    
    # Required columns
    required_columns = {
        'topic_hash': 'TEXT UNIQUE',
        'quality_score': 'REAL',
        'word_count': 'INTEGER'
    }
    
    # Add missing columns
    added = False
    for col_name, col_type in required_columns.items():
        if col_name not in existing_columns:
            print(f"\n⚡ Adding column: {col_name} ({col_type})")
            try:
                cursor.execute(f"ALTER TABLE research_cache ADD COLUMN {col_name} {col_type}")
                print(f"  ✅ Added {col_name}")
                added = True
            except sqlite3.OperationalError as e:
                print(f"  ⚠️ Could not add {col_name}: {e}")
    
    if added:
        conn.commit()
        print("\n✅ Database schema updated successfully!")
    else:
        print("\n✅ Database schema is up to date!")
    
    # Verify
    cursor.execute("PRAGMA table_info(research_cache)")
    final_columns = [row[1] for row in cursor.fetchall()]
    print(f"\n📊 Final columns: {', '.join(final_columns)}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ DATABASE FIX COMPLETE")
    print("="*60)
    print("\nYou can now use Research Writer without errors!")
    print("Restart your application to apply changes.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
