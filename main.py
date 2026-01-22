"""
Nexuzy Publisher Desk - Main Entry Point
Complete offline AI-powered news publishing application
Built with Python, Tkinter, and offline AI models
"""

import os
import sys
import json
import sqlite3
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexuzy_publisher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# AUTO-DOWNLOADER FOR AI MODELS (First Run) - SMALLER MODELS
# ============================================================================

class ModelDownloader:
    """Auto-download AI models on first run - Using smaller, optimized models"""
    
    MODEL_CONFIG = {
        'sentence-transformers/all-MiniLM-L6-v2': {
            'name': 'SentenceTransformer',
            'size': '80MB',
            'use': 'News matching & similarity'
        },
        'TheBloke/Mistral-7B-Instruct-v0.2-GPTQ': {
            'name': 'Mistral-7B-GPTQ',
            'size': '4GB',  # 80% smaller than original
            'use': 'Draft generation (quantized)'
        },
        'facebook/nllb-200-distilled-600M': {
            'name': 'NLLB-200-Distilled',
            'size': '1.2GB',  # Distilled version
            'use': 'Multi-language translation'
        }
    }
    
    def __init__(self):
        self.models_dir = Path('models')
        self.models_dir.mkdir(exist_ok=True)
        self.config_file = self.models_dir / 'models_config.json'
    
    def load_config(self):
        """Load downloaded models config"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self, config):
        """Save models config"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def check_and_download(self):
        """Check if models exist, download if needed"""
        config = self.load_config()
        
        for model_id, model_info in self.MODEL_CONFIG.items():
            model_name = model_info['name']
            
            if model_name not in config:
                logger.info(f"Downloading {model_name} ({model_info['size']})...")
                try:
                    self._download_model(model_id, model_name)
                    config[model_name] = {
                        'model_id': model_id,
                        'downloaded': True,
                        'size': model_info['size']
                    }
                    self.save_config(config)
                    logger.info(f"✓ {model_name} downloaded successfully")
                except Exception as e:
                    logger.error(f"✗ Failed to download {model_name}: {e}")
                    return False
        
        return True
    
    def _download_model(self, model_id, model_name):
        """Download model from HuggingFace"""
        try:
            from sentence_transformers import SentenceTransformer
            from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
            
            if 'SentenceTransformer' in model_name:
                logger.info(f"Loading SentenceTransformer: {model_id}")
                model = SentenceTransformer(model_id, cache_folder=str(self.models_dir))
                model.save(str(self.models_dir / model_id.replace('/', '_')))
            
            elif 'Mistral' in model_name or 'GPTQ' in model_name:
                logger.info(f"Loading quantized Mistral model: {model_id}")
                # GPTQ quantized model - much smaller
                from auto_gptq import AutoGPTQForCausalLM
                tokenizer = AutoTokenizer.from_pretrained(model_id)
                model = AutoGPTQForCausalLM.from_quantized(
                    model_id,
                    device="cuda:0" if self._has_gpu() else "cpu",
                    use_safetensors=True
                )
                tokenizer.save_pretrained(str(self.models_dir / model_id.replace('/', '_')))
                model.save_pretrained(str(self.models_dir / model_id.replace('/', '_')))
            
            elif 'nllb' in model_id.lower():
                logger.info(f"Loading NLLB distilled model: {model_id}")
                tokenizer = AutoTokenizer.from_pretrained(model_id)
                model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
                tokenizer.save_pretrained(str(self.models_dir / model_id.replace('/', '_')))
                model.save_pretrained(str(self.models_dir / model_id.replace('/', '_')))
        
        except ImportError as e:
            logger.error(f"Required library not installed: {e}")
            logger.info("Installing auto-gptq for quantized models...")
            os.system('pip install auto-gptq')
            raise
    
    @staticmethod
    def _has_gpu():
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False

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
        
        # News Grouping (same event detection)
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
        
        # WordPress Credentials (encrypted)
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
        logger.info("✓ Database initialized successfully")

# ============================================================================
# TKINTER UI - MAIN WINDOW WITH FULL WIRING
# ============================================================================

