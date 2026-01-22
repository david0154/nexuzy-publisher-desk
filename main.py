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
from tkinter import messagebox, scrolledtext, ttk
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

# Modern Color Scheme
COLORS = {
    'primary': '#3498db',      # Blue
    'success': '#2ecc71',      # Green
    'warning': '#f39c12',      # Orange
    'danger': '#e74c3c',       # Red
    'dark': '#2c3e50',         # Dark Blue
    'darker': '#1a252f',       # Darker
    'light': '#ecf0f1',        # Light Gray
    'white': '#ffffff',
    'text': '#2c3e50',
    'text_light': '#7f8c8d',
    'border': '#bdc3c7',
    'hover': '#5dade2',
    'active': '#2980b9'
}

# =============================================================================
# ENHANCED MODEL CONFIGURATION
# =============================================================================

MODEL_CONFIGS = {
    'sentence_transformer': {
        'name': 'all-MiniLM-L6-v2',
        'full_name': 'sentence-transformers/all-MiniLM-L6-v2',
        'size': '80MB',
        'purpose': 'News Similarity Matching',
        'type': 'embedding',
        'color': COLORS['success']
    },
    'draft_generator': {
        'name': 'Mistral-7B-Instruct-Q4',
        'full_name': 'TheBloke/Mistral-7B-Instruct-v0.2-GGUF',
        'size': '4.1GB',
        'purpose': 'AI Draft Generation',
        'type': 'llm_gguf',
        'color': COLORS['primary']
    },
    'translator': {
        'name': 'NLLB-200-Distilled',
        'full_name': 'facebook/nllb-200-distilled-600M',
        'size': '1.2GB',
        'purpose': 'Multi-Language Translation',
        'type': 'seq2seq',
        'color': COLORS['warning']
    }
}

# ============================================================================
# DATABASE SETUP
# ============================================================================

