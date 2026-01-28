"""
fix_main_py.py - Automatic Research Writer UI Integration
Run once: python fix_main_py.py
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create backup of original file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def read_file(filepath):
    """Read file content"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    """Write content to file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def add_research_writer_import(content):
    """Add ResearchWriter import to _import_modules"""
    
    # Find the translator import block
    pattern = r"(try:\s+from core\.translator import Translator.*?self\.models_status\['translator'\] = 'Not Available')"
    
    import_code = """
        
        try:
            from core.research_writer import ResearchWriter
            self.research_writer = ResearchWriter(self.db_path)
            self.models_status['research_writer'] = 'Available'
            logger.info("[OK] Research Writer")
        except Exception as e:
            logger.error(f"Research Writer: {e}")
            self.research_writer = None
            self.models_status['research_writer'] = 'Not Available'"""
    
    # Insert after translator block
    if "from core.research_writer import ResearchWriter" not in content:
        content = re.sub(
            pattern,
            r"\1" + import_code,
            content,
            flags=re.DOTALL
        )
        print("✅ Added ResearchWriter import")
    else:
        print("⏭️  ResearchWriter import already exists")
    
    return content

def add_nav_button(content):
    """Add Research Writer navigation button"""
    
    pattern = r'(nav_buttons = \[\s+\("📊 Dashboard".*?\("📰 News Queue"[^)]+\),)'
    
    nav_addition = '\n            ("🔬 Research Writer", self.show_research_writer, \'success\'),'
    
    if '"🔬 Research Writer"' not in content:
        content = re.sub(
            pattern,
            r'\1' + nav_addition,
            content,
            flags=re.DOTALL
        )
        print("✅ Added Research Writer navigation button")
    else:
        print("⏭️  Navigation button already exists")
    
    return content

def add_model_config(content):
    """Add research_writer to MODEL_CONFIGS"""
    
    pattern = r"(MODEL_CONFIGS = \{[^}]+)'vision_ai': \{[^}]+\}"
    
    config_addition = """,
    'research_writer': {
        'display_name': 'Research Writer',
        'size': 'Web-based',
        'purpose': 'AI Research & Article Generation',
        'color': COLORS['success'],
        'module': 'core.research_writer',
        'class': 'ResearchWriter'
    }"""
    
    if "'research_writer':" not in content:
        content = re.sub(
            pattern,
            r"\1'vision_ai': {" + "[VISION_AI_CONFIG]" + "}" + config_addition,
            content
        )
        # Restore vision_ai config
        vision_pattern = r"'vision_ai': \{[^}]+\}"
        vision_match = re.search(vision_pattern, content.split("'research_writer':")[0])
        if vision_match:
            content = content.replace("[VISION_AI_CONFIG]", vision_match.group(0).replace("'vision_ai': {", "").replace("}", ""))
        print("✅ Added research_writer to MODEL_CONFIGS")
    else:
        print("⏭️  MODEL_CONFIGS entry already exists")
    
    return content

