"""
WordPress-Style HTML Formatter
Formats content exactly how WordPress expects it
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class WordPressFormatter:
    """
    Format HTML content to match WordPress editor standards
    
    WordPress uses:
    - <p> tags for paragraphs (NOT <br><br>)
    - Proper heading hierarchy (H1-H6)
    - Block formatting (not inline styles everywhere)
    - Clean, semantic HTML
    - CSS classes for alignment (alignleft, aligncenter, alignright)
    - No JavaScript/forms/iframes in content
    """
    
    # WordPress-standard CSS classes
    WP_IMAGE_CLASSES = {
        'left': 'alignleft',
        'center': 'aligncenter',
        'right': 'alignright',
        'none': 'alignnone'
    }
    
    # WordPress block formats (from TinyMCE)
    WP_BLOCK_FORMATS = {
        'paragraph': 'p',
        'heading1': 'h1',
        'heading2': 'h2',
        'heading3': 'h3',
        'heading4': 'h4',
        'heading5': 'h5',
        'heading6': 'h6',
        'preformatted': 'pre',
        'blockquote': 'blockquote'
    }
    
    def __init__(self):
        pass
    
    def format_for_wordpress(self, html_content: str) -> str:
        """
        Convert any HTML to WordPress-compatible format
        
        Args:
            html_content: Raw HTML content
        
        Returns:
            Clean, WordPress-compatible HTML
        """
        if not html_content:
            return ''
        
        # Step 1: Sanitize dangerous content
        html = self._sanitize_html(html_content)
        
        # Step 2: Fix paragraph formatting
        html = self._fix_paragraphs(html)
        
        # Step 3: Normalize headings
        html = self._normalize_headings(html)
        
        # Step 4: Format blockquotes
        html = self._format_blockquotes(html)
        
        # Step 5: Format lists
        html = self._format_lists(html)
        
        # Step 6: Fix image styling
        html = self._fix_image_classes(html)
        
        # Step 7: Remove inline styles (use CSS classes instead)
        html = self._remove_inline_styles(html)
        
        # Step 8: Clean up whitespace
        html = self._clean_whitespace(html)
        
        return html.strip()
    
    def _sanitize_html(self, html: str) -> str:
        """
        Remove dangerous/unwanted content
        
        WordPress blocks:
        - JavaScript event handlers (onclick, onload, etc.)
        - Script tags
        - Forms
        - Iframes (unless whitelisted)
        - Base64 images (data:image/...)
        """
        # Remove script tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
        
        # Remove inline event handlers (onclick, onload, etc.)
        # IMPROVED: More accurate regex
        html = re.sub(r'\son\w+="[^"]*"', '', html, flags=re.IGNORECASE)
        html = re.sub(r"\son\w+='[^']*'", '', html, flags=re.IGNORECASE)
        
        # Remove forms
        html = re.sub(r'<form[^>]*>.*?</form>', '', html, flags=re.DOTALL|re.IGNORECASE)
        
        # Remove iframes (unless from trusted sources)
        html = re.sub(
            r'<iframe(?!.*?(youtube\.com|vimeo\.com))[^>]*>.*?</iframe>',
            '',
            html,
            flags=re.DOTALL|re.IGNORECASE
        )
        
        # Remove base64 images (WordPress uploads to media library instead)
        html = re.sub(r'<img[^>]*src="data:image/[^"]*"[^>]*>', '', html, flags=re.IGNORECASE)
        
        # Remove dangerous attributes
        dangerous_attrs = ['onerror', 'onload', 'onclick', 'onmouseover']
        for attr in dangerous_attrs:
            html = re.sub(rf'\s{attr}="[^"]*"', '', html, flags=re.IGNORECASE)
        
        return html
    
    def _fix_paragraphs(self, html: str) -> str:
        """
        Convert <br><br> and double newlines to proper <p> tags
        
        WordPress uses <p> tags for paragraphs, NOT <br><br>
        """
        # Remove existing <p> tags first (we'll rebuild them)
        html = re.sub(r'<p[^>]*>', '', html)
        html = re.sub(r'</p>', '', html)
        
        # Convert double <br> to paragraph breaks
        html = re.sub(r'<br\s*/?>\s*<br\s*/?>', '\n\n', html, flags=re.IGNORECASE)
        
        # Convert remaining single <br> to spaces
        html = re.sub(r'<br\s*/?>', ' ', html, flags=re.IGNORECASE)
        
        # Split by double newlines
        paragraphs = html.split('\n\n')
        
        # Wrap each non-empty paragraph in <p> tags
        formatted_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if para:
                # Don't wrap headings, lists, blockquotes
                if not any(para.startswith(f'<{tag}') for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'blockquote', 'pre']):
                    para = f'<p>{para}</p>'
                formatted_paragraphs.append(para)
        
        return '\n\n'.join(formatted_paragraphs)
    
    def _normalize_headings(self, html: str) -> str:
        """
        Ensure proper heading hierarchy
        
        WordPress best practices:
        - H1 is reserved for post title (don't use in content)
        - Start content with H2
        - Maintain hierarchy (H2 → H3 → H4, not H2 → H5)
        """
        # Convert H1 to H2 (H1 is post title)
        html = re.sub(r'<h1([^>]*)>', r'<h2\1>', html, flags=re.IGNORECASE)
        html = re.sub(r'</h1>', '</h2>', html, flags=re.IGNORECASE)
        
        # Add WordPress heading classes
        for i in range(2, 7):
            html = re.sub(
                rf'<h{i}([^>]*)>',
                rf'<h{i} class="wp-block-heading"\1>',
                html,
                flags=re.IGNORECASE
            )
        
        return html
    
    def _format_blockquotes(self, html: str) -> str:
        """
        Format blockquotes with WordPress styling
        """
        # Add WordPress blockquote class
        html = re.sub(
            r'<blockquote([^>]*)>',
            r'<blockquote class="wp-block-quote"\1>',
            html,
            flags=re.IGNORECASE
        )
        
        return html
    
    def _format_lists(self, html: str) -> str:
        """
        Format lists with WordPress styling
        """
        # Add WordPress list class
        html = re.sub(
            r'<ul([^>]*)>',
            r'<ul class="wp-block-list"\1>',
            html,
            flags=re.IGNORECASE
        )
        
        html = re.sub(
            r'<ol([^>]*)>',
            r'<ol class="wp-block-list"\1>',
            html,
            flags=re.IGNORECASE
        )
        
        return html
    
    def _fix_image_classes(self, html: str) -> str:
        """
        Add WordPress image alignment classes
        
        WordPress uses CSS classes for image alignment:
        - alignleft: Float left with margin
        - aligncenter: Center with auto margins
        - alignright: Float right with margin
        - alignnone: No special alignment
        """
        # Replace inline style alignment with CSS classes
        html = re.sub(
            r'<img([^>]*)style="[^"]*text-align:\s*left[^"]*"([^>]*)>',
            r'<img\1 class="alignleft"\2>',
            html,
            flags=re.IGNORECASE
        )
        
        html = re.sub(
            r'<img([^>]*)style="[^"]*text-align:\s*center[^"]*"([^>]*)>',
            r'<img\1 class="aligncenter"\2>',
            html,
            flags=re.IGNORECASE
        )
        
        html = re.sub(
            r'<img([^>]*)style="[^"]*text-align:\s*right[^"]*"([^>]*)>',
            r'<img\1 class="alignright"\2>',
            html,
            flags=re.IGNORECASE
        )
        
        # Add default class if no alignment specified
        html = re.sub(
            r'<img(?![^>]*class=)([^>]*)>',
            r'<img class="alignnone"\1>',
            html,
            flags=re.IGNORECASE
        )
        
        return html
    
    def _remove_inline_styles(self, html: str) -> str:
        """
        Remove inline styles - WordPress uses CSS classes instead
        
        Keeps only essential styles (width, height for images)
        """
        # For images, keep width and height
        def keep_image_dimensions(match):
            tag = match.group(0)
            # Extract width and height
            width = re.search(r'width:\s*(\d+)px', tag, re.IGNORECASE)
            height = re.search(r'height:\s*(\d+)px', tag, re.IGNORECASE)
            
            # Remove all inline styles
            tag = re.sub(r'style="[^"]*"', '', tag)
            
            # Add back width and height as attributes
            if width:
                tag = re.sub(r'<img', f'<img width="{width.group(1)}"', tag)
            if height:
                tag = re.sub(r'<img', f'<img height="{height.group(1)}"', tag)
            
            return tag
        
        # Process images separately
        html = re.sub(r'<img[^>]*style="[^"]*"[^>]*>', keep_image_dimensions, html, flags=re.IGNORECASE)
        
        # Remove all other inline styles
        html = re.sub(r'style="[^"]*"', '', html, flags=re.IGNORECASE)
        
        return html
    
    def _clean_whitespace(self, html: str) -> str:
        """
        Clean up extra whitespace
        
        WordPress standards:
        - Single newline between elements
        - No trailing spaces
        - No empty tags
        """
        # Remove empty tags
        html = re.sub(r'<p>\s*</p>', '', html, flags=re.IGNORECASE)
        html = re.sub(r'<div>\s*</div>', '', html, flags=re.IGNORECASE)
        html = re.sub(r'<span>\s*</span>', '', html, flags=re.IGNORECASE)
        
        # Normalize whitespace inside tags
        html = re.sub(r'>\s+<', '>\n<', html)
        
        # Remove multiple consecutive newlines (max 2)
        html = re.sub(r'\n{3,}', '\n\n', html)
        
        # Remove trailing spaces from lines
        html = '\n'.join(line.rstrip() for line in html.split('\n'))
        
        return html
    
    def convert_to_gutenberg_blocks(self, html: str) -> str:
        """
        Convert HTML to Gutenberg block format
        
        Gutenberg blocks use HTML comments to define structure:
        <!-- wp:paragraph -->
        <p>Content</p>
        <!-- /wp:paragraph -->
        """
        # First, format the HTML properly
        html = self.format_for_wordpress(html)
        
        blocks = []
        
        # Split by tags
        lines = html.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect block type
            if line.startswith('<h2'):
                content = line
                blocks.append(f'''<!-- wp:heading -->
{content}
<!-- /wp:heading -->''')
            
            elif line.startswith('<h3'):
                content = line
                blocks.append(f'''<!-- wp:heading {{"level":3}} -->
{content}
<!-- /wp:heading -->''')
            
            elif line.startswith('<h4'):
                content = line
                blocks.append(f'''<!-- wp:heading {{"level":4}} -->
{content}
<!-- /wp:heading -->''')
            
            elif line.startswith('<blockquote'):
                content = line
                blocks.append(f'''<!-- wp:quote -->
{content}
<!-- /wp:quote -->''')
            
            elif line.startswith('<ul'):
                content = line
                blocks.append(f'''<!-- wp:list -->
{content}
<!-- /wp:list -->''')
            
            elif line.startswith('<ol'):
                content = line
                blocks.append(f'''<!-- wp:list {{"ordered":true}} -->
{content}
<!-- /wp:list -->''')
            
            elif line.startswith('<img') or line.startswith('<figure'):
                content = line
                blocks.append(f'''<!-- wp:image -->
{content}
<!-- /wp:image -->''')
            
            elif line.startswith('<p>'):
                content = line
                blocks.append(f'''<!-- wp:paragraph -->
{content}
<!-- /wp:paragraph -->''')
        
        return '\n\n'.join(blocks)