class DatabaseSetup:
    """Initialize SQLite database with schema"""
    
    def __init__(self, db_path='nexuzy.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Workspaces table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workspaces (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # RSS Feeds table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rss_feeds (
                id INTEGER PRIMARY KEY,
                workspace_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                category TEXT,
                language TEXT,
                priority INTEGER DEFAULT 5,
                enabled BOOLEAN DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
                UNIQUE(workspace_id, url)
            )
        ''')
        
        # News Queue table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_queue (
                id INTEGER PRIMARY KEY,
                workspace_id INTEGER NOT NULL,
                headline TEXT NOT NULL,
                summary TEXT,
                source_url TEXT,
                source_domain TEXT,
                publish_date TIMESTAMP,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'new',
                confidence INTEGER,
                verified_sources INTEGER DEFAULT 1,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
            )
        ''')
        
        # News Grouping
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_groups (
                id INTEGER PRIMARY KEY,
                workspace_id INTEGER NOT NULL,
                group_hash TEXT,
                verified BOOLEAN DEFAULT 0,
                source_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
            )
        ''')
        
        # News Items in Groups
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grouped_news (
                id INTEGER PRIMARY KEY,
                group_id INTEGER NOT NULL,
                news_id INTEGER NOT NULL,
                similarity_score FLOAT,
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
                source_url TEXT,
                confidence FLOAT,
                FOREIGN KEY (news_id) REFERENCES news_queue(id)
            )
        ''')
        
        # AI Drafts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_drafts (
                id INTEGER PRIMARY KEY,
                workspace_id INTEGER NOT NULL,
                news_id INTEGER NOT NULL,
                title TEXT,
                headline_suggestions TEXT,
                body_draft TEXT,
                summary TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                edited BOOLEAN DEFAULT 0,
                edited_by_human BOOLEAN DEFAULT 0,
                word_count INTEGER,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
                FOREIGN KEY (news_id) REFERENCES news_queue(id)
            )
        ''')
        
        # Images
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY,
                draft_id INTEGER NOT NULL,
                image_url TEXT,
                image_path TEXT,
                approved BOOLEAN DEFAULT 0,
                nsfw_detected BOOLEAN DEFAULT 0,
                relevance_score FLOAT,
                FOREIGN KEY (draft_id) REFERENCES ai_drafts(id)
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
        
        # WordPress Posts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wordpress_posts (
                id INTEGER PRIMARY KEY,
                draft_id INTEGER NOT NULL,
                wp_post_id INTEGER,
                wp_site_url TEXT,
                status TEXT DEFAULT 'draft',
                published_at TIMESTAMP,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                last_test TIMESTAMP,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("[OK] Database initialized")

# ============================================================================
# MODERN TKINTER UI
# ============================================================================

class ModernButton(tk.Button):
    """Styled modern button"""
    def __init__(self, parent, text, command=None, color='primary', **kwargs):
        bg_color = COLORS.get(color, COLORS['primary'])
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=COLORS['white'],
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10,
            **kwargs
        )
        
        self.default_bg = bg_color
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, e):
        self['bg'] = COLORS['hover']
    
    def _on_leave(self, e):
        self['bg'] = self.default_bg

class NexuzyPublisherApp(tk.Tk):
    """Main application with modern colorful UI"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Nexuzy Publisher Desk - AI News Platform")
        self.geometry("1400x800")
        self.configure(bg=COLORS['white'])
        
        # Window icon
        try:
            if os.path.exists('resources/logo.ico'):
                self.iconbitmap('resources/logo.ico')
        except:
            pass
        
        self.db_path = 'nexuzy.db'
        self.current_workspace = None
        self.current_workspace_id = None
        
        # Initialize database
        DatabaseSetup(self.db_path)
        
        # Import core modules
        self._import_modules()
        
        # Create UI
        self.create_modern_ui()
        self.load_workspaces()
        
        # Show welcome screen
        self.show_dashboard()
    
    def _import_modules(self):
        """Import core modules"""
        try:
            from core.rss_manager import RSSManager
            from core.news_matcher import NewsMatchEngine
            from core.content_scraper import ContentScraper
            from core.ai_draft_generator import DraftGenerator
            from core.translator import Translator
            from core.wordpress_api import WordPressAPI
            
            self.rss_manager = RSSManager(self.db_path)
            self.news_matcher = NewsMatchEngine(self.db_path)
            self.scraper = ContentScraper(self.db_path)
            self.draft_generator = DraftGenerator(self.db_path)
            self.translator = Translator(self.db_path)
            self.wordpress = WordPressAPI(self.db_path)
            
            logger.info("[OK] Core modules loaded")
        except Exception as e:
            logger.error(f"Module import error: {e}")
            self.rss_manager = None
            self.news_matcher = None
            self.scraper = None
            self.draft_generator = None
            self.translator = None
            self.wordpress = None
    
    def create_modern_ui(self):
        """Create modern colorful UI"""
        # TOP HEADER
        header = tk.Frame(self, bg=COLORS['dark'], height=70)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        
        # Logo and title
        title_frame = tk.Frame(header, bg=COLORS['dark'])
        title_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(
            title_frame,
            text="NEXUZY",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['dark'],
            fg=COLORS['primary']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            title_frame,
            text="Publisher Desk",
            font=('Segoe UI', 16),
            bg=COLORS['dark'],
            fg=COLORS['white']
        ).pack(side=tk.LEFT, padx=10)
        
        # Workspace selector
        workspace_frame = tk.Frame(header, bg=COLORS['dark'])
        workspace_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(
            workspace_frame,
            text="Workspace:",
            font=('Segoe UI', 10),
            bg=COLORS['dark'],
            fg=COLORS['light']
        ).pack(side=tk.LEFT, padx=5)
        
        self.workspace_var = tk.StringVar(value="Select Workspace")
        self.workspace_menu = ttk.Combobox(
            workspace_frame,
            textvariable=self.workspace_var,
            state='readonly',
            width=25,
            font=('Segoe UI', 10)
        )
        self.workspace_menu.pack(side=tk.LEFT, padx=5)
        self.workspace_menu.bind('<<ComboboxSelected>>', self.on_workspace_change)
        
        ModernButton(
            workspace_frame,
            text="+ New",
            command=self.new_workspace,
            color='success'
        ).pack(side=tk.LEFT, padx=5)
        
        # MAIN CONTAINER
        main_container = tk.Frame(self, bg=COLORS['light'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # LEFT SIDEBAR
        sidebar = tk.Frame(main_container, bg=COLORS['darker'], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.show_dashboard, 'primary'),
            ("RSS Feeds", self.show_rss_manager, 'primary'),
            ("News Queue", self.show_news_queue, 'primary'),
            ("AI Editor", self.show_editor, 'success'),
            ("Translations", self.show_translations, 'warning'),
            ("WordPress", self.show_wordpress_config, 'primary'),
            ("Settings", self.show_settings, 'text_light'),
        ]
        
        tk.Label(
            sidebar,
            text="NAVIGATION",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORS['darker'],
            fg=COLORS['text_light'],
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
            statusbar,
            text="Ready | AI-Powered News Platform",
            font=('Segoe UI', 9),
            bg=COLORS['dark'],
            fg=COLORS['light'],
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True)
        
        # Time label
        self.time_label = tk.Label(
            statusbar,
            text=datetime.now().strftime("%H:%M:%S"),
            font=('Segoe UI', 9),
            bg=COLORS['dark'],
            fg=COLORS['light']
        )
        self.time_label.pack(side=tk.RIGHT, padx=15)
        self.update_time()
    
    def create_nav_button(self, parent, text, command, color):
        """Create navigation button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=COLORS['darker'],
            fg=COLORS['white'],
            font=('Segoe UI', 11),
            relief=tk.FLAT,
            cursor='hand2',
            anchor=tk.W,
            padx=20,
            pady=12
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
        """Update time label"""
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.update_time)
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_status(self, message, color='light'):
        """Update status bar"""
        self.status_label.config(text=message, fg=COLORS.get(color, COLORS['light']))
    
    # ===========================================
    # WORKSPACE MANAGEMENT
    # ===========================================
    
    def load_workspaces(self):
        """Load workspaces from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM workspaces')
            workspaces = cursor.fetchall()
            conn.close()
            
            if workspaces:
                names = [ws[1] for ws in workspaces]
                self.workspace_menu['values'] = names
                self.workspace_menu.current(0)
                self.current_workspace = workspaces[0][1]
                self.current_workspace_id = workspaces[0][0]
            else:
                self.workspace_menu['values'] = []
                self.new_workspace()
        except Exception as e:
            logger.error(f"Error loading workspaces: {e}")
    
    def on_workspace_change(self, event=None):
        """Handle workspace selection"""
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
        """Create new workspace dialog"""
        dialog = tk.Toplevel(self)
        dialog.title("New Workspace")
        dialog.geometry("400x150")
        dialog.configure(bg=COLORS['white'])
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="Create New Workspace",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack(pady=15)
        
        tk.Label(
            dialog,
            text="Workspace Name:",
            font=('Segoe UI', 10),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack(pady=5)
        
        name_entry = tk.Entry(dialog, width=30, font=('Segoe UI', 11))
        name_entry.pack(pady=5)
        name_entry.focus()
        
        def create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter workspace name")
                return
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('INSERT INTO workspaces (name) VALUES (?)', (name,))
                conn.commit()
                conn.close()
                
                self.load_workspaces()
                dialog.destroy()
                messagebox.showinfo("Success", f"Workspace '{name}' created successfully!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Workspace name already exists")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
        
        ModernButton(dialog, text="Create Workspace", command=create, color='success').pack(pady=15)
    
    # ===========================================
    # SCREEN VIEWS
    # ===========================================
    
    def show_dashboard(self):
        """Show dashboard with stats and quick actions"""
        self.clear_content()
        self.update_status("Dashboard", 'primary')
        
        # Header
        header = tk.Frame(self.content_frame, bg=COLORS['white'])
        header.pack(fill=tk.X, padx=30, pady=20)
        
        tk.Label(
            header,
            text="Dashboard",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack(side=tk.LEFT)
        
        # Stats cards
        stats_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        stats_frame.pack(fill=tk.X, padx=30, pady=10)
        
        # Get stats
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
        
        # Quick actions
        actions_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        tk.Label(
            actions_frame,
            text="Quick Actions",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack(anchor=tk.W, pady=10)
        
        btn_frame = tk.Frame(actions_frame, bg=COLORS['white'])
        btn_frame.pack(fill=tk.X, pady=10)
        
        ModernButton(btn_frame, "Add RSS Feed", self.show_rss_manager, 'primary').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, "Generate Draft", self.show_editor, 'success').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, "View News", self.show_news_queue, 'warning').pack(side=tk.LEFT, padx=5)
    
    def create_stat_card(self, parent, title, value, color):
        """Create colored stat card"""
        card = tk.Frame(parent, bg=color, relief=tk.RAISED, borderwidth=0)
        card.pack(side=tk.LEFT, padx=10, pady=10, ipadx=30, ipady=20)
        
        tk.Label(
            card,
            text=value,
            font=('Segoe UI', 32, 'bold'),
            bg=color,
            fg=COLORS['white']
        ).pack()
        
        tk.Label(
            card,
            text=title,
            font=('Segoe UI', 12),
            bg=color,
            fg=COLORS['white']
        ).pack()
    
    def show_rss_manager(self):
        """Show RSS feed management interface"""
        self.clear_content()
        self.update_status("RSS Feed Manager", 'primary')
        
        tk.Label(
            self.content_frame,
            text="RSS Feed Manager",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        # Add feed form
        form_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        form_frame.pack(fill=tk.X, padx=30, pady=10, ipady=15)
        
        tk.Label(form_frame, text="RSS Feed URL:", bg=COLORS['light']).pack(side=tk.LEFT, padx=10)
        url_entry = tk.Entry(form_frame, width=50, font=('Segoe UI', 10))
        url_entry.pack(side=tk.LEFT, padx=5)
        
        ModernButton(form_frame, "Add Feed", lambda: self.add_rss_feed(url_entry.get()), 'success').pack(side=tk.LEFT, padx=10)
        
        # Feed list
        list_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(
            list_frame,
            text="Active Feeds",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack(anchor=tk.W, pady=10)
        
        # Scrollable list
        self.feeds_listbox = tk.Listbox(list_frame, font=('Segoe UI', 10), height=15)
        self.feeds_listbox.pack(fill=tk.BOTH, expand=True)
        
        self.load_rss_feeds()
    
    def add_rss_feed(self, url):
        """Add RSS feed to database"""
        if not url or not self.current_workspace_id:
            messagebox.showerror("Error", "Please enter a valid RSS feed URL and select a workspace")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO rss_feeds (workspace_id, url) VALUES (?, ?)',
                (self.current_workspace_id, url)
            )
            conn.commit()
            conn.close()
            
            self.load_rss_feeds()
            self.update_status(f"Feed added: {url}", 'success')
            messagebox.showinfo("Success", "RSS feed added successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This feed is already added")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding feed: {e}")
    
    def load_rss_feeds(self):
        """Load RSS feeds into listbox"""
        if not hasattr(self, 'feeds_listbox'):
            return
        
        self.feeds_listbox.delete(0, tk.END)
        
        if not self.current_workspace_id:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT url, enabled FROM rss_feeds WHERE workspace_id = ?',
                (self.current_workspace_id,)
            )
            feeds = cursor.fetchall()
            conn.close()
            
            for url, enabled in feeds:
                status = "[ACTIVE]" if enabled else "[DISABLED]"
                self.feeds_listbox.insert(tk.END, f"{status} {url}")
        except Exception as e:
            logger.error(f"Error loading feeds: {e}")
    
    def show_news_queue(self):
        """Show news queue"""
        self.clear_content()
        self.update_status("News Queue", 'warning')
        
        tk.Label(
            self.content_frame,
            text="News Queue",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        tk.Label(
            self.content_frame,
            text="Recent news items will appear here after RSS feeds are processed.",
            font=('Segoe UI', 11),
            bg=COLORS['white'],
            fg=COLORS['text_light']
        ).pack(padx=30, pady=10, anchor=tk.W)
        
        ModernButton(self.content_frame, "Fetch from RSS", self.fetch_rss_news, 'primary').pack(padx=30, pady=20, anchor=tk.W)
    
    def fetch_rss_news(self):
        """Fetch news from RSS feeds"""
        if not self.rss_manager or not self.current_workspace_id:
            messagebox.showwarning("Warning", "Please select a workspace first")
            return
        
        self.update_status("Fetching news from RSS feeds...", 'warning')
        # This would trigger actual RSS fetching
        messagebox.showinfo("Info", "RSS fetching will be implemented in the full version")
    
    def show_editor(self):
        """Show AI editor interface"""
        self.clear_content()
        self.update_status("AI Draft Editor", 'success')
        
        tk.Label(
            self.content_frame,
            text="AI Draft Editor",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        tk.Label(
            self.content_frame,
            text="Generate AI-powered article drafts from news items.",
            font=('Segoe UI', 11),
            bg=COLORS['white'],
            fg=COLORS['text_light']
        ).pack(padx=30, pady=10, anchor=tk.W)
        
        ModernButton(self.content_frame, "Generate Draft", self.generate_test_draft, 'success').pack(padx=30, pady=20, anchor=tk.W)
    
    def generate_test_draft(self):
        """Generate test draft"""
        if not self.draft_generator:
            messagebox.showwarning("Warning", "Draft generator not loaded")
            return
        
        self.update_status("Generating draft...", 'success')
        messagebox.showinfo("Info", "Draft generation will work once news items are added")
    
    def show_translations(self):
        """Show translation interface"""
        self.clear_content()
        self.update_status("Multi-Language Translation", 'warning')
        
        tk.Label(
            self.content_frame,
            text="Translation Manager",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        tk.Label(
            self.content_frame,
            text="Translate articles to multiple languages using AI.",
            font=('Segoe UI', 11),
            bg=COLORS['white'],
            fg=COLORS['text_light']
        ).pack(padx=30, pady=10, anchor=tk.W)
    
    def show_wordpress_config(self):
        """Show WordPress configuration"""
        self.clear_content()
        self.update_status("WordPress Integration", 'primary')
        
        tk.Label(
            self.content_frame,
            text="WordPress Integration",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        tk.Label(
            self.content_frame,
            text="Connect your WordPress site to publish articles automatically.",
            font=('Segoe UI', 11),
            bg=COLORS['white'],
            fg=COLORS['text_light']
        ).pack(padx=30, pady=10, anchor=tk.W)
    
    def show_settings(self):
        """Show settings with AI model status"""
        self.clear_content()
        self.update_status("Settings & AI Models", 'text_light')
        
        tk.Label(
            self.content_frame,
            text="Settings & AI Models",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        # Model status section
        models_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        models_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(
            models_frame,
            text="AI Models Configuration",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORS['light'],
            fg=COLORS['text']
        ).pack(padx=20, pady=15, anchor=tk.W)
        
        for model_key, config in MODEL_CONFIGS.items():
            self.create_model_status_card(models_frame, config)
    
    def create_model_status_card(self, parent, config):
        """Create model status card"""
        card = tk.Frame(parent, bg=COLORS['white'], relief=tk.RAISED, borderwidth=1)
        card.pack(fill=tk.X, padx=20, pady=10)
        
        # Header with colored bar
        header = tk.Frame(card, bg=config['color'], height=5)
        header.pack(fill=tk.X)
        
        content = tk.Frame(card, bg=COLORS['white'])
        content.pack(fill=tk.X, padx=15, pady=15)
        
        # Model name
        tk.Label(
            content,
            text=config['name'],
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack(anchor=tk.W)
        
        # Purpose
        tk.Label(
            content,
            text=f"Purpose: {config['purpose']}",
            font=('Segoe UI', 10),
            bg=COLORS['white'],
            fg=COLORS['text_light']
        ).pack(anchor=tk.W, pady=2)
        
        # Size
        tk.Label(
            content,
            text=f"Size: {config['size']}",
            font=('Segoe UI', 10),
            bg=COLORS['white'],
            fg=COLORS['text_light']
        ).pack(anchor=tk.W, pady=2)
        
        # Full name
        tk.Label(
            content,
            text=f"Model: {config['full_name']}",
            font=('Segoe UI', 9),
            bg=COLORS['white'],
            fg=COLORS['text_light']
        ).pack(anchor=tk.W, pady=5)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Application entry point"""
    logger.info("="* 60)
    logger.info("Starting Nexuzy Publisher Desk")
    logger.info("=" * 60)
    
    app = NexuzyPublisherApp()
    app.mainloop()

if __name__ == '__main__':
    main()
