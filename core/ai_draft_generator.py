""" 
AI Draft Generation Module - CLEAN ARTICLES (No Section Headers)
Generates UNIQUE, comprehensive articles WITHOUT visible structure labels

FEATURES:
✅ 800-2000 word articles
✅ Anti-plagiarism system
✅ MANDATORY title uniqueness and rewrite
✅ Enhanced human-like writing
✅ Local image download (WORKING!)
✅ Watermark detection
✅ Clean output (no "Introduction:", "Main Details:" headers)
✅ Synonym variation for uniqueness
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

# Enhanced synonym dictionary for uniqueness
SYNONYM_DICT = {
    'said': ['stated', 'mentioned', 'noted', 'explained', 'announced', 'revealed', 'reported', 'disclosed'],
    'new': ['recent', 'latest', 'fresh', 'novel', 'emerging', 'modern', 'contemporary'],
    'big': ['significant', 'substantial', 'considerable', 'major', 'large-scale', 'extensive'],
    'important': ['crucial', 'vital', 'essential', 'critical', 'key', 'significant', 'pivotal'],
    'show': ['demonstrate', 'illustrate', 'reveal', 'indicate', 'display', 'exhibit'],
    'many': ['numerous', 'multiple', 'several', 'various', 'countless'],
    'good': ['positive', 'beneficial', 'favorable', 'advantageous', 'promising'],
    'bad': ['negative', 'adverse', 'unfavorable', 'detrimental', 'problematic'],
    'make': ['create', 'produce', 'generate', 'develop', 'establish'],
    'use': ['utilize', 'employ', 'apply', 'leverage', 'implement'],
    'get': ['obtain', 'acquire', 'receive', 'secure', 'gain'],
    'very': ['extremely', 'highly', 'particularly', 'exceptionally', 'remarkably'],
    'problem': ['issue', 'challenge', 'concern', 'difficulty', 'complication'],
    'change': ['transform', 'modify', 'alter', 'adjust', 'revise'],
    'help': ['assist', 'aid', 'support', 'facilitate', 'contribute to'],
}

# Title rewrite templates
TITLE_PATTERNS = [
    "{topic}: What This Means for {audience}",
    "Breaking: {topic} - Key Details Revealed",
    "{topic}: A Comprehensive Analysis",
    "Understanding {topic}: The Full Story",
    "{topic}: Impact and Implications",
    "How {topic} Will Change {industry}",
    "{topic}: Expert Analysis and Insights",
    "The Truth About {topic}: What You Need to Know",
    "{topic}: Latest Developments and Updates",
    "Inside {topic}: Complete Report",
]

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
            logger.info("✅ AI Writer LOADED (800-2000 words, Clean Output)")
    
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
    
    def _rewrite_title_mandatory(self, original_headline: str, category: str, topic_info: Dict) -> str:
        """
        🔥 MANDATORY title rewrite - ALWAYS creates unique title
        """
        logger.info(f"🔄 Rewriting title (MANDATORY): {original_headline}")
        
        # Extract key topic
        words = original_headline.split()
        capitalized = [w for w in words if w and len(w) > 2 and w[0].isupper()]
        
        # Get main topic (first 2-3 capitalized words or main subject)
        if capitalized:
            topic = ' '.join(capitalized[:3])
        else:
            # Use first 3-5 words
            topic = ' '.join(words[:5])
        
        # Determine audience based on category
        audience_map = {
            'Technology': 'Tech Industry',
            'Business': 'Investors',
            'Politics': 'Citizens',
            'Health': 'Public Health',
            'Sports': 'Fans',
            'Entertainment': 'Audiences',
        }
        audience = audience_map.get(category, 'Readers')
        
        industry_map = {
            'Technology': 'the Tech Sector',
            'Business': 'Markets',
            'Politics': 'Governance',
            'Health': 'Healthcare',
            'Sports': 'Sports World',
            'Entertainment': 'Entertainment Industry',
        }
        industry = industry_map.get(category, 'the Industry')
        
        # Select random pattern
        pattern = random.choice(TITLE_PATTERNS)
        
        # Apply pattern
        new_title = pattern.format(topic=topic, audience=audience, industry=industry)
        
        # Verify uniqueness
        uniqueness_check = self._check_title_uniqueness(new_title)
        
        if not uniqueness_check['is_unique']:
            # If still not unique, add timestamp-based variation
            new_title = f"{topic}: Complete Analysis ({datetime.now().strftime('%B %Y')})"
            logger.warning(f"⚠️  Pattern title not unique, using timestamped version")
        
        logger.info(f"✅ NEW TITLE: {new_title}")
        return new_title
    
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
        """Generate UNIQUE, LONG article (800-2000 words) with MANDATORY title rewrite"""
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
            
            # Download image locally
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
            
            # 🔥 MANDATORY TITLE REWRITE - ALWAYS generates new unique title
            new_title = self._rewrite_title_mandatory(headline, category, topic_info)
            
            logger.info(f"🤖 Generating LONG UNIQUE article (800-2000 words): {new_title[:50]}...")
            
            draft = self._generate_with_model(new_title, summary, category, source_domain, topic_info)
            
            if 'error' in draft or not draft.get('body_draft'):
                error_msg = draft.get('error', 'AI generation failed')
                logger.error(f"❌ Generation failed: {error_msg}")
                return {'error': error_msg, 'title': new_title, 'body_draft': '', 'word_count': 0}
            
            draft['image_url'] = image_url or ''
            draft['local_image_path'] = local_image_path or ''
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
    
    def _apply_synonym_variation(self, text: str) -> str:
        """
        🔥 NEW: Apply synonym replacement for uniqueness
        """
        words = text.split()
        varied_words = []
        
        for word in words:
            word_lower = word.lower().strip('.,!?;:')
            
            # 30% chance to replace with synonym
            if word_lower in SYNONYM_DICT and random.random() < 0.3:
                synonym = random.choice(SYNONYM_DICT[word_lower])
                # Preserve capitalization
                if word[0].isupper():
                    synonym = synonym.capitalize()
                varied_words.append(synonym)
            else:
                varied_words.append(word)
        
        return ' '.join(varied_words)
    
    def _generate_with_model(self, headline: str, summary: str, category: str, source: str, topic_info: Dict) -> Dict:
        """Generate LONG article with anti-plagiarism and human touch"""
        
        topic_context = f"""Topic: {topic_info['focus']}