def add_research_writer_methods(content):
    """Add all Research Writer UI methods"""
    
    if "def show_research_writer(self):" in content:
        print("⏭️  Research Writer methods already exist")
        return content
    
    methods_code = '''
    def show_research_writer(self):
        """Research Writer - Web Research to Article Generation"""
        self.clear_content()
        self.update_status("Research Writer", 'success')
        
        if not self.current_workspace_id:
            self._show_no_workspace_error()
            return
        
        # Header
        header = tk.Frame(self.content_frame, bg=COLORS['white'])
        header.pack(fill=tk.X, padx=30, pady=20)
        tk.Label(header, text="🔬 Research Writer - AI Article Generation", 
                 font=('Segoe UI', 20, 'bold'), bg=COLORS['white']).pack(side=tk.LEFT)
        
        status_text = self.models_status.get('research_writer', 'Not Available')
        status_color = COLORS['success'] if 'Available' in status_text else COLORS['danger']
        tk.Label(header, text=status_text, font=('Segoe UI', 10, 'bold'), 
                 bg=status_color, fg=COLORS['white'], padx=10, pady=5).pack(side=tk.RIGHT)
        
        # Input Panel
        input_frame = tk.Frame(self.content_frame, bg=COLORS['light'], 
                               relief=tk.RAISED, borderwidth=1)
        input_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(input_frame, text="Research Configuration", 
                 font=('Segoe UI', 14, 'bold'), bg=COLORS['light']).pack(
                     padx=20, pady=15, anchor=tk.W)
        
        # Topic input
        topic_frame = tk.Frame(input_frame, bg=COLORS['light'])
        topic_frame.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(topic_frame, text="Research Topic:", font=('Segoe UI', 10, 'bold'), 
                 bg=COLORS['light'], width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.research_topic = tk.Entry(topic_frame, font=('Segoe UI', 11))
        self.research_topic.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.research_topic.insert(0, "AI in Healthcare 2026")
        
        # Word count
        wc_frame = tk.Frame(input_frame, bg=COLORS['light'])
        wc_frame.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(wc_frame, text="Target Words:", font=('Segoe UI', 10, 'bold'), 
                 bg=COLORS['light'], width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.research_wordcount = tk.IntVar(value=1500)
        self.wc_label = tk.Label(wc_frame, text="1500 words", 
                                 font=('Segoe UI', 10), bg=COLORS['light'])
        self.wc_label.pack(side=tk.RIGHT, padx=10)
        wc_slider = tk.Scale(wc_frame, from_=1000, to=2000, orient=tk.HORIZONTAL,
                             variable=self.research_wordcount, bg=COLORS['light'],
                             relief=tk.FLAT, command=lambda v: self.wc_label.config(
                                 text=f"{int(float(v))} words"))
        wc_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Optional URLs
        url_frame = tk.Frame(input_frame, bg=COLORS['light'])
        url_frame.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(url_frame, text="Custom URLs:", font=('Segoe UI', 10, 'bold'), 
                 bg=COLORS['light'], width=15, anchor=tk.W).pack(side=tk.TOP, anchor=tk.W)
        tk.Label(url_frame, text="(Optional: one per line)", 
                 font=('Segoe UI', 8), bg=COLORS['light'], 
                 fg=COLORS['text_light']).pack(side=tk.TOP, anchor=tk.W, padx=120)
        self.research_urls = scrolledtext.ScrolledText(url_frame, height=4, 
                                                        font=('Segoe UI', 9))
        self.research_urls.pack(fill=tk.X, padx=(120, 10), pady=5)
        
        # Action buttons
        btn_frame = tk.Frame(input_frame, bg=COLORS['light'])
        btn_frame.pack(fill=tk.X, padx=20, pady=15)
        ModernButton(btn_frame, "🔍 Research & Generate", 
                     self.start_research, 'success').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, "🖼️ Find Images", 
                     self.find_images_for_research, 'primary').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, "💾 Save Draft", 
                     self.save_research_as_draft, 'warning').pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, "🗑️ Clear", 
                     self.clear_research, 'danger').pack(side=tk.LEFT, padx=5)
        
        # Results
        result_frame = tk.Frame(self.content_frame, bg=COLORS['white'])
        result_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        tk.Label(result_frame, text="Generated Article with Citations", 
                 font=('Segoe UI', 14, 'bold'), bg=COLORS['white']).pack(
                     anchor=tk.W, pady=10)
        self.research_output = scrolledtext.ScrolledText(result_frame, 
                                                          font=('Segoe UI', 10), 
                                                          wrap=tk.WORD)
        self.research_output.pack(fill=tk.BOTH, expand=True)
        self.research_output.insert(tk.END, 
            "🔬 Research Writer - Generate 1000-2000 word articles\\n\\n"
            "How it works:\\n"
            "1. Enter your research topic\\n"
            "2. Optionally provide specific URLs to scrape\\n"
            "3. Click 'Research & Generate'\\n"
            "4. AI will search web, scrape content, analyze, and generate article\\n"
            "5. Article includes proper citations and sources\\n\\n"
            "Ready to start!")
    
    def start_research(self):
        """Start research and article generation"""
        topic = self.research_topic.get().strip()
        if not topic:
            messagebox.showwarning("Warning", "Enter a research topic")
            return
        
        if not self.research_writer:
            messagebox.showerror("Error", 
                "Research Writer not available.\\n\\n"
                "Install: pip install beautifulsoup4 requests")
            return
        
        # Get optional URLs
        urls_text = self.research_urls.get('1.0', tk.END).strip()
        source_urls = [u.strip() for u in urls_text.split('\\n') 
                       if u.strip()] if urls_text else None
        word_count = self.research_wordcount.get()
        
        self.update_status(f"Researching: {topic}...", 'warning')
        self.research_output.delete('1.0', tk.END)
        self.research_output.insert(tk.END, 
            f"🔬 Researching: {topic}\\n"
            f"📊 Target: {word_count} words\\n"
            f"🌐 Sources: {'Custom URLs' if source_urls else 'Auto-search'}\\n\\n"
            "⏳ Please wait 30-60 seconds...\\n")
        
        def research_thread():
            try:
                result = self.research_writer.research_and_generate(
                    topic=topic,
                    source_urls=source_urls,
                    word_count=word_count
                )
                self.after(0, lambda: self._on_research_complete(result))
            except Exception as e:
                self.after(0, lambda err=str(e): self._on_research_error(err))
        
        threading.Thread(target=research_thread, daemon=True).start()
    
    def _on_research_complete(self, result):
        """Handle research completion"""
        self.research_output.delete('1.0', tk.END)
        
        if result.get('success'):
            article = result['article']
            self.research_output.insert(tk.END, article)
            self.current_research = result  # Store for saving
            
            msg = (f"✅ Generated {result['word_count']} words from "
                   f"{result['sources_used']} sources in {result['generation_time']}")
            self.update_status(msg, 'success')
            messagebox.showinfo("Success", 
                f"Article generated!\\n\\n"
                f"Words: {result['word_count']}\\n"
                f"Sources: {result['sources_used']}\\n"
                f"Time: {result['generation_time']}")
        else:
            error = result.get('error', 'Unknown error')
            self.research_output.insert(tk.END, 
                f"❌ Research failed: {error}\\n\\n"
                "Troubleshooting:\\n"
                "• Check internet connection\\n"
                "• Try different topic\\n"
                "• Provide specific URLs manually")
            self.update_status("Research failed", 'danger')
    
    def _on_research_error(self, error):
        """Handle research error"""
        self.research_output.delete('1.0', tk.END)
        self.research_output.insert(tk.END, f"❌ Error:\\n\\n{error}")
        self.update_status("Research error", 'danger')
        messagebox.showerror("Error", str(error))
    
    def find_images_for_research(self):
        """Find relevant images using Unsplash"""
        topic = self.research_topic.get().strip()
        if not topic:
            messagebox.showwarning("Warning", "Enter topic first")
            return
        
        if not self.research_writer:
            messagebox.showerror("Error", "Research Writer not available")
            return
        
        self.update_status("Finding images...", 'warning')
        
        def find_thread():
            try:
                images = self.research_writer.find_images(topic, count=5)
                self.after(0, lambda: self._show_images(images))
            except Exception as e:
                self.after(0, lambda err=str(e): self._image_error(err))
        
        threading.Thread(target=find_thread, daemon=True).start()
    
    def _show_images(self, images):
        """Display found images in dialog"""
        if not images:
            messagebox.showinfo("No Images", 
                "No images found.\\n\\nTry different keywords.")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Select Image")
        dialog.geometry("600x450")
        dialog.configure(bg=COLORS['white'])
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"Found {len(images)} Images", 
                 font=('Segoe UI', 14, 'bold'), 
                 bg=COLORS['white']).pack(pady=15)
        
        frame = tk.Frame(dialog, bg=COLORS['white'])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(frame, font=('Segoe UI', 10), 
                             yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        for img in images:
            listbox.insert(tk.END, 
                f"{img['title'][:45]}... by {img['author']} ({img['source']})")
        
        def insert_image():
            sel = listbox.curselection()
            if sel:
                img = images[sel[0]]
                text = self.research_output.get('1.0', tk.END)
                self.research_output.delete('1.0', tk.END)
                self.research_output.insert('1.0', 
                    f"[IMAGE: {img['url']}]\\n"
                    f"Caption: {img['title']} (Credit: {img['author']}, {img['source']})\\n\\n")
                self.research_output.insert(tk.END, text)
                messagebox.showinfo("Success", "Image inserted!")
                dialog.destroy()
        
        ModernButton(dialog, "Insert Image URL", insert_image, 
                     'success').pack(pady=10)
        ModernButton(dialog, "Cancel", dialog.destroy, 'danger').pack(pady=5)
        
        self.update_status(f"Found {len(images)} images", 'success')
    
    def _image_error(self, error):
        """Handle image search error"""
        self.update_status("Image search failed", 'danger')
        messagebox.showerror("Error", f"Image search failed:\\n{error}")
    
    def save_research_as_draft(self):
        """Save research article as draft"""
        if not hasattr(self, 'current_research') or not self.current_research:
            messagebox.showwarning("Warning", "Generate article first")
            return
        
        topic = self.research_topic.get().strip()
        article = self.research_output.get('1.0', tk.END).strip()
        
        if len(article) < 100:
            messagebox.showwarning("Warning", "Article too short")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            word_count = len(article.split())
            summary = article[:250] + '...'
            
            cursor.execute("""
                INSERT INTO ai_drafts 
                (workspace_id, title, body_draft, summary, source_url, 
                 word_count, generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.current_workspace_id, topic, article, summary,
                f'research://{topic}', word_count, datetime.now()
            ))
            
            draft_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.update_status(f"Saved as Draft #{draft_id}", 'success')
            messagebox.showinfo("Success", 
                f"Research article saved!\\n\\n"
                f"Draft ID: {draft_id}\\n"
                f"Words: {word_count}\\n\\n"
                "Find it in 'Saved Drafts'")
            
        except Exception as e:
            messagebox.showerror("Error", f"Save failed:\\n{e}")
    
    def clear_research(self):
        """Clear research form"""
        self.research_topic.delete(0, tk.END)
        self.research_topic.insert(0, "AI in Healthcare 2026")
        self.research_urls.delete('1.0', tk.END)
        self.research_output.delete('1.0', tk.END)
        self.research_output.insert(tk.END, "Form cleared. Enter new topic.")
        self.research_wordcount.set(1500)
        if hasattr(self, 'current_research'):
            delattr(self, 'current_research')
        self.update_status("Cleared", 'primary')
    
'''
    
    # Find insertion point (before show_settings method)
    pattern = r'(\n    def show_settings\(self\):)'
    
    if re.search(pattern, content):
        content = re.sub(pattern, methods_code + r'\1', content)
        print("✅ Added all Research Writer methods")
    else:
        print("⚠️  Could not find show_settings method for insertion")
    
    return content

