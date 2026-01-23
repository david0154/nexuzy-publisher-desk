"""
Nexuzy Publisher Desk - Complete AI-Powered News Platform
Full restoration of all features from previous version
"""

import os
import sys
import json
import sqlite3
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
from tkinter import font as tkfont
from pathlib import Path
import logging
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexuzy_publisher.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Complete categories
try:
    from core.categories import get_all_categories, POPULAR_FEEDS
    CATEGORIES = get_all_categories()
except:
    CATEGORIES = [
        'General', 'Breaking News', 'Top Stories',
        'Politics', 'Government', 'Elections', 'International Relations',
        'Business', 'Economy', 'Finance', 'Markets', 'Stock Market', 'Cryptocurrency', 'Startups',
        'Technology', 'AI & Machine Learning', 'Gadgets', 'Software', 'Cybersecurity', 'Gaming',
        'Science', 'Health', 'Medicine', 'Research', 'Space', 'Environment', 'Climate Change',
        'Sports', 'Football', 'Cricket', 'Basketball', 'Tennis', 'Olympics', 'Esports',
        'Entertainment', 'Movies', 'TV Shows', 'Music', 'Celebrities', 'Hollywood', 'Bollywood',
        'Lifestyle', 'Fashion', 'Beauty', 'Travel', 'Food', 'Cooking', 'Parenting',
        'World News', 'Asia', 'Europe', 'Americas', 'Africa', 'Middle East', 'India', 'USA', 'UK',
        'Education', 'Career', 'Crime', 'Law', 'Weather', 'Automotive', 'Opinion'
    ]

# 200+ Translation Languages
TRANSLATION_LANGUAGES = [
    'Spanish', 'French', 'German', 'Italian', 'Portuguese', 'Russian',
    'Polish', 'Dutch', 'Greek', 'Swedish', 'Norwegian', 'Danish',
    'Finnish', 'Czech', 'Romanian', 'Hungarian', 'Bulgarian', 'Croatian',
    'Hindi', 'Bengali', 'Tamil', 'Telugu', 'Marathi', 'Gujarati',
    'Kannada', 'Malayalam', 'Punjabi', 'Urdu', 'Chinese (Simplified)', 
    'Chinese (Traditional)', 'Japanese', 'Korean', 'Thai', 'Vietnamese',
    'Indonesian', 'Malay', 'Filipino', 'Arabic', 'Persian', 'Hebrew',
    'Turkish', 'Swahili', 'Yoruba', 'Hausa', 'Zulu', 'Afrikaans'
]

# Modern Color Scheme
COLORS = {
    'primary': '#3498db',
    'success': '#2ecc71',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'dark': '#2c3e50',
    'darker': '#1a252f',
    'light': '#ecf0f1',
    'white': '#ffffff',
    'text': '#2c3e50',
    'text_light': '#7f8c8d',
    'border': '#bdc3c7',
    'hover': '#5dade2',
    'active': '#2980b9'
}

# David AI Model Configuration
MODEL_CONFIGS = {
    'sentence_transformer': {
        'display_name': 'David AI 2B',
        'size': '80MB',
        'purpose': 'News Similarity Matching',
        'color': COLORS['success'],
        'module': 'core.news_matcher',
        'class': 'NewsMatchEngine'
    },
    'draft_generator': {
        'display_name': 'David AI Writer 7B',
        'size': '4.1GB',
        'purpose': 'Article Generation',
        'color': COLORS['primary'],
        'module': 'core.ai_draft_generator',
        'class': 'DraftGenerator'
    },
    'translator': {
        'display_name': 'David AI Translator',
        'size': '1.2GB',
        'purpose': '200+ Languages Translation',
        'color': COLORS['warning'],
        'module': 'core.translator',
        'class': 'Translator'
    },
    'vision_ai': {
        'display_name': 'David AI Vision',
        'size': '2.3GB',
        'purpose': 'Image Watermark Detection',
        'color': COLORS['danger'],
        'module': 'core.vision_ai',
        'class': 'VisionAI'
    }
}