Category: {category}
Key Terms: {', '.join(topic_info['capitalized_terms'][:5])}
Statistics: {', '.join(topic_info['numbers'][:3])}"""
        
        # Human-like writing styles
        writing_styles = [
            "Write like an experienced journalist with 10+ years experience",
            "Write in a clear, accessible style that engages readers",
            "Write with authority and depth, like a subject matter expert",
            "Write in a narrative style that tells the complete story",
            "Write analytically, connecting facts to broader implications"
        ]
        
        unique_angles = [
            "Focus on the real-world impact and practical implications",
            "Emphasize the human stories and personal experiences involved",
            "Analyze the strategic and economic dimensions",
            "Explore historical context and future projections",
            "Examine the technical details and underlying mechanisms"
        ]
        
        style_instruction = random.choice(writing_styles)
        angle_instruction = random.choice(unique_angles)
        
        # 🔥 IMPROVED PROMPT with human touch instructions
        prompt = f"""You are a professional journalist. {style_instruction}. {angle_instruction}.

Headline: {headline}
Summary: {summary}

{topic_context}

Write a comprehensive news article (1000-1200 words). Requirements:

1. Write naturally with varied sentence structure (mix short and long sentences)
2. Use active voice predominantly  
3. Include specific details, quotes, and facts
4. Connect ideas with smooth transitions
5. Write conversationally but professionally
6. Vary paragraph length (2-5 sentences)
7. Use concrete examples when possible

CRITICAL - DO NOT:
- Include section labels ("Introduction:", "Background:", "Conclusion:")
- Start multiple paragraphs with "Industry experts note that"
- Use repetitive sentence starters
- Write in a robotic, formulaic style
- Include meta-commentary about the article itself

Write the article now in flowing, natural paragraphs:

Article:"""
        
        try:
            logger.info("⏳ Generating LONG content with human touch (60-90 seconds)...")
            
            generated_text = self.llm(
                prompt,
                max_new_tokens=1500,
                temperature=0.88,  # Slightly higher for more creativity
                top_p=0.93,
                repetition_penalty=1.25,  # Stronger penalty
                stop=["\n\n\n\n", "Article:", "Summary:", "Note:"],
                stream=False
            )
            
            if not generated_text or not isinstance(generated_text, str):
                generated_text = str(generated_text) if generated_text else ""
            
            generated_text = generated_text.strip()
            
            if len(generated_text) < 500:
                logger.error(f"❌ Generated text too short: {len(generated_text)} chars")
                return {'error': f'AI generated only {len(generated_text)} chars. Need 800+ words.', 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
            
            # 🔧 CLEAN: Remove section headers and repetitive phrases
            cleaned_text = self._clean_generated_text(generated_text)
            
            if len(cleaned_text) < 500:
                logger.error("❌ Cleaned text too short")
                return {'error': 'Text too short after cleaning', 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
            
            # 🔥 Apply synonym variation for uniqueness
            varied_text = self._apply_synonym_variation(cleaned_text)
            
            # Boost uniqueness further
            boosted_text = self._boost_uniqueness(varied_text, topic_info)
            
            # Convert to HTML
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
                'generation_mode': 'ai_model_long_unique_v2'
            }
        except Exception as e:
            logger.error(f"❌ Model generation error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'error': f"AI generation failed: {str(e)}", 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
    
    def _boost_uniqueness(self, text: str, topic_info: Dict) -> str:
        """Boost content uniqueness with varied sentence starters"""
        sentences = re.split(r'([.!?]\s+)', text)
        varied_sentences = []
        
        # More diverse sentence starters
        starters = [
            'Additionally, ', 'Furthermore, ', 'Moreover, ', 'In particular, ',
            'Notably, ', 'Significantly, ', 'Importantly, ', 'According to analysts, ',
            'Recent reports suggest that ', 'Data indicates that ', 'Experts observe that ',
            'Meanwhile, ', 'Conversely, ', 'In contrast, ', 'As a result, ',
            'Consequently, ', 'Nevertheless, ', 'On the other hand, '
        ]
        
        used_starters = set()
        
        for i, sent in enumerate(sentences):
            if i > 0 and i % 4 == 0 and sent.strip() and len(sent) > 20:
                # Don't reuse starters
                available_starters = [s for s in starters if s not in used_starters]
                if not available_starters:
                    used_starters.clear()
                    available_starters = starters
                
                if not any(sent.strip().startswith(s) for s in starters):
                    if random.random() > 0.6:
                        starter = random.choice(available_starters)
                        used_starters.add(starter)
                        sent = starter + sent.strip()[0].lower() + sent.strip()[1:]
            varied_sentences.append(sent)
        
        return ''.join(varied_sentences)
    
    def _clean_generated_text(self, text: str) -> str:
        """
        🔧 IMPROVED: Clean AI-generated text and remove all section markers
        """
        unwanted_phrases = [
            "Note: This article", "Disclaimer:", "Generated by", "AI-generated",
            "[This article", "This content was", "As an AI", "I cannot", "I apologize",
            "In conclusion,", "To summarize,", "In summary,"
        ]
        
        cleaned = text
        
        # Remove unwanted phrases
        for phrase in unwanted_phrases:
            if phrase in cleaned:
                pos = cleaned.find(phrase)
                if pos > 500:
                    cleaned = cleaned[:pos].strip()
                    break
        
        # 🔥 REMOVE ALL SECTION HEADERS (comprehensive patterns)
        section_patterns = [
            # Explicit headers with colons
            r'^\s*(?:Introduction|Background|Context|Main Details|Analysis|Impact|Conclusion|Summary)\s*:\s*',
            r'\n\s*(?:Introduction|Background|Context|Main Details|Analysis|Impact|Conclusion|Summary)\s*:\s*',
            # Headers with "and"
            r'^\s*(?:Background and Context|Analysis and Impact)\s*:\s*',
            r'\n\s*(?:Background and Context|Analysis and Impact)\s*:\s*',
            # Headers with "&"
            r'^\s*(?:Background & Context|Analysis & Impact)\s*:\s*',
            r'\n\s*(?:Background & Context|Analysis & Impact)\s*:\s*',
        ]
        
        for pattern in section_patterns:
            cleaned = re.sub(pattern, '\n\n', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # 🔥 REMOVE REPETITIVE PHRASES
        repetitive_phrases = [
            r'^Industry experts note that\s+',
            r'\n\s*Industry experts note that\s+',
            r'^According to industry experts,\s+',
            r'\n\s*According to industry experts,\s+',
        ]
        
        for pattern in repetitive_phrases:
            cleaned = re.sub(pattern, '\n', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # Clean up formatting
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r'^\s*[-*•]\s+', '', cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()
        
        logger.debug("🧹 Cleaned section headers, markers, and repetitive phrases")
        
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
        """Store draft WITH local image path in HTML"""
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
                draft.get('image_url', ''),
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
            
            logger.info(f"✅ Stored draft {draft_id}")
            
            return draft_id
        
        except Exception as e:
            logger.error(f"❌ Error storing draft: {e}")
            return 0
    
    def _convert_to_html(self, text: str) -> str:
        """
        🔧 Convert text to clean HTML paragraphs
        """
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
            
            # Only convert explicit markdown headers
            if line.startswith('##'):
                if current_paragraph:
                    html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
                    current_paragraph = []
                html_parts.append(f"<h2>{line.replace('##', '').strip()}</h2>")
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