def main():
    """Main execution"""
    print("=" * 60)
    print("Research Writer UI Auto-Patcher")
    print("=" * 60)
    
    main_py_path = "main.py"
    
    # Check if file exists
    if not os.path.exists(main_py_path):
        print(f"❌ Error: {main_py_path} not found!")
        print("   Run this script from your project root directory.")
        return
    
    # Create backup
    print("\n📦 Creating backup...")
    backup_path = backup_file(main_py_path)
    
    # Read content
    print("📖 Reading main.py...")
    content = read_file(main_py_path)
    
    # Apply patches
    print("\n🔧 Applying patches...")
    content = add_research_writer_import(content)
    content = add_nav_button(content)
    content = add_model_config(content)
    content = add_research_writer_methods(content)
    
    # Write patched file
    print("\n💾 Writing patched main.py...")
    write_file(main_py_path, content)
    
    print("\n" + "=" * 60)
    print("✅ PATCHING COMPLETE!")
    print("=" * 60)
    print(f"\n✓ Original backed up to: {backup_path}")
    print("✓ main.py patched successfully")
    print("\n📋 What was added:")
    print("  • ResearchWriter module import")
    print("  • '🔬 Research Writer' navigation button")
    print("  • MODEL_CONFIGS entry")
    print("  • 9 new UI methods for Research Writer")
    print("\n🚀 Next steps:")
    print("  1. Run: python main.py")
    print("  2. Click '🔬 Research Writer' in sidebar")
    print("  3. Enter topic and generate article!")
    print("\n💡 If anything breaks, restore from backup:")
    print(f"     cp {backup_path} main.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
