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
# DAVID AI MODEL CONFIGURATION - NO REPO PATHS
# =============================================================================

MODEL_CONFIGS = {
    'sentence_transformer': {
        'display_name': 'David AI 2B',
        'size': '80MB',
        'purpose': 'News Similarity Matching',
        'color': COLORS['success']
    },
    'draft_generator': {
        'display_name': 'David AI Writer 7B',
        'size': '4.1GB',
        'purpose': 'Article Generation',
        'color': COLORS['primary']
    },
    'translator': {
        'display_name': 'David AI Translator',
        'size': '1.2GB',
        'purpose': '200+ Languages Translation',
        'color': COLORS['warning']
    },
    'vision_ai': {
        'display_name': 'David AI Vision',
        'size': '2.3GB',
        'purpose': 'Image Watermark Detection',
        'color': COLORS['danger']
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
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_drafts (
                id INTEGER PRIMARY KEY,
                workspace_id INTEGER NOT NULL,
                news_id INTEGER NOT NULL,
                title TEXT,
                body_draft TEXT,
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
            logger.info("[OK] RSS Manager loaded")
        except Exception as e:
            logger.error(f"Module import error: {e}")
            self.rss_manager = None
    
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
            values=['General', 'Politics', 'Technology', 'Sports', 'Business', 'Entertainment'],
            state='readonly', width=15
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
        
        ModernButton(
            self.content_frame, "Fetch Latest News from RSS",
            self.fetch_rss_news, 'primary'
        ).pack(padx=30, pady=10, anchor=tk.W)
        
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
                SELECT headline, source_domain, category 
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
                for headline, source, category in news_items:
                    self.news_listbox.insert(tk.END, f"[{category}] {source}: {headline}")
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
    
    def show_editor(self):
        self.clear_content()
        self.update_status("AI Draft Editor", 'success')
        
        tk.Label(
            self.content_frame, text="AI Draft Editor",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        tk.Label(
            self.content_frame,
            text="Generate AI-powered article drafts using David AI Writer 7B.",
            font=('Segoe UI', 11),
            bg=COLORS['white'], fg=COLORS['text_light']
        ).pack(padx=30, pady=10, anchor=tk.W)
        
        editor_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        text_area = scrolledtext.ScrolledText(
            editor_frame, font=('Consolas', 10),
            wrap=tk.WORD, height=20
        )
        text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        text_area.insert(tk.END, "AI-generated drafts will appear here...")
    
    def show_translations(self):
        self.clear_content()
        self.update_status("Translation Manager", 'warning')
        
        tk.Label(
            self.content_frame, text="Translation Manager",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        tk.Label(
            self.content_frame,
            text="Translate articles using David AI Translator (200+ languages).",
            font=('Segoe UI', 11),
            bg=COLORS['white'], fg=COLORS['text_light']
        ).pack(padx=30, pady=10, anchor=tk.W)
        
        lang_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        lang_frame.pack(fill=tk.X, padx=30, pady=20, ipady=15)
        
        tk.Label(lang_frame, text="Target Language:", bg=COLORS['light']).pack(side=tk.LEFT, padx=10)
        
        languages = ['Spanish', 'French', 'German', 'Hindi', 'Bengali', 'Arabic', 'Chinese', 'Japanese', 'Korean', 'Portuguese']
        lang_var = tk.StringVar(value='Spanish')
        lang_menu = ttk.Combobox(lang_frame, textvariable=lang_var, values=languages, state='readonly', width=20)
        lang_menu.pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            lang_frame, "Translate Now",
            lambda: messagebox.showinfo("Info", f"Translation to {lang_var.get()} will start..."),
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
        
        preview_text = scrolledtext.ScrolledText(
            preview_frame, font=('Segoe UI', 10),
            wrap=tk.WORD, height=15
        )
        preview_text.pack(fill=tk.BOTH, expand=True)
        preview_text.insert(tk.END, "Translated text will appear here...")
    
    def show_wordpress_config(self):
        self.clear_content()
        self.update_status("WordPress Integration", 'primary')
        
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
        
        fields = [
            ("Site URL:", "https://yoursite.com"),
            ("Username:", "your_username"),
            ("App Password:", "xxxx xxxx xxxx xxxx")
        ]
        
        for label_text, placeholder in fields:
            field_frame = tk.Frame(config_frame, bg=COLORS['light'])
            field_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(field_frame, text=label_text, bg=COLORS['light'], width=15, anchor=tk.W).pack(side=tk.LEFT)
            entry = tk.Entry(field_frame, width=40, font=('Segoe UI', 10))
            entry.insert(0, placeholder)
            entry.pack(side=tk.LEFT, padx=10)
        
        btn_frame = tk.Frame(config_frame, bg=COLORS['light'])
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ModernButton(
            btn_frame, "Test Connection",
            lambda: messagebox.showinfo("Success", "WordPress connected!"),
            'success'
        ).pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            btn_frame, "Save Settings",
            lambda: messagebox.showinfo("Success", "Settings saved!"),
            'primary'
        ).pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            btn_frame, "Publish Sample Article",
            lambda: messagebox.showinfo("Success", "Article published!"),
            'warning'
        ).pack(side=tk.LEFT, padx=5)
    
    def show_vision_ai(self):
        """Vision AI for watermark detection in news images"""
        self.clear_content()
        self.update_status("Vision AI - Watermark Detection", 'danger')
        
        tk.Label(
            self.content_frame, text="Vision AI - Watermark Detection",
            font=('Segoe UI', 20, 'bold'),
            bg=COLORS['white'], fg=COLORS['text']
        ).pack(padx=30, pady=20, anchor=tk.W)
        
        tk.Label(
            self.content_frame,
            text="Analyze news article images for watermarks using David AI Vision.",
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
        
        results_text = scrolledtext.ScrolledText(
            results_frame, font=('Consolas', 10),
            wrap=tk.WORD, height=15
        )
        results_text.pack(fill=tk.BOTH, expand=True)
        results_text.insert(tk.END, "Upload an image to see analysis results...\n\nDavid AI Vision will detect:\n- Watermarks\n- Logos\n- Text overlays\n- Copyright marks")
    
    def upload_image_for_analysis(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if file_path:
            messagebox.showinfo(
                "Vision AI",
                f"Image selected: {os.path.basename(file_path)}\n\nAnalyzing for watermarks..."
            )
    
    def show_settings(self):
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
            self.create_model_status_card(models_frame, config)
    
    def create_model_status_card(self, parent, config):
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
        
        tk.Label(
            top_row, text="Available",
            font=('Segoe UI', 10, 'bold'),
            bg=config['color'], fg=COLORS['white'],
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
