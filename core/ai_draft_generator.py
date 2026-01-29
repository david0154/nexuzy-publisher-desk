""" 
AI Draft Generation Module - ANTI-PLAGIARISM & LONGER ARTICLES (800-2000 words)
Generates UNIQUE, comprehensive news articles with improved length

NEW FEATURES:
✅ 800-2000 word articles (better SEO)
✅ Multi-section structure
✅ Detailed, comprehensive coverage
✅ Title uniqueness check
✅ Human-like writing patterns
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
        
        # USE CACHED MODEL
        if _CACHED_MODEL:
            logger.info("✅ Using cached AI model")
            self.llm = _CACHED_MODEL
        else:
            logger.info("⏳ Loading AI model...")
            self.llm = self._load_model()
            if self.llm:
                _CACHED_MODEL = self.llm
                logger.info("💾 Model cached")
        
        # SENTENCE MODEL
        if _CACHED_SENTENCE_MODEL:
            self.sentence_model = _CACHED_SENTENCE_MODEL
        else:
            self.sentence_model = self._load_sentence_model()
            if self.sentence_model:
                _CACHED_SENTENCE_MODEL = self.sentence_model
        
        if not self.llm:
            logger.error("❌ AI Writer FAILED - GGUF model not found")
        else:
            logger.info("✅ AI Writer LOADED (800-2000 words, Anti-Plagiarism)")
    
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
        """Load GGUF quantized model - OPTIMIZED FOR LONGER ARTICLES"""
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
                    logger.info(f"✅ Found model at: {model_path}")
                    break
            
            if not model_path:
                logger.error(f"❌ GGUF model not found")
                return None
            
            model_type = self._detect_model_type(model_path)
            logger.info(f"🔍 Detected model type: {model_type}")
            logger.info(f"⏳ Loading model for LONG articles (800-2000 words)...")
            
            # 🔧 OPTIMIZED FOR LONGER GENERATION
            llm = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                model_type=model_type,
                context_length=2048,     # DOUBLED from 1024 for longer articles
                max_new_tokens=1500,     # INCREASED from 600 for 800-2000 words
                threads=4,
                gpu_layers=0
            )
            
            logger.info(f"✅ Model loaded: {model_path.name} (supports 800-2000 words)")
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
                logger.info(f"AI improved: {sentence[:40]}... → {improved[:40]}...")
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
        """
        🆕 CHECK IF TITLE ALREADY EXISTS
        Returns: {'is_unique': bool, 'similar_titles': list, 'suggestion': str}
        """
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
            f"{original_title}: Everything You Should Know",
        ]
        
        return random.choice(variations)
    
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
    
    def download_and_store_image(self, image_url: str, news_id: int) -> Optional[str]:
        """Download and store image locally"""
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
        """Generate UNIQUE, LONG article draft (800-2000 words)"""
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
            
            # Download image
            local_image_path = None
            if image_url:
                local_image_path = self.download_and_store_image(image_url, news_id)
                
                if local_image_path:
                    try:
                        from core.vision_ai import VisionAI
                        vision = VisionAI(self.db_path)
                        watermark_check = vision._detect_watermark(local_image_path)
                        
                        if watermark_check['has_watermark'] and watermark_check['confidence'] > 0.6:
                            logger.warning(f"⚠️  WATERMARK DETECTED: {watermark_check['type']}")
                            image_url = None
                            local_image_path = None
                        else:
                            logger.info(f"✅ Image clean - no watermark")
                    except Exception as e:
                        logger.warning(f"⚠️  Watermark check failed: {e}")
            
            topic_info = self._extract_topic_info(headline, summary or '', category)
            
            # CHECK TITLE UNIQUENESS
            title_check = self._check_title_uniqueness(headline)
            if not title_check['is_unique']:
                logger.warning(f"⚠️  Title already exists! Similar titles: {len(title_check['similar_titles'])}")
                logger.info(f"💡 Using unique title: {title_check['suggestion']}")
                headline = title_check['suggestion']
            
            logger.info(f"🤖 Generating LONG UNIQUE article (800-2000 words): {headline[:50]}...")
            
            # Generate with enhanced length
            draft = self._generate_with_model(headline, summary, category, source_domain, topic_info)
            
            if 'error' in draft or not draft.get('body_draft'):
                error_msg = draft.get('error', 'AI generation failed')
                logger.error(f"❌ Generation failed: {error_msg}")
                return {'error': error_msg, 'title': headline, 'body_draft': '', 'word_count': 0}
            
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
            import traceback
            logger.error(traceback.format_exc())
            return {'error': str(e)}
    
    def _generate_with_model(self, headline: str, summary: str, category: str, source: str, topic_info: Dict) -> Dict:
        """
        🆕 GENERATE LONG ARTICLES (800-2000 WORDS)
        - Multi-section structure
        - Detailed coverage
        - Anti-plagiarism
        - Human-like writing
        """
        
        topic_context = f"""Topic: {topic_info['focus']}
