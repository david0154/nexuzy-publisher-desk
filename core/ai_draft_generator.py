""" 
AI Draft Generation Module - CLEAN ARTICLES (No Section Headers)
Generates UNIQUE, comprehensive articles WITHOUT visible structure labels

FEATURES:
✅ 800-2500 word articles
✅ Pre-writing angle selection (ONE clear focus)
✅ Neutral tone enforcement
✅ Grammar and spelling checking
✅ Anti-plagiarism system with advanced variation
✅ MANDATORY title uniqueness and rewrite
✅ Enhanced human-like writing with personality
✅ Research writer integration (uses same AI model via GLOBAL CACHE)
✅ Local image download (WORKING!)
✅ Watermark detection
✅ Clean output (no "Introduction:", "Main Details:" headers)
✅ Multi-layer uniqueness engine
✅ Advanced paraphrasing and synonym variation
✅ Contextual sentence restructuring
✅ Natural flow with varied transitions
✅ No fictionalized speeches or excessive rhetorical quotes
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Tuple
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

# GLOBAL MODEL CACHE - shared between AI Writer and Research Writer
_CACHED_MODEL = None
_CACHED_SENTENCE_MODEL = None
_GRAMMAR_CHECKER = None

# Enhanced synonym dictionary for uniqueness
SYNONYM_DICT = {
    'said': ['stated', 'mentioned', 'noted', 'explained', 'announced', 'revealed', 'reported', 'disclosed', 'expressed', 'conveyed', 'declared', 'affirmed', 'remarked'],
    'new': ['recent', 'latest', 'fresh', 'novel', 'emerging', 'modern', 'contemporary', 'current', 'up-to-date', 'innovative', 'groundbreaking'],
    'big': ['significant', 'substantial', 'considerable', 'major', 'large-scale', 'extensive', 'sizeable', 'massive', 'prominent', 'notable'],
    'important': ['crucial', 'vital', 'essential', 'critical', 'key', 'significant', 'pivotal', 'paramount', 'fundamental', 'pressing', 'imperative'],
    'show': ['demonstrate', 'illustrate', 'reveal', 'indicate', 'display', 'exhibit', 'present', 'showcase', 'reflect', 'manifest'],
    'many': ['numerous', 'multiple', 'several', 'various', 'countless', 'myriad', 'abundant', 'plentiful', 'manifold'],
    'good': ['positive', 'beneficial', 'favorable', 'advantageous', 'promising', 'valuable', 'constructive', 'productive', 'fruitful'],
    'bad': ['negative', 'adverse', 'unfavorable', 'detrimental', 'problematic', 'harmful', 'damaging', 'troublesome', 'concerning'],
    'make': ['create', 'produce', 'generate', 'develop', 'establish', 'form', 'construct', 'build', 'forge', 'craft'],
    'use': ['utilize', 'employ', 'apply', 'leverage', 'implement', 'adopt', 'deploy', 'harness', 'incorporate'],
    'get': ['obtain', 'acquire', 'receive', 'secure', 'gain', 'attain', 'procure', 'achieve', 'derive'],
    'very': ['extremely', 'highly', 'particularly', 'exceptionally', 'remarkably', 'significantly', 'notably', 'especially'],
    'problem': ['issue', 'challenge', 'concern', 'difficulty', 'complication', 'obstacle', 'hurdle', 'dilemma'],
    'change': ['transform', 'modify', 'alter', 'adjust', 'revise', 'adapt', 'evolve', 'shift', 'reshape'],
    'help': ['assist', 'aid', 'support', 'facilitate', 'contribute to', 'enable', 'empower', 'bolster'],
    'think': ['believe', 'consider', 'suggest', 'indicate', 'propose', 'maintain', 'posit', 'contend'],
    'see': ['observe', 'notice', 'witness', 'recognize', 'identify', 'detect', 'perceive', 'discern'],
    'know': ['understand', 'recognize', 'acknowledge', 'realize', 'comprehend', 'grasp', 'appreciate'],
    'want': ['desire', 'seek', 'aim for', 'pursue', 'strive for', 'aspire to', 'yearn for'],
    'need': ['require', 'necessitate', 'demand', 'call for', 'warrant', 'entail'],
    'look': ['appear', 'seem', 'indicate', 'suggest', 'signal', 'point to'],
    'find': ['discover', 'uncover', 'identify', 'determine', 'ascertain', 'locate'],
    'give': ['provide', 'offer', 'supply', 'deliver', 'furnish', 'grant', 'bestow'],
    'tell': ['inform', 'notify', 'advise', 'communicate', 'convey', 'relay'],
    'work': ['function', 'operate', 'perform', 'serve', 'act', 'execute'],
    'call': ['designate', 'term', 'label', 'refer to', 'name', 'dub'],
    'try': ['attempt', 'endeavor', 'strive', 'seek', 'aim', 'undertake'],
    'ask': ['inquire', 'question', 'query', 'request', 'seek information'],
    'feel': ['sense', 'experience', 'perceive', 'detect', 'recognize'],
    'become': ['turn into', 'evolve into', 'transform into', 'develop into'],
    'leave': ['depart', 'exit', 'withdraw', 'abandon', 'vacate'],
    'put': ['place', 'position', 'set', 'situate', 'locate', 'install'],
}

# Neutral title templates (avoiding sensationalism)
NEUTRAL_TITLE_PATTERNS = [
    "{topic}: Analysis and Key Details",
    "{topic}: What to Know About Recent Developments",
    "{topic}: Overview of Current Situation",
    "Understanding {topic}: Facts and Context",
    "{topic}: Recent Updates and Information",
    "{topic}: Examining the Details",
    "{topic}: Current Status and Background",
    "{topic}: Key Points and Analysis",
    "{topic}: Developments and Implications",
    "{topic}: A Factual Review",
]

# Article angles for pre-writing step
ARTICLE_ANGLES = {
    'impact': 'Focus on the direct and indirect consequences for stakeholders',
    'analysis': 'Provide analytical breakdown of the situation with data and context',
    'public_reaction': 'Examine how different groups and communities are responding',
    'policy': 'Analyze policy implications and regulatory considerations',
    'symbolism': 'Explore the broader symbolic meaning and cultural significance',
    'expert': 'Present expert interpretations and professional perspectives'
}

class DraftGenerator:
    """Generate UNIQUE, LONG AI-rewritten news articles (800-2500 words)"""
    
    def __init__(self, db_path: str, model_name: str = 'models/mistral-7b-instruct-v0.2.Q4_K_M.gguf'):
        global _CACHED_MODEL, _CACHED_SENTENCE_MODEL, _GRAMMAR_CHECKER
        
        self.db_path = db_path
        self.model_name = model_name
        self.model_file = Path(model_name).name
        self.translation_keywords = self._load_translation_keywords()
        
        # Use GLOBAL cached model (shared with Research Writer)
        if _CACHED_MODEL:
            logger.info("✅ Using GLOBAL cached AI model (shared with Research Writer)")
            self.llm = _CACHED_MODEL
        else:
            logger.info("⏳ Loading AI model for BOTH AI Writer and Research Writer...")
            self.llm = self._load_model()
            if self.llm:
                _CACHED_MODEL = self.llm
                logger.info("💾 Model cached GLOBALLY for AI Writer + Research Writer")
        
        if _CACHED_SENTENCE_MODEL:
            self.sentence_model = _CACHED_SENTENCE_MODEL
        else:
            self.sentence_model = self._load_sentence_model()
            if self.sentence_model:
                _CACHED_SENTENCE_MODEL = self.sentence_model
        
        # Initialize grammar checker
        if _GRAMMAR_CHECKER:
            self.grammar_checker = _GRAMMAR_CHECKER
        else:
            self.grammar_checker = self._load_grammar_checker()
            if self.grammar_checker:
                _GRAMMAR_CHECKER = self.grammar_checker
        
        if not self.llm:
            logger.error("❌ AI Writer FAILED - GGUF model not found")
        else:
            logger.info("✅ AI Writer LOADED (800-2500 words, Clean Output, Grammar Check, Neutral Tone)")
    
    def _load_grammar_checker(self):
        """Load grammar and spelling checker"""
        try:
            import language_tool_python
            logger.info("⏳ Loading grammar checker...")
            tool = language_tool_python.LanguageTool('en-US')
            logger.info("✅ Grammar checker loaded")
            return tool
        except ImportError:
            logger.warning("⚠️  language_tool_python not installed. Run: pip install language-tool-python")
            return None
        except Exception as e:
            logger.warning(f"⚠️  Grammar checker unavailable: {e}")
            return None
    
    def _check_grammar_and_spelling(self, text: str) -> Tuple[str, List[Dict]]:
        """Check and fix grammar and spelling errors"""
        if not self.grammar_checker:
            return text, []
        
        try:
            logger.info("🔍 Checking grammar and spelling...")
            matches = self.grammar_checker.check(text)
            
            # Filter important errors (ignore minor style suggestions)
            important_matches = [
                m for m in matches 
                if m.ruleIssueType in ['misspelling', 'grammar', 'typographical']
            ]
            
            if important_matches:
                logger.info(f"📝 Found {len(important_matches)} grammar/spelling issues")
                corrected_text = language_tool_python.utils.correct(text, important_matches)
                
                errors_fixed = [
                    {
                        'message': m.message,
                        'context': m.context,
                        'replacements': m.replacements[:3]
                    }
                    for m in important_matches[:10]  # Log first 10
                ]
                
                logger.info(f"✅ Grammar check complete. Fixed {len(important_matches)} issues")
                return corrected_text, errors_fixed
            else:
                logger.info("✅ No grammar or spelling errors found")
                return text, []
                
        except Exception as e:
            logger.error(f"❌ Grammar check failed: {e}")
            return text, []
    
    def _select_article_angle(self, headline: str, summary: str, category: str) -> str:
        """🔥 NEW: Pre-writing step - Select ONE clear article angle"""
        text = (headline + ' ' + summary).lower()
        
        # Score each angle based on content
        angle_scores = {}
        
        # Impact indicators
        if any(word in text for word in ['impact', 'affect', 'consequence', 'result', 'effect', 'influence']):
            angle_scores['impact'] = angle_scores.get('impact', 0) + 2
        
        # Analysis indicators  
        if any(word in text for word in ['data', 'statistics', 'report', 'study', 'research', 'analysis', 'findings']):
            angle_scores['analysis'] = angle_scores.get('analysis', 0) + 2
        
        # Public reaction indicators
        if any(word in text for word in ['protest', 'reaction', 'response', 'public', 'people', 'community', 'citizens']):
            angle_scores['public_reaction'] = angle_scores.get('public_reaction', 0) + 2
        
        # Policy indicators
        if any(word in text for word in ['policy', 'law', 'regulation', 'legislation', 'government', 'rule', 'mandate']):
            angle_scores['policy'] = angle_scores.get('policy', 0) + 2
        
        # Symbolism indicators
        if any(word in text for word in ['symbol', 'represent', 'significance', 'meaning', 'historic', 'milestone']):
            angle_scores['symbolism'] = angle_scores.get('symbolism', 0) + 2
        
        # Expert interpretation indicators
        if any(word in text for word in ['expert', 'analyst', 'professor', 'researcher', 'specialist', 'authority']):
            angle_scores['expert'] = angle_scores.get('expert', 0) + 2
        
        # Select angle with highest score, or random if tie
        if angle_scores:
            selected_angle = max(angle_scores, key=angle_scores.get)
        else:
            # Default based on category
            category_angles = {
                'Technology': 'analysis',
                'Business': 'impact',
                'Politics': 'policy',
                'Health': 'expert',
                'Sports': 'analysis',
                'Entertainment': 'public_reaction'
            }
            selected_angle = category_angles.get(category, 'impact')
        
        logger.info(f"📐 Selected article angle: {selected_angle.upper()}")
        return selected_angle
    
    def _extract_topic_nouns(self, headline: str, summary: str) -> List[str]:
        """Extract key topic nouns for first paragraph comparison"""
        text = headline + ' ' + summary
        
        # Extract capitalized terms (likely proper nouns)
        words = text.split()
        capitalized = [
            w.strip('.,!?;:') for w in words 
            if w and len(w) > 2 and w[0].isupper() 
            and w.upper() != w  # Exclude all-caps
            and w not in ['The', 'A', 'An', 'And', 'Or', 'But', 'In', 'On', 'At', 'To', 'For']
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_nouns = []
        for noun in capitalized:
            if noun.lower() not in seen:
                seen.add(noun.lower())
                unique_nouns.append(noun)
        
        return unique_nouns[:5]  # Return top 5
    
    def _create_neutral_opening(self, topic_nouns: List[str], angle: str, summary: str) -> str:
        """Create neutral opening paragraph that compares topic nouns naturally"""
        if len(topic_nouns) < 2:
            return ""
        
        # Create natural comparison based on angle
        angle_templates = {
            'impact': f"{topic_nouns[0]} and {topic_nouns[1]} are experiencing significant developments that affect stakeholders across multiple sectors.",
            'analysis': f"Recent data regarding {topic_nouns[0]} and {topic_nouns[1]} reveals important trends worth examining.",
            'public_reaction': f"The relationship between {topic_nouns[0]} and {topic_nouns[1]} has drawn considerable public attention.",
            'policy': f"Policy discussions involving {topic_nouns[0]} and {topic_nouns[1]} are shaping regulatory approaches.",
            'symbolism': f"The connection between {topic_nouns[0]} and {topic_nouns[1]} carries broader significance.",
            'expert': f"Specialists are analyzing the intersection of {topic_nouns[0]} and {topic_nouns[1]}."
        }
        
        opening = angle_templates.get(angle, f"{topic_nouns[0]} and {topic_nouns[1]} are at the center of recent developments.")
        return opening
    
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
            logger.info("⏳ Loading for long articles (800-2500 words)...")
            
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
            'yeah': 'yes', 'nope': 'no', 'yep': 'yes', 'nah': 'no'
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
    
    def _rewrite_title_neutral(self, original_headline: str, category: str, topic_info: Dict) -> str:
        """
        🔥 IMPROVED: MANDATORY neutral title rewrite
        """
        logger.info(f"🔄 Rewriting title (NEUTRAL TONE): {original_headline}")
        
        # Extract key topic
        words = original_headline.split()
        capitalized = [w for w in words if w and len(w) > 2 and w[0].isupper()]
        
        # Get main topic
        if capitalized:
            topic = ' '.join(capitalized[:3])
        else:
            topic = ' '.join(words[:5])
        
        # Remove sensational words from topic
        sensational_words = ['Breaking', 'Exclusive', 'Shocking', 'Amazing', 'Incredible', 'Stunning', 'Bombshell']
        for word in sensational_words:
            topic = topic.replace(word, '').strip()
        
        # Try neutral patterns
        max_attempts = 5
        for attempt in range(max_attempts):
            pattern = random.choice(NEUTRAL_TITLE_PATTERNS)
            new_title = pattern.format(topic=topic)
            
            uniqueness_check = self._check_title_uniqueness(new_title)
            
            if uniqueness_check['is_unique']:
                logger.info(f"✅ NEW NEUTRAL TITLE: {new_title}")
                return new_title
        
        # Fallback
        new_title = f"{topic}: Current Status and Analysis"
        logger.warning(f"⚠️  Using fallback: {new_title}")
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
            f"{original_title}: Latest Information",
            f"{original_title} - Updated Report",
            f"{original_title}: Key Facts",
            f"{original_title} - Current Analysis",
            f"{original_title}: Complete Overview",
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
        """Generate UNIQUE, LONG article with neutral tone and grammar checking"""
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
            
            # 🔥 PRE-WRITING STEP 1: Select article angle
            selected_angle = self._select_article_angle(headline, summary or '', category)
            
            # 🔥 PRE-WRITING STEP 2: Extract topic nouns for comparison
            topic_nouns = self._extract_topic_nouns(headline, summary or '')
            
            topic_info = self._extract_topic_info(headline, summary or '', category)
            
            # 🔥 NEUTRAL TITLE REWRITE
            new_title = self._rewrite_title_neutral(headline, category, topic_info)
            
            logger.info(f"🤖 Generating article with {selected_angle.upper()} angle...")
            
            draft = self._generate_with_model(new_title, summary, category, source_domain, topic_info, selected_angle, topic_nouns)
            
            if 'error' in draft or not draft.get('body_draft'):
                error_msg = draft.get('error', 'AI generation failed')
                logger.error(f"❌ Generation failed: {error_msg}")
                return {'error': error_msg, 'title': new_title, 'body_draft': '', 'word_count': 0}
            
            # 🔥 GRAMMAR AND SPELLING CHECK
            corrected_body, grammar_errors = self._check_grammar_and_spelling(draft['body_draft'])
            draft['body_draft'] = corrected_body
            draft['grammar_corrections'] = len(grammar_errors)
            
            draft['image_url'] = image_url or ''
            draft['local_image_path'] = local_image_path or ''
            draft['source_url'] = source_url or ''
            draft['source_domain'] = source_domain or ''
            draft['is_html'] = True
            draft['article_angle'] = selected_angle
            
            draft_id = self._store_draft(news_id, workspace_id, draft)
            
            logger.info(f"✅ Generated draft {draft_id}, words: {draft.get('word_count', 0)}, grammar fixes: {draft.get('grammar_corrections', 0)}")
            return {**draft, 'id': draft_id}
        
        except Exception as e:
            logger.error(f"❌ Error generating draft: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'error': str(e)}
    
    def _apply_synonym_variation(self, text: str) -> str:
        """
        🔥 IMPROVED: Apply synonym replacement with intelligent context awareness
        """
        words = text.split()
        varied_words = []
        last_replacement = None
        
        for i, word in enumerate(words):
            word_lower = word.lower().strip('.,!?;:')
            
            # Skip if last word was replaced (avoid over-replacement)
            if last_replacement and i - last_replacement < 3:
                varied_words.append(word)
                continue
            
            # 35% chance to replace with synonym
            if word_lower in SYNONYM_DICT and random.random() < 0.35:
                synonym = random.choice(SYNONYM_DICT[word_lower])
                # Preserve capitalization
                if word and word[0].isupper():
                    synonym = synonym.capitalize()
                varied_words.append(synonym)
                last_replacement = i
            else:
                varied_words.append(word)
        
        return ' '.join(varied_words)
    
    def _generate_with_model(self, headline: str, summary: str, category: str, source: str, topic_info: Dict, angle: str, topic_nouns: List[str]) -> Dict:
        """Generate article with selected angle and neutral tone"""
        
        topic_context = f"""Topic: {topic_info['focus']}