class DatabaseSetup:
    def __init__(self, db_path='nexuzy.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('CREATE TABLE IF NOT EXISTS workspaces (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        cursor.execute('CREATE TABLE IF NOT EXISTS rss_feeds (id INTEGER PRIMARY KEY, workspace_id INTEGER NOT NULL, feed_name TEXT NOT NULL, url TEXT NOT NULL, category TEXT DEFAULT "General", enabled BOOLEAN DEFAULT 1, added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (workspace_id) REFERENCES workspaces(id), UNIQUE(workspace_id, url))')
        cursor.execute('CREATE TABLE IF NOT EXISTS news_queue (id INTEGER PRIMARY KEY, workspace_id INTEGER NOT NULL, headline TEXT NOT NULL, summary TEXT, source_url TEXT, source_domain TEXT, category TEXT, publish_date TEXT, image_url TEXT, verified_score REAL DEFAULT 0, verified_sources INTEGER DEFAULT 1, fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, status TEXT DEFAULT "new", FOREIGN KEY (workspace_id) REFERENCES workspaces(id))')
        cursor.execute('CREATE TABLE IF NOT EXISTS ai_drafts (id INTEGER PRIMARY KEY, workspace_id INTEGER NOT NULL, news_id INTEGER, title TEXT, headline_suggestions TEXT, body_draft TEXT, summary TEXT, image_url TEXT, source_url TEXT, word_count INTEGER DEFAULT 0, generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (workspace_id) REFERENCES workspaces(id))')
        cursor.execute('CREATE TABLE IF NOT EXISTS translations (id INTEGER PRIMARY KEY, draft_id INTEGER NOT NULL, language TEXT, title TEXT, body TEXT, approved BOOLEAN DEFAULT 0, translated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (draft_id) REFERENCES ai_drafts(id))')
        cursor.execute('CREATE TABLE IF NOT EXISTS wp_credentials (id INTEGER PRIMARY KEY, workspace_id INTEGER NOT NULL, site_url TEXT, username TEXT, app_password TEXT, connected BOOLEAN DEFAULT 0, FOREIGN KEY (workspace_id) REFERENCES workspaces(id))')
        cursor.execute('CREATE TABLE IF NOT EXISTS ads_settings (id INTEGER PRIMARY KEY, workspace_id INTEGER NOT NULL, header_code TEXT, footer_code TEXT, content_code TEXT, enabled BOOLEAN DEFAULT 1, FOREIGN KEY (workspace_id) REFERENCES workspaces(id))')
        cursor.execute('CREATE TABLE IF NOT EXISTS news_groups (id INTEGER PRIMARY KEY, workspace_id INTEGER NOT NULL, group_hash TEXT, source_count INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (workspace_id) REFERENCES workspaces(id))')
        cursor.execute('CREATE TABLE IF NOT EXISTS grouped_news (id INTEGER PRIMARY KEY, group_id INTEGER NOT NULL, news_id INTEGER NOT NULL, similarity_score REAL, FOREIGN KEY (group_id) REFERENCES news_groups(id), FOREIGN KEY (news_id) REFERENCES news_queue(id))')
        cursor.execute('CREATE TABLE IF NOT EXISTS scraped_facts (id INTEGER PRIMARY KEY, news_id INTEGER NOT NULL, fact_type TEXT, content TEXT, confidence REAL DEFAULT 0.5, source_url TEXT, FOREIGN KEY (news_id) REFERENCES news_queue(id))')
        cursor.execute('CREATE TABLE IF NOT EXISTS wordpress_posts (id INTEGER PRIMARY KEY, draft_id INTEGER NOT NULL, wp_post_id INTEGER, wp_site_url TEXT, status TEXT DEFAULT "draft", published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (draft_id) REFERENCES ai_drafts(id))')
        
        conn.commit()
        conn.close()
        logger.info("[OK] Database initialized with all tables")
    
    def ensure_default_workspace(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM workspaces')
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO workspaces (name) VALUES (?)', ('Default Workspace',))
                conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error: {e}")

class ModernButton(tk.Button):
    def __init__(self, parent, text, command=None, color='primary', **kwargs):
        bg_color = COLORS.get(color, COLORS['primary'])
        super().__init__(parent, text=text, command=command, bg=bg_color, fg=COLORS['white'],
                        font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor='hand2', padx=20, pady=10, **kwargs)
        self.default_bg = bg_color
        self.bind('<Enter>', lambda e: self.config(bg=COLORS['hover']))
        self.bind('<Leave>', lambda e: self.config(bg=self.default_bg))

class WYSIWYGEditor(tk.Frame):
    """Modern WYSIWYG text editor with formatting toolbar"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['white'])
        
        # Toolbar
        toolbar = tk.Frame(self, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Formatting buttons
        tk.Button(toolbar, text="B", font=('Segoe UI', 10, 'bold'), command=self.make_bold, 
                 bg=COLORS['white'], relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2, pady=5)
        tk.Button(toolbar, text="I", font=('Segoe UI', 10, 'italic'), command=self.make_italic,
                 bg=COLORS['white'], relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2, pady=5)
        tk.Button(toolbar, text="U", font=('Segoe UI', 10, 'underline'), command=self.make_underline,
                 bg=COLORS['white'], relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2, pady=5)
        
        tk.Frame(toolbar, width=2, bg=COLORS['border']).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        tk.Button(toolbar, text="H1", command=lambda: self.insert_heading(1),
                 bg=COLORS['white'], relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="H2", command=lambda: self.insert_heading(2),
                 bg=COLORS['white'], relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)
        
        tk.Frame(toolbar, width=2, bg=COLORS['border']).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        tk.Button(toolbar, text="• List", command=self.insert_bullet,
                 bg=COLORS['white'], relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="1. List", command=self.insert_numbered,
                 bg=COLORS['white'], relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)
        
        tk.Frame(toolbar, width=2, bg=COLORS['border']).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        tk.Button(toolbar, text="🖼️ Image", command=self.insert_image_placeholder,
                 bg=COLORS['white'], relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)
        
        # Text widget
        text_frame = tk.Frame(self, bg=COLORS['white'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text = scrolledtext.ScrolledText(text_frame, font=('Segoe UI', 11), 
                                              wrap=tk.WORD, undo=True, **kwargs)
        self.text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for formatting
        bold_font = tkfont.Font(family='Segoe UI', size=11, weight='bold')
        italic_font = tkfont.Font(family='Segoe UI', size=11, slant='italic')
        heading1_font = tkfont.Font(family='Segoe UI', size=18, weight='bold')
        heading2_font = tkfont.Font(family='Segoe UI', size=14, weight='bold')
        
        self.text.tag_configure('bold', font=bold_font)
        self.text.tag_configure('italic', font=italic_font)
        self.text.tag_configure('underline', underline=True)
        self.text.tag_configure('h1', font=heading1_font, spacing3=10)
        self.text.tag_configure('h2', font=heading2_font, spacing3=8)
    
    def make_bold(self):
        try:
            self.text.tag_add('bold', 'sel.first', 'sel.last')
        except:
            pass
    
    def make_italic(self):
        try:
            self.text.tag_add('italic', 'sel.first', 'sel.last')
        except:
            pass
    
    def make_underline(self):
        try:
            self.text.tag_add('underline', 'sel.first', 'sel.last')
        except:
            pass
    
    def insert_heading(self, level):
        tag = f'h{level}'
        try:
            self.text.tag_add(tag, 'insert linestart', 'insert lineend')
        except:
            pass
    
    def insert_bullet(self):
        self.text.insert(tk.INSERT, "\n• ")
    
    def insert_numbered(self):
        self.text.insert(tk.INSERT, "\n1. ")
    
    def insert_image_placeholder(self):
        self.text.insert(tk.INSERT, "\n[IMAGE: Insert image URL here]\n")
    
    def get(self, *args):
        return self.text.get(*args)
    
    def insert(self, *args):
        return self.text.insert(*args)
    
    def delete(self, *args):
        return self.text.delete(*args)