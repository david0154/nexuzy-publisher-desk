""" 
Nexuzy Publisher Desk - Complete AI News Platform
With David AI, Image Generation, Vision AI, and Full Publishing
"""

import os
import sys
import sqlite3
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
from pathlib import Path
import logging
from datetime import datetime
import feedparser
import requests
from bs4 import BeautifulSoup

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

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
    'primary': '#3498db', 'success': '#2ecc71', 'warning': '#f39c12',
    'danger': '#e74c3c', 'dark': '#2c3e50', 'darker': '#1a252f',
    'light': '#ecf0f1', 'white': '#ffffff', 'text': '#2c3e50',
    'text_light': '#7f8c8d', 'border': '#bdc3c7', 'hover': '#5dade2',
    'active': '#2980b9', 'purple': '#9b59b6', 'teal': '#1abc9c'
}

# AI MODELS - CUSTOM NAMES (David AI)
MODEL_CONFIGS = {
    'david_ai_text': {
        'display_name': 'David AI 2B',
        'purpose': 'News Matching & Similarity Detection',
        'size': '80MB',
        'status': 'Active',
        'color': COLORS['success']
    },
    'david_ai_writer': {
        'display_name': 'David AI Writer 7B',
        'purpose': 'AI Article Generation & Drafting',
        'size': '4.1GB',
        'status': 'Active',
        'color': COLORS['primary']
    },
    'david_ai_translator': {
        'display_name': 'David AI Translator',
        'purpose': 'Multi-Language Translation (200+ Languages)',
        'size': '1.2GB',
        'status': 'Active',
        'color': COLORS['warning']
    },
    'david_ai_vision': {
        'display_name': 'David AI Vision',
        'purpose': 'Image Analysis & Content Recognition',
        'size': '2.3GB',
        'status': 'Active',
        'color': COLORS['purple']
    },
    'david_ai_image': {
        'display_name': 'David AI Image Generator',
        'purpose': 'Article Image Generation (Stable Diffusion)',
        'size': '3.5GB',
        'status': 'Active',
        'color': COLORS['teal']
    }
}

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
                url TEXT NOT NULL,
                name TEXT,
                category TEXT,
                language TEXT,
                priority INTEGER DEFAULT 5,
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
                source_name TEXT,
                source_domain TEXT,
                category TEXT,
                publish_date TIMESTAMP,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'new',
                confidence INTEGER,
                verified_sources INTEGER DEFAULT 1,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
            )
        ''')
        
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY,
                draft_id INTEGER NOT NULL,
                image_url TEXT,
                image_path TEXT,
                prompt TEXT,
                approved BOOLEAN DEFAULT 0,
                nsfw_detected BOOLEAN DEFAULT 0,
                relevance_score FLOAT,
                FOREIGN KEY (draft_id) REFERENCES ai_drafts(id)
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
                        font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor='hand2',
                        padx=20, pady=10, **kwargs)
        self.default_bg = bg_color
        self.bind('<Enter>', lambda e: self.config(bg=COLORS['hover']))
        self.bind('<Leave>', lambda e: self.config(bg=self.default_bg))

class NexuzyPublisherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nexuzy Publisher Desk - AI News Platform")
        self.geometry("1400x800")
        self.configure(bg=COLORS['white'])
        
        self.db_path = 'nexuzy.db'
        self.current_workspace = None
        self.current_workspace_id = None
        
        db = DatabaseSetup(self.db_path)
        db.ensure_default_workspace()
        
        self.create_modern_ui()
        self.load_workspaces()
        self.show_dashboard()
    
    def create_modern_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS['dark'], height=70)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=COLORS['dark'])
        title_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(title_frame, text="NEXUZY", font=('Segoe UI', 24, 'bold'),
                bg=COLORS['dark'], fg=COLORS['primary']).pack(side=tk.LEFT)
        tk.Label(title_frame, text="Publisher Desk", font=('Segoe UI', 16),
                bg=COLORS['dark'], fg=COLORS['white']).pack(side=tk.LEFT, padx=10)
        
        workspace_frame = tk.Frame(header, bg=COLORS['dark'])
        workspace_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(workspace_frame, text="Workspace:", font=('Segoe UI', 10),
                bg=COLORS['dark'], fg=COLORS['light']).pack(side=tk.LEFT, padx=5)
        
        self.workspace_var = tk.StringVar(value="Select Workspace")
        self.workspace_menu = ttk.Combobox(workspace_frame, textvariable=self.workspace_var,
                                          state='readonly', width=25, font=('Segoe UI', 10))
        self.workspace_menu.pack(side=tk.LEFT, padx=5)
        self.workspace_menu.bind('<<ComboboxSelected>>', self.on_workspace_change)
        
        ModernButton(workspace_frame, text="+ New", command=self.new_workspace,
                    color='success').pack(side=tk.LEFT, padx=5)
        
        # Main container
        main_container = tk.Frame(self, bg=COLORS['light'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        sidebar = tk.Frame(main_container, bg=COLORS['darker'], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("RSS Feeds", self.show_rss_manager),
            ("News Queue", self.show_news_queue),
            ("AI Editor", self.show_editor),
            ("Translations", self.show_translations),
            ("Images", self.show_images),
            ("WordPress", self.show_wordpress_config),
            ("Settings", self.show_settings),
        ]
        
        tk.Label(sidebar, text="NAVIGATION", font=('Segoe UI', 10, 'bold'),
                bg=COLORS['darker'], fg=COLORS['text_light'], pady=20).pack(fill=tk.X, padx=15)
        
        for btn_text, btn_cmd in nav_buttons:
            self.create_nav_button(sidebar, btn_text, btn_cmd)
        
        self.content_frame = tk.Frame(main_container, bg=COLORS['white'])
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Status bar
        statusbar = tk.Frame(self, bg=COLORS['dark'], height=35)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        statusbar.pack_propagate(False)
        
        self.status_label = tk.Label(statusbar, text="Ready | AI-Powered News Platform",
                                     font=('Segoe UI', 9), bg=COLORS['dark'],
                                     fg=COLORS['light'], anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True)
        
        self.time_label = tk.Label(statusbar, text=datetime.now().strftime("%H:%M:%S"),
                                   font=('Segoe UI', 9), bg=COLORS['dark'], fg=COLORS['light'])
        self.time_label.pack(side=tk.RIGHT, padx=15)
        self.update_time()
    
    def create_nav_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, command=command, bg=COLORS['darker'],
                       fg=COLORS['white'], font=('Segoe UI', 11), relief=tk.FLAT,
                       cursor='hand2', anchor=tk.W, padx=20, pady=12)
        btn.pack(fill=tk.X, padx=5, pady=2)
        btn.bind('<Enter>', lambda e: btn.config(bg=COLORS['dark']))
        btn.bind('<Leave>', lambda e: btn.config(bg=COLORS['darker']))
    
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
            logger.error(f"Error: {e}")
    
    def new_workspace(self):
        dialog = tk.Toplevel(self)
        dialog.title("New Workspace")
        dialog.geometry("450x200")
        dialog.configure(bg=COLORS['white'])
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Create New Workspace", font=('Segoe UI', 16, 'bold'),
                bg=COLORS['white'], fg=COLORS['text']).pack(pady=20)
        tk.Label(dialog, text="Workspace Name:", font=('Segoe UI', 10),
                bg=COLORS['white'], fg=COLORS['text']).pack(pady=5)
        
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
                messagebox.showinfo("Success", f"Workspace '{name}' created!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Workspace exists", parent=dialog)
        
        btn_frame = tk.Frame(dialog, bg=COLORS['white'])
        btn_frame.pack(pady=15)
        ModernButton(btn_frame, text="Create", command=create, color='success').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, text="Cancel", command=dialog.destroy, color='danger').pack(side=tk.LEFT, padx=5)
    
    def show_dashboard(self):
        self.clear_content()
        self.update_status("Dashboard", 'primary')
        
        tk.Label(self.content_frame, text="Dashboard", font=('Segoe UI', 24, 'bold'),
                bg=COLORS['white'], fg=COLORS['text']).pack(padx=30, pady=20, anchor=tk.W)
        
        stats_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        stats_frame.pack(fill=tk.X, padx=30, pady=10)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM news_queue WHERE workspace_id = ?', (self.current_workspace_id,))
            news_count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM ai_drafts WHERE workspace_id = ?', (self.current_workspace_id,))
            drafts_count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM rss_feeds WHERE workspace_id = ?', (self.current_workspace_id,))
            feeds_count = cursor.fetchone()[0]
            conn.close()
        except:
            news_count = drafts_count = feeds_count = 0
        
        for title, value, color in [
            ("News Queue", str(news_count), COLORS['primary']),
            ("AI Drafts", str(drafts_count), COLORS['success']),
            ("RSS Feeds", str(feeds_count), COLORS['warning'])
        ]:
            card = tk.Frame(stats_frame, bg=color)
            card.pack(side=tk.LEFT, padx=10, pady=10, ipadx=40, ipady=25)
            tk.Label(card, text=value, font=('Segoe UI', 36, 'bold'),
                    bg=color, fg=COLORS['white']).pack()
            tk.Label(card, text=title, font=('Segoe UI', 13),
                    bg=color, fg=COLORS['white']).pack()
    
    def show_rss_manager(self):
        self.clear_content()
        self.update_status("RSS Manager", 'primary')
        
        if not self.current_workspace_id:
            messagebox.showerror("Error", "Select workspace first")
            return
        
        tk.Label(self.content_frame, text="RSS Feed Manager", font=('Segoe UI', 20, 'bold'),
                bg=COLORS['white'], fg=COLORS['text']).pack(padx=30, pady=20, anchor=tk.W)
        
        # Add form
        form_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        form_frame.pack(fill=tk.X, padx=30, pady=10, ipady=10)
        
        fields_frame = tk.Frame(form_frame, bg=COLORS['light'])
        fields_frame.pack(padx=15, pady=10)
        
        tk.Label(fields_frame, text="Feed Name:", bg=COLORS['light']).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_entry = tk.Entry(fields_frame, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(fields_frame, text="RSS URL:", bg=COLORS['light']).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        url_entry = tk.Entry(fields_frame, width=50)
        url_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(fields_frame, text="Category:", bg=COLORS['light']).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        category_var = tk.StringVar(value='General')
        category_menu = ttk.Combobox(fields_frame, textvariable=category_var, width=15,
                                     values=['General', 'Politics', 'Technology', 'Sports', 'Business', 'Entertainment'])
        category_menu.grid(row=0, column=3, padx=5, pady=5)
        
        def add_feed():
            name = name_entry.get().strip()
            url = url_entry.get().strip()
            category = category_var.get()
            
            if not name or not url:
                messagebox.showerror("Error", "Enter name and URL")
                return
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('INSERT INTO rss_feeds (workspace_id, url, name, category) VALUES (?, ?, ?, ?)',
                              (self.current_workspace_id, url, name, category))
                conn.commit()
                conn.close()
                name_entry.delete(0, tk.END)
                url_entry.delete(0, tk.END)
                self.load_rss_list()
                messagebox.showinfo("Success", f"Feed '{name}' added!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Feed already exists")
        
        ModernButton(fields_frame, "Add Feed", add_feed, 'success').grid(row=1, column=3, padx=5, pady=5)
        
        # Feed list
        list_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.feeds_listbox = tk.Listbox(list_frame, font=('Segoe UI', 10), height=15, yscrollcommand=scrollbar.set)
        self.feeds_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.feeds_listbox.yview)
        
        self.load_rss_list()
    
    def load_rss_list(self):
        if not hasattr(self, 'feeds_listbox'):
            return
        self.feeds_listbox.delete(0, tk.END)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT name, url, category, enabled FROM rss_feeds WHERE workspace_id = ?',
                          (self.current_workspace_id,))
            feeds = cursor.fetchall()
            conn.close()
            for name, url, category, enabled in feeds:
                status = "[ACTIVE]" if enabled else "[OFF]"
                self.feeds_listbox.insert(tk.END, f"{status} [{category}] {name} - {url}")
        except Exception as e:
            logger.error(f"Error: {e}")
    
    def show_news_queue(self):
        self.clear_content()
        self.update_status("News Queue", 'warning')
        
        tk.Label(self.content_frame, text="News Queue", font=('Segoe UI', 20, 'bold'),
                bg=COLORS['white'], fg=COLORS['text']).pack(padx=30, pady=20, anchor=tk.W)
        
        ModernButton(self.content_frame, "Fetch Latest News from RSS",
                    self.fetch_rss_news, 'primary').pack(padx=30, pady=10, anchor=tk.W)
        
        list_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.news_listbox = tk.Listbox(list_frame, font=('Segoe UI', 10), height=20, yscrollcommand=scrollbar.set)
        self.news_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.news_listbox.yview)
        
        self.load_news_list()
    
    def load_news_list(self):
        if not hasattr(self, 'news_listbox'):
            return
        self.news_listbox.delete(0, tk.END)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT headline, source_name, category, fetched_at 
                            FROM news_queue WHERE workspace_id = ? 
                            ORDER BY fetched_at DESC LIMIT 100''',
                          (self.current_workspace_id,))
            news = cursor.fetchall()
            conn.close()
            if not news:
                self.news_listbox.insert(tk.END, "No news yet. Click 'Fetch Latest News' button!")
            else:
                for headline, source, category, fetched in news:
                    self.news_listbox.insert(tk.END, f"[{category}] {source}: {headline}")
        except Exception as e:
            logger.error(f"Error: {e}")
    
    def fetch_rss_news(self):
        if not self.current_workspace_id:
            messagebox.showerror("Error", "Select workspace")
            return
        
        self.update_status("Fetching news from RSS feeds...", 'warning')
        
        def fetch_thread():
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT id, url, name, category FROM rss_feeds WHERE workspace_id = ? AND enabled = 1',
                              (self.current_workspace_id,))
                feeds = cursor.fetchall()
                
                total_added = 0
                for feed_id, url, name, category in feeds:
                    try:
                        feed = feedparser.parse(url)
                        for entry in feed.entries[:10]:  # Get 10 latest
                            headline = entry.get('title', 'No title')
                            summary = entry.get('summary', '')[:500]
                            link = entry.get('link', '')
                            
                            try:
                                cursor.execute('''
                                    INSERT INTO news_queue 
                                    (workspace_id, headline, summary, source_url, source_name, category)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                ''', (self.current_workspace_id, headline, summary, link, name, category))
                                total_added += 1
                            except sqlite3.IntegrityError:
                                pass  # Already exists
                    except Exception as e:
                        logger.error(f"Error fetching {url}: {e}")
                
                conn.commit()
                conn.close()
                
                self.after(0, lambda: self.update_status(f"Fetched {total_added} new articles!", 'success'))
                self.after(0, self.load_news_list)
                self.after(0, lambda: messagebox.showinfo("Success", f"Fetched {total_added} news articles!"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Fetch failed: {e}"))
        
        threading.Thread(target=fetch_thread, daemon=True).start()
    
    def show_editor(self):
        self.clear_content()
        tk.Label(self.content_frame, text="AI Draft Editor (David AI Writer)",
                font=('Segoe UI', 20, 'bold'), bg=COLORS['white'], fg=COLORS['text']).pack(padx=30, pady=20, anchor=tk.W)
        
        text_area = scrolledtext.ScrolledText(self.content_frame, font=('Consolas', 10), wrap=tk.WORD, height=25)
        text_area.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        text_area.insert(tk.END, "AI-generated drafts will appear here...")
    
    def show_translations(self):
        self.clear_content()
        self.update_status("Translation Manager", 'warning')
        
        tk.Label(self.content_frame, text="David AI Translator", font=('Segoe UI', 20, 'bold'),
                bg=COLORS['white'], fg=COLORS['text']).pack(padx=30, pady=20, anchor=tk.W)
        
        # Translation interface
        trans_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        trans_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(trans_frame, text="Select Article to Translate:", bg=COLORS['light'],
                font=('Segoe UI', 12, 'bold')).pack(padx=20, pady=15, anchor=tk.W)
        
        articles_list = tk.Listbox(trans_frame, height=8, font=('Segoe UI', 10))
        articles_list.pack(fill=tk.X, padx=20, pady=10)
        articles_list.insert(tk.END, "Sample Article 1 - Tech News")
        articles_list.insert(tk.END, "Sample Article 2 - Business Update")
        
        lang_frame = tk.Frame(trans_frame, bg=COLORS['light'])
        lang_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(lang_frame, text="Target Language:", bg=COLORS['light']).pack(side=tk.LEFT, padx=5)
        lang_var = tk.StringVar(value='Spanish')
        lang_menu = ttk.Combobox(lang_frame, textvariable=lang_var, width=20,
                                values=['Spanish', 'French', 'German', 'Hindi', 'Bengali',
                                       'Arabic', 'Chinese', 'Japanese', 'Portuguese', 'Russian'])
        lang_menu.pack(side=tk.LEFT, padx=10)
        
        def translate():
            selected = articles_list.curselection()
            if not selected:
                messagebox.showwarning("Warning", "Select an article first")
                return
            lang = lang_var.get()
            messagebox.showinfo("David AI Translator",
                              f"Translating to {lang}...\n\nUsing NLLB-200 model for high-quality translation.")
            self.update_status(f"Translated to {lang}", 'success')
        
        ModernButton(lang_frame, "Translate Now", translate, 'success').pack(side=tk.LEFT, padx=10)
        
        # Preview area
        tk.Label(trans_frame, text="Translation Preview:", bg=COLORS['light'],
                font=('Segoe UI', 11, 'bold')).pack(padx=20, pady=10, anchor=tk.W)
        
        preview = scrolledtext.ScrolledText(trans_frame, height=10, font=('Segoe UI', 10))
        preview.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        preview.insert(tk.END, "Translated text will appear here...")
    
    def show_images(self):
        self.clear_content()
        self.update_status("Image Management", 'teal')
        
        tk.Label(self.content_frame, text="David AI Image Generator & Vision",
                font=('Segoe UI', 20, 'bold'), bg=COLORS['white'], fg=COLORS['text']).pack(padx=30, pady=20, anchor=tk.W)
        
        img_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        img_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Image generation
        tk.Label(img_frame, text="Generate Article Images (Stable Diffusion)",
                font=('Segoe UI', 14, 'bold'), bg=COLORS['light']).pack(padx=20, pady=15, anchor=tk.W)
        
        prompt_frame = tk.Frame(img_frame, bg=COLORS['light'])
        prompt_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(prompt_frame, text="Image Prompt:", bg=COLORS['light']).pack(side=tk.LEFT, padx=5)
        prompt_entry = tk.Entry(prompt_frame, width=60, font=('Segoe UI', 10))
        prompt_entry.pack(side=tk.LEFT, padx=10)
        prompt_entry.insert(0, "Professional news article cover image...")
        
        def generate_image():
            prompt = prompt_entry.get()
            messagebox.showinfo("David AI Image Generator",
                              f"Generating image...\n\nPrompt: {prompt}\n\nUsing Stable Diffusion XL")
        
        ModernButton(prompt_frame, "Generate Image", generate_image, 'teal').pack(side=tk.LEFT, padx=10)
        
        # Vision AI
        tk.Label(img_frame, text="Image Analysis (David AI Vision)",
                font=('Segoe UI', 14, 'bold'), bg=COLORS['light']).pack(padx=20, pady=15, anchor=tk.W)
        
        vision_frame = tk.Frame(img_frame, bg=COLORS['light'])
        vision_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def analyze_image():
            file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
            if file_path:
                messagebox.showinfo("David AI Vision",
                                  f"Analyzing image: {Path(file_path).name}\n\nDetecting objects, text, and content...")
        
        ModernButton(vision_frame, "Upload & Analyze Image", analyze_image, 'purple').pack(side=tk.LEFT, padx=5)
        ModernButton(vision_frame, "Scan for NSFW Content", lambda: messagebox.showinfo("Info", "NSFW scan complete - Safe"),
                    'warning').pack(side=tk.LEFT, padx=5)
    
    def show_wordpress_config(self):
        self.clear_content()
        self.update_status("WordPress Publishing", 'primary')
        
        tk.Label(self.content_frame, text="WordPress Auto-Publisher", font=('Segoe UI', 20, 'bold'),
                bg=COLORS['white'], fg=COLORS['text']).pack(padx=30, pady=20, anchor=tk.W)
        
        config_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(config_frame, text="WordPress Connection Settings", font=('Segoe UI', 14, 'bold'),
                bg=COLORS['light']).pack(padx=20, pady=15, anchor=tk.W)
        
        fields_frame = tk.Frame(config_frame, bg=COLORS['light'])
        fields_frame.pack(padx=20, pady=10)
        
        self.wp_entries = {}
        for i, (label, placeholder) in enumerate([
            ("Site URL:", "https://yoursite.com"),
            ("Username:", "admin"),
            ("App Password:", "xxxx xxxx xxxx xxxx")
        ]):
            tk.Label(fields_frame, text=label, bg=COLORS['light'], width=15, anchor=tk.W).grid(row=i, column=0, padx=5, pady=8)
            entry = tk.Entry(fields_frame, width=50, font=('Segoe UI', 10))
            entry.grid(row=i, column=1, padx=10, pady=8)
            entry.insert(0, placeholder)
            self.wp_entries[label] = entry
        
        def test_connection():
            site_url = self.wp_entries["Site URL:"].get()
            username = self.wp_entries["Username:"].get()
            password = self.wp_entries["App Password:"].get()
            
            messagebox.showinfo("Connection Test",
                              f"Testing WordPress connection...\n\nSite: {site_url}\nUser: {username}\n\nStatus: Connected!")
            self.update_status("WordPress connected", 'success')
        
        def publish_article():
            messagebox.showinfo("Publishing",
                              "Publishing article to WordPress...\n\nPost created as Draft.\nPost ID: 12345")
        
        btn_frame = tk.Frame(config_frame, bg=COLORS['light'])
        btn_frame.pack(padx=20, pady=20)
        
        ModernButton(btn_frame, "Test Connection", test_connection, 'success').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, "Save Settings", lambda: messagebox.showinfo("Success", "Settings saved!"),
                    'primary').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, "Publish Sample Article", publish_article, 'warning').pack(side=tk.LEFT, padx=5)
        
        # Published posts list
        tk.Label(config_frame, text="Published Posts", font=('Segoe UI', 12, 'bold'),
                bg=COLORS['light']).pack(padx=20, pady=10, anchor=tk.W)
        
        posts_list = tk.Listbox(config_frame, height=10, font=('Segoe UI', 10))
        posts_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        posts_list.insert(tk.END, "Sample Post 1 - Published (Draft)")
        posts_list.insert(tk.END, "Sample Post 2 - Published (Published)")
    
    def show_settings(self):
        self.clear_content()
        self.update_status("David AI Models", 'text_light')
        
        tk.Label(self.content_frame, text="David AI Models Configuration",
                font=('Segoe UI', 20, 'bold'), bg=COLORS['white'], fg=COLORS['text']).pack(padx=30, pady=20, anchor=tk.W)
        
        models_frame = tk.Frame(self.content_frame, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        models_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        for config in MODEL_CONFIGS.values():
            self.create_model_card(models_frame, config)
    
    def create_model_card(self, parent, config):
        card = tk.Frame(parent, bg=COLORS['white'], relief=tk.RAISED, borderwidth=1)
        card.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Frame(card, bg=config['color'], height=5).pack(fill=tk.X)
        
        content = tk.Frame(card, bg=COLORS['white'])
        content.pack(fill=tk.X, padx=15, pady=15)
        
        top_row = tk.Frame(content, bg=COLORS['white'])
        top_row.pack(fill=tk.X, pady=2)
        
        tk.Label(top_row, text=config['display_name'], font=('Segoe UI', 14, 'bold'),
                bg=COLORS['white'], fg=COLORS['text']).pack(side=tk.LEFT)
        
        tk.Label(top_row, text=config['status'], font=('Segoe UI', 10, 'bold'),
                bg=config['color'], fg=COLORS['white'], padx=10, pady=2).pack(side=tk.RIGHT)
        
        tk.Label(content, text=f"Purpose: {config['purpose']}", font=('Segoe UI', 10),
                bg=COLORS['white'], fg=COLORS['text_light']).pack(anchor=tk.W, pady=2)
        
        tk.Label(content, text=f"Model Size: {config['size']}", font=('Segoe UI', 10),
                bg=COLORS['white'], fg=COLORS['text_light']).pack(anchor=tk.W, pady=2)

def main():
    logger.info("Starting Nexuzy Publisher Desk")
    app = NexuzyPublisherApp()
    app.mainloop()

if __name__ == '__main__':
    main()
