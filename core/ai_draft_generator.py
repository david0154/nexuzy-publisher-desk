""" 
AI Draft Generation Module - Complete Article Rewriting with GGUF Models
Generates professional news articles (800-1200 words) with AI

REQUIRES: GGUF model file in models/ directory
NO SAFE MODE - Fails gracefully if model not available
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
    """Generate complete AI-rewritten news articles with GGUF models"""
    
    def __init__(self, db_path: str, model_name: str = 'models/tinyllama-1.1b-chat-v1.0.Q8_0.gguf'):
        self.db_path = db_path
        self.model_name = model_name
        self.model_file = Path(model_name).name  # Extract filename from path
        self.llm = self._load_model()
        self.translation_keywords = self._load_translation_keywords()
        
        # Initialize sentence improvement model (optional, non-blocking)
        self.sentence_model = self._load_sentence_model()
        
        # Model status - FAIL if model not loaded
        if not self.llm:
            logger.error("❌ AI Writer FAILED - GGUF model not found")
            logger.error("📥 Download model from: https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF")
            logger.error("💡 Place model file in: models/ directory")
            logger.error("⚠️  NO SAFE MODE - Article generation will FAIL without model")
        else:
            logger.info("✅ AI Writer LOADED - Full AI generation enabled")
    
    def _load_model(self):
        """Load GGUF quantized model - NO FALLBACK"""
        try:
            from ctransformers import AutoModelForCausalLM
            
            logger.info(f"Loading GGUF model: {self.model_name}")
            
            # Check multiple possible paths (cross-platform compatible)
            possible_paths = [
                Path(self.model_name),  # Direct path provided
                Path('models') / self.model_file,  # models/filename
                Path.home() / '.cache' / 'nexuzy' / 'models' / self.model_file,  # User cache
                Path('models') / 'tinyllama-1.1b-chat-v1.0.Q8_0.gguf',  # Explicit fallback
                Path('models') / 'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',  # Alternative quant
            ]
            
            model_path = None
            for path in possible_paths:
                if path.exists():
                    model_path = path
                    logger.info(f"✅ Found model at: {model_path}")
                    break
            
            if not model_path:
                logger.error(f"❌ GGUF model not found. Checked paths:")
                for p in possible_paths:
                    logger.error(f"  ✗ {p}")
                return None
            
            logger.info(f"⏳ Loading GGUF model from: {model_path} (this may take 10-30 seconds)...")
            
            # Load GGUF model with ctransformers
            llm = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                model_type='llama',
                context_length=2048,  # Increased for longer articles
                max_new_tokens=1200,
                threads=4,  # Use more CPU threads
                gpu_layers=0  # CPU only
            )
            
            logger.info(f"✅ GGUF model loaded successfully: {model_path.name}")
            return llm
        
        except ImportError:
            logger.error("❌ ctransformers not installed")
            logger.error("📥 Install: pip install ctransformers")
            return None
        except Exception as e:
            logger.error(f"❌ Error loading GGUF model: {e}")
            return None
    
    def _load_sentence_model(self):
        """Load lightweight sentence improvement model (non-blocking, optional)"""
        try:
            from transformers import pipeline
            logger.info("Loading sentence improvement model (flan-t5-base)...")
            
            # Try with timeout handling
            model = pipeline(
                "text2text-generation",
                model="google/flan-t5-base",
                max_length=150,
                device=-1  # CPU only
            )
            logger.info("✅ Sentence improvement model loaded")
            return model
        except Exception as e:
            logger.warning(f"⚠️  Sentence model unavailable (network timeout or error): {e}")
            logger.info("💡 App will use rule-based sentence improvement")
            return None
    
    def improve_sentence(self, sentence: str) -> str:
        """
        Improve a single sentence with AI or rule-based enhancement
        Used by WYSIWYG editor's "🤖 Improve Sentence" button
        """
        if not sentence or len(sentence.strip()) < 10:
            return sentence
        
        # Try AI model if available
        if self.sentence_model:
            try:
                prompt = f"Rewrite this sentence to be more professional and clear: {sentence}"
                result = self.sentence_model(prompt, max_length=150, do_sample=False)
                improved = result[0]['generated_text'].strip()
                logger.info(f"AI improved: {sentence[:40]}... → {improved[:40]}...")
                return improved
            except Exception as e:
                logger.error(f"Sentence improvement error: {e}")
        
        # Fallback: Rule-based improvement
        improved = sentence.strip()
        
        # Add period if missing
        if not improved.endswith(('.', '!', '?')):
            improved += '.'
        
        # Capitalize first letter
        if improved:
            improved = improved[0].upper() + improved[1:]
        
        # Remove multiple spaces
        improved = re.sub(r'\s+', ' ', improved)
        
        # Replace informal words
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
        Download image from URL and store locally
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
            logger.info(f"✅ Image downloaded: {filepath}")
            
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return None
    
    def generate_draft(self, news_id: int, manual_mode: bool = False, manual_content: str = '') -> Dict:
        """
        Generate complete article draft with AI - NO FALLBACK MODE
        Fails if AI model not available
        """
        try:
            # Check if model is loaded
            if not self.llm:
                error_msg = "❌ AI model not loaded. Cannot generate article. Download GGUF model first."
                logger.error(error_msg)
                return {
                    'error': error_msg,
                    'title': '',
                    'body_draft': '',
                    'word_count': 0
                }
            
            # Get news details
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT headline, summary, source_url, source_domain, category, image_url
                FROM news_queue WHERE id = ?
            ''', (news_id,))
            
            news = cursor.fetchone()
            if not news:
                conn.close()
                return {'error': 'News not found'}
            
            headline, summary, source_url, source_domain, category, image_url = news
            
            # Get workspace_id
            cursor.execute('SELECT workspace_id FROM news_queue WHERE id = ?', (news_id,))
            workspace_id = cursor.fetchone()[0]
            conn.close()
            
            # Download and store image locally (optional)
            local_image_path = None
            if image_url:
                local_image_path = self.download_and_store_image(image_url, news_id)
            
            # Extract topic information
            topic_info = self._extract_topic_info(headline, summary or '', category)
            
            # Generate with AI model (REQUIRED)
            logger.info(f"🤖 Generating article with AI for: {headline[:50]}...")
            draft = self._generate_with_model(headline, summary, category, source_domain, topic_info)
            
            # Store original image URL for WordPress upload
            draft['image_url'] = image_url or ''  # IMPORTANT: Keep original URL
            draft['local_image_path'] = local_image_path or ''
            draft['source_url'] = source_url or ''
            draft['source_domain'] = source_domain or ''
            draft['is_html'] = True
            
            # Store draft
            draft_id = self._store_draft(news_id, workspace_id, draft)
            
            logger.info(f"✅ Generated draft {draft_id} for news_id {news_id}, words: {draft.get('word_count', 0)}")
            return {**draft, 'id': draft_id}
        
        except Exception as e:
            logger.error(f"❌ Error generating draft: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'error': str(e)}
    
    def _generate_with_model(self, headline: str, summary: str, category: str, source: str, topic_info: Dict) -> Dict:
        """Generate complete article with AI model - FIXED PROMPT AND PARAMETERS"""
        
        topic_context = f"""Topic: {topic_info['focus']}
