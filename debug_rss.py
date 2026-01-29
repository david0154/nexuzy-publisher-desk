#!/usr/bin/env python3
"""
RSS Feed Inspector - Debug Tool
Shows exactly what fields are in an RSS feed

Usage:
    python debug_rss.py <feed_url>
    
Example:
    python debug_rss.py https://machinelearningmastery.com/feed/
"""

import sys
import feedparser
import requests
from bs4 import BeautifulSoup
import json

def inspect_rss_feed(feed_url):
    print(f"\n{'='*80}")
    print(f"🔍 INSPECTING RSS FEED: {feed_url}")
    print(f"{'='*80}\n")
    
    # Fetch feed
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(feed_url, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
    except:
        feed = feedparser.parse(feed_url)
    
    if not feed.entries:
        print("❌ No entries found in feed!")
        return
    
    print(f"✅ Found {len(feed.entries)} entries\n")
    
    # Inspect first 3 entries
    for idx, entry in enumerate(feed.entries[:3], 1):
        print(f"\n{'='*80}")
        print(f"📰 ENTRY #{idx}: {entry.get('title', 'No title')[:60]}...")
        print(f"{'='*80}\n")
        
        # Show all available keys
        print("📋 AVAILABLE FIELDS:")
        print(f"   Keys: {list(entry.keys())}\n")
        
        # Check common image fields
        print("🖼️  IMAGE FIELD ANALYSIS:\n")
        
        # 1. media_content
        if hasattr(entry, 'media_content'):
            print("   ✅ Has media_content:")
            print(f"      {entry.media_content}\n")
        else:
            print("   ❌ No media_content\n")
        
        # 2. media_thumbnail
        if hasattr(entry, 'media_thumbnail'):
            print("   ✅ Has media_thumbnail:")
            print(f"      {entry.media_thumbnail}\n")
        else:
            print("   ❌ No media_thumbnail\n")
        
        # 3. enclosures
        if hasattr(entry, 'enclosures') and entry.enclosures:
            print("   ✅ Has enclosures:")
            for enc in entry.enclosures:
                print(f"      Type: {enc.get('type', 'unknown')}")
                print(f"      URL:  {enc.get('href', 'no url')}\n")
        else:
            print("   ❌ No enclosures\n")
        
        # 4. Direct image field
        if hasattr(entry, 'image'):
            print("   ✅ Has direct 'image' field:")
            print(f"      {entry.image}\n")
        else:
            print("   ❌ No direct image field\n")
        
        # 5. Summary/description HTML
        print("   🔍 Checking summary/description for images:\n")
        summary = entry.get('summary', entry.get('description', ''))
        if summary:
            soup = BeautifulSoup(summary, 'html.parser')
            img_tags = soup.find_all('img')
            
            if img_tags:
                print(f"      ✅ Found {len(img_tags)} <img> tags in summary:")
                for i, img in enumerate(img_tags[:3], 1):
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    print(f"         {i}. {src}")
                print()
            else:
                print("      ❌ No <img> tags in summary\n")
            
            # Show first 500 chars of summary
            print("      📝 Summary preview (first 500 chars):")
            print(f"      {summary[:500]}...\n")
        else:
            print("      ❌ No summary/description\n")
        
        # 6. content field
        if hasattr(entry, 'content') and entry.content:
            print("   🔍 Checking content field for images:\n")
            for content in entry.content:
                soup = BeautifulSoup(content.get('value', ''), 'html.parser')
                img_tags = soup.find_all('img')
                
                if img_tags:
                    print(f"      ✅ Found {len(img_tags)} <img> tags in content:")
                    for i, img in enumerate(img_tags[:3], 1):
                        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                        print(f"         {i}. {src}")
                    print()
                else:
                    print("      ❌ No <img> tags in content\n")
        else:
            print("   ❌ No content field\n")
        
        # 7. content:encoded
        if hasattr(entry, 'content_encoded'):
            print("   🔍 Checking content:encoded for images:\n")
            soup = BeautifulSoup(entry.content_encoded, 'html.parser')
            img_tags = soup.find_all('img')
            
            if img_tags:
                print(f"      ✅ Found {len(img_tags)} <img> tags in content:encoded:")
                for i, img in enumerate(img_tags[:3], 1):
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    print(f"         {i}. {src}")
                print()
            else:
                print("      ❌ No <img> tags in content:encoded\n")
        else:
            print("   ❌ No content:encoded field\n")
        
        # 8. Links
        if hasattr(entry, 'links'):
            print("   🔍 Checking links:\n")
            for link in entry.links:
                if 'image' in link.get('type', '').lower() or link.get('rel') == 'image':
                    print(f"      ✅ Image link found:")
                    print(f"         Type: {link.get('type', 'unknown')}")
                    print(f"         Rel:  {link.get('rel', 'none')}")
                    print(f"         URL:  {link.get('href', 'no url')}\n")
        
        print(f"\n{'='*80}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_rss.py <feed_url>")
        print("\nExample:")
        print("  python debug_rss.py https://machinelearningmastery.com/feed/")
        sys.exit(1)
    
    feed_url = sys.argv[1]
    inspect_rss_feed(feed_url)
    
    print("\n" + "="*80)
    print("✅ INSPECTION COMPLETE!")
    print("="*80 + "\n")
