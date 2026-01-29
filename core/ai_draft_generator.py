""" 
AI Draft Generation Module - LONG ARTICLES (800-2000 words) + FIXED IMAGE DISPLAY
Generates UNIQUE, comprehensive articles with proper image handling

FIXED:
✅ Images now use original URLs (not local paths)
✅ Local download only for watermark check
✅ WordPress gets clean image URLs
✅ 800-2000 word articles
✅ Anti-plagiarism features
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
import hashlib

logger = logging.getLogger(__name__)

# GLOBAL MODEL CACHE
_CACHED_MODEL = None
_CACHED_SENTENCE_MODEL = None

class DraftGenerator:
    """Generate UNIQUE, LONG AI-rewritten news articles (800-2000 words)"""
    
    def __init__(self, db_path: str, model_name: str = 'models/mistral-7b-instruct-v0.2.Q4_K_M.gguf'):
        global _CACHED_MODEL, _CACHED_SENTENCE_MODEL
        
        self.db_path = db_path
        self.model_name = model_name
        self.model_file = Path(model_name).name
        self.translation_keywords = self._load_translation_keywords()
        
        if _CACHED_MODEL:
            logger.info("✅ Using cached AI model")
            self.llm = _CACHED_MODEL
        else:
            logger.info("⏳ Loading AI model...")
            self.llm = self._load_model()
            if self.llm:
                _CACHED_MODEL = self.llm
                logger.info("💾 Model cached")
        
        if _CACHED_SENTENCE_MODEL:
            self.sentence_model = _CACHED_SENTENCE_MODEL
        else:
            self.sentence_model = self._load_sentence_model()
            if self.sentence_model:
                _CACHED_SENTENCE_MODEL = self.sentence_model
        
        if not self.llm:
            logger.error("❌ AI Writer FAILED - GGUF model not found")
        else:
            logger.info("✅ AI Writer LOADED (800-2000 words, Anti-Plagiarism, Fixed Images)")
    
    def _detect_model_type(self, model_path: Path) -> str:
        """Auto-detect model type"""
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
            logger.warning(f"⚠️  Could not detect model type, defaulting to 'llama'")
            return 'llama'
    
    def _load_model(self):
        """Load GGUF model for long articles"""
        try:
            from ctransformers import AutoModelForCausalLM
            
            possible_paths = [
                Path(self.model_name),
                Path('models') / self.model_file,
                Path.home() / '.cache' / 'nexuzy' / 'models' / self.model_file,
                Path('models') / 'mistral-7b-instruct-v0.2.Q4_K_M.gguf',
                Path('models') / 'tinyllama-1.1b-chat-v1.0.Q8_0.gguf',
            ]
            
            model_path = None
            for path in possible_paths:
                if path.exists():
                    model_path = path
                    logger.info(f"✅ Found model: {model_path}")
                    break
            
            if not model_path:
                logger.error("❌ GGUF model not found")
                return None
            
            model_type = self._detect_model_type(model_path)
            logger.info(f"🔍 Model type: {model_type}")
            logger.info("⏳ Loading for long articles (800-2000 words)...")
            
            llm = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                model_type=model_type,
                context_length=2048,
                max_new_tokens=1500,
                threads=4,
                gpu_layers=0
            )
            
            logger.info(f"✅ Model loaded: {model_path.name}")
            return llm
        
        except ImportError:
            logger.error("❌ ctransformers not installed")
            return None
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            return None
    
    def _load_sentence_model(self):
        """Load sentence improvement model (optional)"""
        try:
            from transformers import pipeline
            logger.info("Loading sentence improvement model...")
            
            model = pipeline(
                "text2text-generation",
                model="google/flan-t5-base",
                max_length=150,
                device=-1
            )
            logger.info("✅ Sentence model loaded")
            return model
        except Exception as e:
            logger.warning(f"⚠️  Sentence model unavailable: {e}")
            return None
    
    def improve_sentence(self, sentence: str) -> str:
        """Improve a single sentence"""
        if not sentence or len(sentence.strip()) < 10:
            return sentence
        
        if self.sentence_model:
            try:
                prompt = f"Rewrite this sentence to be more professional and clear: {sentence}"
                result = self.sentence_model(prompt, max_length=150, do_sample=False)
                improved = result[0]['generated_text'].strip()
                return improved
            except Exception as e:
                logger.error(f"Sentence improvement error: {e}")
        
        # Rule-based improvement
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
        """Load keywords for story structure"""
        return {
            'technology': ['ai', 'technology', 'software', 'app', 'digital', 'tech', 'innovation', 'algorithm', 'system', 'platform', 'blockchain', 'quantum', 'machine learning', 'data', 'cloud', 'cyber'],
            'business': ['revenue', 'profit', 'stock', 'market', 'business', 'company', 'ceo', 'investor', 'startup', 'funding', 'acquisition', 'merger', 'sales', 'growth', 'quarterly', 'earnings'],
            'politics': ['government', 'president', 'minister', 'law', 'policy', 'election', 'parliament', 'congress', 'senate', 'legislation', 'vote', 'political', 'campaign', 'diplomat', 'treaty'],
            'health': ['health', 'medical', 'hospital', 'doctor', 'patient', 'disease', 'treatment', 'vaccine', 'coronavirus', 'covid', 'pandemic', 'epidemic', 'virus', 'cure', 'pharmaceutical'],
            'crisis': ['crisis', 'emergency', 'disaster', 'accident', 'fire', 'flood', 'storm', 'earthquake', 'explosion', 'incident', 'tragedy', 'victim', 'damage', 'rescue', 'alert'],
            'sports': ['team', 'player', 'match', 'game', 'win', 'championship', 'score', 'sport', 'athlete', 'coach', 'tournament', 'league', 'competition', 'season', 'victory'],
        }
    
    def _check_title_uniqueness(self, proposed_title: str) -> Dict:
        """Check if title already exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT title FROM ai_drafts WHERE title IS NOT NULL')
            existing_titles = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            proposed_normalized = proposed_title.lower().strip()
            similar_titles = []
            
            for existing in existing_titles:
                existing_normalized = existing.lower().strip()
                
                if proposed_normalized == existing_normalized:
                    logger.warning(f"⚠️  EXACT TITLE MATCH: '{proposed_title}'")
                    similar_titles.append(existing)
                    continue
                
                proposed_words = set(proposed_normalized.split())
                existing_words = set(existing_normalized.split())
                
                if len(proposed_words) < 3:
                    continue
                
                overlap = len(proposed_words & existing_words)
                similarity = overlap / len(proposed_words)
                
                if similarity > 0.7:
                    logger.warning(f"⚠️  SIMILAR TITLE ({similarity:.0%}): '{existing}'")
                    similar_titles.append(existing)
            
            if similar_titles:
                return {
                    'is_unique': False,
                    'similar_titles': similar_titles[:3],
                    'suggestion': self._generate_unique_title_variant(proposed_title)
                }
            
            return {'is_unique': True, 'similar_titles': [], 'suggestion': proposed_title}
            
        except Exception as e:
            logger.error(f"Title uniqueness check failed: {e}")
            return {'is_unique': True, 'similar_titles': [], 'suggestion': proposed_title}
    
    def _generate_unique_title_variant(self, original_title: str) -> str:
        """Generate unique title variant"""
        variations = [
            f"{original_title}: What You Need to Know",
            f"{original_title} - Latest Update",
            f"{original_title}: Key Details Revealed",
            f"{original_title} - Breaking Analysis",
            f"{original_title}: Complete Report",
            f"{original_title} - Comprehensive Guide",
        ]
        return random.choice(variations)
    
    def _extract_topic_info(self, headline: str, summary: str, category: str) -> Dict:
        """Extract topic information"""
        entities = {'people': [], 'organizations': [], 'places': [], 'events': [], 'numbers': [], 'technical_terms': []}
        
        full_text = (headline + ' ' + summary).lower()
        original_text = headline + ' ' + summary
        original_words = original_text.split()
        capitalized = [w for w in original_words if w and w[0].isupper() and len(w) > 2 and w not in ['The', 'A', 'An', 'And', 'Or', 'But']]
        
        numbers = re.findall(r'\d+(?:\.\d+)?%?|\d{1,3}(?:,\d{3})*', headline + ' ' + summary)
        entities['numbers'] = numbers[:10]
        
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
        """Determine main story focus"""
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
    
    def _check_watermark(self, image_url: str) -> bool:
        """
        🔧 FIXED: Download temporarily, check watermark, delete
        Returns: True if image is clean, False if watermarked
        """
        if not image_url:
            return True
        
        try:
            # Download temporarily
            response = requests.get(image_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code != 200:
                return True  # Can't check, allow image
            
            from PIL import Image
            import tempfile
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(response.content)
                temp_path = tmp_file.name
            
            try:
                from core.vision_ai import VisionAI
                vision = VisionAI(self.db_path)
                watermark_check = vision._detect_watermark(temp_path)
                
                # Delete temp file
                os.unlink(temp_path)
                
                if watermark_check['has_watermark'] and watermark_check['confidence'] > 0.6:
                    logger.warning(f"⚠️  WATERMARK DETECTED: {watermark_check['type']} (confidence: {watermark_check['confidence']:.2f})")
                    return False  # Watermarked
                else:
                    logger.info(f"✅ Image clean - no watermark (confidence: {watermark_check['confidence']:.2f})")
                    return True  # Clean
            except Exception as e:
                # Delete temp file on error
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                logger.warning(f"⚠️  Watermark check failed: {e}")
                return True  # Allow image if check fails
                
        except Exception as e:
            logger.warning(f"⚠️  Could not check watermark: {e}")
            return True  # Allow image if download fails
    
    def generate_draft(self, news_id: int, manual_mode: bool = False, manual_content: str = '') -> Dict:
        """Generate UNIQUE, LONG article (800-2000 words)"""
        try:
            if not self.llm:
                error_msg = "❌ AI model not loaded"
                logger.error(error_msg)
                return {'error': error_msg, 'title': '', 'body_draft': '', 'word_count': 0}
            
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
            
            cursor.execute('SELECT workspace_id FROM news_queue WHERE id = ?', (news_id,))
            workspace_id = cursor.fetchone()[0]
            conn.close()
            
            # 🔧 FIXED: Check watermark without storing local file
            original_image_url = image_url  # Keep original URL
            if image_url:
                is_clean = self._check_watermark(image_url)
                if not is_clean:
                    logger.warning("❌ Rejecting watermarked image")
                    image_url = None  # Don't use watermarked image
                    original_image_url = None
            
            topic_info = self._extract_topic_info(headline, summary or '', category)
            
            # CHECK TITLE UNIQUENESS
            title_check = self._check_title_uniqueness(headline)
            if not title_check['is_unique']:
                logger.warning(f"⚠️  Title exists! Using unique variant")
                logger.info(f"💡 New title: {title_check['suggestion']}")
                headline = title_check['suggestion']
            
            logger.info(f"🤖 Generating LONG UNIQUE article (800-2000 words): {headline[:50]}...")
            
            draft = self._generate_with_model(headline, summary, category, source_domain, topic_info)
            
            if 'error' in draft or not draft.get('body_draft'):
                error_msg = draft.get('error', 'AI generation failed')
                logger.error(f"❌ Generation failed: {error_msg}")
                return {'error': error_msg, 'title': headline, 'body_draft': '', 'word_count': 0}
            
            # 🔧 FIXED: Store original URL (not local path)
            draft['image_url'] = original_image_url or ''  # Original URL for WordPress
            draft['source_url'] = source_url or ''
            draft['source_domain'] = source_domain or ''
            draft['is_html'] = True
            
            draft_id = self._store_draft(news_id, workspace_id, draft)
            
            logger.info(f"✅ Generated draft {draft_id}, words: {draft.get('word_count', 0)}")
            return {**draft, 'id': draft_id}
        
        except Exception as e:
            logger.error(f"❌ Error generating draft: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'error': str(e)}
    
    def _generate_with_model(self, headline: str, summary: str, category: str, source: str, topic_info: Dict) -> Dict:
        """Generate LONG article with anti-plagiarism"""
        
        topic_context = f"""Topic: {topic_info['focus']}
Category: {category}
Key Terms: {', '.join(topic_info['capitalized_terms'][:5])}
Statistics: {', '.join(topic_info['numbers'][:3])}"""
        
        writing_styles = [
            "Write in an investigative journalism style",
            "Write in an analytical news reporting style",
            "Write in a feature article narrative style",
            "Write in a breaking news reporting style",
            "Write in an explanatory journalism style"
        ]
        
        unique_angles = [
            "Focus on the broader implications and context",
            "Emphasize the human impact and real-world effects",
            "Analyze the technical and strategic aspects",
            "Explore the historical background and future outlook",
            "Examine the economic and social dimensions"
        ]
        
        style_instruction = random.choice(writing_styles)
        angle_instruction = random.choice(unique_angles)
        
        prompt = f"""You are a professional journalist. {style_instruction}. {angle_instruction}.

Headline: {headline}
Summary: {summary}

{topic_context}

Write a COMPREHENSIVE, DETAILED news article (1000-1200 words minimum) with these sections:

1. INTRODUCTION (100-150 words):
   - Compelling hook
   - Key facts summary  
   - Context

2. BACKGROUND & CONTEXT (200-300 words):
   - Historical context
   - Relevant background
   - Related developments

3. MAIN DETAILS (400-500 words):
   - Important facts
   - Quotes and statistics
   - Multiple angles
   - Thorough explanation

4. ANALYSIS & IMPACT (200-300 words):
   - Implications
   - Future outlook
   - Who is affected

5. CONCLUSION (100-150 words):
   - Key takeaways
   - Next developments

Write in a UNIQUE, original style with:
- Fresh perspective and creative phrasing
- Natural, human-like flow
- Specific details
- Professional tone
- NO generic phrases

Aim for 1000-1200 words.

Article:"""
        
        try:
            logger.info("⏳ Generating LONG content (60-90 seconds)...")
            
            generated_text = self.llm(
                prompt,
                max_new_tokens=1500,
                temperature=0.85,
                top_p=0.92,
                repetition_penalty=1.2,
                stop=["\n\n\n\n", "Article:", "Summary:"],
                stream=False
            )
            
            if not generated_text or not isinstance(generated_text, str):
                generated_text = str(generated_text) if generated_text else ""
            
            generated_text = generated_text.strip()
            
            if len(generated_text) < 500:
                logger.error(f"❌ Generated text too short: {len(generated_text)} chars")
                return {'error': f'AI generated only {len(generated_text)} chars. Need 800+ words.', 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
            
            cleaned_text = self._clean_generated_text(generated_text)
            
            if len(cleaned_text) < 500:
                logger.error("❌ Cleaned text too short")
                return {'error': 'Text too short after cleaning', 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
            
            boosted_text = self._boost_uniqueness(cleaned_text, topic_info)
            html_content = self._convert_to_html(boosted_text)
            
            word_count = len(boosted_text.split())
            
            if word_count < 800:
                logger.warning(f"⚠️  Word count low: {word_count} (target: 800-2000)")
            elif word_count > 2000:
                logger.info(f"✅ Excellent! {word_count} words (exceeds target)")
            else:
                logger.info(f"✅ Perfect! {word_count} words (within range)")
            
            return {
                'title': headline,
                'body_draft': html_content,
                'summary': summary,
                'word_count': word_count,
                'is_ai_generated': True,
                'generation_mode': 'ai_model_long_unique'
            }
        except Exception as e:
            logger.error(f"❌ Model generation error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'error': f"AI generation failed: {str(e)}", 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
    
    def _boost_uniqueness(self, text: str, topic_info: Dict) -> str:
        """Boost content uniqueness"""
        sentences = re.split(r'([.!?]\s+)', text)
        varied_sentences = []
        
        starters = [
            'Additionally, ', 'Furthermore, ', 'Moreover, ', 'In particular, ',
            'Notably, ', 'Significantly, ', 'Importantly, ', 'According to sources, ',
            'Industry experts note that ', 'Analysts suggest that '
        ]
        
        for i, sent in enumerate(sentences):
            if i > 0 and i % 4 == 0 and sent.strip() and len(sent) > 20:
                if not any(sent.strip().startswith(s) for s in starters):
                    if random.random() > 0.7:
                        starter = random.choice(starters)
                        sent = starter + sent.strip()[0].lower() + sent.strip()[1:]
            varied_sentences.append(sent)
        
        return ''.join(varied_sentences)
    
    def _clean_generated_text(self, text: str) -> str:
        """Clean AI-generated text"""
        unwanted_phrases = [
            "Note: This article", "Disclaimer:", "Generated by", "AI-generated",
            "[This article", "This content was", "As an AI", "I cannot", "I apologize"
        ]
        
        cleaned = text
        for phrase in unwanted_phrases:
            if phrase in cleaned:
                pos = cleaned.find(phrase)
                if pos > 500:
                    cleaned = cleaned[:pos].strip()
                    break
        
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r'^\s*[-*]\s+', '', cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _check_column_exists(self, cursor, table: str, column: str) -> bool:
        """Check if column exists"""
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            return column in columns
        except Exception:
            return False
    
    def _store_draft(self, news_id: int, workspace_id: int, draft: Dict) -> int:
        """
        🔧 FIXED: Store draft WITHOUT local image path in HTML
        Image URL is stored separately for WordPress to handle
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 🔧 CRITICAL: Don't add local image path to HTML body!
            # WordPress will handle the featured_media from image_url field
            html_body = draft.get('body_draft', '')
            
            # Image URL stored separately - WordPress uploads from this URL
            columns = ['workspace_id', 'news_id', 'title', 'body_draft', 'summary', 'word_count', 'image_url', 'source_url', 'generated_at']
            values = [
                workspace_id, news_id, draft.get('title', ''), html_body,
                draft.get('summary', ''), draft.get('word_count', 0),
                draft.get('image_url', ''),  # Original URL - WordPress downloads from this
                draft.get('source_url', ''),
                datetime.now().isoformat()
            ]
            
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
            
            cursor.execute(f'INSERT INTO ai_drafts ({column_names}) VALUES ({placeholders})', values)
            
            conn.commit()
            draft_id = cursor.lastrowid
            conn.close()
            
            logger.info(f"✅ Stored draft {draft_id} with image URL: {draft.get('image_url', 'None')[:50]}...")
            
            return draft_id
        
        except Exception as e:
            logger.error(f"❌ Error storing draft: {e}")
            return 0
    
    def _convert_to_html(self, text: str) -> str:
        """Convert text to HTML"""
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
            elif line.endswith(':') and len(line) < 80 and len(line.split()) <= 8:
                if current_paragraph:
                    html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
                    current_paragraph = []
                html_parts.append(f"<h3>{line}</h3>")
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
        """Remove old news from queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
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
            logger.error(f"❌ Error cleaning up: {e}")
            return 0
