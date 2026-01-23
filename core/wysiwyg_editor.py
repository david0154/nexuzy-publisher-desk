"""
WYSIWYG Editor Integration Module
Provides modern rich text editing capabilities for article drafts
"""

import logging
from typing import Dict, Optional
import re

logger = logging.getLogger(__name__)

class WYSIWYGEditor:
    """Manage WYSIWYG editor integration and HTML content"""
    
    def __init__(self):
        self.editor_type = 'tinymce'  # or 'ckeditor'
        self.config = self._get_editor_config()
    
    def _get_editor_config(self) -> Dict:
        """Get TinyMCE configuration"""
        if self.editor_type == 'tinymce':
            return {
                'selector': '#editor',
                'height': 500,
                'plugins': [
                    'advlist', 'autolink', 'lists', 'link', 'image', 'charmap',
                    'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                    'insertdatetime', 'media', 'table', 'preview', 'help', 'wordcount'
                ],
                'toolbar': '''undo redo | formatselect | bold italic backcolor | alignleft aligncenter
                             alignright alignjustify | bullist numlist outdent indent | removeformat | help''',
                'toolbar_mode': 'sliding',
                'file_picker_types': 'image media',
                'images_upload_handler': 'uploadImageHandler',
                'automatic_uploads': True,
                'paste_data_images': True,
                'relative_urls': False
            }
        else:
            return {
                'editor.width': '100%',
                'editor.height': '500px',
                'toolbar': ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', 'insertTable'],
                'language': 'en'
            }
    
    def generate_tinymce_script(self) -> str:
        """Generate TinyMCE initialization script"""
        return f"""
<script src="https://cdn.jsdelivr.net/npm/tinymce@6/tinymce.min.js"></script>
<script>
  tinymce.init({{
    selector: '#editor',
    height: 500,
    plugins: 'advlist autolink lists link image charmap anchor searchreplace visualblocks code fullscreen insertdatetime media table preview help wordcount',
    toolbar: 'undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help',
    toolbar_mode: 'sliding',
    paste_data_images: true,
    images_upload_handler: uploadImageHandler
  }});
  
  async function uploadImageHandler(blobInfo) {{
    const formData = new FormData();
    formData.append('image', blobInfo.blob());
    
    const response = await fetch('/api/upload-image', {{
      method: 'POST',
      body: formData
    }});
    
    const data = await response.json();
    return data.url;
  }}
</script>
"""
    
    def generate_ckeditor_script(self) -> str:
        """Generate CKEditor 5 initialization script"""
        return f"""
<script src="https://cdn.ckeditor.com/ckeditor5/38.0.0/classic/ckeditor.js"></script>
<script>
  class MyUploadAdapter {{
    constructor(loader) {{
      this.loader = loader;
    }}
    
    upload() {{
      return this.loader.file.then(file => new Promise((resolve, reject) => {{
        const formData = new FormData();
        formData.append('upload', file);
        
        fetch('/api/upload-image', {{
          method: 'POST',
          body: formData
        }}).then(response => response.json())
          .then(data => resolve({{
            default: data.url
          }}))
          .catch(reject);
      }}));
    }}
  }}
  
  function MyCustomUploadAdapterPlugin(editor) {{
    editor.plugins.get('FileRepository').createUploadAdapter = (loader) => {{
      return new MyUploadAdapter(loader);
    }};
  }}
  
  ClassicEditor.create(document.querySelector('#editor'), {{
    extraPlugins: [MyCustomUploadAdapterPlugin],
    toolbar: {{
      items: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', 'insertTable', 'undo', 'redo']
    }}
  }}).catch(error => console.error(error));
</script>
"""
    
    def sanitize_html(self, html_content: str) -> str:
        """
        Sanitize HTML content to prevent XSS attacks
        """
        # Remove script tags
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove event handlers
        html_content = re.sub(r'\s*on\w+\s*=', ' ', html_content, flags=re.IGNORECASE)
        
        # Remove dangerous tags
        dangerous_tags = ['iframe', 'object', 'embed', 'form']
        for tag in dangerous_tags:
            html_content = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        return html_content
    
    def convert_markdown_to_html(self, markdown_content: str) -> str:
        """
        Convert markdown-style formatting to HTML
        """
        html = markdown_content
        
        # Headers
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        
        # Bold and italic
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'_(.*?)_', r'<em>\1</em>', html)
        
        # Code blocks
        html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
        
        # Links
        html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
        
        # Line breaks
        html = re.sub(r'\n\n', '</p><p>', html)
        html = f'<p>{html}</p>'.replace('<p></p>', '')
        
        return html
    
    def convert_html_to_markdown(self, html_content: str) -> str:
        """
        Convert HTML back to markdown format
        """
        markdown = html_content
        
        # Headers
        markdown = re.sub(r'<h2>(.*?)</h2>', r'## \1', markdown, flags=re.IGNORECASE)
        markdown = re.sub(r'<h3>(.*?)</h3>', r'### \1', markdown, flags=re.IGNORECASE)
        markdown = re.sub(r'<h4>(.*?)</h4>', r'#### \1', markdown, flags=re.IGNORECASE)
        
        # Bold and italic
        markdown = re.sub(r'<strong>(.*?)</strong>', r'**\1**', markdown, flags=re.IGNORECASE)
        markdown = re.sub(r'<em>(.*?)</em>', r'_\1_', markdown, flags=re.IGNORECASE)
        
        # Code
        markdown = re.sub(r'<pre><code>(.*?)</code></pre>', r'```\1```', markdown, flags=re.DOTALL | re.IGNORECASE)
        markdown = re.sub(r'<code>(.*?)</code>', r'`\1`', markdown, flags=re.IGNORECASE)
        
        # Links
        markdown = re.sub(r'<a href="(.*?)">(.*?)</a>', r'[\2](\1)', markdown, flags=re.IGNORECASE)
        
        # Paragraphs
        markdown = re.sub(r'</p><p>', '\n\n', markdown, flags=re.IGNORECASE)
        markdown = re.sub(r'<p>(.*?)</p>', r'\1', markdown, flags=re.IGNORECASE)
        
        return markdown.strip()
    
    def embed_image_in_html(self, html_content: str, image_base64: str, alt_text: str = '') -> str:
        """
        Embed base64 image directly in HTML content
        """
        # Determine image format from base64 string
        if image_base64.startswith('/9j/') or 'jpeg' in image_base64[:50]:
            mime_type = 'image/jpeg'
        elif 'png' in image_base64[:50]:
            mime_type = 'image/png'
        else:
            mime_type = 'image/jpeg'  # Default
        
        image_html = f'<img src="data:{mime_type};base64,{image_base64}" alt="{alt_text}" style="max-width: 100%; height: auto;"/>'
        
        # Insert at the beginning of content
        return f'{image_html}\n\n{html_content}'
    
    def extract_text_from_html(self, html_content: str) -> str:
        """
        Extract plain text from HTML content
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Decode HTML entities
        import html
        text = html.unescape(text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def generate_table_of_contents(self, html_content: str) -> str:
        """
        Generate table of contents from headings
        """
        headings = re.findall(r'<h([2-4])>(.*?)</h[2-4]>', html_content, re.IGNORECASE)
        
        if not headings:
            return ''
        
        toc = '<div class="table-of-contents"><h3>Table of Contents</h3><ul>'
        
        for level, heading in headings:
            heading_text = re.sub(r'<[^>]+>', '', heading)  # Remove any remaining tags
            indent = '  ' * (int(level) - 2)
            toc += f'{indent}<li><a href="#{heading_text.replace(" ", "-").lower()}">{heading_text}</a></li>'
        
        toc += '</ul></div>'
        
        return toc
