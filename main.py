# [KEEPING ALL EXISTING CODE ABOVE show_editor() - Lines 1-687]
# Only replacing the show_editor() method:

    def show_editor(self):
        """AI Draft Editor - Shows fetched news and generates drafts"""
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
        
        tk.Label(
            self.content_frame,
            text="Select news to generate AI-powered drafts using David AI Writer 7B.",
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
            self.generate_ai_draft, 'success'
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
            content += "Click 'Generate AI Draft' to create article..."
            self.draft_body.insert(tk.END, content)
    
    def generate_ai_draft(self):
        """Generate AI draft from selected news"""
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
        
        self.update_status("Generating AI draft...", 'warning')
        
        # Simulate AI draft generation (you can integrate actual AI model here)
        draft_title = news['headline']
        draft_body = f"""# {news['headline']}

## Introduction

{news['summary']}

This article explores the latest developments in {news['category'].lower()}.

## Main Content

According to {news['source']}, recent events have shown significant importance in this area. The situation continues to evolve as more information becomes available.

### Key Points

- Important development in {news['category']}
- Expert analysis and insights
- Impact on industry and stakeholders
- Future implications and trends

## Analysis

Our AI analysis suggests that this development could have far-reaching consequences. Industry experts are closely monitoring the situation for further updates.

## Conclusion

As this story develops, we will continue to provide updates and in-depth coverage. Stay tuned for more information.

---

**Source:** {news['source']}  
**Read more:** {news['url']}
**Category:** {news['category']}
**Generated by:** David AI Writer 7B
"""
        
        if hasattr(self, 'draft_title'):
            self.draft_title.delete(0, tk.END)
            self.draft_title.insert(0, draft_title)
        
        if hasattr(self, 'draft_body'):
            self.draft_body.delete('1.0', tk.END)
            self.draft_body.insert(tk.END, draft_body)
        
        self.update_status("AI draft generated successfully!", 'success')
        messagebox.showinfo("Success", "AI draft generated! You can now edit and save it.")
    
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

# [KEEP ALL REMAINING CODE BELOW - show_translations(), show_wordpress_config(), etc.]
