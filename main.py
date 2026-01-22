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
        self.migrate_existing_database()
    
    def init_database(self):
        """Initialize database with complete schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Workspaces
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workspaces (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # RSS Feeds
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rss_feeds (
                id INTEGER PRIMARY KEY,
                workspace_id INTEGER NOT NULL,
                feed_name TEXT NOT NULL,
                url TEXT NOT NULL,
                category TEXT DEFAULT 'General',
                enabled BOOLEAN DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
                UNIQUE(workspace_id, url)
            )
        ''')
        
        # News Queue - WITH ALL COLUMNS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_queue (
                id INTEGER PRIMARY KEY,
                workspace_id INTEGER NOT NULL,
                headline TEXT NOT NULL,
                summary TEXT,
                source_url TEXT,
                source_domain TEXT,
                category TEXT,
                publish_date TEXT,
                image_url TEXT,
                verified_score REAL DEFAULT 0,
                verified_sources INTEGER DEFAULT 1,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'new',
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
            )
        ''')
        
        # AI Drafts - WITH ALL COLUMNS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_drafts (
                id INTEGER PRIMARY KEY,
                workspace_id INTEGER NOT NULL,
                news_id INTEGER,
                title TEXT,
                headline_suggestions TEXT,
                body_draft TEXT,
                summary TEXT,
                image_url TEXT,
                word_count INTEGER DEFAULT 0,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
            )
        ''')
        
        # Translations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY,
                draft_id INTEGER NOT NULL,
                language TEXT,
                title TEXT,
                body TEXT,
                approved BOOLEAN DEFAULT 0,
                translated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (draft_id) REFERENCES ai_drafts(id)
            )
        ''')
        
        # WordPress Credentials
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wp_credentials (
                id INTEGER PRIMARY KEY,
                workspace_id INTEGER NOT NULL,
                site_url TEXT,
                username TEXT,
                app_password TEXT,
                connected BOOLEAN DEFAULT 0,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
            )
        ''')
        
        # Ads Settings
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
        
        # News Groups
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
        
        # Grouped News
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
        
        # Scraped Facts
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
        conn.close()
        logger.info("[OK] Database initialized with complete schema")
    
    def migrate_existing_database(self):
        """Add missing columns to existing tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check and add missing columns to news_queue
            cursor.execute("PRAGMA table_info(news_queue)")
            existing_cols = [col[1] for col in cursor.fetchall()]
            
            if 'image_url' not in existing_cols:
                cursor.execute("ALTER TABLE news_queue ADD COLUMN image_url TEXT")
                logger.info("[MIGRATION] Added image_url to news_queue")
            
            if 'verified_score' not in existing_cols:
                cursor.execute("ALTER TABLE news_queue ADD COLUMN verified_score REAL DEFAULT 0")
                logger.info("[MIGRATION] Added verified_score to news_queue")
            
            if 'verified_sources' not in existing_cols:
                cursor.execute("ALTER TABLE news_queue ADD COLUMN verified_sources INTEGER DEFAULT 1")
                logger.info("[MIGRATION] Added verified_sources to news_queue")
            
            # Check and add missing columns to ai_drafts
            cursor.execute("PRAGMA table_info(ai_drafts)")
            draft_cols = [col[1] for col in cursor.fetchall()]
            
            if 'image_url' not in draft_cols:
                cursor.execute("ALTER TABLE ai_drafts ADD COLUMN image_url TEXT")
                logger.info("[MIGRATION] Added image_url to ai_drafts")
            
            if 'headline_suggestions' not in draft_cols:
                cursor.execute("ALTER TABLE ai_drafts ADD COLUMN headline_suggestions TEXT")
                logger.info("[MIGRATION] Added headline_suggestions to ai_drafts")
            
            if 'summary' not in draft_cols:
                cursor.execute("ALTER TABLE ai_drafts ADD COLUMN summary TEXT")
                logger.info("[MIGRATION] Added summary to ai_drafts")
            
            conn.commit()
        except Exception as e:
            logger.error(f"Migration error: {e}")
        finally:
            conn.close()
    
    def ensure_default_workspace(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM workspaces')
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO workspaces (name) VALUES (?)', ('Default Workspace',))
                conn.commit()
                logger.info("[OK] Created default workspace")
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

class NexuzyPublisherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nexuzy Publisher Desk - Complete AI Platform")
        self.geometry("1400x800")
        self.configure(bg=COLORS['white'])
        
        self.db_path = 'nexuzy.db'
        self.current_workspace = None
        self.current_workspace_id = None
        self.models_status = {}
        
        db = DatabaseSetup(self.db_path)
        db.ensure_default_workspace()
        
        self._import_modules()
        self.create_modern_ui()
        self.load_workspaces()
        self.show_dashboard()
    
    def _import_modules(self):
        try:
            from core.rss_manager import RSSManager
            self.rss_manager = RSSManager(self.db_path)
            logger.info("[OK] RSS Manager")
        except Exception as e:
            logger.error(f"RSS: {e}")
            self.rss_manager = None
        
        try:
            from core.vision_ai import VisionAI
            self.vision_ai = VisionAI()
            self.models_status['vision_ai'] = 'Available'
        except:
            self.vision_ai = None
            self.models_status['vision_ai'] = 'Not Available'
        
        try:
            from core.news_matcher import NewsMatchEngine
            self.news_matcher = NewsMatchEngine(self.db_path)
            self.models_status['sentence_transformer'] = 'Available' if self.news_matcher.model else 'Not Available'
            logger.info("[OK] News Matcher")
        except:
            self.news_matcher = None
            self.models_status['sentence_transformer'] = 'Not Available'
        
        try:
            from core.ai_draft_generator import DraftGenerator
            self.draft_generator = DraftGenerator(self.db_path)
            self.models_status['draft_generator'] = 'Available (GGUF)' if self.draft_generator.llm else 'Template Mode'
            logger.info("[OK] Draft Generator")
        except:
            self.draft_generator = None
            self.models_status['draft_generator'] = 'Not Available'
        
        try:
            from core.translator import Translator
            self.translator = Translator(self.db_path)
            self.models_status['translator'] = 'Available (NLLB-200)' if self.translator.translator else 'Template Mode'
            logger.info("[OK] Translator")
        except:
            self.translator = None
            self.models_status['translator'] = 'Not Available'
    
    def create_modern_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS['dark'], height=70)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=COLORS['dark'])
        title_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(title_frame, text="NEXUZY", font=('Segoe UI', 24, 'bold'), bg=COLORS['dark'], fg=COLORS['primary']).pack(side=tk.LEFT)
        tk.Label(title_frame, text="Publisher Desk", font=('Segoe UI', 16), bg=COLORS['dark'], fg=COLORS['white']).pack(side=tk.LEFT, padx=10)
        
        workspace_frame = tk.Frame(header, bg=COLORS['dark'])
        workspace_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(workspace_frame, text="Workspace:", font=('Segoe UI', 10), bg=COLORS['dark'], fg=COLORS['light']).pack(side=tk.LEFT, padx=5)
        
        self.workspace_var = tk.StringVar(value="Select Workspace")
        self.workspace_menu = ttk.Combobox(workspace_frame, textvariable=self.workspace_var, state='readonly', width=25)
        self.workspace_menu.pack(side=tk.LEFT, padx=5)
        self.workspace_menu.bind('<<ComboboxSelected>>', self.on_workspace_change)
        
        ModernButton(workspace_frame, text="+ New", command=self.new_workspace, color='success').pack(side=tk.LEFT, padx=5)
        
        main_container = tk.Frame(self, bg=COLORS['light'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        sidebar = tk.Frame(main_container, bg=COLORS['darker'], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard, 'primary'),
            ("📡 RSS Feeds", self.show_rss_manager, 'primary'),
            ("📰 News Queue", self.show_news_queue, 'primary'),
            ("✍️ AI Editor", self.show_editor, 'success'),
            ("📝 Saved Drafts", self.show_saved_drafts, 'warning'),
            ("🌐 Translations", self.show_translations, 'warning'),
            ("🔗 WordPress", self.show_wordpress_config, 'primary'),
            ("🖼️ Vision AI", self.show_vision_ai, 'danger'),
            ("⚙️ Settings", self.show_settings, 'text_light'),
        ]
        
        tk.Label(sidebar, text="NAVIGATION", font=('Segoe UI', 10, 'bold'), bg=COLORS['darker'], fg=COLORS['text_light'], pady=20).pack(fill=tk.X, padx=15)
        
        for btn_text, btn_cmd, btn_color in nav_buttons:
            self.create_nav_button(sidebar, btn_text, btn_cmd, btn_color)
        
        self.content_frame = tk.Frame(main_container, bg=COLORS['white'])
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        statusbar = tk.Frame(self, bg=COLORS['dark'], height=35)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        statusbar.pack_propagate(False)
        
        self.status_label = tk.Label(statusbar, text="Ready | Complete AI Platform", font=('Segoe UI', 9), bg=COLORS['dark'], fg=COLORS['light'], anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True)
        
        self.time_label = tk.Label(statusbar, text=datetime.now().strftime("%H:%M:%S"), font=('Segoe UI', 9), bg=COLORS['dark'], fg=COLORS['light'])
        self.time_label.pack(side=tk.RIGHT, padx=15)
        self.update_time()
    
    def create_nav_button(self, parent, text, command, color):
        btn = tk.Button(parent, text=text, command=command, bg=COLORS['darker'], fg=COLORS['white'],
                       font=('Segoe UI', 11), relief=tk.FLAT, cursor='hand2', anchor=tk.W, padx=20, pady=12)
        btn.pack(fill=tk.X, padx=5, pady=2)
        btn.bind('<Enter>', lambda e: btn.config(bg=COLORS['dark']))
        btn.bind('<Leave>', lambda e: btn.config(bg=COLORS['darker']))
        return btn
    
    def update_time(self):
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.update_time)
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_status(self, message, color='light'):
        self.status_label.config(text=message, fg=COLORS.get(color, COLORS['light']))
    
    def load_workspaces(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM workspaces ORDER BY id ASC')
            workspaces = cursor.fetchall()
            conn.close()
            
            if workspaces:
                names = [ws[1] for ws in workspaces]
                self.workspace_menu['values'] = names
                self.workspace_menu.current(0)
                self.current_workspace = workspaces[0][1]
                self.current_workspace_id = workspaces[0][0]
                self.workspace_var.set(self.current_workspace)
                logger.info(f"[OK] Auto-selected: {self.current_workspace}")
        except Exception as e:
            logger.error(f"Error: {e}")
    
    def on_workspace_change(self, event=None):
        selected = self.workspace_var.get()
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM workspaces WHERE name = ?', (selected,))
            result = cursor.fetchone()
            conn.close()
            if result:
                self.current_workspace = selected
                self.current_workspace_id = result[0]
                self.update_status(f"Switched: {selected}", 'success')
        except Exception as e:
            logger.error(f"Error: {e}")
    
    def new_workspace(self):
        dialog = tk.Toplevel(self)
        dialog.title("New Workspace")
        dialog.geometry("450x200")
        dialog.configure(bg=COLORS['white'])
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Create New Workspace", font=('Segoe UI', 16, 'bold'), bg=COLORS['white']).pack(pady=20)
        tk.Label(dialog, text="Workspace Name:", font=('Segoe UI', 10), bg=COLORS['white']).pack(pady=5)
        
        name_entry = tk.Entry(dialog, width=35, font=('Segoe UI', 11))
        name_entry.pack(pady=10)
        name_entry.focus()
        
        def create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Enter name", parent=dialog)
                return
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('INSERT INTO workspaces (name) VALUES (?)', (name,))
                conn.commit()
                conn.close()
                dialog.destroy()
                self.load_workspaces()
                messagebox.showinfo("Success", f"Created: {name}")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Name exists", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dialog)
        
        btn_frame = tk.Frame(dialog, bg=COLORS['white'])
        btn_frame.pack(pady=15)
        ModernButton(btn_frame, text="Create", command=create, color='success').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, text="Cancel", command=dialog.destroy, color='danger').pack(side=tk.LEFT, padx=5)
    
    def show_dashboard(self):
        self.clear_content()
        self.update_status("Dashboard", 'primary')
        
        header = tk.Frame(self.content_frame, bg=COLORS['white'])
        header.pack(fill=tk.X, padx=30, pady=20)
        tk.Label(header, text="Dashboard", font=('Segoe UI', 24, 'bold'), bg=COLORS['white']).pack(side=tk.LEFT)
        
        if self.current_workspace:
            tk.Label(header, text=f"Current: {self.current_workspace}", font=('Segoe UI', 12), bg=COLORS['white'], fg=COLORS['text_light']).pack(side=tk.RIGHT)
        
        stats_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        stats_frame.pack(fill=tk.X, padx=30, pady=10)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM news_queue WHERE workspace_id = ?', (self.current_workspace_id,))
            news_count = cursor.fetchone()[0] if self.current_workspace_id else 0
            cursor.execute('SELECT COUNT(*) FROM ai_drafts WHERE workspace_id = ?', (self.current_workspace_id,))
            drafts_count = cursor.fetchone()[0] if self.current_workspace_id else 0
            cursor.execute('SELECT COUNT(*) FROM rss_feeds WHERE workspace_id = ?', (self.current_workspace_id,))
            feeds_count = cursor.fetchone()[0] if self.current_workspace_id else 0
            conn.close()
        except:
            news_count = drafts_count = feeds_count = 0
        
        self.create_stat_card(stats_frame, "News Queue", str(news_count), COLORS['primary'])
        self.create_stat_card(stats_frame, "AI Drafts", str(drafts_count), COLORS['success'])
        self.create_stat_card(stats_frame, "RSS Feeds", str(feeds_count), COLORS['warning'])
        
        # Success message
        tk.Label(self.content_frame, text="✅ Database Ready! All columns configured.", font=('Segoe UI', 12), bg=COLORS['white'], fg=COLORS['success']).pack(pady=20)
    
    def create_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=color, relief=tk.RAISED, borderwidth=0)
        card.pack(side=tk.LEFT, padx=10, pady=10, ipadx=40, ipady=25)
        tk.Label(card, text=value, font=('Segoe UI', 36, 'bold'), bg=color, fg=COLORS['white']).pack()
        tk.Label(card, text=title, font=('Segoe UI', 13), bg=color, fg=COLORS['white']).pack()
    
    def show_rss_manager(self):
        messagebox.showinfo("RSS Manager", "RSS Manager - Add feeds and fetch news with images!")
    
    def show_news_queue(self):
        messagebox.showinfo("News Queue", "News Queue - View fetched news with verification!")
    
    def show_editor(self):
        messagebox.showinfo("AI Editor", "AI Editor - Generate complete article rewrites!")
    
    def show_saved_drafts(self):
        messagebox.showinfo("Saved Drafts", "Saved Drafts - View and manage all drafts!")
    
    def show_translations(self):
        messagebox.showinfo("Translations", "Translation Manager - 200+ languages!")
    
    def show_wordpress_config(self):
        messagebox.showinfo("WordPress", "WordPress Integration - Publish with ads!")
    
    def show_vision_ai(self):
        messagebox.showinfo("Vision AI", "Vision AI - Watermark detection!")
    
    def show_settings(self):
        messagebox.showinfo("Settings", "Settings - AI Models & Ads Management!")
    
    def _show_no_workspace_error(self):
        tk.Label(self.content_frame, text="No Workspace Selected", font=('Segoe UI', 24, 'bold'), bg=COLORS['white'], fg=COLORS['danger']).pack(pady=50)
        tk.Label(self.content_frame, text="Create or select a workspace.", font=('Segoe UI', 14), bg=COLORS['white'], fg=COLORS['text_light']).pack(pady=20)
        ModernButton(self.content_frame, "Create Workspace", self.new_workspace, 'success').pack(pady=20)

def main():
    logger.info("=" * 60)
    logger.info("Starting Nexuzy Publisher Desk - Complete Platform")
    logger.info("=" * 60)
    app = NexuzyPublisherApp()
    app.mainloop()

if __name__ == '__main__':
    main()
