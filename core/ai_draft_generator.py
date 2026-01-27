"""
AI Draft Generation Module - Full Article Rewriting with AI Model Loading
Generates complete, professional news articles (1000+ words) with AI sentence improvement
"""

import sqlite3
import logging
from typing import Dict, List, Optional
from pathlib import Path
import random
import re
from datetime import datetime, timedelta
import json
import requests
from io import BytesIO
import os
import sys

logger = logging.getLogger(__name__)

class DraftGenerator:
    """Generate complete AI-rewritten news articles with sentence-level AI improvement"""
    
    def __init__(self, db_path: str, model_name: str = 'models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf'):
        self.db_path = db_path
        self.model_name = model_name
        self.model_file = "tinyllama-1.1b-chat-v1.0.Q8_0.gguf"
        self.llm = self._load_model()
        self.translation_keywords = self._load_translation_keywords()
        
        # Initialize sentence improvement model (lighter weight for quick improvements)
        self.sentence_model = self._load_sentence_model()
        
        # Model status
        if not self.llm:
            logger.warning("⚠️  AI Writer in SAFE MODE - Using template-based generation")
            logger.warning("📥 Download GGUF model for full AI features")
        else:
            logger.info("✅ AI Writer LOADED - Full AI generation enabled")
    
    def _load_model(self):
        """Load GGUF quantized Mistral model with safe fallback"""
        try:
            from ctransformers import AutoModelForCausalLM
            
            logger.info(f"Loading GGUF model: {self.model_name}")
            
            # Check multiple possible paths (cross-platform compatible)
            model_name_safe = self.model_name.replace('/', '_')
            possible_paths = [
                Path('models') / model_name_safe / self.model_file,
                Path('models') / self.model_file,
                Path(self.model_file),
                Path.home() / '.cache' / 'nexuzy' / 'models' / model_name_safe / self.model_file
            ]
            
            model_path = None
            for path in possible_paths:
                if path.exists():
                    model_path = path
                    logger.info(f"Found model at: {model_path}")
                    break
            
            if not model_path:
                logger.warning(f"⚠️  GGUF model not found. Checked paths:")
                for p in possible_paths:
                    logger.warning(f"  - {p}")
                logger.warning("📥 Download from: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/blob/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
                logger.warning("💡 Place in: models/ folder")
                logger.warning("✅ App continues in SAFE MODE with template generation")
                return None
            
            logger.info(f"Loading GGUF model from: {model_path}")
            
            # Load GGUF model with ctransformers
            llm = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                model_type='llama',
                context_length=1024,
                max_new_tokens=800,
                threads=2,  # Auto-detect CPU cores
                gpu_layers=0
            )
            
            logger.info("✅ Mistral-7B-GGUF Q4_K_M loaded successfully (4.1GB)")
            return llm
        
        except ImportError:
            logger.warning("⚠️  ctransformers not installed. Install: pip install ctransformers")
            logger.warning("✅ App continues in SAFE MODE with template generation")
            return None
        except Exception as e:
            logger.warning(f"⚠️  Error loading GGUF model: {e}")
            logger.warning("✅ App continues in SAFE MODE with template generation")
            return None
    
    def _load_sentence_model(self):
        """Load lightweight sentence improvement model"""
        try:
            from transformers import pipeline
            logger.info("Loading sentence improvement model...")
            model = pipeline("text2text-generation", model="google/flan-t5-base", max_length=150)
            logger.info("✅ Sentence improvement model loaded")
            return model
        except Exception as e:
            logger.warning(f"⚠️  Sentence model unavailable: {e}")
            return None
    
    def improve_sentence(self, sentence: str) -> str:
        """
        Improve a single sentence with AI
        This is used by the WYSIWYG editor's "🤖 Improve Sentence" button
        """
        if not sentence or len(sentence.strip()) < 10:
            return sentence
        
        # If AI model available, use it
        if self.sentence_model:
            try:
                prompt = f"Rewrite this sentence to be more professional and clear: {sentence}"
                result = self.sentence_model(prompt, max_length=150, do_sample=False)
                improved = result[0]['generated_text'].strip()
                logger.info(f"AI improved sentence: {sentence[:50]}... -> {improved[:50]}...")
                return improved
            except Exception as e:
                logger.error(f"Sentence improvement error: {e}")
        
        # Fallback: Manual improvement rules
        improved = sentence.strip()
        
        # Basic improvements
        if not improved.endswith(('.', '!', '?')):
            improved += '.'
        
        # Capitalize first letter
        if improved:
            improved = improved[0].upper() + improved[1:]
        
        # Remove multiple spaces
        improved = re.sub(r'\s+', ' ', improved)
        
        # Replace common informal words
        replacements = {
            'gonna': 'going to',
            'wanna': 'want to',
            'gotta': 'got to',
            'kinda': 'kind of',
            'sorta': 'sort of',
            'dunno': "don't know",
            'yeah': 'yes',
            'nope': 'no'
        }
        
        for informal, formal in replacements.items():
            improved = re.sub(r'\b' + informal + r'\b', formal, improved, flags=re.IGNORECASE)
        
        return improved
    
    def _load_translation_keywords(self) -> Dict:
        """Load keywords for story structure detection"""
        return {
            'technology': ['ai', 'technology', 'software', 'app', 'digital', 'tech', 'innovation', 'algorithm', 'system', 'platform', 'blockchain', 'quantum', 'machine learning', 'data', 'cloud', 'cyber'],
            'business': ['revenue', 'profit', 'stock', 'market', 'business', 'company', 'ceo', 'investor', 'startup', 'funding', 'acquisition', 'merger', 'sales', 'growth', 'quarterly', 'earnings'],
            'politics': ['government', 'president', 'minister', 'law', 'policy', 'election', 'parliament', 'congress', 'senate', 'legislation', 'vote', 'political', 'campaign', 'diplomat', 'treaty'],
            'health': ['health', 'medical', 'hospital', 'doctor', 'patient', 'disease', 'treatment', 'vaccine', 'coronavirus', 'covid', 'pandemic', 'epidemic', 'virus', 'cure', 'pharmaceutical'],
            'crisis': ['crisis', 'emergency', 'disaster', 'accident', 'fire', 'flood', 'storm', 'earthquake', 'explosion', 'incident', 'tragedy', 'victim', 'damage', 'rescue', 'alert'],
            'sports': ['team', 'player', 'match', 'game', 'win', 'championship', 'score', 'sport', 'athlete', 'coach', 'tournament', 'league', 'competition', 'season', 'victory'],
        }
    
    def _extract_topic_info(self, headline: str, summary: str, category: str) -> Dict:
        """Extract comprehensive topic information"""
        entities = {
            'people': [],
            'organizations': [],
            'places': [],
            'events': [],
            'numbers': [],
            'technical_terms': []
        }
        
        full_text = (headline + ' ' + summary).lower()
        
        # Find capitalized words (potential names/places)
        original_text = headline + ' ' + summary
        original_words = original_text.split()
        capitalized = [w for w in original_words if w and w[0].isupper() and len(w) > 2 and w not in ['The', 'A', 'An', 'And', 'Or', 'But']]
        
        # Extract numbers/statistics
        numbers = re.findall(r'\d+(?:\.\d+)?%?|\d{1,3}(?:,\d{3})*', headline + ' ' + summary)
        entities['numbers'] = numbers[:10]
        
        # Extract technical terms
        for keyword_list in self.translation_keywords.values():
            for keyword in keyword_list:
                if keyword in full_text:
                    entities['technical_terms'].append(keyword)
        
        topic_focus = self._determine_focus(headline, summary, category)
        
        return {
            'entities': entities,
            'capitalized_terms': capitalized[:15],
            'numbers': numbers,
            'focus': topic_focus,
            'category': category,
            'summary': summary[:200]
        }
    
    def _determine_focus(self, headline: str, summary: str, category: str) -> str:
        """Determine the main focus/angle of the story"""
        text = (headline + ' ' + summary).lower()
        scores = {}
        
        for topic, keywords in self.translation_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[topic] = score
        
        if scores:
            top_topic = max(scores, key=scores.get)
            return f"{top_topic} development"
        
        return f"{category.lower()} development"
    
    def download_and_store_image(self, image_url: str, news_id: int) -> Optional[str]:
        """
        Download image from URL, verify no watermark, and store locally
        Returns local file path or None
        """
        if not image_url:
            return None
        
        try:
            logger.info(f"Downloading image: {image_url}")
            response = requests.get(image_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code != 200:
                logger.error(f"Failed to download image: HTTP {response.status_code}")
                return None
            
            from PIL import Image
            img = Image.open(BytesIO(response.content))
            
            # Create images directory if not exists
            images_dir = Path('downloaded_images')
            images_dir.mkdir(exist_ok=True)
            
            # Generate filename
            ext = image_url.split('.')[-1].split('?')[0]
            if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                ext = 'jpg'
            
            filename = f"news_{news_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            filepath = images_dir / filename
            
            # Save image
            img.save(filepath)
            logger.info(f"✅ Image downloaded and saved: {filepath}")
            
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return None
    
    def generate_draft(self, news_id: int, manual_mode: bool = False, manual_content: str = '') -> Dict:
        """
        Generate complete article draft with AI or template-based fallback
        SAFE MODE: Falls back to template generation if model unavailable
        """
        try:
            # Get news details
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT headline, summary, source_url, source_domain, category, image_url
                FROM news_queue WHERE id = ?
            ''', (news_id,))
            
            news = cursor.fetchone()
            if not news:
                return {}
            
            headline, summary, source_url, source_domain, category, image_url = news
            
            # Get workspace_id
            cursor.execute('SELECT workspace_id FROM news_queue WHERE id = ?', (news_id,))
            workspace_id = cursor.fetchone()[0]
            conn.close()
            
            # Download and store image locally
            local_image_path = None
            if image_url:
                local_image_path = self.download_and_store_image(image_url, news_id)
            
            # Extract topic information
            topic_info = self._extract_topic_info(headline, summary or '', category)
            
            # Generate or enhance content
            if manual_mode and manual_content:
                draft = self._enhance_manual_content(manual_content, headline, category, topic_info)
            elif self.llm:
                draft = self._generate_with_model(headline, summary, category, source_domain, topic_info)
            else:
                # SAFE MODE: Template-based generation
                logger.info("Using template-based generation (SAFE MODE)")
                draft = self._generate_template_based(headline, summary, category, topic_info)
            
            # Embed image properly in article (local path, not URL)
            draft['image_url'] = image_url or ''
            draft['local_image_path'] = local_image_path or ''
            draft['source_url'] = source_url or ''
            draft['source_domain'] = source_domain or ''
            draft['is_html'] = True
            
            # Store draft
            draft_id = self._store_draft(news_id, workspace_id, draft)
            
            logger.info(f"✅ Generated draft for news_id {news_id}, words: {draft.get('word_count', 0)}")
            return {**draft, 'id': draft_id}
        
        except Exception as e:
            logger.error(f"❌ Error generating draft: {e}")
            return {}
    
    def _generate_template_based(self, headline: str, summary: str, category: str, topic_info: Dict) -> Dict:
        """
        Template-based draft generation for SAFE MODE
        Creates professional articles without requiring AI model
        """
        logger.info("Generating template-based article (SAFE MODE)")
        
        # Extract key information
        capitalized = topic_info.get('capitalized_terms', [])
        numbers = topic_info.get('numbers', [])
        focus = topic_info.get('focus', category)
        
        # Build article sections
        sections = []
        
        # Introduction
        intro = f"<h2>Introduction</h2>\n<p>{headline} - This {category.lower()} development has gained significant attention. "
        if summary:
            intro += f"{summary[:200]}..."
        intro += "</p>"
        sections.append(intro)
        
        # Background
        background = f"<h2>Background</h2>\n<p>This story relates to recent developments in {focus}. "
        if capitalized:
            background += f"Key entities involved include {', '.join(capitalized[:3])}. "
        if numbers:
            background += f"Notable figures mentioned include {', '.join(numbers[:3])}."
        background += "</p>"
        sections.append(background)
        
        # Main Content
        main = f"<h2>Key Details</h2>\n<p>{summary or 'This development represents a significant event in the ' + category.lower() + ' sector.'}</p>"
        sections.append(main)
        
        # Analysis
        analysis = f"<h2>Analysis</h2>\n<p>Industry experts are closely monitoring this situation. "
        analysis += f"The implications for {focus} remain to be fully understood as more information becomes available.</p>"
        sections.append(analysis)
        
        # Note about template generation
        template_note = "\n<p><em>Note: This article was generated using template-based content generation. For full AI-powered drafts, download the Mistral-7B GGUF model.</em></p>"
        
        body = "\n\n".join(sections) + template_note
        
        return {
            'title': headline,
            'body_draft': body,
            'summary': summary or '',
            'word_count': len(body.split()),
            'is_template_generated': True,
            'generation_mode': 'template'
        }
    
    def _enhance_manual_content(self, content: str, headline: str, category: str, topic_info: Dict) -> Dict:
        """Enhance user-written content with AI sentence improvement"""
        logger.info("Enhancing manual content")
        
        # Structure the content
        structured_content = self._structure_content(content, topic_info)
        
        # Enhance sentences
        enhanced = self._enhance_sentences(structured_content, topic_info)
        
        return {
            'title': headline,
            'body_draft': enhanced,
            'summary': topic_info.get('summary', ''),
            'word_count': len(enhanced.split()),
            'is_manual_enhanced': True
        }
    
    def _structure_content(self, content: str, topic_info: Dict) -> str:
        """Structure user content with proper formatting"""
        lines = content.split('\n')
        structured_parts = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if len(line) < 100 and line.isupper():
                structured_parts.append(f"\n<h2>{line}</h2>\n")
            else:
                structured_parts.append(f"<p>{line}</p>")
        
        return "\n".join(structured_parts)
    
    def _enhance_sentences(self, text: str, topic_info: Dict) -> str:
        """Enhance sentences for better readability"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        enhanced_sentences = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            # Use AI improvement if available
            if len(sentence.split()) < 8 and self.sentence_model:
                enhanced = self.improve_sentence(sentence)
                enhanced_sentences.append(enhanced)
            else:
                enhanced_sentences.append(sentence)
        
        return " ".join(enhanced_sentences)
    
    def _generate_with_model(self, headline: str, summary: str, category: str, source: str, topic_info: Dict) -> Dict:
        """Generate with AI model - optimized for speed"""
        """Generate with real AI model"""
        
        topic_context = f"""Topic Focus: {topic_info['focus']}
Category: {category}
Key Terms: {', '.join(topic_info['capitalized_terms'][:5])}
Key Numbers: {', '.join(topic_info['numbers'][:3])}"""
        
        prompt = f"""<s>[INST] You are a professional journalist. Write a complete, detailed news article (1000-1200 words) based on this headline.

Write in professional journalism style with clear sections.
Include: Introduction, Background, Main Content, and Analysis.

IMPORTANT RULES:
- DO NOT add conclusions or summary sections
- DO NOT add risk assessments
- DO NOT add "final thoughts" or "looking ahead" sections
- DO NOT mention AI, bots, or automated systems
- STOP after completing the main analysis section

Headline: {headline}
Summary: {summary}

{topic_context}

Write the COMPLETE article now (END after analysis, NO conclusions): [/INST]"""
        
        try:
            generated_text = self.llm(
                prompt,
                max_new_tokens=800,
                temperature=0.6,
                top_p=0.9,
                stop=["</s>", "[/INST]", "Conclusion", "Risk Assessment", "Summary", "Final Thoughts", "Looking Ahead"],
                stream=False
            )
            
            # Remove any conclusion or risk sections that might have been generated
            cleaned_text = self._remove_unwanted_sections(generated_text)
            
            return {
                'title': headline,
                'body_draft': cleaned_text.strip(),
                'summary': summary,
                'word_count': len(cleaned_text.split()),
                'is_ai_generated': True,
                'generation_mode': 'ai_model'
            }
        except Exception as e:
            logger.error(f"❌ Model generation error: {e}")
            logger.info("Falling back to template generation")
            return self._generate_template_based(headline, summary, category, topic_info)
    
    def _remove_unwanted_sections(self, text: str) -> str:
        """Remove conclusion, risk assessment, summary sections"""
        unwanted_patterns = [
            r'## Conclusion.*$',
            r'## Risk.*$',
            r'## Summary.*$',
            r'## Final.*$',
            r'## Looking Ahead.*$',
            r'\n\nConclusion:.*$',
            r'\n\nRisk.*:.*$',
            r'\n\nSummary:.*$',
            r'\n\nFinal Thoughts.*$',
            r'\n\nLooking Ahead.*$',
            r'\n\n---\n\n.*Conclusion.*$',
            r'\n\n\*\*Conclusion\*\*.*$',
            r'\n\n\*\*Risk.*\*\*.*$',
            r'\n\n\*\*Summary\*\*.*$',
        ]
        
        cleaned = text
        for pattern in unwanted_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        cleaned = cleaned.strip()
        logger.info("✅ Removed unwanted sections")
        return cleaned
    
    def _check_column_exists(self, cursor, table: str, column: str) -> bool:
        """Check if a column exists in a table"""
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            return column in columns
        except Exception:
            return False

    def _store_draft(self, news_id: int, workspace_id: int, draft: Dict) -> int:
        """Store draft in database with HTML format"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert to HTML
            html_body = self._convert_to_html(draft.get('body_draft', ''))
            
            # Embed local image in HTML if available
            if draft.get('local_image_path'):
                image_html = f'<figure><img src="{draft["local_image_path"]}" alt="{draft.get("title", "")}" /></figure>\n\n'
                html_body = image_html + html_body
            
            # Dynamic Insert
            columns = ['workspace_id', 'news_id', 'title', 'body_draft', 'summary', 'word_count', 'image_url', 'source_url', 'generated_at']
            values = [
                workspace_id,
                news_id,
                draft.get('title', ''),
                html_body,
                draft.get('summary', ''),
                draft.get('word_count', 0),
                draft.get('local_image_path', ''),
                draft.get('source_url', ''),
                datetime.now().isoformat()
            ]

            # Optional columns
            if self._check_column_exists(cursor, 'ai_drafts', 'source_domain'):
                columns.append('source_domain')
                values.append(draft.get('source_domain', ''))
            
            if self._check_column_exists(cursor, 'ai_drafts', 'is_html'):
                columns.append('is_html')
                values.append(1)
            
            if self._check_column_exists(cursor, 'ai_drafts', 'generation_mode'):
                columns.append('generation_mode')
                values.append(draft.get('generation_mode', 'unknown'))

            placeholders = ', '.join(['?' for _ in values])
            column_names = ', '.join(columns)
            
            cursor.execute(f'''
                INSERT INTO ai_drafts 
                ({column_names})
                VALUES ({placeholders})
            ''', values)
            
            conn.commit()
            draft_id = cursor.lastrowid
            conn.close()
            
            return draft_id
        
        except Exception as e:
            logger.error(f"❌ Error storing draft: {e}")
            return 0
    
    def _convert_to_html(self, text: str) -> str:
        """Convert markdown-style text to HTML"""
        # Convert headers
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        
        # Convert paragraphs
        paragraphs = text.split('\n\n')
        html_paragraphs = []
        for para in paragraphs:
            if not para.strip():
                continue
            if not para.strip().startswith('<'):
                para = f'<p>{para.strip()}</p>'
            html_paragraphs.append(para)
        
        return '\n'.join(html_paragraphs)
    
    def cleanup_old_queue(self, days: int = 15):
        """Remove news items older than specified days from queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                UPDATE news_queue
                SET status = 'archived'
                WHERE created_at < ? AND status = 'pending'
            ''', (cutoff_date.isoformat(),))
            
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            
            logger.info(f"Archived {affected_rows} news items older than {days} days")
            return affected_rows
        
        except Exception as e:
            logger.error(f"❌ Error cleaning up queue: {e}")
            return 0