Category: {category}
Key Terms: {', '.join(topic_info['capitalized_terms'][:5])}
Statistics: {', '.join(topic_info['numbers'][:3])}"""
        
        # Get angle-specific instruction
        angle_instruction = ARTICLE_ANGLES[angle]
        
        # Create opening hook
        opening_hook = self._create_neutral_opening(topic_nouns, angle, summary)
        
        # 🔥 IMPROVED PROMPT with 800-2500 word range
        prompt = f"""You are a professional journalist writing a factual news article. Write in a neutral, objective tone without sensationalism.

Article Angle: {angle_instruction}

Headline: {headline}
Summary: {summary}

{topic_context}

Opening Hook (use this as your first sentence): {opening_hook}

Write a comprehensive news article (800-2500 words). Requirements:

NEUTRAL TONE:
1. Use factual, objective language
2. Avoid emotional or sensational words
3. Present multiple perspectives fairly
4. Cite facts and verifiable information
5. Maintain professional distance

WRITING STYLE:
1. Vary sentence structure naturally
2. Use active voice primarily
3. Keep paragraphs 2-4 sentences
4. Include specific details and data
5. Connect ideas logically

CRITICAL - DO NOT:
- Include long speeches or monologues (max 1-2 short sentences per quote)
- Use multiple rhetorical quotes
- Include section labels ("Introduction:", "Background:")
- Start paragraphs repetitively
- Use cliché phrases
- Include sensational language
- Write fictional or speculative quotes

