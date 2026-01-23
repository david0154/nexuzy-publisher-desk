"""
Nexuzy Publisher Desk - Complete AI-Powered News Platform
"""

import os
import sys
import sqlite3
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
from tkinter import font as tkfont
from pathlib import Path
import logging
from datetime import datetime

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

try:
    from core.categories import get_all_categories, POPULAR_FEEDS
    CATEGORIES = get_all_categories()
except:
    CATEGORIES = [
        'General', 'Breaking News', 'Politics', 'Business', 'Technology', 
        'Science', 'Health', 'Sports', 'Entertainment', 'World News'
    ]

TRANSLATION_LANGUAGES = [
    'Spanish', 'French', 'German', 'Italian', 'Portuguese', 'Russian',
    'Hindi', 'Bengali', 'Tamil', 'Chinese (Simplified)', 'Japanese', 'Korean', 'Arabic'
]

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
        cursor.execute('CREATE TABLE IF NOT EXISTS wordpress_posts (id INTEGER PRIMARY KEY, draft_id INTEGER NOT NULL, wp_post_id INTEGER, wp_site_url TEXT, status TEXT DEFAULT "draft", published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (draft_id) REFERENCES ai_drafts(id))')
        
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
                        font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor='hand2', padx=20, pady=10, **kwargs)
        self.default_bg = bg_color
        self.bind('<Enter>', lambda e: self.config(bg=COLORS['hover']))
        self.bind('<Leave>', lambda e: self.config(bg=self.default_bg))