Category: {category}
Key Terms: {', '.join(topic_info['capitalized_terms'][:5])}
Statistics: {', '.join(topic_info['numbers'][:3])}"""
        
        # IMPROVED PROMPT - Natural article structure
        prompt = f"""<s>[INST] You are a professional journalist. Write a complete, detailed news article (800-1200 words) based on this headline.

Headline: {headline}
Summary: {summary}

{topic_context}

Write in professional journalism style with these sections:
1. Introduction (lead paragraph)
2. Background and context
3. Key details and facts
4. Analysis and implications
5. Future outlook (brief)

Rules:
- Be factual, objective, and professional
- Use clear, journalistic language
- Include relevant details from the summary
- Do not mention AI, bots, or automation
- Write naturally without meta-commentary

Write the complete article now:[/INST]"""
        
        try:
            logger.info("⏳ Generating with AI model (30-60 seconds)...")
            
            generated_text = self.llm(
                prompt,
                max_new_tokens=1200,  # INCREASED from 512
                temperature=0.7,       # Slightly creative
                top_p=0.95,            # Better diversity
                repetition_penalty=1.15,  # Reduce repetition
                stop=["</s>", "[INST]", "[/INST]"],  # REMOVED aggressive stops
                stream=False
            )
            
            # Clean the generated text
            cleaned_text = self._clean_generated_text(generated_text)
            
            # Convert to HTML
            html_content = self._convert_to_html(cleaned_text)
            
            word_count = len(cleaned_text.split())
            logger.info(f"✅ AI generated {word_count} words")
            
            return {
                'title': headline,
                'body_draft': html_content,
                'summary': summary,
                'word_count': word_count,
                'is_ai_generated': True,
                'generation_mode': 'ai_model'
            }
        except Exception as e:
            logger.error(f"❌ Model generation error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'error': f"AI generation failed: {str(e)}",
                'title': headline,
                'body_draft': '',
                'summary': summary,
                'word_count': 0
            }
    
    def _clean_generated_text(self, text: str) -> str:
        """Clean and format AI-generated text"""
        # Remove unwanted disclaimers
        unwanted_phrases = [
            "Note: This article",
            "Disclaimer:",
            "Generated by",
            "AI-generated",
            "[This article",
            "This content was",
            "As an AI",
            "I cannot",
            "I apologize"
        ]
        
        cleaned = text
        for phrase in unwanted_phrases:
            if phrase in cleaned:
                pos = cleaned.find(phrase)
                if pos > 200:  # Only cut if substantial content exists
                    cleaned = cleaned[:pos].strip()
                    break
        
        # Clean up formatting
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)  # Max 2 newlines
        cleaned = re.sub(r'^\s*[-*]\s+', '', cleaned, flags=re.MULTILINE)  # Remove bullets
        cleaned = cleaned.strip()
        
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
            
            html_body = draft.get('body_draft', '')
            
            # Embed local image in HTML if available (for preview)
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
                draft.get('image_url', ''),  # Store original URL for WordPress
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
        """Convert plain text / markdown to proper HTML"""
        lines = text.split('\n')
        html_parts = []
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                # Empty line - end current paragraph
                if current_paragraph:
                    html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
                    current_paragraph = []
                continue
            
            # Check if it's a heading
            if line.startswith('##'):
                if current_paragraph:
                    html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
                    current_paragraph = []
                html_parts.append(f"<h2>{line.replace('##', '').strip()}</h2>")
            elif line.isupper() and len(line) < 60 and len(line.split()) > 1:
                if current_paragraph:
                    html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
                    current_paragraph = []
                html_parts.append(f"<h2>{line.title()}</h2>")
            else:
                # Regular text - add to paragraph
                current_paragraph.append(line)
        
        # Add final paragraph
        if current_paragraph:
            html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
        
        return '\n\n'.join(html_parts)
    
    def cleanup_old_queue(self, days: int = 15):
        """Remove news items older than specified days from queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # FIXED: Use fetched_at instead of created_at (column doesn't exist)
            cursor.execute('''
                UPDATE news_queue
                SET status = 'archived'
                WHERE fetched_at < ? AND status = 'pending'
            ''', (cutoff_date.isoformat(),))
            
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            
            logger.info(f"Archived {affected_rows} news items older than {days} days")
            return affected_rows
        
        except Exception as e:
            logger.error(f"❌ Error cleaning up queue: {e}")
            return 0
