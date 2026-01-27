""" 
AI Draft Generation Module - Complete Article Rewriting with GGUF Models
Generates professional news articles (400-600 words) with AI - OPTIMIZED FOR SPEED

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
    
    def __init__(self, db_path: str, model_name: str = 'models/mistral-7b-instruct-v0.2.Q4_K_M.gguf'):
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
            logger.error("📥 Download mistral-7b from: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
            logger.error("💡 Place model file in: models/ directory")
            logger.error("⚠️  NO SAFE MODE - Article generation will FAIL without model")
        else:
            logger.info("✅ AI Writer LOADED - Full AI generation enabled")
    
    def _detect_model_type(self, model_path: Path) -> str:
        """Auto-detect model type from filename"""
        filename_lower = str(model_path).lower()
        
        if 'phi-2' in filename_lower or 'phi2' in filename_lower:
            return 'phi'
        elif 'mistral' in filename_lower:
            return 'mistral'
        elif 'llama' in filename_lower or 'tinyllama' in filename_lower:
            return 'llama'
        elif 'qwen' in filename_lower:
            return 'qwen'
        else:
            logger.warning(f"⚠️  Could not detect model type from '{model_path.name}', defaulting to 'llama'")
            return 'llama'
    
    def _load_model(self):
        """Load GGUF quantized model - AUTO-DETECT MODEL TYPE - OPTIMIZED FOR SPEED"""
        try:
            from ctransformers import AutoModelForCausalLM
            
            logger.info(f"Loading GGUF model: {self.model_name}")
            
            # Check multiple possible paths (cross-platform compatible)
            possible_paths = [
                Path(self.model_name),  # Direct path provided
                Path('models') / self.model_file,  # models/filename
                Path.home() / '.cache' / 'nexuzy' / 'models' / self.model_file,  # User cache
                Path('models') / 'mistral-7b-instruct-v0.2.Q4_K_M.gguf',  # Recommended model
               Path('models') / 'mistral-7b-instruct-v0.2.Q4_K_M.gguf',  # Alternative quant
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
            
            # Auto-detect model type
            model_type = self._detect_model_type(model_path)
            logger.info(f"🔍 Detected model type: {model_type}")
            
            logger.info(f"⏳ Loading GGUF model from: {model_path} (this may take 10-30 seconds)...")
            
            # Load GGUF model with ctransformers - OPTIMIZED FOR SPEED
            llm = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                model_type=model_type,
                context_length=1024,  # REDUCED from 2048 (2x faster loading)
                max_new_tokens=600,   # REDUCED from 1200 (2x faster generation)
                threads=4,
                gpu_layers=0
            )
            
            logger.info(f"✅ GGUF model loaded successfully: {model_path.name} (type: {model_type})")
            logger.info("⚡ Model optimized for fast generation (30-40s per article)")
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
            
            model = pipeline(
                "text2text-generation",
                model="google/flan-t5-base",
                max_length=150,
                device=-1
            )
            logger.info("✅ Sentence improvement model loaded")
            return model
        except Exception as e:
            logger.warning(f"⚠️  Sentence model unavailable: {e}")
            logger.info("💡 App will use rule-based sentence improvement")
            return None
    
    def improve_sentence(self, sentence: str) -> str:
        if not sentence or len(sentence.strip()) < 10:
            return sentence
        
        if self.sentence_model:
            try:
                prompt = f"Rewrite this sentence to be more professional and clear: {sentence}"
                result = self.sentence_model(prompt, max_length=150, do_sample=False)
                improved = result[0]['generated_text'].strip()
                logger.info(f"AI improved: {sentence[:40]}... → {improved[:40]}...")
                return improved
            except Exception as e:
                logger.error(f"Sentence improvement error: {e}")
        
        improved = sentence.strip()
        if not improved.endswith(('.', '!', '?')):
            improved += '.'
        if improved:
            improved = improved[0].upper() + improved[1:]
        improved = re.sub(r'\s+', ' ', improved)
        
        replacements = {
            'gonna': 'going to', 'wanna': 'want to', 'gotta': 'got to',
            'kinda': 'kind of', 'sorta': 'sort of', 'dunno': "don't know",
            'yeah': 'yes', 'nope': 'no'
        }
        for informal, formal in replacements.items():
            improved = re.sub(r'\b' + informal + r'\b', formal, improved, flags=re.IGNORECASE)
        
        return improved
    
    def _load_translation_keywords(self) -> Dict:
        return {
            'technology': ['ai', 'technology', 'software', 'app', 'digital', 'tech', 'innovation'],
            'business': ['revenue', 'profit', 'stock', 'market', 'business', 'company', 'ceo'],
            'politics': ['government', 'president', 'minister', 'law', 'policy', 'election'],
            'health': ['health', 'medical', 'hospital', 'doctor', 'patient', 'disease'],
            'crisis': ['crisis', 'emergency', 'disaster', 'accident', 'fire', 'flood'],
            'sports': ['team', 'player', 'match', 'game', 'win', 'championship'],
        }
    
    def _extract_topic_info(self, headline: str, summary: str, category: str) -> Dict:
        entities = {'people': [], 'organizations': [], 'places': [], 'events': [], 'numbers': [], 'technical_terms': []}
        full_text = (headline + ' ' + summary).lower()
        original_text = headline + ' ' + summary
        original_words = original_text.split()
        capitalized = [w for w in original_words if w and w[0].isupper() and len(w) > 2 and w not in ['The', 'A', 'An', 'And', 'Or', 'But']]
        numbers = re.findall(r'\d+(?:\.\d+)?%?|\d{1,3}(?:,\d{3})*', headline + ' ' + summary)
        
        return {
            'capitalized_terms': capitalized[:5],  # REDUCED from 15
            'numbers': numbers[:3],  # REDUCED from 10
            'category': category,
        }
    
    def download_and_store_image(self, image_url: str, news_id: int) -> Optional[str]:
        if not image_url:
            return None
        try:
            logger.info(f"Downloading image: {image_url}")
            response = requests.get(image_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code != 200:
                return None
            from PIL import Image
            img = Image.open(BytesIO(response.content))
            images_dir = Path('downloaded_images')
            images_dir.mkdir(exist_ok=True)
            ext = image_url.split('.')[-1].split('?')[0]
            if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                ext = 'jpg'
            filename = f"news_{news_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            filepath = images_dir / filename
            img.save(filepath)
            logger.info(f"✅ Image downloaded: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return None
    
    def generate_draft(self, news_id: int, manual_mode: bool = False, manual_content: str = '') -> Dict:
        try:
            if not self.llm:
                return {'error': '❌ AI model not loaded', 'title': '', 'body_draft': '', 'word_count': 0}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT headline, summary, source_url, source_domain, category, image_url FROM news_queue WHERE id = ?', (news_id,))
            news = cursor.fetchone()
            if not news:
                conn.close()
                return {'error': 'News not found'}
            headline, summary, source_url, source_domain, category, image_url = news
            cursor.execute('SELECT workspace_id FROM news_queue WHERE id = ?', (news_id,))
            workspace_id = cursor.fetchone()[0]
            conn.close()
            
            local_image_path = None
            if image_url:
                local_image_path = self.download_and_store_image(image_url, news_id)
            
            topic_info = self._extract_topic_info(headline, summary or '', category)
            logger.info(f"🤖 Generating article with AI for: {headline[:50]}...")
            draft = self._generate_with_model(headline, summary, category, source_domain, topic_info)
            
            if 'error' in draft or not draft.get('body_draft'):
                return {'error': draft.get('error', 'AI generation failed'), 'title': headline, 'body_draft': '', 'word_count': 0}
            
            draft['image_url'] = image_url or ''
            draft['local_image_path'] = local_image_path or ''
            draft['source_url'] = source_url or ''
            draft['source_domain'] = source_domain or ''
            draft['is_html'] = True
            draft_id = self._store_draft(news_id, workspace_id, draft)
            logger.info(f"✅ Generated draft {draft_id} for news_id {news_id}, words: {draft.get('word_count', 0)}")
            return {**draft, 'id': draft_id}
        except Exception as e:
            logger.error(f"❌ Error generating draft: {e}")
            return {'error': str(e)}
    
    def _generate_with_model(self, headline: str, summary: str, category: str, source: str, topic_info: Dict) -> Dict:
        # SIMPLIFIED PROMPT FOR SPEED
        prompt = f"""Write a 400-word news article.

