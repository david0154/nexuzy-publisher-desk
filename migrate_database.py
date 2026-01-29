"""
Database Migration Script - FIX IMAGE PATHS
Removes local image paths from existing drafts
Ensures WordPress gets clean HTML + original image URLs
"""

import sqlite3
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_local_image_paths(html_body: str) -> str:
    """
    🔧 REMOVE LOCAL IMAGE PATHS FROM HTML
    Removes: <figure><img src="downloaded_images/..." /></figure>
    Keeps: Original article text
    """
    if not html_body:
        return html_body
    
    # Remove local image tags
    patterns = [
        r'<figure>\s*<img[^>]*src="downloaded_images/[^"]*"[^>]*/>\s*</figure>\s*',
        r'<img[^>]*src="downloaded_images/[^"]*"[^>]*/?>\s*',
        r'<figure>\s*<img[^>]*src="[^"]*downloaded_images[^"]*"[^>]*/>\s*</figure>\s*',
    ]
    
    cleaned = html_body
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()

def migrate_fix_image_paths(db_path='nexuzy.db'):
    """
    🔧 FIX: Remove local image paths from all existing drafts
    WordPress will use image_url field for featured images
    """
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if ai_drafts table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_drafts'")
        if not cursor.fetchone():
            logger.info("ℹ️  ai_drafts table doesn't exist yet - nothing to migrate")
            conn.close()
            return True
        
        # Get all drafts
        cursor.execute('SELECT id, body_draft, image_url FROM ai_drafts')
        drafts = cursor.fetchall()
        
        if not drafts:
            logger.info("ℹ️  No drafts found - nothing to migrate")
            conn.close()
            return True
        
        logger.info(f"🔍 Checking {len(drafts)} drafts for local image paths...")
        
        fixed_count = 0
        for draft_id, body_draft, image_url in drafts:
            if not body_draft:
                continue
            
            # Check if has local image path
            if 'downloaded_images/' in body_draft or 'src="downloaded_images' in body_draft:
                # Clean the HTML
                cleaned_body = clean_local_image_paths(body_draft)
                
                # Update database
                cursor.execute(
                    'UPDATE ai_drafts SET body_draft = ? WHERE id = ?',
                    (cleaned_body, draft_id)
                )
                
                fixed_count += 1
                logger.info(f"✅ Fixed draft {draft_id} - removed local image path")
        
        conn.commit()
        conn.close()
        
        if fixed_count > 0:
            logger.info(f"🎉 Successfully fixed {fixed_count} drafts!")
            logger.info(f"✅ WordPress will now use image_url field for featured images")
        else:
            logger.info("✅ All drafts are already clean - no local paths found")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def migrate_add_placeholder_image(db_path='nexuzy.db'):
    """Add placeholder_image column to ads_settings (legacy migration)"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if ads_settings exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ads_settings'")
        if not cursor.fetchone():
            logger.info("ℹ️  ads_settings table doesn't exist - skipping")
            conn.close()
            return True
        
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
            logger.info("✅ Added placeholder_image column")
        else:
            logger.info("✅ placeholder_image column already exists")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    logger.info("="*70)
    logger.info("🔧 DATABASE MIGRATION: Fix Image Paths + Placeholder Support")
    logger.info("="*70)
    
    success = True
    
    # Migration 1: Fix local image paths in existing drafts
    logger.info("\n📋 Step 1: Cleaning local image paths from existing drafts...")
    if not migrate_fix_image_paths():
        success = False
    
    # Migration 2: Add placeholder image support (legacy)
    logger.info("\n📋 Step 2: Adding placeholder image support...")
    if not migrate_add_placeholder_image():
        success = False
    
    logger.info("\n" + "="*70)
    if success:
        logger.info("✅ ALL MIGRATIONS COMPLETED SUCCESSFULLY!")
        logger.info("")
        logger.info("What was fixed:")
        logger.info("  ✅ Removed local image paths from draft HTML")
        logger.info("  ✅ WordPress will use image_url field for images")
        logger.info("  ✅ All drafts now have clean HTML")
        logger.info("  ✅ Placeholder image support added")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Generate new drafts (will use original URLs)")
        logger.info("  2. Publish to WordPress (images will work!)")
        logger.info("  3. Old drafts are now fixed and ready")
    else:
        logger.error("❌ SOME MIGRATIONS FAILED!")
        logger.error("Check the errors above and try again.")
    
    logger.info("="*70)
