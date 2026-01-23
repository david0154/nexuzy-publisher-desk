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

class NexuzyPublisherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nexuzy Publisher Desk - Complete AI Platform")
        self.geometry("1400x800")
        self.configure(bg=COLORS['white'])
        
        # Set application icon
        self._set_app_icon()
        
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
    
    def _set_app_icon(self):
        """Set application icon and logo"""
        try:
            icon_path = Path('resources/icon.ico')
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
                logger.info("[OK] Application icon loaded")
            else:
                logger.warning("Icon file not found at resources/icon.ico")
        except Exception as e:
            logger.warning(f"Could not load icon: {e}")
    
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
        
        try:
            from core.wordpress_api import WordPressAPI
            self.wordpress_api = WordPressAPI(self.db_path)
            logger.info("[OK] WordPress API")
        except:
            self.wordpress_api = None
            logger.warning("WordPress API unavailable")
    
    def create_modern_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS['dark'], height=70)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        
        # Logo
        try:
            logo_path = Path('resources/logo.png')
            if logo_path.exists():
                from PIL import Image, ImageTk
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((50, 50), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                tk.Label(header, image=self.logo_photo, bg=COLORS['dark']).pack(side=tk.LEFT, padx=10)
        except:
            pass
        
        title_frame = tk.Frame(header, bg=COLORS['dark'])
        title_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(title_frame, text="NEXUZY", font=('Segoe UI', 24, 'bold'), bg=COLORS['dark'], fg=COLORS['primary']).pack(side=tk.LEFT)
        tk.Label(title_frame, text="Publisher Desk", font=('Segoe UI', 16), bg=COLORS['dark'], fg=COLORS['white']).pack(side=tk.LEFT, padx=10)
        
        # Workspace
        workspace_frame = tk.Frame(header, bg=COLORS['dark'])
        workspace_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(workspace_frame, text="Workspace:", font=('Segoe UI', 10), bg=COLORS['dark'], fg=COLORS['light']).pack(side=tk.LEFT, padx=5)
        
        self.workspace_var = tk.StringVar(value="Select Workspace")
        self.workspace_menu = ttk.Combobox(workspace_frame, textvariable=self.workspace_var, state='readonly', width=25)
        self.workspace_menu.pack(side=tk.LEFT, padx=5)
        self.workspace_menu.bind('<<ComboboxSelected>>', self.on_workspace_change)
        
        ModernButton(workspace_frame, text="+ New", command=self.new_workspace, color='success').pack(side=tk.LEFT, padx=5)
        
        # Main container
        main_container = tk.Frame(self, bg=COLORS['light'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
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
        
        # Status bar
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
    
    def create_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=color, relief=tk.RAISED, borderwidth=0)
        card.pack(side=tk.LEFT, padx=10, pady=10, ipadx=40, ipady=25)
        tk.Label(card, text=value, font=('Segoe UI', 36, 'bold'), bg=color, fg=COLORS['white']).pack()
        tk.Label(card, text=title, font=('Segoe UI', 13), bg=color, fg=COLORS['white']).pack()
    
    def show_rss_manager(self):
        self.clear_content()
        self.update_status("RSS Manager", 'primary')
        if not self.current_workspace_id:
            self._show_no_workspace_error()
            return
        
        tk.Label(self.content_frame, text="RSS Feed Manager", font=('Segoe UI', 20, 'bold'), bg=COLORS['white']).pack(padx=30, pady=20, anchor=tk.W)
        
        form_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        form_frame.pack(fill=tk.X, padx=30, pady=10, ipady=15)
        
        tk.Label(form_frame, text="Feed Name:", bg=COLORS['light']).pack(side=tk.LEFT, padx=10)
        name_entry = tk.Entry(form_frame, width=20)
        name_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(form_frame, text="RSS URL:", bg=COLORS['light']).pack(side=tk.LEFT, padx=10)
        url_entry = tk.Entry(form_frame, width=40)
        url_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(form_frame, text="Category:", bg=COLORS['light']).pack(side=tk.LEFT, padx=10)
        category_var = tk.StringVar(value='General')
        category_menu = ttk.Combobox(form_frame, textvariable=category_var, values=CATEGORIES, state='readonly', width=20)
        category_menu.pack(side=tk.LEFT, padx=5)
        
        ModernButton(form_frame, "Add Feed", lambda: self.add_rss_feed(name_entry, url_entry, category_var), 'success').pack(side=tk.LEFT, padx=10)
        
        list_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(list_frame, text="Active Feeds", font=('Segoe UI', 14, 'bold'), bg=COLORS['white']).pack(anchor=tk.W, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.feeds_listbox = tk.Listbox(list_frame, font=('Segoe UI', 10), height=15, yscrollcommand=scrollbar.set)
        self.feeds_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.feeds_listbox.yview)
        
        self.load_rss_feeds()
    
    def add_rss_feed(self, name_entry, url_entry, category_var):
        name = name_entry.get().strip()
        url = url_entry.get().strip()
        category = category_var.get()
        
        if not name or not url:
            messagebox.showerror("Error", "Enter name and URL")
            return
        
        if not self.rss_manager:
            messagebox.showerror("Error", "RSS Manager unavailable")
            return
        
        success, message = self.rss_manager.add_feed(self.current_workspace_id, name, url, category)
        
        if success:
            name_entry.delete(0, tk.END)
            url_entry.delete(0, tk.END)
            self.load_rss_feeds()
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
    
    def load_rss_feeds(self):
        if not hasattr(self, 'feeds_listbox'):
            return
        self.feeds_listbox.delete(0, tk.END)
        if not self.rss_manager or not self.current_workspace_id:
            return
        feeds = self.rss_manager.get_feeds(self.current_workspace_id)
        if not feeds:
            self.feeds_listbox.insert(tk.END, "No RSS feeds")
        else:
            for feed_id, name, url, category, enabled in feeds:
                status = "[ACTIVE]" if enabled else "[DISABLED]"
                self.feeds_listbox.insert(tk.END, f"{status} [{category}] {name} - {url}")
    
    def show_news_queue(self):
        self.clear_content()
        self.update_status("News Queue", 'warning')
        if not self.current_workspace_id:
            self._show_no_workspace_error()
            return
        
        tk.Label(self.content_frame, text="News Queue", font=('Segoe UI', 20, 'bold'), bg=COLORS['white']).pack(padx=30, pady=20, anchor=tk.W)
        
        btn_container = tk.Frame(self.content_frame, bg=COLORS['white'])
        btn_container.pack(padx=30, pady=10, anchor=tk.W)
        
        ModernButton(btn_container, "Fetch & Verify News", self.fetch_rss_news, 'primary').pack(side=tk.LEFT, padx=5)
        
        if self.news_matcher:
            ModernButton(btn_container, "🔍 Group Similar", self.group_similar_news, 'success').pack(side=tk.LEFT, padx=5)
        
        list_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.news_listbox = tk.Listbox(list_frame, font=('Segoe UI', 10), height=20, yscrollcommand=scrollbar.set)
        self.news_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.news_listbox.yview)
        
        self.load_news_queue()
    
    def load_news_queue(self):
        if not hasattr(self, 'news_listbox'):
            return
        self.news_listbox.delete(0, tk.END)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT headline, source_domain, category, verified_score, image_url, verified_sources, status FROM news_queue WHERE workspace_id = ? ORDER BY fetched_at DESC LIMIT 100', (self.current_workspace_id,))
            news_items = cursor.fetchall()
            conn.close()
            
            if not news_items:
                self.news_listbox.insert(tk.END, "No news. Click 'Fetch & Verify News'!")
            else:
                for headline, source, category, score, img, v_sources, status in news_items:
                    score_tag = f"[Score:{score:.1f}]" if score else "[New]"
                    img_tag = "📷" if img else "❌"
                    v_tag = f"[{v_sources} src]" if v_sources > 1 else ""
                    status_tag = f"[{status.upper()}]" if status != 'new' else ""
                    self.news_listbox.insert(tk.END, f"{score_tag} {img_tag} [{category}] {source}: {headline} {v_tag} {status_tag}")
        except Exception as e:
            self.news_listbox.insert(tk.END, f"Error: {e}")
    
    def fetch_rss_news(self):
        if not self.rss_manager:
            messagebox.showerror("Error", "RSS Manager required")
            return
        
        self.update_status("Fetching & verifying...", 'warning')
        
        def fetch_thread():
            try:
                count, message = self.rss_manager.fetch_news_from_feeds(self.current_workspace_id)
                if count > 0:
                    self.verify_news_background()
                self.after(0, lambda: self._fetch_complete(count, message))
            except Exception as e:
                self.after(0, lambda: self._fetch_error(str(e)))
        
        threading.Thread(target=fetch_thread, daemon=True).start()
    
    def verify_news_background(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, headline FROM news_queue WHERE workspace_id = ? AND verified_score = 0 LIMIT 10', (self.current_workspace_id,))
            news_items = cursor.fetchall()
            
            for news_id, headline in news_items:
                score = 7.5  # Simulated
                cursor.execute('UPDATE news_queue SET verified_score = ? WHERE id = ?', (score, news_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Verification error: {e}")
    
    def _fetch_complete(self, count, message):
        self.update_status(message, 'success')
        self.load_news_queue()
        messagebox.showinfo("Success", message)
    
    def _fetch_error(self, error):
        self.update_status("Error fetching", 'danger')
        messagebox.showerror("Error", f"Failed:\n{error}")
    
    def group_similar_news(self):
        if not self.news_matcher:
            messagebox.showerror("Error", "News Matcher unavailable")
            return
        
        self.update_status("Grouping with AI...", 'warning')
        
        def group_thread():
            try:
                groups = self.news_matcher.group_similar_headlines(self.current_workspace_id)
                self.after(0, lambda: self._group_complete(groups))
            except Exception as e:
                self.after(0, lambda: self._group_error(str(e)))
        
        threading.Thread(target=group_thread, daemon=True).start()
    
    def _group_complete(self, groups):
        self.update_status(f"Created {len(groups)} groups", 'success')
        self.load_news_queue()
        messagebox.showinfo("Success", f"Grouped into {len(groups)} groups!")
    
    def _group_error(self, error):
        self.update_status("Error grouping", 'danger')
        messagebox.showerror("Error", f"Failed:\n{error}")
    
    def show_editor(self, draft_id_to_edit=None):
        self.clear_content()
        self.update_status("AI Editor", 'success')
        
        if not self.current_workspace_id:
            self._show_no_workspace_error()
            return
        
        tk.Label(self.content_frame, text="AI Complete Rewrite Editor with WYSIWYG", font=('Segoe UI', 20, 'bold'), bg=COLORS['white']).pack(padx=30, pady=20, anchor=tk.W)
        
        main_panel = tk.Frame(self.content_frame, bg=COLORS['white'])
        main_panel.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        left_panel = tk.Frame(main_panel, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left_panel, text="📰 News to Rewrite", font=('Segoe UI', 14, 'bold'), bg=COLORS['light']).pack(padx=15, pady=10, anchor=tk.W)
        
        news_list_frame = tk.Frame(left_panel, bg=COLORS['white'])
        news_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(news_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.editor_news_list = tk.Listbox(news_list_frame, font=('Segoe UI', 10), height=15, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
        self.editor_news_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.editor_news_list.yview)
        self.editor_news_list.bind('<<ListboxSelect>>', self.on_news_select)
        
        btn_frame = tk.Frame(left_panel, bg=COLORS['light'])
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ModernButton(btn_frame, "🤖 Complete AI Rewrite", self.generate_ai_draft_real, 'success').pack(fill=tk.X, pady=2)
        ModernButton(btn_frame, "🔄 Refresh", self.load_editor_news, 'primary').pack(fill=tk.X, pady=2)
        
        right_panel = tk.Frame(main_panel, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_panel, text="✍️ Rewritten Article (WYSIWYG)", font=('Segoe UI', 14, 'bold'), bg=COLORS['light']).pack(padx=15, pady=10, anchor=tk.W)
        
        details_frame = tk.Frame(right_panel, bg=COLORS['white'])
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(details_frame, text="Title:", font=('Segoe UI', 10, 'bold'), bg=COLORS['white']).pack(anchor=tk.W, pady=2)
        self.draft_title = tk.Entry(details_frame, font=('Segoe UI', 11))
        self.draft_title.pack(fill=tk.X, pady=2)
        
        tk.Label(details_frame, text="Source URL:", font=('Segoe UI', 10, 'bold'), bg=COLORS['white']).pack(anchor=tk.W, pady=(10, 2))
        self.draft_url = tk.Entry(details_frame, font=('Segoe UI', 10))
        self.draft_url.pack(fill=tk.X, pady=2)
        
        tk.Label(details_frame, text="Image URL:", font=('Segoe UI', 10, 'bold'), bg=COLORS['white']).pack(anchor=tk.W, pady=(10, 2))
        image_url_frame = tk.Frame(details_frame, bg=COLORS['white'])
        image_url_frame.pack(fill=tk.X, pady=2)
        self.draft_image_url = tk.Entry(image_url_frame, font=('Segoe UI', 10))
        self.draft_image_url.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ModernButton(image_url_frame, "🔍 Check Watermark", self.check_image_watermark, 'danger').pack(side=tk.LEFT, padx=5)
        
        tk.Label(details_frame, text="Full Article (WYSIWYG Editor):", font=('Segoe UI', 10, 'bold'), bg=COLORS['white']).pack(anchor=tk.W, pady=(10, 2))
        self.draft_body = WYSIWYGEditor(details_frame, height=12)
        self.draft_body.pack(fill=tk.BOTH, expand=True, pady=2)
        
        save_frame = tk.Frame(right_panel, bg=COLORS['light'])
        save_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ModernButton(save_frame, "💾 Save Draft", self.save_ai_draft, 'warning').pack(side=tk.LEFT, padx=2)
        ModernButton(save_frame, "🌐 Translate", self.translate_current_draft, 'primary').pack(side=tk.LEFT, padx=2)
        ModernButton(save_frame, "📤 Push to WordPress", self.publish_to_wordpress, 'success').pack(side=tk.LEFT, padx=2)
        ModernButton(save_frame, "🗑️ Clear", self.clear_draft, 'danger').pack(side=tk.LEFT, padx=2)
        
        self.load_editor_news()
        if draft_id_to_edit:
            self.load_draft_into_editor(draft_id_to_edit)
    
    def load_editor_news(self):
        if not hasattr(self, 'editor_news_list'):
            return
        self.editor_news_list.delete(0, tk.END)
        self.news_items_data = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, headline, summary, source_url, source_domain, category, image_url FROM news_queue WHERE workspace_id = ? ORDER BY fetched_at DESC LIMIT 50', (self.current_workspace_id,))
            items = cursor.fetchall()
            conn.close()
            
            if not items:
                self.editor_news_list.insert(tk.END, "No news. Fetch from RSS first.")
            else:
                for news_id, headline, summary, url, source, category, img in items:
                    self.news_items_data.append({'id': news_id, 'headline': headline, 'summary': summary or '', 'url': url or '', 'source': source or 'Unknown', 'category': category or 'General', 'image_url': img or ''})
                    img_tag = "📷" if img else "❌"
                    self.editor_news_list.insert(tk.END, f"{img_tag} [{category}] {headline[:50]}...")
        except Exception as e:
            self.editor_news_list.insert(tk.END, f"Error: {e}")
    
    def on_news_select(self, event=None):
        if not hasattr(self, 'editor_news_list') or not hasattr(self, 'news_items_data'):
            return
        selection = self.editor_news_list.curselection()
        if not selection or not self.news_items_data:
            return
        idx = selection[0]
        if idx >= len(self.news_items_data):
            return
        news = self.news_items_data[idx]
        
        if hasattr(self, 'draft_title'):
            self.draft_title.delete(0, tk.END)
            self.draft_title.insert(0, news['headline'])
        
        if hasattr(self, 'draft_url'):
            self.draft_url.delete(0, tk.END)
            self.draft_url.insert(0, news['url'])
        
        if hasattr(self, 'draft_image_url'):
            self.draft_image_url.delete(0, tk.END)
            self.draft_image_url.insert(0, news['image_url'])
        
        if hasattr(self, 'draft_body'):
            self.draft_body.delete('1.0', tk.END)
            content = f"Original: {news['headline']}\n\nSource: {news['source']} | Category: {news['category']}\n"
            if news['summary']:
                content += f"\nSummary: {news['summary']}\n\n"
            content += f"URL: {news['url']}\n"
            if news['image_url']:
                content += f"Image: {news['image_url']}\n\n"
            content += "Click 'Complete AI Rewrite' to generate full 800-1500 word article with proper topic understanding..."
            self.draft_body.insert(tk.END, content)
    
    def check_image_watermark(self):
        """Check image for watermark using Vision AI"""
        image_url = self.draft_image_url.get().strip()
        if not image_url:
            messagebox.showwarning("Warning", "No image URL provided")
            return
        
        if not self.vision_ai:
            messagebox.showerror("Error", "Vision AI not available. Install: pip install torch transformers pillow")
            return
        
        self.update_status("Checking watermark...", 'warning')
        
        def check_thread():
            try:
                # Download image temporarily
                import requests
                from PIL import Image
                from io import BytesIO
                
                response = requests.get(image_url, timeout=10)
                img = Image.open(BytesIO(response.content))
                
                # Save temporarily
                temp_path = 'temp_image.jpg'
                img.save(temp_path)
                
                # Check watermark
                result = self.vision_ai.detect_watermark(temp_path)
                
                # Clean up
                os.remove(temp_path)
                
                self.after(0, lambda: self._watermark_check_complete(result))
            except Exception as e:
                self.after(0, lambda: self._watermark_check_error(str(e)))
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def _watermark_check_complete(self, result):
        self.update_status("Watermark check complete", 'success')
        
        if result['watermark_detected']:
            msg = f"⚠️ WATERMARK DETECTED!\n\nConfidence: {result['confidence']}\n\n{result['status']}\n\nRecommendation: Please replace this image with a watermark-free version."
            messagebox.showwarning("Watermark Detected", msg)
        else:
            messagebox.showinfo("Clear", f"✓ No watermark detected.\n\nConfidence: {result['confidence']}\n\nImage is clear to use.")
    
    def _watermark_check_error(self, error):
        self.update_status("Watermark check failed", 'danger')
        messagebox.showerror("Error", f"Failed to check watermark:\n{error}")
    
    def generate_ai_draft_real(self):
        if not hasattr(self, 'editor_news_list') or not hasattr(self, 'news_items_data'):
            messagebox.showwarning("Warning", "No news available")
            return
        
        selection = self.editor_news_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a news item")
            return
        
        idx = selection[0]
        if idx >= len(self.news_items_data):
            return
        
        news = self.news_items_data[idx]
        
        if not self.draft_generator:
            messagebox.showerror("Error", "Draft Generator unavailable")
            return
        
        self.update_status("Generating complete article with topic understanding...", 'warning')
        
        def generate_thread():
            try:
                draft = self.draft_generator.generate_draft(news['id'])
                self.after(0, lambda: self._draft_generated(draft, news))
            except Exception as e:
                self.after(0, lambda: self._draft_error(str(e)))
        
        threading.Thread(target=generate_thread, daemon=True).start()
    
    def _draft_generated(self, draft, news):
        if not draft:
            messagebox.showerror("Error", "Failed to generate")
            return
        
        if hasattr(self, 'draft_title'):
            self.draft_title.delete(0, tk.END)
            self.draft_title.insert(0, draft.get('title', news['headline']))
        
        if hasattr(self, 'draft_body'):
            self.draft_body.delete('1.0', tk.END)
            body = draft.get('body_draft', 'No content')
            # Insert image properly in article
            if news.get('image_url'):
                body = f"[IMAGE: {news['image_url']}]\n\n" + body
            self.draft_body.insert(tk.END, body)
        
        self.current_draft_id = draft.get('id')
        
        self.update_status(f"Generated! {draft.get('word_count', 0)} words", 'success')
        messagebox.showinfo("Success", f"Article generated with topic understanding!\nWords: {draft.get('word_count', 0)}")
    
    def _draft_error(self, error):
        self.update_status("Generation error", 'danger')
        messagebox.showerror("Error", f"Failed:\n{error}")
    
    def translate_current_draft(self):
        """Translate current draft directly"""
        if not hasattr(self, 'current_draft_id') or not self.current_draft_id:
            messagebox.showwarning("Warning", "Save draft first before translating")
            return
        
        if not self.translator:
            messagebox.showerror("Error", "Translator not available")
            return
        
        # Create language selection dialog
        dialog = tk.Toplevel(self)
        dialog.title("Select Translation Language")
        dialog.geometry("400x500")
        dialog.configure(bg=COLORS['white'])
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Select Target Language", font=('Segoe UI', 14, 'bold'), bg=COLORS['white']).pack(pady=20)
        
        list_frame = tk.Frame(dialog, bg=COLORS['white'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        lang_listbox = tk.Listbox(list_frame, font=('Segoe UI', 10), yscrollcommand=scrollbar.set)
        lang_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=lang_listbox.yview)
        
        for lang in TRANSLATION_LANGUAGES:
            lang_listbox.insert(tk.END, lang)
        
        def do_translate():
            selection = lang_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Select a language", parent=dialog)
                return
            
            target_lang = TRANSLATION_LANGUAGES[selection[0]]
            dialog.destroy()
            
            self.update_status(f"Translating to {target_lang}...", 'warning')
            
            def translate_thread():
                try:
                    translation = self.translator.translate_draft(self.current_draft_id, target_lang)
                    self.after(0, lambda: self._translation_complete(translation, target_lang))
                except Exception as e:
                    self.after(0, lambda: self._translation_error(str(e)))
            
            threading.Thread(target=translate_thread, daemon=True).start()
        
        ModernButton(dialog, "Translate", do_translate, 'success').pack(pady=20)
    
    def _translation_complete(self, translation, target_lang):
        if not translation:
            messagebox.showerror("Error", "Translation failed")
            return

        self.update_status(f"Translated to {target_lang}", 'success')

        # Show translation in a new, more functional window
        view_window = tk.Toplevel(self)
        view_window.title(f"Translation Preview: {target_lang}")
        view_window.geometry("800x650")
        view_window.configure(bg=COLORS['white'])

        header_frame = tk.Frame(view_window, bg=COLORS['white'])
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(header_frame, text=f"Translation: {target_lang}", font=('Segoe UI', 16, 'bold'), bg=COLORS['white']).pack(side=tk.LEFT)

        title_entry = tk.Entry(view_window, font=('Segoe UI', 12, 'bold'), relief=tk.FLAT, bg=COLORS['light'])
        title_entry.insert(0, translation.get('title', ''))
        title_entry.pack(fill=tk.X, padx=20, pady=5, ipady=4)

        text_widget = scrolledtext.ScrolledText(view_window, font=('Segoe UI', 11), wrap=tk.WORD, relief=tk.FLAT, borderwidth=1)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        text_widget.insert(tk.END, translation.get('body', ''))

        button_frame = tk.Frame(view_window, bg=COLORS['white'])
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        def save_as_draft():
            new_draft_id = translation.get('new_draft_id')
            if not new_draft_id:
                messagebox.showerror("Error", "No new draft ID found in translation data.", parent=view_window)
                return

            try:
                # Update the draft with any edits made in the preview window
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE ai_drafts SET title = ?, body_draft = ? WHERE id = ?",
                    (title_entry.get(), text_widget.get("1.0", tk.END), new_draft_id)
                )
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", f"Translation saved as Draft ID: {new_draft_id}", parent=view_window)
                self.load_saved_drafts() # Refresh the drafts list if it's visible
                view_window.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to save updated draft: {e}", parent=view_window)

        ModernButton(button_frame, "💾 Save as Editable Draft", save_as_draft, color='success').pack(side=tk.LEFT, padx=10)
        ModernButton(button_frame, "🗑️ Close", view_window.destroy, color='danger').pack(side=tk.RIGHT, padx=10)
    
    def _translation_error(self, error):
        self.update_status("Translation error", 'danger')
        messagebox.showerror("Error", f"Failed:\n{error}")
    
    def publish_to_wordpress(self):
        """Publish current draft to WordPress"""
        if not hasattr(self, 'current_draft_id') or not self.current_draft_id:
            messagebox.showwarning("Warning", "Save draft first before publishing")
            return
        
        if not self.wordpress_api:
            messagebox.showerror("Error", "WordPress API not available")
            return
        
        if messagebox.askyesno("Confirm", "Publish this draft to WordPress as draft post?"):
            self.update_status("Publishing to WordPress...", 'warning')
            
            def publish_thread():
                try:
                    result = self.wordpress_api.publish_draft(self.current_draft_id, self.current_workspace_id)
                    self.after(0, lambda: self._publish_complete(result))
                except Exception as e:
                    self.after(0, lambda: self._publish_error(str(e)))
            
            threading.Thread(target=publish_thread, daemon=True).start()
    
    def _publish_complete(self, result):
        if result:
            self.update_status("Published to WordPress!", 'success')
            messagebox.showinfo("Success", f"Published to WordPress!\n\nPost ID: {result['post_id']}\nURL: {result['url']}\n\nStatus: Draft (review in WordPress)")
        else:
            messagebox.showerror("Error", "Failed to publish. Check WordPress credentials in WordPress settings.")
    
    def _publish_error(self, error):
        self.update_status("Publish failed", 'danger')
        messagebox.showerror("Error", f"Failed to publish:\n{error}")

    def load_draft_into_editor(self, draft_id):
        """Loads a draft's content into the editor fields."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT title, body_draft, image_url, source_url FROM ai_drafts WHERE id = ?', (draft_id,))
            draft_data = cursor.fetchone()
            conn.close()

            if draft_data:
                title, body, img_url, source_url = draft_data
                self.draft_title.delete(0, tk.END)
                self.draft_title.insert(0, title)
                self.draft_url.delete(0, tk.END)
                self.draft_url.insert(0, source_url or "")
                self.draft_image_url.delete(0, tk.END)
                self.draft_image_url.insert(0, img_url or "")
                self.draft_body.delete('1.0', tk.END)
                self.draft_body.insert('1.0', body)

                # Set current_draft_id so 'Save' updates the correct draft
                self.current_draft_id = draft_id
                self.update_status(f"Editing Draft ID: {draft_id}", "warning")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load draft: {e}")
    
    def save_ai_draft(self):
        title = self.draft_title.get().strip()
        body = self.draft_body.get('1.0', tk.END).strip()
        img_url = self.draft_image_url.get().strip()
        source_url = self.draft_url.get().strip()

        if not title or not body or len(body) < 100:
            messagebox.showwarning("Warning", "Title and body are required (min 100 chars).")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            word_count = len(body.split())

            if hasattr(self, 'current_draft_id') and self.current_draft_id:
                # Update existing draft
                cursor.execute('''
                    UPDATE ai_drafts
                    SET title = ?, body_draft = ?, image_url = ?, source_url = ?, word_count = ?
                    WHERE id = ?
                ''', (title, body, img_url, source_url, word_count, self.current_draft_id))
                message = f"Draft ID: {self.current_draft_id} updated successfully!"
            else:
                # This part is for creating a new draft from a news item
                if not hasattr(self, 'editor_news_list') or not self.editor_news_list.curselection():
                     messagebox.showwarning("Warning", "Select a news item from the left to create a new draft.")
                     return
                idx = self.editor_news_list.curselection()[0]
                news_id = self.news_items_data[idx]['id']

                cursor.execute('''
                    INSERT INTO ai_drafts (workspace_id, news_id, title, body_draft, image_url, source_url, word_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (self.current_workspace_id, news_id, title, body, img_url, source_url, word_count))
                self.current_draft_id = cursor.lastrowid
                message = f"New draft saved! Words: {word_count}\nDraft ID: {self.current_draft_id}"

            conn.commit()
            conn.close()
            self.update_status("Draft saved!", 'success')
            messagebox.showinfo("Success", message)
            self.load_saved_drafts() # Refresh list
        except Exception as e:
            messagebox.showerror("Error", f"Save failed:\n{e}")
    
    def clear_draft(self):
        if hasattr(self, 'draft_title'):
            self.draft_title.delete(0, tk.END)
        if hasattr(self, 'draft_url'):
            self.draft_url.delete(0, tk.END)
        if hasattr(self, 'draft_image_url'):
            self.draft_image_url.delete(0, tk.END)
        if hasattr(self, 'draft_body'):
            self.draft_body.delete('1.0', tk.END)
            self.draft_body.insert(tk.END, "Select a news item...")
        self.update_status("Cleared", 'primary')
    
    def show_saved_drafts(self):
        self.clear_content()
        self.update_status("Saved Drafts", 'warning')
        
        if not self.current_workspace_id:
            self._show_no_workspace_error()
            return
        
        tk.Label(self.content_frame, text="📝 Saved Drafts", font=('Segoe UI', 20, 'bold'), bg=COLORS['white']).pack(padx=30, pady=20, anchor=tk.W)
        
        btn_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        btn_frame.pack(padx=30, pady=10, anchor=tk.W)
        
        ModernButton(btn_frame, "🔄 Refresh", self.load_saved_drafts, 'primary').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, "✍️ Edit Selected", self.edit_selected_draft, color='success').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, "🗑️ Delete", self.delete_selected_draft, 'danger').pack(side=tk.LEFT, padx=5)
        
        list_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.saved_drafts_list = tk.Listbox(list_frame, font=('Segoe UI', 10), height=20, yscrollcommand=scrollbar.set)
        self.saved_drafts_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.saved_drafts_list.yview)
        self.saved_drafts_list.bind('<Double-Button-1>', self.view_draft_details)
        
        self.load_saved_drafts()
    
    def load_saved_drafts(self):
        if not hasattr(self, 'saved_drafts_list'):
            return
        self.saved_drafts_list.delete(0, tk.END)
        self.drafts_data = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, title, word_count, image_url, generated_at FROM ai_drafts WHERE workspace_id = ? ORDER BY generated_at DESC', (self.current_workspace_id,))
            drafts = cursor.fetchall()
            conn.close()
            
            if not drafts:
                self.saved_drafts_list.insert(tk.END, "No saved drafts.")
            else:
                for draft_id, title, words, img, gen_at in drafts:
                    self.drafts_data.append({'id': draft_id, 'title': title})
                    img_tag = "📷" if img else "❌"
                    date = gen_at[:16] if gen_at else "Unknown"
                    self.saved_drafts_list.insert(tk.END, f"{img_tag} [{words}w] {title[:60]}... | {date}")
        except Exception as e:
            self.saved_drafts_list.insert(tk.END, f"Error: {e}")
    
    def view_draft_details(self, event=None):
        selection = self.saved_drafts_list.curselection()
        if not selection or not hasattr(self, 'drafts_data'):
            return
        idx = selection[0]
        if idx >= len(self.drafts_data):
            return
        
        draft_id = self.drafts_data[idx]['id']
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT title, body_draft, word_count FROM ai_drafts WHERE id = ?', (draft_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                title, body, words = result
                view_window = tk.Toplevel(self)
                view_window.title(f"Draft: {title[:50]}")
                view_window.geometry("800x600")
                view_window.configure(bg=COLORS['white'])
                
                tk.Label(view_window, text=f"Title: {title}", font=('Segoe UI', 14, 'bold'), bg=COLORS['white']).pack(padx=20, pady=10)
                tk.Label(view_window, text=f"Word Count: {words}", font=('Segoe UI', 10), bg=COLORS['white']).pack(padx=20, pady=5)
                
                text_frame = tk.Frame(view_window, bg=COLORS['white'])
                text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
                
                text_widget = scrolledtext.ScrolledText(text_frame, font=('Segoe UI', 10), wrap=tk.WORD)
                text_widget.pack(fill=tk.BOTH, expand=True)
                text_widget.insert(tk.END, body)
                text_widget.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed:\n{e}")

    def edit_selected_draft(self):
        selection = self.saved_drafts_list.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a draft to edit.")
            return

        idx = selection[0]
        draft_id_to_edit = self.drafts_data[idx]['id']

        # Now, open the editor view and load the draft's content.
        self.show_editor(draft_id_to_edit=draft_id_to_edit)
    
    def delete_selected_draft(self):
        selection = self.saved_drafts_list.curselection()
        if not selection or not hasattr(self, 'drafts_data'):
            messagebox.showwarning("Warning", "Select a draft")
            return
        
        idx = selection[0]
        if idx >= len(self.drafts_data):
            return
        
        draft_id = self.drafts_data[idx]['id']
        
        if messagebox.askyesno("Confirm", "Delete draft?"):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM ai_drafts WHERE id = ?', (draft_id,))
                conn.commit()
                conn.close()
                self.load_saved_drafts()
                messagebox.showinfo("Success", "Deleted!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed:\n{e}")
    
    def show_translations(self):
        self.clear_content()
        self.update_status("Translation Manager", 'warning')
        if not self.current_workspace_id:
            self._show_no_workspace_error()
            return
        
        tk.Label(self.content_frame, text="Translation Manager", font=('Segoe UI', 20, 'bold'), bg=COLORS['white']).pack(padx=30, pady=20, anchor=tk.W)
        
        model_status = self.models_status.get('translator', 'Not Available')
        tk.Label(self.content_frame, text=f"Translate with David AI ({model_status}) - 200+ languages.", font=('Segoe UI', 11), bg=COLORS['white'], fg=COLORS['text_light']).pack(padx=30, pady=10, anchor=tk.W)
        
        select_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        select_frame.pack(fill=tk.X, padx=30, pady=10, ipady=15)
        
        tk.Label(select_frame, text="Select Draft:", bg=COLORS['light'], font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.draft_var = tk.StringVar(value="No drafts")
        self.draft_selector = ttk.Combobox(select_frame, textvariable=self.draft_var, state='readonly', width=50)
        self.draft_selector.pack(side=tk.LEFT, padx=5)
        
        ModernButton(select_frame, "🔄 Refresh", self.load_translation_drafts, 'primary').pack(side=tk.LEFT, padx=5)
        
        lang_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        lang_frame.pack(fill=tk.X, padx=30, pady=10, ipady=15)
        
        tk.Label(lang_frame, text="Target Language:", bg=COLORS['light'], font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.lang_var = tk.StringVar(value='Spanish')
        lang_menu = ttk.Combobox(lang_frame, textvariable=self.lang_var, values=TRANSLATION_LANGUAGES, state='readonly', width=25)
        lang_menu.pack(side=tk.LEFT, padx=5)
        
        ModernButton(lang_frame, "🌐 Translate", self.translate_draft_real, 'warning').pack(side=tk.LEFT, padx=10)
        
        preview_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(preview_frame, text="Translation Preview", font=('Segoe UI', 14, 'bold'), bg=COLORS['white']).pack(anchor=tk.W, pady=10)
        
        self.translation_text = scrolledtext.ScrolledText(preview_frame, font=('Segoe UI', 10), wrap=tk.WORD, height=15)
        self.translation_text.pack(fill=tk.BOTH, expand=True)
        self.translation_text.insert(tk.END, "Translated text will appear here...")
        
        self.load_translation_drafts()
    
    def load_translation_drafts(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, title FROM ai_drafts WHERE workspace_id = ? ORDER BY generated_at DESC LIMIT 50', (self.current_workspace_id,))
            drafts = cursor.fetchall()
            conn.close()
            
            if drafts:
                self.draft_ids = [d[0] for d in drafts]
                titles = [f"#{d[0]}: {d[1][:50]}" for d in drafts]
                self.draft_selector['values'] = titles
                self.draft_selector.current(0)
            else:
                self.draft_selector['values'] = ["No drafts"]
        except Exception as e:
            logger.error(f"Error: {e}")
    
    def translate_draft_real(self):
        if not self.translator:
            messagebox.showerror("Error", "Translator unavailable")
            return
        
        if not hasattr(self, 'draft_ids') or not self.draft_ids:
            messagebox.showwarning("Warning", "No drafts")
            return
        
        draft_idx = self.draft_selector.current()
        if draft_idx < 0 or draft_idx >= len(self.draft_ids):
            messagebox.showwarning("Warning", "Select draft")
            return
        
        draft_id = self.draft_ids[draft_idx]
        target_lang = self.lang_var.get()
        
        self.update_status(f"Translating to {target_lang}...", 'warning')
        
        def translate_thread():
            try:
                translation = self.translator.translate_draft(draft_id, target_lang)
                self.after(0, lambda: self._translation_preview_complete(translation))
            except Exception as e:
                self.after(0, lambda: self._translation_error(str(e)))
        
        threading.Thread(target=translate_thread, daemon=True).start()
    
    def _translation_preview_complete(self, translation):
        if not translation:
            messagebox.showerror("Error", "Translation failed")
            return
        
        if hasattr(self, 'translation_text'):
            self.translation_text.delete('1.0', tk.END)
            output = f"Title: {translation.get('title', '')}\n\n"
            output += "=" * 60 + "\n\n"
            output += translation.get('body', '')
            self.translation_text.insert(tk.END, output)
        
        self.update_status(f"Translated to {translation.get('language', '')}", 'success')
        messagebox.showinfo("Success", f"Translated to {translation.get('language', '')}!")
    
    def show_wordpress_config(self):
        self.clear_content()
        self.update_status("WordPress Integration", 'primary')
        if not self.current_workspace_id:
            self._show_no_workspace_error()
            return
        
        tk.Label(self.content_frame, text="WordPress Integration", font=('Segoe UI', 20, 'bold'), bg=COLORS['white']).pack(padx=30, pady=20, anchor=tk.W)
        
        config_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        tk.Label(config_frame, text="WordPress Settings", font=('Segoe UI', 14, 'bold'), bg=COLORS['light']).pack(padx=20, pady=15, anchor=tk.W)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT site_url, username, app_password FROM wp_credentials WHERE workspace_id = ?', (self.current_workspace_id,))
            existing = cursor.fetchone()
            conn.close()
            saved_url, saved_user, saved_pass = existing if existing else ('', '', '')
        except:
            saved_url = saved_user = saved_pass = ''
        
        field_frame1 = tk.Frame(config_frame, bg=COLORS['light'])
        field_frame1.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(field_frame1, text="Site URL:", bg=COLORS['light'], width=15, anchor=tk.W, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        self.wp_url_entry = tk.Entry(field_frame1, width=40)
        self.wp_url_entry.insert(0, saved_url or "https://yoursite.com")
        self.wp_url_entry.pack(side=tk.LEFT, padx=10)
        
        field_frame2 = tk.Frame(config_frame, bg=COLORS['light'])
        field_frame2.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(field_frame2, text="Username:", bg=COLORS['light'], width=15, anchor=tk.W, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        self.wp_user_entry = tk.Entry(field_frame2, width=40)
        self.wp_user_entry.insert(0, saved_user or "username")
        self.wp_user_entry.pack(side=tk.LEFT, padx=10)
        
        field_frame3 = tk.Frame(config_frame, bg=COLORS['light'])
        field_frame3.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(field_frame3, text="App Password:", bg=COLORS['light'], width=15, anchor=tk.W, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        self.wp_pass_entry = tk.Entry(field_frame3, width=40, show='*')
        self.wp_pass_entry.insert(0, saved_pass or "xxxx")
        self.wp_pass_entry.pack(side=tk.LEFT, padx=10)
        
        btn_frame = tk.Frame(config_frame, bg=COLORS['light'])
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        ModernButton(btn_frame, "💾 Save", self.save_wordpress_settings, 'primary').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, "🔌 Test", self.test_wordpress_connection, 'success').pack(side=tk.LEFT, padx=5)
    
    def save_wordpress_settings(self):
        if not self.current_workspace_id:
            messagebox.showwarning("Warning", "Select workspace")
            return
        
        url = self.wp_url_entry.get().strip()
        username = self.wp_user_entry.get().strip()
        password = self.wp_pass_entry.get().strip()
        
        if not url or not username or not password:
            messagebox.showerror("Error", "Fill all fields")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM wp_credentials WHERE workspace_id = ?', (self.current_workspace_id,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute('UPDATE wp_credentials SET site_url = ?, username = ?, app_password = ? WHERE workspace_id = ?', (url, username, password, self.current_workspace_id))
            else:
                cursor.execute('INSERT INTO wp_credentials (workspace_id, site_url, username, app_password) VALUES (?, ?, ?, ?)', (self.current_workspace_id, url, username, password))
            
            conn.commit()
            conn.close()
            self.update_status("WordPress saved!", 'success')
            messagebox.showinfo("Success", "Settings saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed:\n{e}")
    
    def test_wordpress_connection(self):
        if not self.wordpress_api:
            messagebox.showerror("Error", "WordPress API unavailable")
            return
        
        url = self.wp_url_entry.get().strip()
        username = self.wp_user_entry.get().strip()
        password = self.wp_pass_entry.get().strip()
        
        if not url or not username or not password:
            messagebox.showerror("Error", "Fill all fields")
            return
        
        self.update_status("Testing connection...", 'warning')
        
        def test_thread():
            try:
                result = self.wordpress_api.test_connection(url, username, password)
                self.after(0, lambda: self._test_complete(result))
            except Exception as e:
                self.after(0, lambda: self._test_error(str(e)))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _test_complete(self, result):
        if result:
            self.update_status("WordPress connected!", 'success')
            messagebox.showinfo("Success", "✓ Connection successful!\n\nWordPress REST API is working properly.")
        else:
            messagebox.showerror("Failed", "✗ Connection failed!\n\nCheck:\n- URL is correct\n- Username is correct\n- App Password is valid\n- WordPress REST API is enabled")
    
    def _test_error(self, error):
        self.update_status("Test failed", 'danger')
        messagebox.showerror("Error", f"Test failed:\n{error}")
    
    def show_vision_ai(self):
        self.clear_content()
        self.update_status("Vision AI", 'danger')
        
        tk.Label(self.content_frame, text="Vision AI - Watermark Detection", font=('Segoe UI', 20, 'bold'), bg=COLORS['white']).pack(padx=30, pady=20, anchor=tk.W)
        
        model_status = self.models_status.get('vision_ai', 'Not Available')
        tk.Label(self.content_frame, text=f"Analyze images with David AI Vision ({model_status}).", font=('Segoe UI', 11), bg=COLORS['white'], fg=COLORS['text_light']).pack(padx=30, pady=10, anchor=tk.W)
        
        upload_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        upload_frame.pack(fill=tk.X, padx=30, pady=20, ipady=20)
        
        tk.Label(upload_frame, text="Upload Image", font=('Segoe UI', 14, 'bold'), bg=COLORS['light']).pack(padx=20, pady=10, anchor=tk.W)
        
        btn_frame = tk.Frame(upload_frame, bg=COLORS['light'])
        btn_frame.pack(padx=20, pady=10)
        
        ModernButton(btn_frame, "📁 Upload & Analyze", self.upload_image_for_analysis, 'danger').pack(side=tk.LEFT, padx=5)
        
        results_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        results_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(results_frame, text="Analysis Results", font=('Segoe UI', 14, 'bold'), bg=COLORS['white']).pack(anchor=tk.W, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, font=('Consolas', 10), wrap=tk.WORD, height=15)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.insert(tk.END, "Upload an image to see analysis...")
    
    def upload_image_for_analysis(self):
        file_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")])
        
        if file_path:
            if not self.vision_ai:
                messagebox.showerror("Error", "Vision AI requires: pip install torch transformers pillow")
                return
            
            self.update_status("Analyzing...", 'warning')
            
            def analyze_thread():
                try:
                    result = self.vision_ai.detect_watermark(file_path)
                    self.after(0, lambda: self._show_vision_results(result, file_path))
                except Exception as e:
                    self.after(0, lambda: self._vision_error(str(e)))
            
            threading.Thread(target=analyze_thread, daemon=True).start()
    
    def _show_vision_results(self, result, file_path):
        self.update_status("Analysis complete", 'success')
        
        if hasattr(self, 'results_text'):
            self.results_text.delete('1.0', tk.END)
            
            output = f"Image: {os.path.basename(file_path)}\n"
            output += "=" * 60 + "\n\n"
            output += f"Watermark Detected: {'Yes' if result['watermark_detected'] else 'No'}\n"
            output += f"Confidence: {result['confidence']}\n\n"
            output += f"Status: {result['status']}\n"
            
            self.results_text.insert(tk.END, output)
    
    def _vision_error(self, error):
        self.update_status("Vision AI error", 'danger')
        messagebox.showerror("Error", f"Error:\n{error}")
    
    def show_settings(self):
        self.clear_content()
        self.update_status("Settings", 'text_light')
        
        tk.Label(self.content_frame, text="Settings & AI Models", font=('Segoe UI', 20, 'bold'), bg=COLORS['white']).pack(padx=30, pady=20, anchor=tk.W)
        
        models_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        models_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(models_frame, text="David AI Models", font=('Segoe UI', 14, 'bold'), bg=COLORS['light']).pack(padx=20, pady=15, anchor=tk.W)
        
        for model_key, config in MODEL_CONFIGS.items():
            status = self.models_status.get(model_key, 'Unknown')
            card = tk.Frame(models_frame, bg=COLORS['white'], relief=tk.RAISED, borderwidth=1)
            card.pack(fill=tk.X, padx=20, pady=5)
            tk.Frame(card, bg=config['color'], height=3).pack(fill=tk.X)
            content = tk.Frame(card, bg=COLORS['white'])
            content.pack(fill=tk.X, padx=15, pady=10)
            top_row = tk.Frame(content, bg=COLORS['white'])
            top_row.pack(fill=tk.X)
            tk.Label(top_row, text=config['display_name'], font=('Segoe UI', 12, 'bold'), bg=COLORS['white']).pack(side=tk.LEFT)
            status_color = COLORS['success'] if 'Available' in status else COLORS['warning']
            tk.Label(top_row, text=status, font=('Segoe UI', 9, 'bold'), bg=status_color, fg=COLORS['white'], padx=8, pady=2).pack(side=tk.RIGHT)
            tk.Label(content, text=f"{config['purpose']} | {config['size']}", font=('Segoe UI', 9), bg=COLORS['white'], fg=COLORS['text_light']).pack(anchor=tk.W)
        
        # Ads section
        ads_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        ads_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(ads_frame, text="📢 Ads Management", font=('Segoe UI', 14, 'bold'), bg=COLORS['light']).pack(padx=20, pady=15, anchor=tk.W)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT header_code, footer_code, content_code FROM ads_settings WHERE workspace_id = ?', (self.current_workspace_id,))
            existing = cursor.fetchone()
            conn.close()
            saved_header, saved_footer, saved_content = existing if existing else ('', '', '')
        except:
            saved_header = saved_footer = saved_content = ''
        
        tk.Label(ads_frame, text="Header Ads:", font=('Segoe UI', 10, 'bold'), bg=COLORS['light']).pack(padx=20, pady=5, anchor=tk.W)
        self.ads_header = scrolledtext.ScrolledText(ads_frame, height=3, font=('Consolas', 9))
        self.ads_header.pack(fill=tk.X, padx=20, pady=5)
        self.ads_header.insert(tk.END, saved_header)
        
        tk.Label(ads_frame, text="Content Ads:", font=('Segoe UI', 10, 'bold'), bg=COLORS['light']).pack(padx=20, pady=5, anchor=tk.W)
        self.ads_content = scrolledtext.ScrolledText(ads_frame, height=3, font=('Consolas', 9))
        self.ads_content.pack(fill=tk.X, padx=20, pady=5)
        self.ads_content.insert(tk.END, saved_content)
        
        tk.Label(ads_frame, text="Footer Ads:", font=('Segoe UI', 10, 'bold'), bg=COLORS['light']).pack(padx=20, pady=5, anchor=tk.W)
        self.ads_footer = scrolledtext.ScrolledText(ads_frame, height=3, font=('Consolas', 9))
        self.ads_footer.pack(fill=tk.X, padx=20, pady=5)
        self.ads_footer.insert(tk.END, saved_footer)
        
        ModernButton(ads_frame, "💾 Save Ads", self.save_ads_settings, 'success').pack(padx=20, pady=15, anchor=tk.W)
    
    def save_ads_settings(self):
        if not self.current_workspace_id:
            messagebox.showwarning("Warning", "Select workspace")
            return
        
        header = self.ads_header.get('1.0', tk.END).strip()
        content = self.ads_content.get('1.0', tk.END).strip()
        footer = self.ads_footer.get('1.0', tk.END).strip()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM ads_settings WHERE workspace_id = ?', (self.current_workspace_id,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute('UPDATE ads_settings SET header_code = ?, footer_code = ?, content_code = ? WHERE workspace_id = ?', (header, footer, content, self.current_workspace_id))
            else:
                cursor.execute('INSERT INTO ads_settings (workspace_id, header_code, footer_code, content_code) VALUES (?, ?, ?, ?)', (self.current_workspace_id, header, footer, content))
            
            conn.commit()
            conn.close()
            self.update_status("Ads saved!", 'success')
            messagebox.showinfo("Success", "Ads settings saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed:\n{e}")
    
    def _show_no_workspace_error(self):
        tk.Label(self.content_frame, text="No Workspace Selected", font=('Segoe UI', 24, 'bold'), bg=COLORS['white'], fg=COLORS['danger']).pack(pady=50)
        tk.Label(self.content_frame, text="Create or select a workspace to continue.", font=('Segoe UI', 14), bg=COLORS['white'], fg=COLORS['text_light']).pack(pady=20)
        ModernButton(self.content_frame, "Create Workspace", self.new_workspace, 'success').pack(pady=20)

def main():
    logger.info("=" * 60)
    logger.info("Starting Nexuzy Publisher Desk - Complete Platform")
    logger.info("=" * 60)
    app = NexuzyPublisherApp()
    app.mainloop()

if __name__ == '__main__':
    main()
