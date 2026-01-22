"""
Nexuzy Publisher Desk - Main Entry Point
Complete AI-powered news publishing application with Modern UI
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

# Fix Windows encoding issues
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

# Load comprehensive categories
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

# =============================================================================
# DAVID AI MODEL CONFIGURATION
# =============================================================================

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

# ============================================================================
# DATABASE SETUP
# ============================================================================

class DatabaseSetup:
    def __init__(self, db_path='nexuzy.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workspaces (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'new',
                verified_sources INTEGER DEFAULT 1,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_drafts (
                id INTEGER PRIMARY KEY,
                workspace_id INTEGER NOT NULL,
                news_id INTEGER NOT NULL,
                title TEXT,
                headline_suggestions TEXT,
                body_draft TEXT,
                summary TEXT,
                word_count INTEGER DEFAULT 0,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
                FOREIGN KEY (news_id) REFERENCES news_queue(id)
            )
        ''')
        
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
        logger.info("[OK] Database initialized")
    
    def ensure_default_workspace(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM workspaces')
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.execute('INSERT INTO workspaces (name) VALUES (?)', ('Default Workspace',))
                conn.commit()
                logger.info("[OK] Created default workspace")
            
            conn.close()
        except Exception as e:
            logger.error(f"Error ensuring default workspace: {e}")

# ============================================================================
# MODERN UI
# ============================================================================

class ModernButton(tk.Button):
    def __init__(self, parent, text, command=None, color='primary', **kwargs):
        bg_color = COLORS.get(color, COLORS['primary'])
        super().__init__(
            parent, text=text, command=command,
            bg=bg_color, fg=COLORS['white'],
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT, cursor='hand2',
            padx=20, pady=10, **kwargs
        )
        self.default_bg = bg_color
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, e):
        self['bg'] = COLORS['hover']
    
    def _on_leave(self, e):
        self['bg'] = self.default_bg

class NexuzyPublisherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Nexuzy Publisher Desk - AI News Platform")
        self.geometry("1400x800")
        self.configure(bg=COLORS['white'])
        
        # Window icon
        try:
            icon_path = os.path.join('resources', 'icon.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"Could not load icon: {e}")
        
        self.db_path = 'nexuzy.db'
        self.current_workspace = None
        self.current_workspace_id = None
        
        # AI Models status
        self.models_status = {}
        
        db = DatabaseSetup(self.db_path)
        db.ensure_default_workspace()
        
        self._import_modules()
        self.create_modern_ui()
        self.load_workspaces()
        self.show_dashboard()
    
    def _import_modules(self):
        """Import all core modules and AI models"""
        # RSS Manager
        try:
            from core.rss_manager import RSSManager
            self.rss_manager = RSSManager(self.db_path)
            logger.info("[OK] RSS Manager loaded")
        except Exception as e:
            logger.error(f"RSS Manager error: {e}")
            self.rss_manager = None
        
        # Vision AI
        try:
            from core.vision_ai import VisionAI
            self.vision_ai = VisionAI()
            self.models_status['vision_ai'] = 'Available'
            logger.info("[OK] Vision AI loaded")
        except Exception as e:
            logger.warning(f"Vision AI not available: {e}")
            self.vision_ai = None
            self.models_status['vision_ai'] = 'Not Available'
        
        # News Matcher (SentenceTransformer)
        try:
            from core.news_matcher import NewsMatchEngine
            self.news_matcher = NewsMatchEngine(self.db_path)
            if self.news_matcher.model:
                self.models_status['sentence_transformer'] = 'Available'
                logger.info("[OK] News Matcher (SentenceTransformer) loaded")
            else:
                self.models_status['sentence_transformer'] = 'Model Not Loaded'
        except Exception as e:
            logger.warning(f"News Matcher not available: {e}")
            self.news_matcher = None
            self.models_status['sentence_transformer'] = 'Not Available'
        
        # Draft Generator (Mistral-7B-GGUF)
        try:
            from core.ai_draft_generator import DraftGenerator
            self.draft_generator = DraftGenerator(self.db_path)
            if self.draft_generator.llm:
                self.models_status['draft_generator'] = 'Available (GGUF)'
                logger.info("[OK] Draft Generator (Mistral-7B-GGUF) loaded")
            else:
                self.models_status['draft_generator'] = 'Template Mode'
                logger.info("[INFO] Draft Generator in template mode")
        except Exception as e:
            logger.warning(f"Draft Generator not available: {e}")
            self.draft_generator = None
            self.models_status['draft_generator'] = 'Not Available'
        
        # Translator (NLLB-200)
        try:
            from core.translator import Translator
            self.translator = Translator(self.db_path)
            if self.translator.translator:
                self.models_status['translator'] = 'Available (NLLB-200)'
                logger.info("[OK] Translator (NLLB-200) loaded")
            else:
                self.models_status['translator'] = 'Template Mode'
                logger.info("[INFO] Translator in template mode")
        except Exception as e:
            logger.warning(f"Translator not available: {e}")
            self.translator = None
            self.models_status['translator'] = 'Not Available'
    
    def create_modern_ui(self):
        # TOP HEADER
        header = tk.Frame(self, bg=COLORS['dark'], height=70)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        
        # Logo + title
        title_frame = tk.Frame(header, bg=COLORS['dark'])
        title_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Try to load logo
        try:
            logo_path = os.path.join('resources', 'logo.png')
            if os.path.exists(logo_path):
                from PIL import Image, ImageTk
                img = Image.open(logo_path)
                img = img.resize((40, 40), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                logo_label = tk.Label(title_frame, image=photo, bg=COLORS['dark'])
                logo_label.image = photo
                logo_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            logger.warning(f"Could not load logo: {e}")
        
        tk.Label(
            title_frame, text="NEXUZY",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['dark'], fg=COLORS['primary']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            title_frame, text="Publisher Desk",
            font=('Segoe UI', 16),
            bg=COLORS['dark'], fg=COLORS['white']
        ).pack(side=tk.LEFT, padx=10)
        
        # Workspace selector
        workspace_frame = tk.Frame(header, bg=COLORS['dark'])
        workspace_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(
            workspace_frame, text="Workspace:",
            font=('Segoe UI', 10),
            bg=COLORS['dark'], fg=COLORS['light']
        ).pack(side=tk.LEFT, padx=5)
        
        self.workspace_var = tk.StringVar(value="Select Workspace")
        self.workspace_menu = ttk.Combobox(
            workspace_frame, textvariable=self.workspace_var,
            state='readonly', width=25, font=('Segoe UI', 10)
        )
        self.workspace_menu.pack(side=tk.LEFT, padx=5)
        self.workspace_menu.bind('<<ComboboxSelected>>', self.on_workspace_change)
        
        ModernButton(
            workspace_frame, text="+ New",
            command=self.new_workspace, color='success'
        ).pack(side=tk.LEFT, padx=5)
        
        # MAIN CONTAINER
        main_container = tk.Frame(self, bg=COLORS['light'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # LEFT SIDEBAR
        sidebar = tk.Frame(main_container, bg=COLORS['darker'], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard, 'primary'),
            ("📡 RSS Feeds", self.show_rss_manager, 'primary'),
            ("📰 News Queue", self.show_news_queue, 'primary'),
            ("✍️ AI Editor", self.show_editor, 'success'),
            ("🌐 Translations", self.show_translations, 'warning'),
            ("🔗 WordPress", self.show_wordpress_config, 'primary'),
            ("🖼️ Vision AI", self.show_vision_ai, 'danger'),
            ("⚙️ Settings", self.show_settings, 'text_light'),
        ]
        
        tk.Label(
            sidebar, text="NAVIGATION",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORS['darker'], fg=COLORS['text_light'],
            pady=20
        ).pack(fill=tk.X, padx=15)
        
        for btn_text, btn_cmd, btn_color in nav_buttons:
            self.create_nav_button(sidebar, btn_text, btn_cmd, btn_color)
        
        # Content area
        self.content_frame = tk.Frame(main_container, bg=COLORS['white'])
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # BOTTOM STATUS BAR
        statusbar = tk.Frame(self, bg=COLORS['dark'], height=35)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        statusbar.pack_propagate(False)
        
        self.status_label = tk.Label(
            statusbar, text="Ready | AI-Powered News Platform",
            font=('Segoe UI', 9),
            bg=COLORS['dark'], fg=COLORS['light'],
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True)
        
        self.time_label = tk.Label(
            statusbar, text=datetime.now().strftime("%H:%M:%S"),
            font=('Segoe UI', 9),
            bg=COLORS['dark'], fg=COLORS['light']
        )
        self.time_label.pack(side=tk.RIGHT, padx=15)
        self.update_time()
    
    def create_nav_button(self, parent, text, command, color):
        btn = tk.Button(
            parent, text=text, command=command,
            bg=COLORS['darker'], fg=COLORS['white'],
            font=('Segoe UI', 11), relief=tk.FLAT,
            cursor='hand2', anchor=tk.W,
            padx=20, pady=12, state=tk.NORMAL
        )
        btn.pack(fill=tk.X, padx=5, pady=2)
        
        def on_enter(e):
            btn['bg'] = COLORS['dark']
        def on_leave(e):
            btn['bg'] = COLORS['darker']
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        return btn
    
    def update_time(self):
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.update_time)
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_status(self, message, color='light'):
        self.status_label.config(text=message, fg=COLORS.get(color, COLORS['light']))
    
    # WORKSPACE MANAGEMENT
    
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
                logger.info(f"[OK] Auto-selected workspace: {self.current_workspace}")
        except Exception as e:
            logger.error(f"Error loading workspaces: {e}")
    
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
                self.update_status(f"Switched to: {selected}", 'success')
        except Exception as e:
            logger.error(f"Error switching workspace: {e}")
    
    def new_workspace(self):
        dialog = tk.Toplevel(self)
        dialog.title("New Workspace")
        dialog.geometry("450x200")
        dialog.configure(bg=COLORS['white'])
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f'450x200+{x}+{y}')
        
        tk.Label(
            dialog, text="Create New Workspace",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(pady=20)
        
        tk.Label(
            dialog, text="Workspace Name:",
            font=('Segoe UI', 10),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(pady=5)
        
        name_entry = tk.Entry(dialog, width=35, font=('Segoe UI', 11))
        name_entry.pack(pady=10)
        name_entry.focus()
        
        def create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter workspace name", parent=dialog)
                return
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('INSERT INTO workspaces (name) VALUES (?)', (name,))
                conn.commit()
                conn.close()
                
                dialog.destroy()
                self.load_workspaces()
                self.update_status(f"Created workspace: {name}", 'success')
                messagebox.showinfo("Success", f"Workspace '{name}' created successfully!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Workspace name already exists", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}", parent=dialog)
        
        btn_frame = tk.Frame(dialog, bg=COLORS['white'])
        btn_frame.pack(pady=15)
        
        ModernButton(btn_frame, text="Create", command=create, color='success').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, text="Cancel", command=dialog.destroy, color='danger').pack(side=tk.LEFT, padx=5)
    
    # SCREEN VIEWS
    
    def show_dashboard(self):
        self.clear_content()
        self.update_status("Dashboard", 'primary')
        
        header = tk.Frame(self.content_frame, bg=COLORS['white'])
        header.pack(fill=tk.X, padx=30, pady=20)
        
        tk.Label(
            header, text="Dashboard",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(side=tk.LEFT)
        
        if self.current_workspace:
            tk.Label(
                header, text=f"Current: {self.current_workspace}",
                font=('Segoe UI', 12),
                bg=COLORS['white'], fg=COLORS['text_light']
            ).pack(side=tk.RIGHT)
        
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
        
        actions_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        tk.Label(
            actions_frame, text="Quick Actions",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(anchor=tk.W, pady=10)
        
        btn_frame = tk.Frame(actions_frame, bg=COLORS['white'])
        btn_frame.pack(fill=tk.X, pady=10)
        
        ModernButton(btn_frame, "Add RSS Feed", self.show_rss_manager, 'primary').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, "View News", self.show_news_queue, 'success').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, "AI Editor", self.show_editor, 'warning').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, "Vision AI", self.show_vision_ai, 'danger').pack(side=tk.LEFT, padx=5)
    
    def create_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=color, relief=tk.RAISED, borderwidth=0)
        card.pack(side=tk.LEFT, padx=10, pady=10, ipadx=40, ipady=25)
        
        tk.Label(
            card, text=value,
            font=('Segoe UI', 36, 'bold'),
            bg=color, fg=COLORS['white']
        ).pack()
        
        tk.Label(
            card, text=title,
            font=('Segoe UI', 13),
            bg=color, fg=COLORS['white']
        ).pack()
    
    def show_rss_manager(self):
        self.clear_content()
        self.update_status("RSS Feed Manager", 'primary')
        
        if not self.current_workspace_id:
            self._show_no_workspace_error()
            return
        
        tk.Label(
            self.content_frame, text="RSS Feed Manager",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        # Add feed form
        form_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        form_frame.pack(fill=tk.X, padx=30, pady=10, ipady=15)
        
        tk.Label(form_frame, text="Feed Name:", bg=COLORS['light'], font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=10)
        name_entry = tk.Entry(form_frame, width=20, font=('Segoe UI', 10))
        name_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(form_frame, text="RSS URL:", bg=COLORS['light'], font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=10)
        url_entry = tk.Entry(form_frame, width=40, font=('Segoe UI', 10))
        url_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(form_frame, text="Category:", bg=COLORS['light'], font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=10)
        category_var = tk.StringVar(value='General')
        category_menu = ttk.Combobox(
            form_frame, textvariable=category_var,
            values=CATEGORIES,
            state='readonly', width=20
        )
        category_menu.pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            form_frame, "Add Feed",
            lambda: self.add_rss_feed(name_entry, url_entry, category_var),
            'success'
        ).pack(side=tk.LEFT, padx=10)
        
        # Feed list
        list_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(
            list_frame, text="Active Feeds",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(anchor=tk.W, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.feeds_listbox = tk.Listbox(
            list_frame, font=('Segoe UI', 10),
            height=15, yscrollcommand=scrollbar.set
        )
        self.feeds_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.feeds_listbox.yview)
        
        self.load_rss_feeds()
    
    def add_rss_feed(self, name_entry, url_entry, category_var):
        name = name_entry.get().strip()
        url = url_entry.get().strip()
        category = category_var.get()
        
        if not name or not url:
            messagebox.showerror("Error", "Please enter feed name and URL")
            return
        
        if not self.rss_manager:
            messagebox.showerror("Error", "RSS Manager module not available")
            return
        
        success, message = self.rss_manager.add_feed(
            self.current_workspace_id, name, url, category
        )
        
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
            self.feeds_listbox.insert(tk.END, "No RSS feeds added yet.")
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
        
        tk.Label(
            self.content_frame, text="News Queue",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        btn_container = tk.Frame(self.content_frame, bg=COLORS['white'])
        btn_container.pack(padx=30, pady=10, anchor=tk.W)
        
        ModernButton(
            btn_container, "Fetch Latest News from RSS",
            self.fetch_rss_news, 'primary'
        ).pack(side=tk.LEFT, padx=5)
        
        if self.news_matcher:
            ModernButton(
                btn_container, "🔍 Group Similar News",
                self.group_similar_news, 'success'
            ).pack(side=tk.LEFT, padx=5)
        
        # News list
        list_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.news_listbox = tk.Listbox(
            list_frame, font=('Segoe UI', 10),
            height=20, yscrollcommand=scrollbar.set
        )
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
            cursor.execute('''
                SELECT headline, source_domain, category, verified_sources, status 
                FROM news_queue 
                WHERE workspace_id = ? 
                ORDER BY fetched_at DESC 
                LIMIT 100
            ''', (self.current_workspace_id,))
            news_items = cursor.fetchall()
            conn.close()
            
            if not news_items:
                self.news_listbox.insert(tk.END, "No news items yet. Click 'Fetch Latest News from RSS' above!")
            else:
                for headline, source, category, verified_sources, status in news_items:
                    verified_tag = f"[{verified_sources} sources]" if verified_sources > 1 else ""
                    status_tag = f"[{status.upper()}]" if status != 'new' else ""
                    self.news_listbox.insert(tk.END, f"{status_tag} [{category}] {source}: {headline} {verified_tag}")
        except Exception as e:
            self.news_listbox.insert(tk.END, f"Error: {e}")
    
    def fetch_rss_news(self):
        if not self.rss_manager:
            messagebox.showerror("Error", "RSS Manager module required. Install dependencies:\npip install feedparser beautifulsoup4")
            return
        
        if not self.current_workspace_id:
            messagebox.showwarning("Warning", "Please select a workspace first")
            return
        
        self.update_status("Fetching news from RSS feeds...", 'warning')
        
        def fetch_thread():
            try:
                count, message = self.rss_manager.fetch_news_from_feeds(self.current_workspace_id)
                self.after(0, lambda: self._fetch_complete(count, message))
            except Exception as e:
                self.after(0, lambda: self._fetch_error(str(e)))
        
        threading.Thread(target=fetch_thread, daemon=True).start()
    
    def _fetch_complete(self, count, message):
        self.update_status(message, 'success')
        self.load_news_queue()
        messagebox.showinfo("Success", message)
    
    def _fetch_error(self, error):
        self.update_status("Error fetching news", 'danger')
        messagebox.showerror("Error", f"Failed to fetch news:\n{error}")
    
    def group_similar_news(self):
        """Group similar news using AI News Matcher"""
        if not self.news_matcher:
            messagebox.showerror("Error", "News Matcher not available")
            return
        
        self.update_status("Grouping similar news with AI...", 'warning')
        
        def group_thread():
            try:
                groups = self.news_matcher.group_similar_headlines(self.current_workspace_id)
                self.after(0, lambda: self._group_complete(groups))
            except Exception as e:
                self.after(0, lambda: self._group_error(str(e)))
        
        threading.Thread(target=group_thread, daemon=True).start()
    
    def _group_complete(self, groups):
        self.update_status(f"Created {len(groups)} news groups", 'success')
        self.load_news_queue()
        messagebox.showinfo("Success", f"Grouped news into {len(groups)} similar event groups!")
    
    def _group_error(self, error):
        self.update_status("Error grouping news", 'danger')
        messagebox.showerror("Error", f"Failed to group news:\n{error}")
    
    def show_editor(self):
        """AI Draft Editor - Shows fetched news and generates drafts with AI models"""
        self.clear_content()
        self.update_status("AI Draft Editor", 'success')
        
        if not self.current_workspace_id:
            self._show_no_workspace_error()
            return
        
        # Header
        tk.Label(
            self.content_frame, text="AI Draft Editor",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        model_status = self.models_status.get('draft_generator', 'Not Available')
        tk.Label(
            self.content_frame,
            text=f"Generate AI-powered drafts with David AI Writer 7B ({model_status}).",
            font=('Segoe UI', 11),
            bg=COLORS['white'], fg=COLORS['text_light']
        ).pack(padx=30, pady=5, anchor=tk.W)
        
        # Split into two panels: News list (left) and Draft editor (right)
        main_panel = tk.Frame(self.content_frame, bg=COLORS['white'])
        main_panel.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # LEFT PANEL - News List
        left_panel = tk.Frame(main_panel, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(
            left_panel, text="📰 Fetched News",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['light'], fg=COLORS['text']
        ).pack(padx=15, pady=10, anchor=tk.W)
        
        # News listbox with scrollbar
        news_list_frame = tk.Frame(left_panel, bg=COLORS['white'])
        news_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(news_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.editor_news_list = tk.Listbox(
            news_list_frame, font=('Segoe UI', 10),
            height=15, yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        self.editor_news_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.editor_news_list.yview)
        self.editor_news_list.bind('<<ListboxSelect>>', self.on_news_select)
        
        # Action buttons
        btn_frame = tk.Frame(left_panel, bg=COLORS['light'])
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ModernButton(
            btn_frame, "🤖 Generate AI Draft",
            self.generate_ai_draft_real, 'success'
        ).pack(fill=tk.X, pady=2)
        
        ModernButton(
            btn_frame, "🔄 Refresh News List",
            self.load_editor_news, 'primary'
        ).pack(fill=tk.X, pady=2)
        
        # RIGHT PANEL - Draft Editor
        right_panel = tk.Frame(main_panel, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            right_panel, text="✍️ AI Draft",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['light'], fg=COLORS['text']
        ).pack(padx=15, pady=10, anchor=tk.W)
        
        # Draft details frame
        details_frame = tk.Frame(right_panel, bg=COLORS['white'])
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            details_frame, text="Title:",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORS['white']
        ).pack(anchor=tk.W, pady=2)
        
        self.draft_title = tk.Entry(details_frame, font=('Segoe UI', 11), width=50)
        self.draft_title.pack(fill=tk.X, pady=2)
        
        tk.Label(
            details_frame, text="Source URL:",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORS['white']
        ).pack(anchor=tk.W, pady=(10, 2))
        
        self.draft_url = tk.Entry(details_frame, font=('Segoe UI', 10), width=50)
        self.draft_url.pack(fill=tk.X, pady=2)
        
        tk.Label(
            details_frame, text="Image URL (optional):",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORS['white']
        ).pack(anchor=tk.W, pady=(10, 2))
        
        self.draft_image_url = tk.Entry(details_frame, font=('Segoe UI', 10), width=50)
        self.draft_image_url.pack(fill=tk.X, pady=2)
        
        # Draft body
        tk.Label(
            details_frame, text="Article Body:",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORS['white']
        ).pack(anchor=tk.W, pady=(10, 2))
        
        self.draft_body = scrolledtext.ScrolledText(
            details_frame, font=('Consolas', 10),
            wrap=tk.WORD, height=15
        )
        self.draft_body.pack(fill=tk.BOTH, expand=True, pady=2)
        self.draft_body.insert(tk.END, "Select a news item and click 'Generate AI Draft'...")
        
        # Save button
        save_frame = tk.Frame(right_panel, bg=COLORS['light'])
        save_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ModernButton(
            save_frame, "💾 Save Draft",
            self.save_ai_draft, 'warning'
        ).pack(side=tk.LEFT, padx=2)
        
        ModernButton(
            save_frame, "📋 Copy to Clipboard",
            self.copy_draft, 'primary'
        ).pack(side=tk.LEFT, padx=2)
        
        ModernButton(
            save_frame, "🗑️ Clear",
            self.clear_draft, 'danger'
        ).pack(side=tk.LEFT, padx=2)
        
        # Load news items
        self.load_editor_news()
    
    def load_editor_news(self):
        """Load fetched news into editor list"""
        if not hasattr(self, 'editor_news_list'):
            return
        
        self.editor_news_list.delete(0, tk.END)
        self.news_items_data = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, headline, summary, source_url, source_domain, category
                FROM news_queue 
                WHERE workspace_id = ? 
                ORDER BY fetched_at DESC 
                LIMIT 50
            ''', (self.current_workspace_id,))
            items = cursor.fetchall()
            conn.close()
            
            if not items:
                self.editor_news_list.insert(tk.END, "No news items found. Go to 'News Queue' to fetch news.")
            else:
                for news_id, headline, summary, url, source, category in items:
                    self.news_items_data.append({
                        'id': news_id,
                        'headline': headline,
                        'summary': summary or '',
                        'url': url or '',
                        'source': source or 'Unknown',
                        'category': category or 'General'
                    })
                    display_text = f"[{category}] {headline[:60]}..."
                    self.editor_news_list.insert(tk.END, display_text)
                
                self.update_status(f"Loaded {len(items)} news items", 'success')
        except Exception as e:
            self.editor_news_list.insert(tk.END, f"Error loading news: {e}")
            logger.error(f"Error loading news for editor: {e}")
    
    def on_news_select(self, event=None):
        """Handle news item selection"""
        if not hasattr(self, 'editor_news_list') or not hasattr(self, 'news_items_data'):
            return
        
        selection = self.editor_news_list.curselection()
        if not selection or not self.news_items_data:
            return
        
        idx = selection[0]
        if idx >= len(self.news_items_data):
            return
        
        news = self.news_items_data[idx]
        
        # Display news details
        if hasattr(self, 'draft_title'):
            self.draft_title.delete(0, tk.END)
            self.draft_title.insert(0, news['headline'])
        
        if hasattr(self, 'draft_url'):
            self.draft_url.delete(0, tk.END)
            self.draft_url.insert(0, news['url'])
        
        if hasattr(self, 'draft_body'):
            self.draft_body.delete('1.0', tk.END)
            content = f"Original Headline:\n{news['headline']}\n\n"
            content += f"Source: {news['source']}\n"
            content += f"Category: {news['category']}\n\n"
            if news['summary']:
                content += f"Summary:\n{news['summary']}\n\n"
            content += f"URL: {news['url']}\n\n"
            content += "Click 'Generate AI Draft' to create article with David AI Writer 7B..."
            self.draft_body.insert(tk.END, content)
    
    def generate_ai_draft_real(self):
        """Generate AI draft using real DraftGenerator model"""
        if not hasattr(self, 'editor_news_list') or not hasattr(self, 'news_items_data'):
            messagebox.showwarning("Warning", "No news list available")
            return
        
        selection = self.editor_news_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a news item first")
            return
        
        idx = selection[0]
        if idx >= len(self.news_items_data):
            return
        
        news = self.news_items_data[idx]
        news_id = news['id']
        
        if not self.draft_generator:
            messagebox.showerror("Error", "Draft Generator not available. Install: pip install ctransformers")
            return
        
        self.update_status("Generating AI draft with David AI Writer 7B...", 'warning')
        
        def generate_thread():
            try:
                draft = self.draft_generator.generate_draft(news_id)
                self.after(0, lambda: self._draft_generated(draft, news))
            except Exception as e:
                self.after(0, lambda: self._draft_error(str(e)))
        
        threading.Thread(target=generate_thread, daemon=True).start()
    
    def _draft_generated(self, draft, news):
        """Handle generated draft"""
        if not draft:
            messagebox.showerror("Error", "Failed to generate draft")
            return
        
        if hasattr(self, 'draft_title'):
            self.draft_title.delete(0, tk.END)
            self.draft_title.insert(0, draft.get('title', news['headline']))
        
        if hasattr(self, 'draft_body'):
            self.draft_body.delete('1.0', tk.END)
            body = draft.get('body_draft', 'No content generated')
            self.draft_body.insert(tk.END, body)
        
        self.update_status("AI draft generated successfully!", 'success')
        messagebox.showinfo("Success", f"AI draft generated! Word count: {draft.get('word_count', 0)}")
    
    def _draft_error(self, error):
        self.update_status("Draft generation error", 'danger')
        messagebox.showerror("Error", f"Failed to generate draft:\n{error}")
    
    def save_ai_draft(self):
        """Save AI draft to database"""
        if not hasattr(self, 'editor_news_list') or not hasattr(self, 'news_items_data'):
            messagebox.showwarning("Warning", "No news selected")
            return
        
        selection = self.editor_news_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a news item first")
            return
        
        idx = selection[0]
        if idx >= len(self.news_items_data):
            return
        
        news = self.news_items_data[idx]
        
        title = self.draft_title.get().strip()
        body = self.draft_body.get('1.0', tk.END).strip()
        
        if not title or not body:
            messagebox.showwarning("Warning", "Please generate a draft first")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ai_drafts (workspace_id, news_id, title, body_draft)
                VALUES (?, ?, ?, ?)
            ''', (self.current_workspace_id, news['id'], title, body))
            conn.commit()
            conn.close()
            
            self.update_status("Draft saved successfully!", 'success')
            messagebox.showinfo("Success", "AI draft saved to database!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save draft:\n{e}")
            logger.error(f"Error saving draft: {e}")
    
    def copy_draft(self):
        """Copy draft to clipboard"""
        if not hasattr(self, 'draft_body'):
            return
        
        draft_text = self.draft_body.get('1.0', tk.END).strip()
        if not draft_text:
            messagebox.showwarning("Warning", "No draft to copy")
            return
        
        self.clipboard_clear()
        self.clipboard_append(draft_text)
        self.update_status("Draft copied to clipboard!", 'success')
        messagebox.showinfo("Success", "Draft copied to clipboard!")
    
    def clear_draft(self):
        """Clear draft editor"""
        if hasattr(self, 'draft_title'):
            self.draft_title.delete(0, tk.END)
        if hasattr(self, 'draft_url'):
            self.draft_url.delete(0, tk.END)
        if hasattr(self, 'draft_image_url'):
            self.draft_image_url.delete(0, tk.END)
        if hasattr(self, 'draft_body'):
            self.draft_body.delete('1.0', tk.END)
            self.draft_body.insert(tk.END, "Select a news item and click 'Generate AI Draft'...")
        
        self.update_status("Draft editor cleared", 'primary')
    
    def show_translations(self):
        """Translation Manager with real NLLB-200 model"""
        self.clear_content()
        self.update_status("Translation Manager", 'warning')
        
        if not self.current_workspace_id:
            self._show_no_workspace_error()
            return
        
        tk.Label(
            self.content_frame, text="Translation Manager",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        model_status = self.models_status.get('translator', 'Not Available')
        tk.Label(
            self.content_frame,
            text=f"Translate articles using David AI Translator ({model_status}) - 200+ languages.",
            font=('Segoe UI', 11),
            bg=COLORS['white'], fg=COLORS['text_light']
        ).pack(padx=30, pady=10, anchor=tk.W)
        
        # Draft selection
        select_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        select_frame.pack(fill=tk.X, padx=30, pady=10, ipady=15)
        
        tk.Label(select_frame, text="Select Draft:", bg=COLORS['light'], font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.draft_var = tk.StringVar(value="No drafts")
        self.draft_selector = ttk.Combobox(
            select_frame, textvariable=self.draft_var,
            state='readonly', width=50
        )
        self.draft_selector.pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            select_frame, "🔄 Refresh Drafts",
            self.load_translation_drafts, 'primary'
        ).pack(side=tk.LEFT, padx=5)
        
        # Language selection
        lang_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        lang_frame.pack(fill=tk.X, padx=30, pady=10, ipady=15)
        
        tk.Label(lang_frame, text="Target Language:", bg=COLORS['light'], font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.lang_var = tk.StringVar(value='Spanish')
        lang_menu = ttk.Combobox(
            lang_frame, textvariable=self.lang_var,
            values=TRANSLATION_LANGUAGES,
            state='readonly', width=25
        )
        lang_menu.pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            lang_frame, "🌐 Translate Now",
            self.translate_draft_real,
            'warning'
        ).pack(side=tk.LEFT, padx=10)
        
        # Preview area
        preview_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(
            preview_frame, text="Translation Preview",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(anchor=tk.W, pady=10)
        
        self.translation_text = scrolledtext.ScrolledText(
            preview_frame, font=('Segoe UI', 10),
            wrap=tk.WORD, height=15
        )
        self.translation_text.pack(fill=tk.BOTH, expand=True)
        self.translation_text.insert(tk.END, "Translated text will appear here...")
        
        # Load drafts
        self.load_translation_drafts()
    
    def load_translation_drafts(self):
        """Load available drafts for translation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title FROM ai_drafts 
                WHERE workspace_id = ? 
                ORDER BY generated_at DESC 
                LIMIT 50
            ''', (self.current_workspace_id,))
            drafts = cursor.fetchall()
            conn.close()
            
            if drafts:
                self.draft_ids = [d[0] for d in drafts]
                titles = [f"#{d[0]}: {d[1][:50]}" for d in drafts]
                self.draft_selector['values'] = titles
                self.draft_selector.current(0)
            else:
                self.draft_selector['values'] = ["No drafts available"]
        except Exception as e:
            logger.error(f"Error loading drafts: {e}")
    
    def translate_draft_real(self):
        """Translate draft using real NLLB-200 model"""
        if not self.translator:
            messagebox.showerror("Error", "Translator not available. Install: pip install transformers")
            return
        
        if not hasattr(self, 'draft_ids') or not self.draft_ids:
            messagebox.showwarning("Warning", "No drafts available to translate")
            return
        
        draft_idx = self.draft_selector.current()
        if draft_idx < 0 or draft_idx >= len(self.draft_ids):
            messagebox.showwarning("Warning", "Please select a draft")
            return
        
        draft_id = self.draft_ids[draft_idx]
        target_lang = self.lang_var.get()
        
        self.update_status(f"Translating to {target_lang} with NLLB-200...", 'warning')
        
        def translate_thread():
            try:
                translation = self.translator.translate_draft(draft_id, target_lang)
                self.after(0, lambda: self._translation_complete(translation))
            except Exception as e:
                self.after(0, lambda: self._translation_error(str(e)))
        
        threading.Thread(target=translate_thread, daemon=True).start()
    
    def _translation_complete(self, translation):
        """Handle completed translation"""
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
        messagebox.showinfo("Success", f"Translation to {translation.get('language', '')} complete!")
    
    def _translation_error(self, error):
        self.update_status("Translation error", 'danger')
        messagebox.showerror("Error", f"Translation failed:\n{error}")
    
    def show_wordpress_config(self):
        """WordPress Integration with proper save functionality"""
        self.clear_content()
        self.update_status("WordPress Integration", 'primary')
        
        if not self.current_workspace_id:
            self._show_no_workspace_error()
            return
        
        tk.Label(
            self.content_frame, text="WordPress Integration",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        config_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        tk.Label(
            config_frame, text="WordPress Connection Settings",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['light'], fg=COLORS['text']
        ).pack(padx=20, pady=15, anchor=tk.W)
        
        # Load existing settings
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT site_url, username, app_password 
                FROM wp_credentials 
                WHERE workspace_id = ?
            ''', (self.current_workspace_id,))
            existing = cursor.fetchone()
            conn.close()
            
            if existing:
                saved_url, saved_user, saved_pass = existing
            else:
                saved_url = saved_user = saved_pass = ''
        except:
            saved_url = saved_user = saved_pass = ''
        
        # Site URL
        field_frame1 = tk.Frame(config_frame, bg=COLORS['light'])
        field_frame1.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(field_frame1, text="Site URL:", bg=COLORS['light'], width=15, anchor=tk.W,
                font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        self.wp_url_entry = tk.Entry(field_frame1, width=40, font=('Segoe UI', 10))
        self.wp_url_entry.insert(0, saved_url or "https://yoursite.com")
        self.wp_url_entry.pack(side=tk.LEFT, padx=10)
        
        # Username
        field_frame2 = tk.Frame(config_frame, bg=COLORS['light'])
        field_frame2.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(field_frame2, text="Username:", bg=COLORS['light'], width=15, anchor=tk.W,
                font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        self.wp_user_entry = tk.Entry(field_frame2, width=40, font=('Segoe UI', 10))
        self.wp_user_entry.insert(0, saved_user or "your_username")
        self.wp_user_entry.pack(side=tk.LEFT, padx=10)
        
        # App Password
        field_frame3 = tk.Frame(config_frame, bg=COLORS['light'])
        field_frame3.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(field_frame3, text="App Password:", bg=COLORS['light'], width=15, anchor=tk.W,
                font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        self.wp_pass_entry = tk.Entry(field_frame3, width=40, font=('Segoe UI', 10), show='*')
        self.wp_pass_entry.insert(0, saved_pass or "xxxx xxxx xxxx xxxx")
        self.wp_pass_entry.pack(side=tk.LEFT, padx=10)
        
        # Buttons
        btn_frame = tk.Frame(config_frame, bg=COLORS['light'])
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ModernButton(
            btn_frame, "💾 Save Settings",
            self.save_wordpress_settings, 'primary'
        ).pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            btn_frame, "🔌 Test Connection",
            self.test_wordpress_connection, 'success'
        ).pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            btn_frame, "📤 Publish Sample Article",
            self.publish_wordpress_sample, 'warning'
        ).pack(side=tk.LEFT, padx=5)
    
    def save_wordpress_settings(self):
        """Save WordPress credentials to database"""
        if not self.current_workspace_id:
            messagebox.showwarning("Warning", "Please select a workspace first")
            return
        
        url = self.wp_url_entry.get().strip()
        username = self.wp_user_entry.get().strip()
        password = self.wp_pass_entry.get().strip()
        
        if not url or not username or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if settings exist
            cursor.execute('''
                SELECT id FROM wp_credentials WHERE workspace_id = ?
            ''', (self.current_workspace_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing
                cursor.execute('''
                    UPDATE wp_credentials 
                    SET site_url = ?, username = ?, app_password = ?, connected = 0
                    WHERE workspace_id = ?
                ''', (url, username, password, self.current_workspace_id))
            else:
                # Insert new
                cursor.execute('''
                    INSERT INTO wp_credentials (workspace_id, site_url, username, app_password, connected)
                    VALUES (?, ?, ?, ?, 0)
                ''', (self.current_workspace_id, url, username, password))
            
            conn.commit()
            conn.close()
            
            self.update_status("WordPress settings saved successfully!", 'success')
            messagebox.showinfo("Success", "WordPress settings saved to database!")
            logger.info(f"WordPress settings saved for workspace {self.current_workspace_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{e}")
            logger.error(f"Error saving WordPress settings: {e}")
    
    def test_wordpress_connection(self):
        """Test WordPress connection"""
        url = self.wp_url_entry.get().strip()
        if not url or url == "https://yoursite.com":
            messagebox.showwarning("Warning", "Please enter a valid WordPress site URL")
            return
        
        self.update_status("Testing WordPress connection...", 'warning')
        messagebox.showinfo("Test Connection", f"Testing connection to:\n{url}\n\nThis feature requires WordPress REST API setup.")
    
    def publish_wordpress_sample(self):
        """Publish a sample article to WordPress"""
        messagebox.showinfo("Publish", "Publishing feature will be implemented with WordPress REST API integration.\n\nMake sure to save your settings first!")
    
    def show_vision_ai(self):
        """Vision AI for watermark detection in news images"""
        self.clear_content()
        self.update_status("Vision AI - Watermark Detection", 'danger')
        
        tk.Label(
            self.content_frame, text="Vision AI - Watermark Detection",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        model_status = self.models_status.get('vision_ai', 'Not Available')
        tk.Label(
            self.content_frame,
            text=f"Analyze news article images for watermarks using David AI Vision ({model_status}).",
            font=('Segoe UI', 11),
            bg=COLORS['white'], fg=COLORS['text_light']
        ).pack(padx=30, pady=10, anchor=tk.W)
        
        # Upload section
        upload_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        upload_frame.pack(fill=tk.X, padx=30, pady=20, ipady=20)
        
        tk.Label(
            upload_frame, text="Upload Image for Analysis",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['light'], fg=COLORS['text']
        ).pack(padx=20, pady=10, anchor=tk.W)
        
        btn_frame = tk.Frame(upload_frame, bg=COLORS['light'])
        btn_frame.pack(padx=20, pady=10)
        
        ModernButton(
            btn_frame, "📁 Upload & Analyze Image",
            self.upload_image_for_analysis,
            'danger'
        ).pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            btn_frame, "🔍 Scan for Watermarks",
            lambda: messagebox.showinfo("Vision AI", "Scanning image for watermarks..."),
            'warning'
        ).pack(side=tk.LEFT, padx=5)
        
        # Results area
        results_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        results_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(
            results_frame, text="Analysis Results",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(anchor=tk.W, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame, font=('Consolas', 10),
            wrap=tk.WORD, height=15
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.insert(tk.END, "Upload an image to see analysis results...\n\nDavid AI Vision will detect:\n- Watermarks\n- Logos\n- Text overlays\n- Copyright marks")
    
    def upload_image_for_analysis(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if file_path:
            if not self.vision_ai:
                messagebox.showerror(
                    "Error",
                    "Vision AI requires: pip install torch transformers pillow"
                )
                return
            
            self.update_status("Analyzing image with Vision AI...", 'warning')
            
            def analyze_thread():
                try:
                    result = self.vision_ai.detect_watermark(file_path)
                    self.after(0, lambda: self._show_vision_results(result, file_path))
                except Exception as e:
                    self.after(0, lambda: self._vision_error(str(e)))
            
            threading.Thread(target=analyze_thread, daemon=True).start()
    
    def _show_vision_results(self, result, file_path):
        self.update_status("Vision AI analysis complete", 'success')
        
        if hasattr(self, 'results_text'):
            self.results_text.delete('1.0', tk.END)
            
            output = f"Image: {os.path.basename(file_path)}\n"
            output += "=" * 60 + "\n\n"
            output += f"Watermark Detected: {'Yes' if result['watermark_detected'] else 'No'}\n"
            output += f"Confidence: {result['confidence']}\n\n"
            output += f"Watermark Score: {result['watermark_score']}\n"
            output += f"Clean Score: {result['clean_score']}\n\n"
            output += f"Status: {result['status']}\n\n"
            
            if result.get('detailed_scores'):
                output += "Detailed Analysis:\n"
                output += "-" * 60 + "\n"
                for key, value in result['detailed_scores'].items():
                    output += f"{key}: {value}\n"
            
            self.results_text.insert(tk.END, output)
    
    def _vision_error(self, error):
        self.update_status("Vision AI error", 'danger')
        messagebox.showerror("Error", f"Vision AI error:\n{error}")
    
    def show_settings(self):
        """Settings & AI Models Status"""
        self.clear_content()
        self.update_status("Settings & AI Models", 'text_light')
        
        tk.Label(
            self.content_frame, text="Settings & AI Models",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        models_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        models_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(
            models_frame, text="David AI Models Configuration",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORS['light'], fg=COLORS['text']
        ).pack(padx=20, pady=15, anchor=tk.W)
        
        for model_key, config in MODEL_CONFIGS.items():
            status = self.models_status.get(model_key, 'Unknown')
            self.create_model_status_card(models_frame, config, status)
    
    def create_model_status_card(self, parent, config, status):
        card = tk.Frame(parent, bg=COLORS['white'], relief=tk.RAISED, borderwidth=1)
        card.pack(fill=tk.X, padx=20, pady=10)
        
        header = tk.Frame(card, bg=config['color'], height=5)
        header.pack(fill=tk.X)
        
        content = tk.Frame(card, bg=COLORS['white'])
        content.pack(fill=tk.X, padx=15, pady=15)
        
        top_row = tk.Frame(content, bg=COLORS['white'])
        top_row.pack(fill=tk.X, pady=2)
        
        tk.Label(
            top_row, text=config['display_name'],
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(side=tk.LEFT)
        
        # Status badge
        status_color = COLORS['success'] if 'Available' in status else COLORS['warning']
        tk.Label(
            top_row, text=status,
            font=('Segoe UI', 10, 'bold'),
            bg=status_color, fg=COLORS['white'],
            padx=10, pady=2
        ).pack(side=tk.RIGHT)
        
        tk.Label(
            content, text=f"Purpose: {config['purpose']}",
            font=('Segoe UI', 10),
            bg=COLORS['white'], fg=COLORS['text_light']
        ).pack(anchor=tk.W, pady=2)
        
        tk.Label(
            content, text=f"Size: {config['size']}",
            font=('Segoe UI', 10),
            bg=COLORS['white'], fg=COLORS['text_light']
        ).pack(anchor=tk.W, pady=2)
    
    def _show_no_workspace_error(self):
        tk.Label(
            self.content_frame, text="No Workspace Selected",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['white'], fg=COLORS['danger']
        ).pack(pady=50)
        
        tk.Label(
            self.content_frame,
            text="Please create or select a workspace to continue.",
            font=('Segoe UI', 14),
            bg=COLORS['white'], fg=COLORS['text_light']
        ).pack(pady=20)
        
        ModernButton(
            self.content_frame, "Create Workspace",
            self.new_workspace, 'success'
        ).pack(pady=20)

def main():
    logger.info("=" * 60)
    logger.info("Starting Nexuzy Publisher Desk")
    logger.info("=" * 60)
    
    app = NexuzyPublisherApp()
    app.mainloop()

if __name__ == '__main__':
    main()