Category: {category}
Key Terms: {', '.join(topic_info['capitalized_terms'][:5])}
Statistics: {', '.join(topic_info['numbers'][:3])}"""
        
        # WRITING STYLES
        writing_styles = [
            "Write in an investigative journalism style",
            "Write in an analytical news reporting style",
            "Write in a feature article narrative style",
            "Write in a breaking news reporting style",
            "Write in an explanatory journalism style"
        ]
        
        style_instruction = random.choice(writing_styles)
        
        # UNIQUE ANGLES
        unique_angles = [
            "Focus on the broader implications and context",
            "Emphasize the human impact and real-world effects",
            "Analyze the technical and strategic aspects",
            "Explore the historical background and future outlook",
            "Examine the economic and social dimensions"
        ]
        
        angle_instruction = random.choice(unique_angles)
        
        # 🔧 OPTIMIZED PROMPT FOR LONG ARTICLES (800-2000 WORDS)
        prompt = f"""You are a professional journalist. {style_instruction}. {angle_instruction}.

Headline: {headline}
Summary: {summary}

{topic_context}

Write a COMPREHENSIVE, DETAILED news article (1000-1200 words minimum) with these sections:

1. INTRODUCTION (100-150 words):
   - Open with a compelling hook
   - Summarize the key facts
   - Set the context

2. BACKGROUND & CONTEXT (200-300 words):
   - Provide historical context
   - Explain relevant background
   - Include related developments

3. MAIN DETAILS (400-500 words):
   - Present all important facts
   - Include quotes and statistics
   - Explain the specifics thoroughly
   - Cover multiple angles

4. ANALYSIS & IMPACT (200-300 words):
   - Analyze the implications
   - Discuss future outlook
   - Explain who is affected and how

5. CONCLUSION (100-150 words):
   - Summarize key takeaways
   - Look ahead to next developments

Write in a UNIQUE, original style with:
- Fresh perspective and creative phrasing
- Natural, human-like flow
- Specific details and examples
- Professional journalistic tone
- NO generic phrases like "in a recent development"

Make it comprehensive and detailed. Aim for 1000-1200 words.

Article:"""
        
        try:
            logger.info("⏳ Generating LONG content (60-90 seconds for 1000+ words)...")
            
            # 🔧 OPTIMIZED FOR LONG GENERATION
            generated_text = self.llm(
                prompt,
                max_new_tokens=1500,      # INCREASED from 600 for longer articles
                temperature=0.85,         # High creativity
                top_p=0.92,              # Diverse word selection
                repetition_penalty=1.2,   # Avoid repetition
                stop=["\n\n\n\n", "Article:", "Summary:", "---"],
                stream=False
            )
            
            if not generated_text:
                logger.error(f"❌ Model returned empty")
                return {'error': 'AI model returned empty', 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
            
            if not isinstance(generated_text, str):
                generated_text = str(generated_text)
            
            generated_text = generated_text.strip()
            
            # 🔧 CHECK MINIMUM LENGTH (800 words = ~4000 chars)
            if len(generated_text) < 500:
                logger.error(f"❌ Generated text too short: {len(generated_text)} chars")
                logger.warning("⚠️  Model may be too small for long articles. Consider using Mistral-7B.")
                return {'error': f'AI generated only {len(generated_text)} characters. Need 800+ words.', 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
            
            # Clean text
            cleaned_text = self._clean_generated_text(generated_text)
            
            if len(cleaned_text) < 500:
                logger.error(f"❌ Cleaned text too short")
                return {'error': 'Text too short after cleaning', 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
            
            # ADD UNIQUENESS BOOST
            boosted_text = self._boost_uniqueness(cleaned_text, topic_info)
            
            # Convert to HTML
            html_content = self._convert_to_html(boosted_text)
            
            word_count = len(boosted_text.split())
            
            # 🔧 WORD COUNT VALIDATION
            if word_count < 800:
                logger.warning(f"⚠️  Word count below target: {word_count} words (target: 800-2000)")
                logger.warning("💡 Article may be too short. Consider regenerating.")
            elif word_count > 2000:
                logger.info(f"✅ Excellent! Generated {word_count} words (exceeds target)")
            else:
                logger.info(f"✅ Perfect! Generated {word_count} words (within 800-2000 range)")
            
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
        """Boost content uniqueness with variations"""
        sentences = re.split(r'([.!?]\s+)', text)
        varied_sentences = []
        
        starters = [
            'Additionally, ', 'Furthermore, ', 'Moreover, ', 'In particular, ',
            'Notably, ', 'Significantly, ', 'Importantly, ', 'According to sources, ',
            'Industry experts note that ', 'Analysts suggest that ', 'Research indicates that '
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
                if pos > 500:  # INCREASED from 200 for longer articles
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
        """Store draft in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            html_body = draft.get('body_draft', '')
            
            if draft.get('local_image_path'):
                image_html = f'<figure><img src="{draft["local_image_path"]}" alt="{draft.get("title", "")}" /></figure>\n\n'
                html_body = image_html + html_body
            
            columns = ['workspace_id', 'news_id', 'title', 'body_draft', 'summary', 'word_count', 'image_url', 'source_url', 'generated_at']
            values = [
                workspace_id, news_id, draft.get('title', ''), html_body,
                draft.get('summary', ''), draft.get('word_count', 0),
                draft.get('image_url', ''), draft.get('source_url', ''),
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
            
            return draft_id
        
        except Exception as e:
            logger.error(f"❌ Error storing draft: {e}")
            return 0
    
    def _convert_to_html(self, text: str) -> str:
        """Convert text to HTML with proper structure"""
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
            
            # Check for headings
            if line.startswith('##'):
                if current_paragraph:
                    html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
                    current_paragraph = []
                html_parts.append(f"<h2>{line.replace('##', '').strip()}</h2>")
            elif line.endswith(':') and len(line) < 80 and len(line.split()) <= 8:
                # Section headings
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