class WYSIWYGEditor(tk.Frame):
    """Modern WYSIWYG text editor"""
    
    def __init__(self, parent, ai_callback=None, **kwargs):
        super().__init__(parent, bg=COLORS['white'])
        self.ai_callback = ai_callback
        
        toolbar = tk.Frame(self, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
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
        
        tk.Frame(toolbar, width=2, bg=COLORS['border']).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # AI sentence improvement
        if self.ai_callback:
            tk.Button(toolbar, text="🤖 Improve Sentence", command=self.improve_selected,
                     bg=COLORS['success'], fg=COLORS['white'], relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)
        
        text_frame = tk.Frame(self, bg=COLORS['white'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text = scrolledtext.ScrolledText(text_frame, font=('Segoe UI', 11), 
                                              wrap=tk.WORD, undo=True, **kwargs)
        self.text.pack(fill=tk.BOTH, expand=True)
        
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
    
    def improve_selected(self):
        """Improve selected sentence with AI"""
        try:
            selected = self.text.get('sel.first', 'sel.last')
            if selected and self.ai_callback:
                improved = self.ai_callback(selected)
                if improved and improved != selected:
                    self.text.delete('sel.first', 'sel.last')
                    self.text.insert(tk.INSERT, improved)
        except:
            messagebox.showinfo("Info", "Select text to improve")
    
    def get(self, *args):
        return self.text.get(*args)
    
    def insert(self, *args):
        return self.text.insert(*args)
    
    def delete(self, *args):
        return self.text.delete(*args)

class NexuzyPublisherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nexuzy Publisher Desk")
        self.geometry("1400x800")
        self.configure(bg=COLORS['white'])
        
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
        
        # Auto cleanup on startup
        if self.draft_generator and self.current_workspace_id:
            self.draft_generator.cleanup_old_queue(self.current_workspace_id, 15)
    
    def _set_app_icon(self):
        try:
            icon_path = Path('resources/icon.ico')
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
                logger.info("[OK] Icon loaded")
        except Exception as e:
            logger.warning(f"Icon load failed: {e}")
    
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
            from core.ai_draft_generator import DraftGenerator
            self.draft_generator = DraftGenerator(self.db_path)
            self.models_status['draft_generator'] = 'Available' if self.draft_generator.llm else 'Template Mode'
            logger.info("[OK] Draft Generator")
        except:
            self.draft_generator = None
            self.models_status['draft_generator'] = 'Not Available'
        
        try:
            from core.translator import Translator
            self.translator = Translator(self.db_path)
            self.models_status['translator'] = 'Available' if self.translator.translator else 'Template Mode'
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
    
    def create_modern_ui(self):
        header = tk.Frame(self, bg=COLORS['dark'], height=70)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        
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
        ]
        
        tk.Label(sidebar, text="NAVIGATION", font=('Segoe UI', 10, 'bold'), bg=COLORS['darker'], fg=COLORS['text_light'], pady=20).pack(fill=tk.X, padx=15)
        
        for btn_text, btn_cmd, btn_color in nav_buttons:
            self.create_nav_button(sidebar, btn_text, btn_cmd, btn_color)
        
        self.content_frame = tk.Frame(main_container, bg=COLORS['white'])
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        statusbar = tk.Frame(self, bg=COLORS['dark'], height=35)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        statusbar.pack_propagate(False)
        
        self.status_label = tk.Label(statusbar, text="Ready", font=('Segoe UI', 9), bg=COLORS['dark'], fg=COLORS['light'], anchor=tk.W)
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
                logger.info(f"[OK] Selected: {self.current_workspace}")
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
            # IMPORTANT: Only count non-drafted items in queue
            cursor.execute('SELECT COUNT(*) FROM news_queue WHERE workspace_id = ? AND status NOT IN ("drafted", "archived")', (self.current_workspace_id,))
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
        
        tk.Label(self.content_frame, text="News Queue (Last 15 Days, Not Drafted)", font=('Segoe UI', 20, 'bold'), bg=COLORS['white']).pack(padx=30, pady=20, anchor=tk.W)
        
        btn_container = tk.Frame(self.content_frame, bg=COLORS['white'])
        btn_container.pack(padx=30, pady=10, anchor=tk.W)
        
        ModernButton(btn_container, "Fetch News", self.fetch_rss_news, 'primary').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_container, "🧹 Cleanup Old", self.cleanup_queue, 'warning').pack(side=tk.LEFT, padx=5)
        
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
            # CRITICAL: Hide drafted items from queue
            cursor.execute('''
                SELECT headline, source_domain, category, image_url
                FROM news_queue 
                WHERE workspace_id = ? 
                AND status NOT IN ('drafted', 'archived')
                ORDER BY fetched_at DESC 
                LIMIT 100
            ''', (self.current_workspace_id,))
            news_items = cursor.fetchall()
            conn.close()
            
            if not news_items:
                self.news_listbox.insert(tk.END, "No news. Click 'Fetch News'!")
            else:
                for headline, source, category, img in news_items:
                    img_tag = "📷" if img else "❌"
                    self.news_listbox.insert(tk.END, f"{img_tag} [{category}] {source}: {headline}")
        except Exception as e:
            self.news_listbox.insert(tk.END, f"Error: {e}")
    
    def fetch_rss_news(self):
        if not self.rss_manager:
            messagebox.showerror("Error", "RSS Manager required")
            return
        
        self.update_status("Fetching...", 'warning')
        
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
        self.update_status("Error fetching", 'danger')
        messagebox.showerror("Error", f"Failed:\n{error}")
    
    def cleanup_queue(self):
        """Cleanup items older than 15 days"""
        if not self.draft_generator:
            messagebox.showinfo("Info", "Cleanup not available")
            return
        
        if messagebox.askyesno("Confirm", "Archive news older than 15 days?"):
            count = self.draft_generator.cleanup_old_queue(self.current_workspace_id, 15)
            self.load_news_queue()
            messagebox.showinfo("Success", f"Archived {count} old items")
    
    def show_editor(self):
        self.clear_content()
        self.update_status("AI Editor", 'success')
        
        if not self.current_workspace_id:
            self._show_no_workspace_error()
            return
        
        tk.Label(self.content_frame, text="AI Editor - Real News Rewriting", font=('Segoe UI', 20, 'bold'), bg=COLORS['white']).pack(padx=30, pady=20, anchor=tk.W)
        
        main_panel = tk.Frame(self.content_frame, bg=COLORS['white'])
        main_panel.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        left_panel = tk.Frame(main_panel, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left_panel, text="📰 Available News", font=('Segoe UI', 14, 'bold'), bg=COLORS['light']).pack(padx=15, pady=10, anchor=tk.W)
        
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
        
        ModernButton(btn_frame, "🤖 AI Rewrite", self.generate_ai_draft_real, 'success').pack(fill=tk.X, pady=2)
        ModernButton(btn_frame, "🔄 Refresh", self.load_editor_news, 'primary').pack(fill=tk.X, pady=2)
        
        right_panel = tk.Frame(main_panel, bg=COLORS['light'], relief=tk.RAISED, borderwidth=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_panel, text="✍️ Article Editor", font=('Segoe UI', 14, 'bold'), bg=COLORS['light']).pack(padx=15, pady=10, anchor=tk.W)
        
        details_frame = tk.Frame(right_panel, bg=COLORS['white'])
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(details_frame, text="Title:", font=('Segoe UI', 10, 'bold'), bg=COLORS['white']).pack(anchor=tk.W, pady=2)
        self.draft_title = tk.Entry(details_frame, font=('Segoe UI', 11))
        self.draft_title.pack(fill=tk.X, pady=2)
        
        tk.Label(details_frame, text="Image URL:", font=('Segoe UI', 10, 'bold'), bg=COLORS['white']).pack(anchor=tk.W, pady=(10, 2))
        image_url_frame = tk.Frame(details_frame, bg=COLORS['white'])
        image_url_frame.pack(fill=tk.X, pady=2)
        self.draft_image_url = tk.Entry(image_url_frame, font=('Segoe UI', 10))
        self.draft_image_url.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if self.vision_ai:
            ModernButton(image_url_frame, "🔍 Check", self.check_image_watermark, 'danger').pack(side=tk.LEFT, padx=5)
        
        tk.Label(details_frame, text="Article Body:", font=('Segoe UI', 10, 'bold'), bg=COLORS['white']).pack(anchor=tk.W, pady=(10, 2))
        
        # AI sentence improvement callback
        ai_improve_callback = None
        if self.draft_generator and self.draft_generator.llm:
            ai_improve_callback = lambda text: self.draft_generator.improve_sentence(text)
        
        self.draft_body = WYSIWYGEditor(details_frame, ai_callback=ai_improve_callback, height=12)
        self.draft_body.pack(fill=tk.BOTH, expand=True, pady=2)
        
        save_frame = tk.Frame(right_panel, bg=COLORS['light'])
        save_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ModernButton(save_frame, "💾 Save", self.save_ai_draft, 'warning').pack(side=tk.LEFT, padx=2)
        
        if self.translator:
            ModernButton(save_frame, "🌐 Translate", self.translate_current_draft, 'primary').pack(side=tk.LEFT, padx=2)
        
        if self.wordpress_api:
            ModernButton(save_frame, "📤 Push to WP", self.publish_to_wordpress, 'success').pack(side=tk.LEFT, padx=2)
        
        ModernButton(save_frame, "🗑️ Clear", self.clear_draft, 'danger').pack(side=tk.LEFT, padx=2)
        
        self.load_editor_news()
    
    def load_editor_news(self):
        if not hasattr(self, 'editor_news_list'):
            return
        self.editor_news_list.delete(0, tk.END)
        self.news_items_data = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Only show non-drafted items
            cursor.execute('''
                SELECT id, headline, summary, source_url, source_domain, category, image_url
                FROM news_queue 
                WHERE workspace_id = ? 
                AND status NOT IN ('drafted', 'archived')
                ORDER BY fetched_at DESC 
                LIMIT 50
            ''', (self.current_workspace_id,))
            items = cursor.fetchall()
            conn.close()
            
            if not items:
                self.editor_news_list.insert(tk.END, "No news. Fetch from RSS first.")
            else:
                for news_id, headline, summary, url, source, category, img in items:
                    self.news_items_data.append({
                        'id': news_id, 
                        'headline': headline, 
                        'summary': summary or '', 
                        'url': url or '', 
                        'source': source or 'Unknown', 
                        'category': category or 'General', 
                        'image_url': img or ''
                    })
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
        
        if hasattr(self, 'draft_image_url'):
            self.draft_image_url.delete(0, tk.END)
            self.draft_image_url.insert(0, news['image_url'])
        
        if hasattr(self, 'draft_body'):
            self.draft_body.delete('1.0', tk.END)
            content = f"Headline: {news['headline']}\n\nSummary: {news['summary']}\n\nSource: {news['source']}\nCategory: {news['category']}\n\nClick 'AI Rewrite' to generate article..."
            self.draft_body.insert(tk.END, content)
    
    def check_image_watermark(self):
        image_url = self.draft_image_url.get().strip()
        if not image_url:
            messagebox.showwarning("Warning", "No image URL")
            return
        
        if not self.vision_ai:
            messagebox.showerror("Error", "Vision AI not available")
            return
        
        self.update_status("Checking watermark...", 'warning')
        
        def check_thread():
            try:
                import requests
                from PIL import Image
                from io import BytesIO
                
                response = requests.get(image_url, timeout=10)
                img = Image.open(BytesIO(response.content))
                
                temp_path = 'temp_image.jpg'
                img.save(temp_path)
                
                result = self.vision_ai.detect_watermark(temp_path)
                
                os.remove(temp_path)
                
                self.after(0, lambda: self._watermark_check_complete(result))
            except Exception as e:
                self.after(0, lambda: self._watermark_check_error(str(e)))
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def _watermark_check_complete(self, result):
        self.update_status("Watermark check complete", 'success')
        
        if result['watermark_detected']:
            msg = f"⚠️ WATERMARK DETECTED!\n\nConfidence: {result['confidence']}\n\n{result['status']}\n\nReplace this image."
            messagebox.showwarning("Watermark Detected", msg)
        else:
            messagebox.showinfo("Clear", f"✓ No watermark detected.\n\nConfidence: {result['confidence']}")
    
    def _watermark_check_error(self, error):
        self.update_status("Watermark check failed", 'danger')
        messagebox.showerror("Error", f"Failed:\n{error}")
    
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
        
        self.update_status("Generating real news article...", 'warning')
        
        def generate_thread():
            try:
                draft = self.draft_generator.generate_draft(news['id'])
                self.after(0, lambda: self._draft_generated(draft))
            except Exception as e:
                self.after(0, lambda: self._draft_error(str(e)))
        
        threading.Thread(target=generate_thread, daemon=True).start()
    
    def _draft_generated(self, draft):
        if not draft:
            messagebox.showerror("Error", "Failed to generate")
            return
        
        if hasattr(self, 'draft_title'):
            self.draft_title.delete(0, tk.END)
            self.draft_title.insert(0, draft.get('title', ''))
        
        if hasattr(self, 'draft_image_url'):
            self.draft_image_url.delete(0, tk.END)
            self.draft_image_url.insert(0, draft.get('image_url', ''))
        
        if hasattr(self, 'draft_body'):
            self.draft_body.delete('1.0', tk.END)
            self.draft_body.insert(tk.END, draft.get('body_draft', 'No content'))
        
        self.current_draft_id = draft.get('id')
        
        # Refresh news list to hide drafted item
        self.load_editor_news()
        
        self.update_status(f"Generated! {draft.get('word_count', 0)} words", 'success')
        messagebox.showinfo("Success", f"Real news article generated!\nWords: {draft.get('word_count', 0)}")
    
    def _draft_error(self, error):
        self.update_status("Generation error", 'danger')
        messagebox.showerror("Error", f"Failed:\n{error}")
    
    def translate_current_draft(self):
        if not hasattr(self, 'current_draft_id') or not self.current_draft_id:
            messagebox.showwarning("Warning", "Save draft first")
            return
        
        if not self.translator:
            messagebox.showerror("Error", "Translator not available")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Select Language")
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
        
        view_window = tk.Toplevel(self)
        view_window.title(f"Translation: {target_lang}")
        view_window.geometry("800x600")
        view_window.configure(bg=COLORS['white'])
        
        tk.Label(view_window, text=f"Translation: {target_lang}", font=('Segoe UI', 16, 'bold'), bg=COLORS['white']).pack(padx=20, pady=10)
        tk.Label(view_window, text=f"Title: {translation.get('title', '')}", font=('Segoe UI', 12), bg=COLORS['white']).pack(padx=20, pady=5)
        
        text_frame = tk.Frame(view_window, bg=COLORS['white'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        text_widget = scrolledtext.ScrolledText(text_frame, font=('Segoe UI', 10), wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, translation.get('body', ''))
        text_widget.config(state=tk.DISABLED)
        
        messagebox.showinfo("Success", f"Translated to {target_lang}!")
    
    def _translation_error(self, error):
        self.update_status("Translation error", 'danger')
        messagebox.showerror("Error", f"Failed:\n{error}")
    
    def publish_to_wordpress(self):
        if not hasattr(self, 'current_draft_id') or not self.current_draft_id:
            messagebox.showwarning("Warning", "Save draft first")
            return
        
        if not self.wordpress_api:
            messagebox.showerror("Error", "WordPress API not available")
            return
        
        if messagebox.askyesno("Confirm", "Publish to WordPress?"):
            self.update_status("Publishing...", 'warning')
            
            def publish_thread():
                try:
                    result = self.wordpress_api.publish_draft(self.current_draft_id, self.current_workspace_id)
                    self.after(0, lambda: self._publish_complete(result))
                except Exception as e:
                    self.after(0, lambda: self._publish_error(str(e)))
            
            threading.Thread(target=publish_thread, daemon=True).start()
    
    def _publish_complete(self, result):
        if result:
            self.update_status("Published!", 'success')
            messagebox.showinfo("Success", f"Published to WordPress!\n\nPost ID: {result['post_id']}\nURL: {result['url']}")
        else:
            messagebox.showerror("Error", "Failed to publish. Check credentials.")
    
    def _publish_error(self, error):
        self.update_status("Publish failed", 'danger')
        messagebox.showerror("Error", f"Failed:\n{error}")
    
    def save_ai_draft(self):
        # Draft is auto-saved during generation, just show confirmation
        if hasattr(self, 'current_draft_id') and self.current_draft_id:
            messagebox.showinfo("Info", f"Draft already saved (ID: {self.current_draft_id})")
        else:
            messagebox.showwarning("Warning", "Generate article first")
    
    def clear_draft(self):
        if hasattr(self, 'draft_title'):
            self.draft_title.delete(0, tk.END)
        if hasattr(self, 'draft_image_url'):
            self.draft_image_url.delete(0, tk.END)
        if hasattr(self, 'draft_body'):
            self.draft_body.delete('1.0', tk.END)
            self.draft_body.insert(tk.END, "Select news...")
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
        self.update_status("Translations", 'warning')
        if not self.current_workspace_id:
            self._show_no_workspace_error()
            return
        
        tk.Label(self.content_frame, text="Translation Manager", font=('Segoe UI', 20, 'bold'), bg=COLORS['white']).pack(padx=30, pady=20, anchor=tk.W)
        tk.Label(self.content_frame, text="Use the AI Editor to translate drafts after saving them.", font=('Segoe UI', 11), bg=COLORS['white'], fg=COLORS['text_light']).pack(padx=30, pady=10, anchor=tk.W)
    
    def show_wordpress_config(self):
        self.clear_content()
        self.update_status("WordPress", 'primary')
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
        
        if self.wordpress_api:
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
        
        self.update_status("Testing...", 'warning')
        
        def test_thread():
            try:
                result = self.wordpress_api.test_connection(url, username, password)
                self.after(0, lambda: self._test_complete(result))
            except Exception as e:
                self.after(0, lambda: self._test_error(str(e)))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _test_complete(self, result):
        if result:
            self.update_status("Connected!", 'success')
            messagebox.showinfo("Success", "✓ Connection successful!")
        else:
            messagebox.showerror("Failed", "✗ Connection failed!\n\nCheck credentials.")
    
    def _test_error(self, error):
        self.update_status("Test failed", 'danger')
        messagebox.showerror("Error", f"Test failed:\n{error}")
    
    def _show_no_workspace_error(self):
        tk.Label(self.content_frame, text="No Workspace Selected", font=('Segoe UI', 24, 'bold'), bg=COLORS['white'], fg=COLORS['danger']).pack(pady=50)
        tk.Label(self.content_frame, text="Create or select a workspace to continue.", font=('Segoe UI', 14), bg=COLORS['white'], fg=COLORS['text_light']).pack(pady=20)
        ModernButton(self.content_frame, "Create Workspace", self.new_workspace, 'success').pack(pady=20)

def main():
    logger.info("=" * 60)
    logger.info("Starting Nexuzy Publisher Desk")
    logger.info("=" * 60)
    app = NexuzyPublisherApp()
    app.mainloop()

if __name__ == '__main__':
    main()
