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

logger = logging.getLogger(__name__)

class DraftGenerator:
    """Generate complete AI-rewritten news articles with sentence-level AI improvement"""
    
    def __init__(self, db_path: str, model_name: str = 'TheBloke/Mistral-7B-Instruct-v0.2-GGUF'):
        self.db_path = db_path
        self.model_name = model_name
        self.model_file = 'mistral-7b-instruct-v0.2.Q4_K_M.gguf'
        self.llm = self._load_model()
        self.translation_keywords = self._load_translation_keywords()
        
        # Initialize sentence improvement model (lighter weight for quick improvements)
        self.sentence_model = self._load_sentence_model()
    
    def _load_model(self):
        """Load GGUF quantized Mistral model - NO FALLBACK TO TEMPLATE MODE"""
        try:
            from ctransformers import AutoModelForCausalLM
            
            logger.info(f"Loading GGUF model: {self.model_name}")
            
            # Check multiple possible paths
            possible_paths = [
                Path('models') / self.model_name.replace('/', '_') / self.model_file,
                Path('models') / self.model_file,
                Path(self.model_file)
            ]
            
            model_path = None
            for path in possible_paths:
                if path.exists():
                    model_path = path
                    break
            
            if not model_path:
                logger.error(f"GGUF model not found. Checked paths:")
                for p in possible_paths:
                    logger.error(f"  - {p}")
                logger.error("Download model: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF")
                return None
            
            logger.info(f"Loading GGUF model from: {model_path}")
            
            # Load GGUF model with ctransformers
            llm = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                model_type='mistral',
                context_length=4096,
                max_new_tokens=1500,
                threads=4,
                gpu_layers=0
            )
            
            logger.info("[OK] Mistral-7B-GGUF Q4_K_M loaded successfully (4.1GB)")
            return llm
        
        except ImportError:
            logger.error("ctransformers not installed. Install: pip install ctransformers")
            return None
        except Exception as e:
            logger.error(f"Error loading GGUF model: {e}")
            return None
    
    def _load_sentence_model(self):
        """Load lightweight sentence improvement model"""
        try:
            from transformers import pipeline
            logger.info("Loading sentence improvement model...")
            model = pipeline("text2text-generation", model="google/flan-t5-base", max_length=150)
            logger.info("[OK] Sentence improvement model loaded")
            return model
        except Exception as e:
            logger.warning(f"Sentence model unavailable: {e}")
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
    
    def generate_draft(self, news_id: int, manual_mode: bool = False, manual_content: str = '') -> Dict:
        """
        Generate complete article draft with AI or manual content enhancement
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
            
            # Extract topic information
            topic_info = self._extract_topic_info(headline, summary or '', category)
            
            # Generate or enhance content
            if manual_mode and manual_content:
                draft = self._enhance_manual_content(manual_content, headline, category, topic_info)
            elif self.llm:
                draft = self._generate_with_model(headline, summary, category, source_domain, topic_info)
            else:
                logger.error("AI model not loaded! Cannot generate draft without model.")
                return {
                    'title': headline,
                    'body_draft': 'ERROR: AI model not loaded. Please download the model first.',
                    'summary': summary or '',
                    'word_count': 0,
                    'error': 'Model not loaded'
                }
            
            # Embed image properly in article (not just URL)
            draft['image_url'] = image_url or ''
            draft['source_url'] = source_url or ''
            draft['source_domain'] = source_domain or ''
            draft['is_html'] = True
            
            # Store draft
            draft_id = self._store_draft(news_id, workspace_id, draft)
            
            logger.info(f"Generated draft for news_id {news_id}, words: {draft.get('word_count', 0)}")
            return {**draft, 'id': draft_id}
        
        except Exception as e:
            logger.error(f"Error generating draft: {e}")
            return {}
    
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
        """Generate with real AI model"""
        
        topic_context = f"""Topic Focus: {topic_info['focus']}
Category: {category}
Key Terms: {', '.join(topic_info['capitalized_terms'][:5])}
Key Numbers: {', '.join(topic_info['numbers'][:3])}"""
        
        prompt = f"""<s>[INST] You are a professional journalist. Write a complete, detailed news article (1000-1200 words) based on this headline.

Write in professional journalism style with clear sections.
Include: Introduction, Background, Main Content, and Analysis.
DO NOT add conclusions or risk assessments.
DO NOT mention AI, bots, or automated systems.

Headline: {headline}
Summary: {summary}

{topic_context}

Write the COMPLETE article now: [/INST]"""
        
        try:
            generated_text = self.llm(
                prompt,
                max_new_tokens=1500,
                temperature=0.7,
                top_p=0.9,
                stop=["</s>", "[/INST]", "Conclusion:", "Risk Assessment:"],
                stream=False
            )
            
            # Remove any conclusion or risk sections that might have been generated
            cleaned_text = self._remove_unwanted_sections(generated_text)
            
            return {
                'title': headline,
                'body_draft': cleaned_text.strip(),
                'summary': summary,
                'word_count': len(cleaned_text.split()),
                'is_ai_generated': True
            }
        except Exception as e:
            logger.error(f"Model generation error: {e}")
            return {
                'title': headline,
                'body_draft': f'ERROR: {str(e)}',
                'summary': summary,
                'word_count': 0,
                'error': str(e)
            }
    
    def _remove_unwanted_sections(self, text: str) -> str:
        """Remove conclusion, risk assessment, and other unwanted sections"""
        # Patterns to remove
        unwanted_patterns = [
            r'## Conclusion.*$',
            r'## Risk.*$',
            r'## Summary.*$',
            r'## Final.*$',
            r'\n\nConclusion:.*$',
            r'\n\nRisk.*:.*$',
            r'\n\nSummary:.*$'
        ]
        
        cleaned = text
        for pattern in unwanted_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        return cleaned.strip()
    
    def _store_draft(self, news_id: int, workspace_id: int, draft: Dict) -> int:
        """Store draft in database with HTML format"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert to HTML
            html_body = self._convert_to_html(draft.get('body_draft', ''))
            
            cursor.execute('''
                INSERT INTO ai_drafts 
                (workspace_id, news_id, title, body_draft, summary, word_count, image_url, source_url, source_domain, is_html, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                workspace_id,
                news_id,
                draft.get('title', ''),
                html_body,
                draft.get('summary', ''),
                draft.get('word_count', 0),
                draft.get('image_url', ''),
                draft.get('source_url', ''),
                draft.get('source_domain', ''),
                1,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            draft_id = cursor.lastrowid
            conn.close()
            
            return draft_id
        
        except Exception as e:
            logger.error(f"Error storing draft: {e}")
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
            logger.error(f"Error cleaning up queue: {e}")
            return 0
