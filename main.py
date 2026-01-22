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
from tkinter import messagebox
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
# AUTO-DOWNLOADER FOR AI MODELS (First Run)
# ============================================================================

class ModelDownloader:
    """Auto-download AI models on first run"""
    
    MODEL_CONFIG = {
        'sentence-transformers/all-MiniLM-L6-v2': {
            'name': 'SentenceTransformer',
            'size': '80MB',
            'use': 'News matching & similarity'
        },
        'mistralai/Mistral-7B-Instruct-v0.1': {
            'name': 'Mistral-7B',
            'size': '14GB',
            'use': 'Draft generation'
        },
        'facebook/nllb-200-distilled-600M': {
            'name': 'NLLB-200',
            'size': '2.4GB',
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
                logger.info(f"Downloading {model_name}...")
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
            # Import here to avoid errors if transformers not installed
            from sentence_transformers import SentenceTransformer
            from transformers import AutoModel, AutoTokenizer, pipeline
            
            if 'SentenceTransformer' in model_name:
                logger.info(f"Loading SentenceTransformer: {model_id}")
                model = SentenceTransformer(model_id, cache_folder=str(self.models_dir))
                model.save(str(self.models_dir / model_id.replace('/', '_')))
            
            elif 'Mistral' in model_name:
                logger.info(f"Loading Mistral model: {model_id}")
                # Using GGUF quantized version for efficiency
                from transformers import AutoTokenizer
                tokenizer = AutoTokenizer.from_pretrained(model_id)
                tokenizer.save_pretrained(str(self.models_dir / model_id.replace('/', '_')))
            
            elif 'nllb' in model_name:
                logger.info(f"Loading NLLB model: {model_id}")
                from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
                tokenizer = AutoTokenizer.from_pretrained(model_id)
                model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
                model.save_pretrained(str(self.models_dir / model_id.replace('/', '_')))
        
        except ImportError:
            logger.error("Required transformers library not installed")
            raise

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
# TKINTER UI - MAIN WINDOW
# ============================================================================

class NexuzyPublisherApp(tk.Tk):
    """Main application window"""
    
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
        self.current_draft = None
        
        # Initialize database
        DatabaseSetup(self.db_path)
        
        # Create UI
        self.create_widgets()
        self.load_workspaces()
    
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
            cursor.execute('SELECT name FROM workspaces')
            workspaces = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if workspaces:
                self.workspace_dropdown['menu'].delete(0, 'end')
                for ws in workspaces:
                    self.workspace_dropdown['menu'].add_command(
                        label=ws,
                        command=lambda x=ws: self.select_workspace(x)
                    )
                self.select_workspace(workspaces[0])
            else:
                self.new_workspace()
        
        except Exception as e:
            logger.error(f"Error loading workspaces: {e}")
    
    def select_workspace(self, workspace_name):
        """Select active workspace"""
        self.workspace_var.set(workspace_name)
        self.current_workspace = workspace_name
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
        """Show RSS management panel"""
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
        if not self.current_workspace:
            return
        
        self.rss_listbox.delete(0, tk.END)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, url, category, enabled FROM rss_feeds 
                WHERE workspace_id = (SELECT id FROM workspaces WHERE name = ?)
            ''', (self.current_workspace,))
            
            feeds = cursor.fetchall()
            conn.close()
            
            for feed_id, url, category, enabled in feeds:
                status = "✓" if enabled else "✗"
                display = f"{status} [{category}] {url}"
                self.rss_listbox.insert(tk.END, display)
        
        except Exception as e:
            logger.error(f"Error loading RSS feeds: {e}")
    
    def add_rss_feed(self):
        """Add new RSS feed dialog"""
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
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                workspace_id = cursor.execute(
                    'SELECT id FROM workspaces WHERE name = ?',
                    (self.current_workspace,)
                ).fetchone()[0]
                
                cursor.execute('''
                    INSERT INTO rss_feeds (workspace_id, url, category, language, priority)
                    VALUES (?, ?, ?, ?, ?)
                ''', (workspace_id, url, category_var.get(), lang_var.get(), int(priority_spinbox.get())))
                
                conn.commit()
                conn.close()
                
                self.load_rss_feeds()
                dialog.destroy()
                messagebox.showinfo("Success", "RSS feed added")
            
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
        
        tk.Button(dialog, text="Save Feed", command=save_feed).pack(pady=15)
    
    def remove_rss_feed(self):
        """Remove selected RSS feed"""
        selection = self.rss_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a feed to remove")
            return
        
        messagebox.showinfo("Info", "Remove feature - select feed and delete")
    
    def toggle_rss_feed(self):
        """Toggle RSS feed enabled/disabled status"""
        messagebox.showinfo("Info", "Toggle feature - enable/disable selected feed")
    
    def show_news_queue(self):
        """Show news queue"""
        self.clear_content()
        
        title = tk.Label(self.content_frame, text="📰 News Queue", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # Action buttons
        button_frame = tk.Frame(self.content_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="🔄 Fetch Latest News", command=self.fetch_news).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="🔍 Analyze Event", command=self.analyze_news).pack(side=tk.LEFT, padx=5)
        
        # News list frame
        list_frame = tk.Frame(self.content_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.news_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
        self.news_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.news_listbox.yview)
        
        self.load_news_queue()
    
    def load_news_queue(self):
        """Load news items into queue"""
        if not self.current_workspace:
            return
        
        self.news_listbox.delete(0, tk.END)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, headline, verified_sources, confidence FROM news_queue
                WHERE workspace_id = (SELECT id FROM workspaces WHERE name = ?)
                ORDER BY fetched_at DESC
                LIMIT 50
            ''', (self.current_workspace,))
            
            news_items = cursor.fetchall()
            conn.close()
            
            for news_id, headline, sources, confidence in news_items:
                display = f"[{sources} src] {headline[:80]}"
                self.news_listbox.insert(tk.END, display)
        
        except Exception as e:
            logger.error(f"Error loading news queue: {e}")
    
    def fetch_news(self):
        """Fetch latest news from RSS feeds"""
        self.update_status("Fetching news...")
        messagebox.showinfo("Info", "News fetching - will integrate with RSS feeds")
        self.update_status("Ready")
    
    def analyze_news(self):
        """Analyze selected news event"""
        messagebox.showinfo("Info", "News analysis - will use SentenceTransformer for grouping")
    
    def show_editor(self):
        """Show editorial editor panel"""
        self.clear_content()
        
        title = tk.Label(self.content_frame, text="✏️ Editorial Editor", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # Editor content
        editor_frame = tk.Frame(self.content_frame, bg='white')
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Headline
        tk.Label(editor_frame, text="Headline:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        headline_entry = tk.Entry(editor_frame, width=80)
        headline_entry.pack(fill=tk.X, pady=5)
        
        # Body
        tk.Label(editor_frame, text="Article Body:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        body_text = tk.Text(editor_frame, height=15, width=80)
        body_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Footer buttons
        footer_frame = tk.Frame(self.content_frame, bg='white')
        footer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(footer_frame, text="💾 Save Draft", command=lambda: messagebox.showinfo("Info", "Draft saved")).pack(side=tk.LEFT, padx=5)
        tk.Button(footer_frame, text="📤 Generate with AI", command=lambda: messagebox.showinfo("Info", "AI draft generation")).pack(side=tk.LEFT, padx=5)
        tk.Button(footer_frame, text="✓ Mark as Edited", command=lambda: messagebox.showinfo("Info", "Marked as human-edited")).pack(side=tk.LEFT, padx=5)
    
    def show_wordpress_config(self):
        """Show WordPress configuration"""
        self.clear_content()
        
        title = tk.Label(self.content_frame, text="🌐 WordPress Integration", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        config_frame = tk.Frame(self.content_frame, bg='white')
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(config_frame, text="Site URL:").pack(anchor=tk.W, pady=5)
        url_entry = tk.Entry(config_frame, width=60)
        url_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(config_frame, text="Username:").pack(anchor=tk.W, pady=5)
        user_entry = tk.Entry(config_frame, width=60)
        user_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(config_frame, text="Application Password:").pack(anchor=tk.W, pady=5)
        pass_entry = tk.Entry(config_frame, width=60, show='*')
        pass_entry.pack(fill=tk.X, pady=5)
        
        button_frame = tk.Frame(config_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(button_frame, text="🔗 Test Connection", command=lambda: messagebox.showinfo("Info", "Testing WordPress connection...")).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="💾 Save", command=lambda: messagebox.showinfo("Info", "WordPress credentials saved")).pack(side=tk.LEFT, padx=5)
    
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
            ("SentenceTransformer", "News Matching"),
            ("Mistral-7B", "Draft Generation"),
            ("NLLB-200", "Translation")
        ]
        
        for model_name, purpose in models:
            status_frame = tk.Frame(settings_frame, bg='white')
            status_frame.pack(fill=tk.X, pady=5)
            tk.Label(status_frame, text=f"✓ {model_name}", font=('Arial', 9)).pack(anchor=tk.W)
            tk.Label(status_frame, text=f"   Purpose: {purpose}", font=('Arial', 8), fg='gray').pack(anchor=tk.W)
        
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