Headline: {headline}
Summary: {summary}

Write clear paragraphs with facts.

Article:"""
        
        try:
            logger.info("⏳ Generating (30-40s)...")
            generated_text = self.llm(
                prompt,
                max_new_tokens=600,       # OPTIMIZED
                temperature=0.6,          # REDUCED
                top_p=0.9,               # REDUCED
                repetition_penalty=1.2,  # INCREASED
                stop=["\n\n\n\n", "Summary:", "Article:"],
                stream=False
            )
            
            logger.info(f"🔍 Output: {len(str(generated_text)) if generated_text else 0} chars")
            
            if not generated_text or len(str(generated_text)) < 100:
                return {'error': 'AI generated too little text', 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
            
            generated_text = str(generated_text).strip()
            cleaned_text = self._clean_generated_text(generated_text)
            
            if len(cleaned_text) < 100:
                return {'error': 'Cleaned text too short', 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
            
            html_content = self._convert_to_html(cleaned_text)
            word_count = len(cleaned_text.split())
            logger.info(f"✅ Generated {word_count} words")
            
            return {'title': headline, 'body_draft': html_content, 'summary': summary, 'word_count': word_count, 'is_ai_generated': True, 'generation_mode': 'ai_model'}
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            return {'error': f"AI generation failed: {str(e)}", 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
    
    def _clean_generated_text(self, text: str) -> str:
        unwanted = ["Note:", "Disclaimer:", "Generated by", "AI-generated", "As an AI", "I cannot", "I apologize"]
        cleaned = text
        for phrase in unwanted:
            if phrase in cleaned:
                pos = cleaned.find(phrase)
                if pos > 200:
                    cleaned = cleaned[:pos].strip()
                    break
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r'^\s*[-*]\s+', '', cleaned, flags=re.MULTILINE)
        return cleaned.strip()
    
    def _check_column_exists(self, cursor, table: str, column: str) -> bool:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            return column in [col[1] for col in cursor.fetchall()]
        except:
            return False
    
    def _store_draft(self, news_id: int, workspace_id: int, draft: Dict) -> int:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            html_body = draft.get('body_draft', '')
            if draft.get('local_image_path'):
                html_body = f'<figure><img src="{draft["local_image_path"]}" alt="{draft.get("title", "")}" /></figure>\n\n' + html_body
            
            columns = ['workspace_id', 'news_id', 'title', 'body_draft', 'summary', 'word_count', 'image_url', 'source_url', 'generated_at']
            values = [workspace_id, news_id, draft.get('title', ''), html_body, draft.get('summary', ''), draft.get('word_count', 0), draft.get('image_url', ''), draft.get('source_url', ''), datetime.now().isoformat()]
            
            if self._check_column_exists(cursor, 'ai_drafts', 'source_domain'):
                columns.append('source_domain')
                values.append(draft.get('source_domain', ''))
            if self._check_column_exists(cursor, 'ai_drafts', 'is_html'):
                columns.append('is_html')
                values.append(1)
            if self._check_column_exists(cursor, 'ai_drafts', 'generation_mode'):
                columns.append('generation_mode')
                values.append(draft.get('generation_mode', 'unknown'))
            
            cursor.execute(f"INSERT INTO ai_drafts ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in values])})", values)
            conn.commit()
            draft_id = cursor.lastrowid
            conn.close()
            return draft_id
        except Exception as e:
            logger.error(f"❌ Error storing draft: {e}")
            return 0
    
    def _convert_to_html(self, text: str) -> str:
        lines = text.split('\n')
        html_parts = []
        current_paragraph = []
        for line in lines:
            line = line.strip()
            if not line:
                if current_paragraph:
                    html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
                    current_paragraph = []
                continue
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
                current_paragraph.append(line)
        if current_paragraph:
            html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
        return '\n\n'.join(html_parts)
    
    def cleanup_old_queue(self, days: int = 15):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cutoff_date = datetime.now() - timedelta(days=days)
            cursor.execute('UPDATE news_queue SET status = "archived" WHERE fetched_at < ? AND status = "pending"', (cutoff_date.isoformat(),))
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            logger.info(f"Archived {affected} news items older than {days} days")
            return affected
        except Exception as e:
            logger.error(f"❌ Error cleaning queue: {e}")
            return 0