QUOTES (if needed):
- Keep quotes brief (1-2 sentences maximum)
- Attribute clearly to real sources
- Use sparingly (no more than 2-3 total)
- Focus on factual statements, not rhetoric

Write the article now:

Article:"""
        
        try:
            logger.info("⏳ Generating neutral-tone article with selected angle...")
            
            generated_text = self.llm(
                prompt,
                max_new_tokens=1500,
                temperature=0.85,  # Slightly lower for more factual tone
                top_p=0.92,
                repetition_penalty=1.35,
                stop=["\n\n\n\n", "Article:", "Summary:", "Note:", "Disclaimer:"],
                stream=False
            )
            
            if not generated_text or not isinstance(generated_text, str):
                generated_text = str(generated_text) if generated_text else ""
            
            generated_text = generated_text.strip()
            
            if len(generated_text) < 500:
                logger.error(f"❌ Generated text too short: {len(generated_text)} chars")
                return {'error': f'AI generated only {len(generated_text)} chars. Need 800+ words.', 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
            
            # Clean text
            cleaned_text = self._clean_generated_text(generated_text)
            
            # Remove long speeches and excessive quotes
            cleaned_text = self._remove_long_speeches(cleaned_text)
            
            if len(cleaned_text) < 500:
                logger.error("❌ Cleaned text too short")
                return {'error': 'Text too short after cleaning', 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
            
            # Apply uniqueness layers
            varied_text = self._apply_synonym_variation(cleaned_text)
            restructured_text = self._vary_sentence_structure(varied_text)
            boosted_text = self._boost_uniqueness(restructured_text, topic_info)
            final_text = self._advanced_paraphrase(boosted_text)
            
            # Convert to HTML
            html_content = self._convert_to_html(final_text)
            
            word_count = len(final_text.split())
            uniqueness_score = self._calculate_uniqueness_score(final_text)
            
            logger.info(f"✅ Article generated: {word_count} words, uniqueness: {uniqueness_score:.1%}")
            
            return {
                'title': headline,
                'body_draft': html_content,
                'summary': summary,
                'word_count': word_count,
                'uniqueness_score': uniqueness_score,
                'is_ai_generated': True,
                'generation_mode': 'neutral_tone_angle_based_v5'
            }
        except Exception as e:
            logger.error(f"❌ Model generation error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'error': f"AI generation failed: {str(e)}", 'title': headline, 'body_draft': '', 'summary': summary, 'word_count': 0}
    
    def _remove_long_speeches(self, text: str) -> str:
        """🔥 NEW: Remove long speeches and excessive quotes"""
        # Find quoted sections
        quote_pattern = r'"([^"]{100,})"'  # Quotes longer than 100 chars
        
        def shorten_quote(match):
            full_quote = match.group(1)
            # Keep only first sentence
            sentences = re.split(r'[.!?]+', full_quote)
            if sentences:
                return f'"{sentences[0].strip()}."'
            return match.group(0)
        
        # Shorten long quotes
        text = re.sub(quote_pattern, shorten_quote, text)
        
        # Remove rhetorical patterns
        rhetorical_patterns = [
            r'"How can we[^"]{30,}"',
            r'"Why should[^"]{30,}"',
            r'"What if[^"]{30,}"',
            r'"Is it not[^"]{30,}"',
        ]
        
        for pattern in rhetorical_patterns:
            text = re.sub(pattern, '', text)
        
        # Limit consecutive paragraphs with quotes
        paragraphs = text.split('\n\n')
        filtered_paragraphs = []
        consecutive_quotes = 0
        
        for para in paragraphs:
            if '"' in para:
                consecutive_quotes += 1
                if consecutive_quotes <= 2:  # Max 2 consecutive quote paragraphs
                    filtered_paragraphs.append(para)
            else:
                consecutive_quotes = 0
                filtered_paragraphs.append(para)
        
        return '\n\n'.join(filtered_paragraphs)
    
    def _vary_sentence_structure(self, text: str) -> str:
        """Vary sentence structure for better uniqueness"""
        sentences = re.split(r'([.!?]\s+)', text)
        varied_sentences = []
        
        for i, sent in enumerate(sentences):
            if not sent.strip() or sent in ['. ', '! ', '? ']:
                varied_sentences.append(sent)
                continue
            
            # 20% chance to restructure
            if random.random() < 0.20 and len(sent) > 40:
                if ', ' in sent:
                    parts = sent.split(', ', 1)
                    if len(parts) == 2 and len(parts[1]) > 20:
                        if parts[1][0].islower():
                            sent = f"{parts[1][0].upper()}{parts[1][1:]}, while {parts[0].lower()}"
                        else:
                            sent = f"{parts[1]}, while {parts[0].lower()}"
            
            varied_sentences.append(sent)
        
        return ''.join(varied_sentences)
    
    def _advanced_paraphrase(self, text: str) -> str:
        """Advanced paraphrasing for uniqueness"""
        sentences = re.split(r'([.!?]\s+)', text)
        paraphrased_sentences = []
        
        phrase_replacements = {
            'in order to': 'to',
            'due to the fact that': 'because',
            'at this point in time': 'now',
            'in the event that': 'if',
            'for the purpose of': 'to',
            'in spite of': 'despite',
            'by means of': 'by',
            'in the near future': 'soon',
            'at the present time': 'currently',
            'in the process of': 'while',
        }
        
        for sent in sentences:
            if sent.strip() and sent not in ['. ', '! ', '? ']:
                for wordy, concise in phrase_replacements.items():
                    if random.random() < 0.3:
                        sent = sent.replace(wordy, concise)
            
            paraphrased_sentences.append(sent)
        
        return ''.join(paraphrased_sentences)
    
    def _calculate_uniqueness_score(self, text: str) -> float:
        """Calculate uniqueness score"""
        words = text.lower().split()
        if len(words) < 50:
            return 0.5
        
        unique_words = set(words)
        vocabulary_diversity = len(unique_words) / len(words)
        
        common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']
        content_words = [w for w in words if w not in common_words]
        
        if not content_words:
            return 0.5
        
        unique_content = len(set(content_words)) / len(content_words)
        
        sentences = re.split(r'[.!?]+', text)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        
        if len(sentence_lengths) > 1:
            import statistics
            length_variance = statistics.stdev(sentence_lengths) / statistics.mean(sentence_lengths) if statistics.mean(sentence_lengths) > 0 else 0
        else:
            length_variance = 0
        
        uniqueness = (vocabulary_diversity * 0.4 + unique_content * 0.4 + min(length_variance, 1.0) * 0.2)
        
        return uniqueness
    
    def _boost_uniqueness(self, text: str, topic_info: Dict) -> str:
        """Boost content uniqueness with varied connectors"""
        sentences = re.split(r'([.!?]\s+)', text)
        varied_sentences = []
        
        starters = [
            'Additionally, ', 'Furthermore, ', 'Moreover, ', 'In particular, ',
            'Notably, ', 'Significantly, ', 'Importantly, ',
            'Recent reports suggest that ', 'Data indicates that ',
            'Meanwhile, ', 'Conversely, ', 'In contrast, ', 'As a result, ',
            'Consequently, ', 'Nevertheless, ', 'On the other hand, ',
            'Interestingly, ', 'Remarkably, ', 'In fact, ',
        ]
        
        used_starters = set()
        
        for i, sent in enumerate(sentences):
            if i > 0 and i % 4 == 0 and sent.strip() and len(sent) > 20:
                available_starters = [s for s in starters if s not in used_starters]
                if not available_starters:
                    used_starters.clear()
                    available_starters = starters
                
                if not any(sent.strip().startswith(s.strip()) for s in starters):
                    if random.random() > 0.5:
                        starter = random.choice(available_starters)
                        used_starters.add(starter)
                        sent = starter + sent.strip()[0].lower() + sent.strip()[1:]
            varied_sentences.append(sent)
        
        return ''.join(varied_sentences)
    
    def _clean_generated_text(self, text: str) -> str:
        """Clean AI-generated text and remove section markers"""
        unwanted_phrases = [
            "Note: This article", "Disclaimer:", "Generated by", "AI-generated",
            "[This article", "This content was", "As an AI", "I cannot", "I apologize",
            "In conclusion,", "To summarize,", "In summary,", "To sum up,",
            "only time will tell", "remains to be seen", "it goes without saying"
        ]
        
        cleaned = text
        
        for phrase in unwanted_phrases:
            if phrase in cleaned:
                pos = cleaned.find(phrase)
                if pos > 500:
                    cleaned = cleaned[:pos].strip()
                    break
        
        # Remove section headers
        section_patterns = [
            r'^\s*(?:Introduction|Background|Context|Main Details|Analysis|Impact|Conclusion|Summary|Overview)\s*:\s*',
            r'\n\s*(?:Introduction|Background|Context|Main Details|Analysis|Impact|Conclusion|Summary|Overview)\s*:\s*',
            r'^\s*(?:Background and Context|Analysis and Impact)\s*:\s*',
            r'\n\s*(?:Background and Context|Analysis and Impact)\s*:\s*',
        ]
        
        for pattern in section_patterns:
            cleaned = re.sub(pattern, '\n\n', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove repetitive phrases
        repetitive_phrases = [
            r'^Industry experts note that\s+',
            r'\n\s*Industry experts note that\s+',
            r'^According to industry experts,\s+',
            r'\n\s*According to industry experts,\s+',
        ]
        
        for pattern in repetitive_phrases:
            cleaned = re.sub(pattern, '\n', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # Clean formatting
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r'^\s*[-*•]\s+', '', cleaned, flags=re.MULTILINE)
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
        """Store draft with local image path"""
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
            
            return draft_id
        
        except Exception as e:
            logger.error(f"❌ Error storing draft: {e}")
            return 0
    
    def _convert_to_html(self, text: str) -> str:
        """Convert text to clean HTML paragraphs"""
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
