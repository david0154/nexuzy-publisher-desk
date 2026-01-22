"""
Database Migration Script - Fix schema for new columns
"""

import sqlite3
import os

db_path = 'nexuzy.db'

print("Nexuzy Publisher Desk - Database Migration")
print("="*60)

# Check if database exists
if os.path.exists(db_path):
    print(f"Found existing database: {db_path}")
    print("\nOption 1: Delete and recreate (RECOMMENDED - clean slate)")
    print("Option 2: Try to migrate (may fail if schema is very different)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == '1':
        os.remove(db_path)
        print(f"✓ Deleted old database: {db_path}")
        print("✓ New database will be created when you run main.py")
    elif choice == '2':
        print("\nAttempting migration...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Add missing columns to rss_feeds
            cursor.execute("ALTER TABLE rss_feeds ADD COLUMN feed_name TEXT DEFAULT ''")
            print("✓ Added feed_name column to rss_feeds")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("  - feed_name column already exists")
            else:
                print(f"  ✗ Error: {e}")
        
        try:
            cursor.execute("ALTER TABLE news_queue ADD COLUMN category TEXT DEFAULT 'General'")
            print("✓ Added category column to news_queue")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("  - category column already exists")
            else:
                print(f"  ✗ Error: {e}")
        
        conn.commit()
        conn.close()
        print("\n✓ Migration completed!")
    else:
        print("Invalid choice. Exiting.")
else:
    print(f"No existing database found. A new one will be created automatically.")

print("\n" + "="*60)
print("Next step: Run 'python main.py' to start the application")
print("="*60)