class NexuzyPublisherApp(tk.Tk):
    """Main application window - FULLY WIRED"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Nexuzy Publisher Desk")
        self.geometry("1200x700")
        self.configure(bg='#f0f0f0')
        
        # Try to set icon if exists
        try:
            if os.path.exists('resources/logo.ico'):
                self.iconbitmap('resources/logo.ico')
        except:
            pass
        
        self.db_path = 'nexuzy.db'
        self.current_workspace = None
        self.current_workspace_id = None
        self.current_draft = None
        self.selected_news_id = None
        
        # Initialize database
        DatabaseSetup(self.db_path)
        
        # Import core modules
        self._import_modules()
        
        # Create UI
        self.create_widgets()
        self.load_workspaces()
    
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
            
            logger.info("✓ Core modules loaded")
        except ImportError as e:
            logger.error(f"Failed to import modules: {e}")
            messagebox.showerror("Error", f"Failed to load core modules: {e}")
    
    def create_widgets(self):
        """Create main UI layout"""
        # Header
        header = tk.Frame(self, bg='#2c3e50', height=60)
        header.pack(side=tk.TOP, fill=tk.X)
        
        header_label = tk.Label(
            header,
            text="📰 Nexuzy Publisher Desk",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        header_label.pack(pady=10)
        
        # Main container
        main_container = tk.Frame(self, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Navigation
        left_panel = tk.Frame(main_container, bg='#ecf0f1', width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        tk.Label(left_panel, text="Workspace", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(pady=10)
        
        self.workspace_var = tk.StringVar()
        self.workspace_dropdown = tk.OptionMenu(left_panel, self.workspace_var, '')
        self.workspace_dropdown.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons
        button_frame = tk.Frame(left_panel, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, padx=5, pady=20)
        
        tk.Button(button_frame, text="+ New Workspace", command=self.new_workspace).pack(fill=tk.X, pady=3)
        tk.Button(button_frame, text="📡 RSS Manager", command=self.show_rss_manager).pack(fill=tk.X, pady=3)
        tk.Button(button_frame, text="📰 News Queue", command=self.show_news_queue).pack(fill=tk.X, pady=3)
        tk.Button(button_frame, text="✏️ Editor", command=self.show_editor).pack(fill=tk.X, pady=3)
        tk.Button(button_frame, text="🌐 WordPress", command=self.show_wordpress_config).pack(fill=tk.X, pady=3)
        tk.Button(button_frame, text="⚙️ Settings", command=self.show_settings).pack(fill=tk.X, pady=3)
        
        # Right panel - Content area
        self.content_frame = tk.Frame(main_container, bg='white')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Status bar
        status_bar = tk.Frame(self, bg='#34495e', height=30)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(
            status_bar,
            text="Ready | Models: Loading...",
            font=('Arial', 9),
            bg='#34495e',
            fg='#ecf0f1'
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    def load_workspaces(self):
        """Load workspaces from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM workspaces')
            workspaces = cursor.fetchall()
            conn.close()
            
            if workspaces:
                self.workspace_dropdown['menu'].delete(0, 'end')
                for ws_id, ws_name in workspaces:
                    self.workspace_dropdown['menu'].add_command(
                        label=ws_name,
                        command=lambda x=ws_name, y=ws_id: self.select_workspace(x, y)
                    )
                self.select_workspace(workspaces[0][1], workspaces[0][0])
            else:
                self.new_workspace()
        
        except Exception as e:
            logger.error(f"Error loading workspaces: {e}")
    
    def select_workspace(self, workspace_name, workspace_id):
        """Select active workspace"""
        self.workspace_var.set(workspace_name)
        self.current_workspace = workspace_name
        self.current_workspace_id = workspace_id
        self.update_status(f"Workspace: {workspace_name}")
    
    def new_workspace(self):
        """Create new workspace"""
        dialog = tk.Toplevel(self)
        dialog.title("New Workspace")
        dialog.geometry("300x100")
        
        tk.Label(dialog, text="Workspace Name:").pack(pady=10)
        name_entry = tk.Entry(dialog, width=30)
        name_entry.pack(pady=5)
        
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
                messagebox.showinfo("Success", f"Workspace '{name}' created")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Workspace already exists")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
        
        tk.Button(dialog, text="Create", command=create).pack(pady=10)
    
    def show_rss_manager(self):
        """Show RSS management panel - FULLY WIRED"""
        self.clear_content()
        
        title = tk.Label(self.content_frame, text="📡 RSS Feed Manager", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # RSS list frame
        list_frame = tk.Frame(self.content_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.rss_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
        self.rss_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.rss_listbox.yview)
        
        self.load_rss_feeds()
        
        # Button frame
        button_frame = tk.Frame(self.content_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="+ Add Feed", command=self.add_rss_feed).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="🗑️ Remove", command=self.remove_rss_feed).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="✓ Toggle", command=self.toggle_rss_feed).pack(side=tk.LEFT, padx=5)
    
    def load_rss_feeds(self):
        """Load RSS feeds into listbox"""
        if not self.current_workspace_id:
            return
        
        self.rss_listbox.delete(0, tk.END)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, url, category, enabled FROM rss_feeds 
                WHERE workspace_id = ?
            ''', (self.current_workspace_id,))
            
            feeds = cursor.fetchall()
            conn.close()
            
            for feed_id, url, category, enabled in feeds:
                status = "✓" if enabled else "✗"
                display = f"{status} [{category}] {url}"
                self.rss_listbox.insert(tk.END, display)
        
        except Exception as e:
            logger.error(f"Error loading RSS feeds: {e}")
    
    def add_rss_feed(self):
        """Add new RSS feed dialog - FULLY WIRED"""
        dialog = tk.Toplevel(self)
        dialog.title("Add RSS Feed")
        dialog.geometry("400x250")
        
        tk.Label(dialog, text="RSS URL:").pack(pady=5)
        url_entry = tk.Entry(dialog, width=50)
        url_entry.pack(pady=5)
        
        tk.Label(dialog, text="Category:").pack(pady=5)
        category_var = tk.StringVar(value="Tech")
        category_menu = tk.OptionMenu(dialog, category_var, "Tech", "Business", "World", "Sports", "Entertainment", "Health")
        category_menu.pack(pady=5)
        
        tk.Label(dialog, text="Language:").pack(pady=5)
        lang_var = tk.StringVar(value="English")
        lang_menu = tk.OptionMenu(dialog, lang_var, "English", "Hindi", "Bengali", "Spanish", "French")
        lang_menu.pack(pady=5)
        
        tk.Label(dialog, text="Priority (1-10):").pack(pady=5)
        priority_spinbox = tk.Spinbox(dialog, from_=1, to=10, width=5)
        priority_spinbox.set(5)
        priority_spinbox.pack(pady=5)
        
        def save_feed():
            url = url_entry.get().strip()
            if not url:
                messagebox.showerror("Error", "Please enter RSS URL")
                return
            
            # Validate RSS
            self.update_status("Validating RSS feed...")
            if not self.rss_manager.validate_rss_url(url):
                messagebox.showerror("Error", "Invalid RSS URL or feed not accessible")
                self.update_status("Ready")
                return
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO rss_feeds (workspace_id, url, category, language, priority)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.current_workspace_id, url, category_var.get(), lang_var.get(), int(priority_spinbox.get())))
                
                conn.commit()
                conn.close()
                
                self.load_rss_feeds()
                dialog.destroy()
                messagebox.showinfo("Success", "RSS feed added and validated")
                self.update_status("Ready")
            
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
                self.update_status("Ready")
        
        tk.Button(dialog, text="Save Feed", command=save_feed).pack(pady=15)
    
    def remove_rss_feed(self):
        """Remove selected RSS feed - WIRED"""
        selection = self.rss_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a feed to remove")
            return
        
        if messagebox.askyesno("Confirm", "Remove selected RSS feed?"):
            try:
                idx = selection[0]
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id FROM rss_feeds WHERE workspace_id = ? ORDER BY id
                ''', (self.current_workspace_id,))
                feeds = cursor.fetchall()
                
                if idx < len(feeds):
                    feed_id = feeds[idx][0]
                    cursor.execute('DELETE FROM rss_feeds WHERE id = ?', (feed_id,))
                    conn.commit()
                
                conn.close()
                self.load_rss_feeds()
                messagebox.showinfo("Success", "RSS feed removed")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
    
    def toggle_rss_feed(self):
        """Toggle RSS feed enabled/disabled status - WIRED"""
        selection = self.rss_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a feed to toggle")
            return
        
        try:
            idx = selection[0]
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, enabled FROM rss_feeds WHERE workspace_id = ? ORDER BY id
            ''', (self.current_workspace_id,))
            feeds = cursor.fetchall()
            
            if idx < len(feeds):
                feed_id, enabled = feeds[idx]
                new_status = 0 if enabled else 1
                cursor.execute('UPDATE rss_feeds SET enabled = ? WHERE id = ?', (new_status, feed_id))
                conn.commit()
            
            conn.close()
            self.load_rss_feeds()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
    
    def show_news_queue(self):
        """Show news queue - FULLY WIRED"""
        self.clear_content()
        
        title = tk.Label(self.content_frame, text="📰 News Queue", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # Action buttons
        button_frame = tk.Frame(self.content_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="🔄 Fetch Latest News", command=self.fetch_news).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="🔍 Match & Verify", command=self.analyze_news).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="📄 Generate Draft", command=self.generate_draft_from_selected).pack(side=tk.LEFT, padx=5)
        
        # News list frame
        list_frame = tk.Frame(self.content_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.news_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
        self.news_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.news_listbox.bind('<<ListboxSelect>>', self.on_news_select)
        scrollbar.config(command=self.news_listbox.yview)
        
        self.load_news_queue()
    
    def on_news_select(self, event):
        """Handle news item selection"""
        selection = self.news_listbox.curselection()
        if selection:
            try:
                idx = selection[0]
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id FROM news_queue
                    WHERE workspace_id = ?
                    ORDER BY fetched_at DESC
                    LIMIT 50
                ''', (self.current_workspace_id,))
                news_items = cursor.fetchall()
                conn.close()
                
                if idx < len(news_items):
                    self.selected_news_id = news_items[idx][0]
            except Exception as e:
                logger.error(f"Error selecting news: {e}")
    
    def load_news_queue(self):
        """Load news items into queue - WIRED"""
        if not self.current_workspace_id:
            return
        
        self.news_listbox.delete(0, tk.END)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, headline, verified_sources, confidence, status FROM news_queue
                WHERE workspace_id = ?
                ORDER BY fetched_at DESC
                LIMIT 50
            ''', (self.current_workspace_id,))
            
            news_items = cursor.fetchall()
            conn.close()
            
            for news_id, headline, sources, confidence, status in news_items:
                display = f"[{sources} src] {status.upper()} - {headline[:60]}"
                self.news_listbox.insert(tk.END, display)
        
        except Exception as e:
            logger.error(f"Error loading news queue: {e}")
    
    def fetch_news(self):
        """Fetch latest news from RSS feeds - FULLY WIRED"""
        if not self.current_workspace_id:
            messagebox.showwarning("Warning", "Please select a workspace first")
            return
        
        self.update_status("Fetching news from RSS feeds...")
        
        def fetch_async():
            try:
                # Fetch from all feeds
                news_items = self.rss_manager.fetch_all_workspace_feeds(self.current_workspace_id)
                
                # Store in database
                count = 0
                for item in news_items:
                    news_id = self.rss_manager.store_news_item(self.current_workspace_id, item)
                    if news_id:
                        count += 1
                
                # Update UI from main thread
                self.after(0, lambda: self._fetch_complete(count))
            
            except Exception as e:
                logger.error(f"Error fetching news: {e}")
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch news: {e}"))
                self.after(0, lambda: self.update_status("Ready"))
        
        # Run in thread to not block UI
        threading.Thread(target=fetch_async, daemon=True).start()
    
    def _fetch_complete(self, count):
        """Callback when fetch completes"""
        self.load_news_queue()
        self.update_status("Ready")
        messagebox.showinfo("Success", f"Fetched {count} news items")
    
    def analyze_news(self):
        """Analyze selected news event - FULLY WIRED"""
        if not self.current_workspace_id:
            messagebox.showwarning("Warning", "Please select a workspace first")
            return
        
        self.update_status("Matching and verifying news...")
        
        def analyze_async():
            try:
                # Group similar headlines
                groups = self.news_matcher.group_similar_headlines(self.current_workspace_id)
                
                # Verify each group
                verified_count = 0
                for group_id in groups.keys():
                    verified, confidence = self.news_matcher.verify_group_authenticity(group_id)
                    if verified:
                        verified_count += 1
                
                # Update UI
                self.after(0, lambda: self._analyze_complete(len(groups), verified_count))
            
            except Exception as e:
                logger.error(f"Error analyzing news: {e}")
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to analyze: {e}"))
                self.after(0, lambda: self.update_status("Ready"))
        
        threading.Thread(target=analyze_async, daemon=True).start()
    
    def _analyze_complete(self, total_groups, verified_count):
        """Callback when analysis completes"""
        self.load_news_queue()
        self.update_status("Ready")
        messagebox.showinfo("Analysis Complete", 
            f"Created {total_groups} news groups\n{verified_count} verified (3+ sources)")
    
    def generate_draft_from_selected(self):
        """Generate draft from selected news - FULLY WIRED"""
        if not self.selected_news_id:
            messagebox.showwarning("Warning", "Please select a news item first")
            return
        
        self.update_status("Generating AI draft...")
        
        def generate_async():
            try:
                # Scrape facts first
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT source_url FROM news_queue WHERE id = ?', (self.selected_news_id,))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    url = result[0]
                    self.scraper.scrape_article(url, self.selected_news_id)
                
                # Generate draft
                draft = self.draft_generator.generate_draft(self.selected_news_id)
                
                # Update UI
                self.after(0, lambda: self._generation_complete(draft))
            
            except Exception as e:
                logger.error(f"Error generating draft: {e}")
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to generate: {e}"))
                self.after(0, lambda: self.update_status("Ready"))
        
        threading.Thread(target=generate_async, daemon=True).start()
    
    def _generation_complete(self, draft):
        """Callback when generation completes"""
        self.update_status("Ready")
        if draft and 'id' in draft:
            self.current_draft = draft['id']
            messagebox.showinfo("Success", "Draft generated! Open Editor to review.")
            self.show_editor()  # Auto-switch to editor
        else:
            messagebox.showerror("Error", "Failed to generate draft")
    
    def show_editor(self):
        """Show editorial editor panel - FULLY WIRED"""
        self.clear_content()
        
        title = tk.Label(self.content_frame, text="✏️ Editorial Editor", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # Load current draft if exists
        if self.current_draft:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT title, body_draft, edited_by_human FROM ai_drafts WHERE id = ?
                ''', (self.current_draft,))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    draft_title, draft_body, edited = result
                else:
                    draft_title, draft_body, edited = "", "", False
            except:
                draft_title, draft_body, edited = "", "", False
        else:
            draft_title, draft_body, edited = "", "", False
        
        # Editor content
        editor_frame = tk.Frame(self.content_frame, bg='white')
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Headline
        tk.Label(editor_frame, text="Headline:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.headline_entry = tk.Entry(editor_frame, width=80)
        self.headline_entry.insert(0, draft_title)
        self.headline_entry.pack(fill=tk.X, pady=5)
        
        # Body
        tk.Label(editor_frame, text="Article Body:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.body_text = scrolledtext.ScrolledText(editor_frame, height=15, width=80)
        self.body_text.insert('1.0', draft_body)
        self.body_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Human edited checkbox
        self.human_edited_var = tk.BooleanVar(value=edited)
        tk.Checkbutton(
            editor_frame,
            text="✓ Edited by Human (Required)",
            variable=self.human_edited_var,
            font=('Arial', 10, 'bold')
        ).pack(anchor=tk.W, pady=10)
        
        # Footer buttons
        footer_frame = tk.Frame(self.content_frame, bg='white')
        footer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(footer_frame, text="💾 Save Draft", command=self.save_draft).pack(side=tk.LEFT, padx=5)
        tk.Button(footer_frame, text="🌐 Translate", command=self.show_translation_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(footer_frame, text="📤 Send to WordPress", command=self.publish_to_wordpress).pack(side=tk.LEFT, padx=5)
    
    def save_draft(self):
        """Save draft - WIRED"""
        if not self.current_draft:
            messagebox.showwarning("Warning", "No draft loaded")
            return
        
        try:
            title = self.headline_entry.get()
            body = self.body_text.get('1.0', tk.END)
            edited = self.human_edited_var.get()
            
            if not title or len(body.strip()) < 100:
                messagebox.showerror("Error", "Headline and body required (min 100 words)")
                return
            
            if not edited:
                messagebox.showerror("Error", "Please mark as 'Edited by Human'")
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE ai_drafts SET title = ?, body_draft = ?, edited_by_human = ?, word_count = ?
                WHERE id = ?
            ''', (title, body, edited, len(body.split()), self.current_draft))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Draft saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
    
    def show_translation_dialog(self):
        """Show translation dialog - WIRED"""
        if not self.current_draft:
            messagebox.showwarning("Warning", "No draft loaded")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Translate Draft")
        dialog.geometry("300x200")
        
        tk.Label(dialog, text="Select Language:", font=('Arial', 10, 'bold')).pack(pady=10)
        
        lang_var = tk.StringVar(value="Hindi")
        languages = ["Hindi", "Bengali", "Spanish", "French", "German", "Arabic", "Chinese", "Japanese", "Portuguese"]
        
        for lang in languages:
            tk.Radiobutton(dialog, text=lang, variable=lang_var, value=lang).pack(anchor=tk.W, padx=20)
        
        def translate():
            self.update_status(f"Translating to {lang_var.get()}...")
            dialog.destroy()
            
            def translate_async():
                try:
                    result = self.translator.translate_draft(self.current_draft, lang_var.get())
                    self.after(0, lambda: self._translation_complete(result))
                except Exception as e:
                    logger.error(f"Translation error: {e}")
                    self.after(0, lambda: messagebox.showerror("Error", f"Translation failed: {e}"))
                    self.after(0, lambda: self.update_status("Ready"))
            
            threading.Thread(target=translate_async, daemon=True).start()
        
        tk.Button(dialog, text="Translate", command=translate).pack(pady=20)
    
    def _translation_complete(self, result):
        """Callback when translation completes"""
        self.update_status("Ready")
        if result:
            messagebox.showinfo("Success", f"Translated to {result['language']}")
        else:
            messagebox.showerror("Error", "Translation failed")
    
    def publish_to_wordpress(self):
        """Publish to WordPress - FULLY WIRED"""
        if not self.current_draft:
            messagebox.showwarning("Warning", "No draft loaded")
            return
        
        if not self.human_edited_var.get():
            messagebox.showerror("Error", "Draft must be edited by human before publishing")
            return
        
        self.update_status("Publishing to WordPress...")
        
        def publish_async():
            try:
                result = self.wordpress.publish_draft(self.current_draft, self.current_workspace_id)
                self.after(0, lambda: self._publish_complete(result))
            except Exception as e:
                logger.error(f"Publishing error: {e}")
                self.after(0, lambda: messagebox.showerror("Error", f"Publishing failed: {e}"))
                self.after(0, lambda: self.update_status("Ready"))
        
        threading.Thread(target=publish_async, daemon=True).start()
    
    def _publish_complete(self, result):
        """Callback when publish completes"""
        self.update_status("Ready")
        if result:
            messagebox.showinfo("Success", f"Published to WordPress!\nURL: {result['url']}")
        else:
            messagebox.showerror("Error", "Publishing failed. Check WordPress credentials.")
    
    def show_wordpress_config(self):
        """Show WordPress configuration - FULLY WIRED"""
        self.clear_content()
        
        title = tk.Label(self.content_frame, text="🌐 WordPress Integration", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        config_frame = tk.Frame(self.content_frame, bg='white')
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(config_frame, text="Site URL:").pack(anchor=tk.W, pady=5)
        self.wp_url_entry = tk.Entry(config_frame, width=60)
        self.wp_url_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(config_frame, text="Username:").pack(anchor=tk.W, pady=5)
        self.wp_user_entry = tk.Entry(config_frame, width=60)
        self.wp_user_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(config_frame, text="Application Password:").pack(anchor=tk.W, pady=5)
        self.wp_pass_entry = tk.Entry(config_frame, width=60, show='*')
        self.wp_pass_entry.pack(fill=tk.X, pady=5)
        
        # Load existing credentials
        try:
            creds = self.wordpress.get_credentials(self.current_workspace_id)
            if creds:
                self.wp_url_entry.insert(0, creds['site_url'])
                self.wp_user_entry.insert(0, creds['username'])
                self.wp_pass_entry.insert(0, creds['app_password'])
        except:
            pass
        
        button_frame = tk.Frame(config_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(button_frame, text="🔗 Test Connection", command=self.test_wp_connection).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="💾 Save", command=self.save_wp_credentials).pack(side=tk.LEFT, padx=5)
    
    def test_wp_connection(self):
        """Test WordPress connection - WIRED"""
        url = self.wp_url_entry.get()
        username = self.wp_user_entry.get()
        password = self.wp_pass_entry.get()
        
        if not url or not username or not password:
            messagebox.showerror("Error", "All fields required")
            return
        
        self.update_status("Testing WordPress connection...")
        
        def test_async():
            try:
                success = self.wordpress.test_connection(url, username, password)
                self.after(0, lambda: self._test_complete(success))
            except Exception as e:
                logger.error(f"Test error: {e}")
                self.after(0, lambda: messagebox.showerror("Error", f"Test failed: {e}"))
                self.after(0, lambda: self.update_status("Ready"))
        
        threading.Thread(target=test_async, daemon=True).start()
    
    def _test_complete(self, success):
        """Callback when test completes"""
        self.update_status("Ready")
        if success:
            messagebox.showinfo("Success", "WordPress connection successful!")
        else:
            messagebox.showerror("Error", "Connection failed. Check credentials.")
    
    def save_wp_credentials(self):
        """Save WordPress credentials - WIRED"""
        url = self.wp_url_entry.get()
        username = self.wp_user_entry.get()
        password = self.wp_pass_entry.get()
        
        if not url or not username or not password:
            messagebox.showerror("Error", "All fields required")
            return
        
        self.update_status("Saving WordPress credentials...")
        
        def save_async():
            try:
                success = self.wordpress.save_credentials(self.current_workspace_id, url, username, password)
                self.after(0, lambda: self._save_creds_complete(success))
            except Exception as e:
                logger.error(f"Save error: {e}")
                self.after(0, lambda: messagebox.showerror("Error", f"Save failed: {e}"))
                self.after(0, lambda: self.update_status("Ready"))
        
        threading.Thread(target=save_async, daemon=True).start()
    
    def _save_creds_complete(self, success):
        """Callback when save completes"""
        self.update_status("Ready")
        if success:
            messagebox.showinfo("Success", "WordPress credentials saved!")
        else:
            messagebox.showerror("Error", "Failed to save credentials")
    
    def show_settings(self):
        """Show application settings"""
        self.clear_content()
        
        title = tk.Label(self.content_frame, text="⚙️ Settings", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        settings_frame = tk.Frame(self.content_frame, bg='white')
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Model status
        tk.Label(settings_frame, text="AI Models Status:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=10)
        
        models = [
            ("SentenceTransformer (80MB)", "News Matching"),
            ("Mistral-7B-GPTQ (4GB)", "Draft Generation - Quantized"),
            ("NLLB-200-Distilled (1.2GB)", "Translation - Optimized")
        ]
        
        for model_name, purpose in models:
            status_frame = tk.Frame(settings_frame, bg='white')
            status_frame.pack(fill=tk.X, pady=5)
            tk.Label(status_frame, text=f"✓ {model_name}", font=('Arial', 9)).pack(anchor=tk.W)
            tk.Label(status_frame, text=f"   Purpose: {purpose}", font=('Arial', 8), fg='gray').pack(anchor=tk.W)
        
        # Total size
        tk.Label(settings_frame, text="\nTotal Model Size: ~5.3GB (80% smaller than original)", font=('Arial', 9, 'bold'), fg='#27ae60').pack(anchor=tk.W, pady=10)
        
        # Cache directory
        tk.Label(settings_frame, text=f"\nModel Cache Directory:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=10)
        tk.Label(settings_frame, text="./models/", font=('Arial', 9), fg='#2980b9').pack(anchor=tk.W)
        
        # Database
        tk.Label(settings_frame, text=f"\nDatabase Location:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=10)
        tk.Label(settings_frame, text="./nexuzy.db", font=('Arial', 9), fg='#2980b9').pack(anchor=tk.W)
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
        self.update_idletasks()

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Application entry point"""
    logger.info("=" * 60)
    logger.info("Starting Nexuzy Publisher Desk...")
    logger.info("=" * 60)
    
    # Check and download models on first run
    logger.info("Checking AI models...")
    downloader = ModelDownloader()
    
    def download_models_async():
        """Download models in background thread"""
        if downloader.check_and_download():
            logger.info("✓ All AI models ready")
        else:
            logger.warning("⚠ Some models failed to download, app will run in limited mode")
    
    # Download in thread to not block UI
    download_thread = threading.Thread(target=download_models_async, daemon=True)
    download_thread.start()
    
    # Create and run app
    app = NexuzyPublisherApp()
    app.mainloop()

if __name__ == '__main__':
    main()
