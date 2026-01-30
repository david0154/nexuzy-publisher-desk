"""
Research Writer Module - AI-Powered Research & Article Generation
Features: Web search, Article scraping, AI analysis, Auto-generated articles with citations
🔥 NOW USES SAME AI MODEL as AI Draft Generator (GLOBAL CACHE SHARED)
"""

import logging
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sqlite3
from pathlib import Path
import re
import time
import random
from urllib.parse import urlparse

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

logger = logging.getLogger(__name__)

# GLOBAL MODEL CACHE - shared with AI Draft Generator
_CACHED_MODEL = None
_CACHED_SENTENCE_MODEL = None

# Import synonym dictionary and uniqueness functions from ai_draft_generator
try:
    from core.ai_draft_generator import SYNONYM_DICT, TITLE_PATTERNS
except:
    # Fallback if import fails
    SYNONYM_DICT = {
        'said': ['stated', 'mentioned', 'noted', 'explained', 'announced'],
        'new': ['recent', 'latest', 'fresh', 'novel', 'emerging'],
        'important': ['crucial', 'vital', 'essential', 'critical', 'key'],
    }
    TITLE_PATTERNS = ["{topic}: What This Means", "{topic}: Analysis"]

class ResearchWriter:
    """AI-powered research and article generation engine"""
    
    def __init__(self, db_path: str = 'nexuzy.db', cache_articles: bool = True, model_name: str = 'models/mistral-7b-instruct-v0.2.Q4_K_M.gguf'):
        global _CACHED_MODEL, _CACHED_SENTENCE_MODEL
        
        self.db_path = db_path
        self.cache_articles = cache_articles
        self.article_cache = {}  # In-memory cache
        self.session = self._create_session()
        self.model_name = model_name
        self._ensure_research_table()
        
        # Use GLOBAL cached model (shared with AI Draft Generator)
        if _CACHED_MODEL:
            logger.info("✅ Research Writer using GLOBAL cached AI model (shared with AI Draft Generator)")
            self.llm = _CACHED_MODEL
        else:
            logger.info("⏳ Loading AI model for Research Writer (will be shared with AI Draft Generator)...")
            self.llm = self._load_model()
            if self.llm:
                _CACHED_MODEL = self.llm
                logger.info("💾 Model cached GLOBALLY for Research Writer + AI Draft Generator")
        
        if _CACHED_SENTENCE_MODEL:
            self.sentence_model = _CACHED_SENTENCE_MODEL
        else:
            self.sentence_model = self._load_sentence_model()
            if self.sentence_model:
                _CACHED_SENTENCE_MODEL = self.sentence_model
        
        if not self.llm:
            logger.warning("⚠️ Research Writer operating without AI model - will use template generation")
        else:
            logger.info("✅ Research Writer LOADED with AI model (800-2000 words, enhanced uniqueness)")
    
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
            logger.warning(f"⚠️ Could not detect model type, defaulting to 'llama'")
            return 'llama'
    
    def _load_model(self):
        """Load GGUF model (same as AI Draft Generator)"""
        try:
            from ctransformers import AutoModelForCausalLM
            
            model_file = Path(self.model_name).name
            
            possible_paths = [
                Path(self.model_name),
                Path('models') / model_file,
                Path.home() / '.cache' / 'nexuzy' / 'models' / model_file,
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
            logger.info("⏳ Loading for research articles (800-2000 words)...")
            
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
            logger.warning(f"⚠️ Sentence model unavailable: {e}")
            return None
    
    def _create_session(self) -> requests.Session:
        """Create configured requests session"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        session.timeout = 30
        return session
    
    def _ensure_research_table(self):
        """Ensure research cache table exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS research_cache (
                    id INTEGER PRIMARY KEY,
                    topic TEXT UNIQUE,
                    article_content TEXT,
                    sources TEXT,
                    created_date TIMESTAMP,
                    word_count INTEGER
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Could not create research table: {e}")
    
    def research_and_generate(self, 
                             topic: str, 
                             source_urls: Optional[List[str]] = None,
                             word_count: int = 1500) -> Dict:
        """
        Complete research workflow: Search → Scrape → Analyze → Generate
        🔥 NOW USES SAME AI MODEL AS AI DRAFT GENERATOR
        
        Args:
            topic: Research topic
            source_urls: Optional pre-specified URLs to scrape
            word_count: Target article length (1000-2000)
        
        Returns:
            Dict with generated article and metadata
        """
        logger.info(f"🔬 Starting AI research for: {topic}")
        start_time = time.time()
        
        # Check cache
        if self.cache_articles and topic in self.article_cache:
            logger.info(f"📦 Using cached article for: {topic}")
            return self.article_cache[topic]
        
        try:
            # Step 1: Gather sources
            logger.info("🌐 Step 1: Gathering sources...")
            if source_urls:
                sources = source_urls
                logger.info(f"   Using {len(sources)} provided URLs")
            else:
                sources = self._web_search(topic, num_results=5)
            
            if not sources:
                logger.warning("No sources found")
                return {
                    'success': False,
                    'error': 'No sources found for topic',
                    'topic': topic
                }
            
            # Step 2: Scrape articles
            logger.info(f"📰 Step 2: Scraping {len(sources)} articles...")
            articles = self._scrape_articles(sources)
            scraped_count = len([a for a in articles if a.get('content')])
            logger.info(f"   Successfully scraped: {scraped_count}/{len(sources)} articles")
            
            if not articles:
                logger.warning("No articles scraped")
                return {
                    'success': False,
                    'error': 'Could not scrape any articles',
                    'topic': topic
                }
            
            # Step 3: Analyze and extract key points
            logger.info("🧠 Step 3: Analyzing content...")
            key_points = self._extract_key_points(articles, topic)
            
            # Step 4: Generate article WITH AI MODEL (same as AI Draft Generator)
            logger.info(f"✍️ Step 4: Generating {word_count}-word article with AI model...")
            article = self._generate_article_with_ai(topic, key_points, articles, word_count)
            
            # Step 5: Add citations and format
            logger.info("📚 Step 5: Adding citations...")
            formatted_article = self._format_with_citations(article, articles)
            
            elapsed = time.time() - start_time
            
            result = {
                'success': True,
                'topic': topic,
                'article': formatted_article,
                'sources_used': len(articles),
                'word_count': len(formatted_article.split()),
                'sources': [{'url': a.get('url'), 'title': a.get('title')} for a in articles],
                'generation_time': f"{elapsed:.1f}s",
                'status': '✅ Article generated successfully with AI model'
            }
            
            # Cache result
            if self.cache_articles:
                self.article_cache[topic] = result
            
            logger.info(f"✅ Complete! Generated {result['word_count']} words in {elapsed:.1f}s")
            return result
        
        except Exception as e:
            logger.error(f"❌ Research generation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'topic': topic
            }
    
    def _web_search(self, topic: str, num_results: int = 5) -> List[str]:
        """
        Perform web search for topic (using Google Custom Search or DuckDuckGo fallback)
        
        Args:
            topic: Search query
            num_results: Number of results to return
        
        Returns:
            List of source URLs
        """
        try:
            # Using DuckDuckGo which doesn't require API key
            search_url = "https://duckduckgo.com/"
            params = {'q': topic}
            
            response = self.session.get(search_url, params=params, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Search failed: {response.status_code}")
                return []
            
            # Parse search results
            soup = BeautifulSoup(response.content, 'html.parser') if BeautifulSoup else None
            if not soup:
                logger.warning("BeautifulSoup not available for parsing")
                # Fallback: extract URLs from response text
                urls = re.findall(r'https?://[^\s"<>]+', response.text)
                return urls[:num_results]
            
            urls = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('http') and 'duckduckgo' not in href:
                    urls.append(href)
                    if len(urls) >= num_results:
                        break
            
            logger.info(f"   Found {len(urls)} search results")
            return urls
        
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []
    
    def _scrape_articles(self, urls: List[str]) -> List[Dict]:
        """
        Scrape article content from URLs
        
        Args:
            urls: List of URLs to scrape
        
        Returns:
            List of dicts with 'url', 'title', 'content'
        """
        articles = []
        
        for url in urls:
            try:
                logger.debug(f"   Scraping: {url[:50]}...")
                response = self.session.get(url, timeout=15)
                
                if response.status_code != 200:
                    logger.debug(f"   Failed: HTTP {response.status_code}")
                    continue
                
                if not BeautifulSoup:
                    logger.debug("   BeautifulSoup not available")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                title = None
                title_tag = soup.find('h1') or soup.find('title')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                
                # Extract main content
                content = None
                
                # Try common article containers
                article_selectors = [
                    soup.find('article'),
                    soup.find('main'),
                    soup.find(class_='content'),
                    soup.find(class_='article'),
                    soup.find(class_='post')
                ]
                
                for selector in article_selectors:
                    if selector:
                        # Remove scripts and styles
                        for tag in selector.find_all(['script', 'style', 'nav']):
                            tag.decompose()
                        
                        content = selector.get_text(separator=' ', strip=True)
                        if len(content) > 200:  # Minimum content length
                            break
                
                # Fallback: get all body text
                if not content or len(content) < 200:
                    body = soup.find('body')
                    if body:
                        # Remove scripts and styles
                        for tag in body.find_all(['script', 'style', 'nav', 'aside']):
                            tag.decompose()
                        content = body.get_text(separator=' ', strip=True)
                
                if content and len(content) > 200:
                    articles.append({
                        'url': url,
                        'title': title or url,
                        'content': ' '.join(content.split())[:5000]  # Limit to 5000 chars
                    })
                    logger.debug(f"   ✅ Scraped {len(content)} characters")
                else:
                    logger.debug(f"   ⚠️ Insufficient content")
            
            except Exception as e:
                logger.debug(f"   Error scraping {url[:30]}...: {e}")
                continue
            
            time.sleep(0.5)  # Rate limiting
        
        return articles
    
    def _extract_key_points(self, articles: List[Dict], topic: str) -> List[str]:
        """
        Extract key points from scraped articles
        
        Args:
            articles: List of scraped article dicts
            topic: Topic to extract points for
        
        Returns:
            List of key point sentences
        """
        key_points = []
        
        for article in articles:
            content = article.get('content', '')
            if not content:
                continue
            
            # Simple sentence extraction
            sentences = re.split(r'[.!?]+', content)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence.split()) > 5 and len(sentence.split()) < 50:
                    # Check if sentence is relevant to topic
                    if any(word in sentence.lower() for word in topic.lower().split()):
                        key_points.append(sentence)
                        if len(key_points) >= 15:  # Limit key points
                            break
            
            if len(key_points) >= 15:
                break
        
        return key_points[:15]
    
    def _generate_article_with_ai(self, 
                                 topic: str, 
                                 key_points: List[str], 
                                 articles: List[Dict],
                                 target_words: int) -> str:
        """
        🔥 NEW: Generate article using SAME AI MODEL as AI Draft Generator
        Falls back to template-based generation if LLM unavailable
        
        Args:
            topic: Article topic
            key_points: Key points to include
            articles: Source articles for reference
            target_words: Target word count
        
        Returns:
            Generated article text
        """
        if not self.llm:
            logger.warning("⚠️ AI model not available, using template generation")
            return self._template_article(topic, key_points, articles)
        
        try:
            # Prepare research context from scraped articles
            research_context = self._prepare_research_context(key_points, articles)
            
            # Human-like writing styles (same as AI Draft Generator)
            writing_styles = [
                "Write like an experienced researcher with expertise in this field",
                "Write in a clear, accessible style that educates readers",
                "Write with authority backed by research and data",
                "Write in an analytical style connecting research to real-world applications",
                "Write comprehensively, exploring multiple perspectives",
            ]
            
            style_instruction = random.choice(writing_styles)
            
            # 🔥 ENHANCED PROMPT with research context and uniqueness requirements
            prompt = f"""You are a professional researcher and writer. {style_instruction}

Topic: {topic}

Research Context:
{research_context}

Write a comprehensive, UNIQUE research-based article ({target_words} words). Requirements:

WRITING STYLE:
1. Write naturally with varied sentence structure (mix short and long sentences)
2. Use active voice with strategic passive voice
3. Include specific details and evidence from research
4. Connect ideas with smooth, logical transitions
5. Write professionally but accessibly
6. Vary paragraph length (2-5 sentences)
7. Use concrete examples and data points
8. Add analytical insights and interpretation

UNIQUENESS REQUIREMENTS:
1. NEVER copy phrases from typical articles
2. Use original phrasing and fresh vocabulary
3. Present information from unique analytical angles
4. Include deep analysis and interpretation
5. Connect to broader implications
6. Use varied sentence beginnings and structures

CRITICAL - DO NOT:
- Include section labels ("Introduction:", "Background:", etc.)
- Use repetitive sentence starters
- Write in a robotic, predictable style
- Include meta-commentary
- Use cliché phrases

Write the research article now in flowing, natural paragraphs:

Article:"""
            
            logger.info("⏳ Generating research article with AI model (60-90 seconds)...")
            
            generated_text = self.llm(
                prompt,
                max_new_tokens=1500,
                temperature=0.90,
                top_p=0.95,
                repetition_penalty=1.35,
                stop=["\n\n\n\n", "Article:", "Summary:", "Note:", "Disclaimer:"],
                stream=False
            )
            
            if not generated_text or not isinstance(generated_text, str):
                generated_text = str(generated_text) if generated_text else ""
            
            generated_text = generated_text.strip()
            
            if len(generated_text) < 500:
                logger.error(f"❌ Generated text too short: {len(generated_text)} chars")
                return self._template_article(topic, key_points, articles)
            
            # Clean and enhance uniqueness (same methods as AI Draft Generator)
            cleaned_text = self._clean_generated_text(generated_text)
            varied_text = self._apply_synonym_variation(cleaned_text)
            restructured_text = self._vary_sentence_structure(varied_text)
            final_text = self._boost_uniqueness(restructured_text)
            
            word_count = len(final_text.split())
            logger.info(f"✅ AI generated {word_count} words")
            
            return final_text
        
        except Exception as e:
            logger.error(f"❌ AI generation failed: {e}, using template")
            import traceback
            logger.error(traceback.format_exc())
            return self._template_article(topic, key_points, articles)
    
    def _prepare_research_context(self, key_points: List[str], articles: List[Dict]) -> str:
        """Prepare research context summary for AI"""
        context_parts = []
        
        if key_points:
            context_parts.append("Key Research Findings:")
            for i, point in enumerate(key_points[:8], 1):
                context_parts.append(f"• {point}")
        
        if articles:
            context_parts.append(f"\nBased on {len(articles)} authoritative sources")
        
        return "\n".join(context_parts)
    
    def _apply_synonym_variation(self, text: str) -> str:
        """Apply synonym replacement (same as AI Draft Generator)"""
        words = text.split()
        varied_words = []
        last_replacement = None
        
        for i, word in enumerate(words):
            word_lower = word.lower().strip('.,!?;:')
            
            if last_replacement and i - last_replacement < 3:
                varied_words.append(word)
                continue
            
            if word_lower in SYNONYM_DICT and random.random() < 0.40:
                synonym = random.choice(SYNONYM_DICT[word_lower])
                if word and word[0].isupper():
                    synonym = synonym.capitalize()
                varied_words.append(synonym)
                last_replacement = i
            else:
                varied_words.append(word)
        
        return ' '.join(varied_words)
    
    def _vary_sentence_structure(self, text: str) -> str:
        """Vary sentence structure (same as AI Draft Generator)"""
        sentences = re.split(r'([.!?]\s+)', text)
        varied_sentences = []
        
        for i, sent in enumerate(sentences):
            if not sent.strip() or sent in ['. ', '! ', '? ']:
                varied_sentences.append(sent)
                continue
            
            if random.random() < 0.25 and len(sent) > 40:
                if ', ' in sent:
                    parts = sent.split(', ', 1)
                    if len(parts) == 2 and len(parts[1]) > 20:
                        if parts[1][0].islower():
                            sent = f"{parts[1][0].upper()}{parts[1][1:]}, while {parts[0].lower()}"
                        else:
                            sent = f"{parts[1]}, while {parts[0].lower()}"
            
            varied_sentences.append(sent)
        
        return ''.join(varied_sentences)
    
    def _boost_uniqueness(self, text: str) -> str:
        """Boost uniqueness with varied connectors (same as AI Draft Generator)"""
        sentences = re.split(r'([.!?]\s+)', text)
        varied_sentences = []
        
        starters = [
            'Additionally, ', 'Furthermore, ', 'Moreover, ', 'In particular, ',
            'Notably, ', 'Significantly, ', 'Research indicates that ', 
            'According to studies, ', 'Data suggests that ', 'Evidence shows that ',
            'Meanwhile, ', 'In contrast, ', 'As a result, ', 'Consequently, ',
            'Interestingly, ', 'Remarkably, ', 'In fact, ', 'What\'s more, ',
            'From this perspective, ', 'Taking into account these findings, ',
        ]
        
        used_starters = set()
        
        for i, sent in enumerate(sentences):
            if i > 0 and i % 4 == 0 and sent.strip() and len(sent) > 20:
                available_starters = [s for s in starters if s not in used_starters]
                if not available_starters:
                    used_starters.clear()
                    available_starters = starters
                
                if not any(sent.strip().startswith(s.strip()) for s in starters):
                    if random.random() > 0.4:
                        starter = random.choice(available_starters)
                        used_starters.add(starter)
                        sent = starter + sent.strip()[0].lower() + sent.strip()[1:]
            varied_sentences.append(sent)
        
        return ''.join(varied_sentences)
    
    def _clean_generated_text(self, text: str) -> str:
        """Clean AI-generated text (same as AI Draft Generator)"""
        unwanted_phrases = [
            "Note: This article", "Disclaimer:", "Generated by", "AI-generated",
            "[This article", "This content was", "As an AI", "I cannot", "I apologize",
            "In conclusion,", "To summarize,", "In summary,", "To sum up,",
        ]
        
        cleaned = text
        
        for phrase in unwanted_phrases:
            if phrase in cleaned:
                pos = cleaned.find(phrase)
                if pos > 500:
                    cleaned = cleaned[:pos].strip()
                    break
        
        section_patterns = [
            r'^\s*(?:Introduction|Background|Context|Main Details|Analysis|Impact|Conclusion|Summary|Overview)\s*:\s*',
            r'\n\s*(?:Introduction|Background|Context|Main Details|Analysis|Impact|Conclusion|Summary|Overview)\s*:\s*',
        ]
        
        for pattern in section_patterns:
            cleaned = re.sub(pattern, '\n\n', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r'^\s*[-*•]\s+', '', cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _generate_article(self, 
                         topic: str, 
                         key_points: List[str], 
                         articles: List[Dict],
                         target_words: int) -> str:
        """
        DEPRECATED: Use _generate_article_with_ai instead
        Kept for backward compatibility
        """
        return self._generate_article_with_ai(topic, key_points, articles, target_words)
    
    def _template_article(self, 
                         topic: str, 
                         key_points: List[str], 
                         articles: List[Dict]) -> str:
        """
        Generate article using template-based approach (fallback)
        
        Args:
            topic: Article topic
            key_points: Key points to include
            articles: Source articles
        
        Returns:
            Article text
        """
        sections = []
        
        # Introduction
        intro = f"""# {topic}

This comprehensive article explores the key aspects and recent developments in {topic}. 
Based on research from multiple authoritative sources, we examine the most important points 
and implications related to this topic.

## Introduction

{topic} has become increasingly important in recent times. This article provides an in-depth 
analysis of the subject matter, drawing from current research and expert perspectives.
"""
        sections.append(intro)
        
        # Main content sections
        if key_points:
            sections.append("\n## Key Findings\n")
            for i, point in enumerate(key_points[:8], 1):
                sections.append(f"{i}. {point}")
        
        # Analysis section
        sections.append(f"""
## Analysis and Implications

The research indicates several important trends in {topic}:

- There is growing recognition of the importance of this topic across various sectors
- Recent developments have highlighted new opportunities and challenges
- Stakeholders are increasingly focused on understanding and addressing key issues
- Future developments are likely to be shaped by evolving technological and market factors

## Conclusion

{topic} represents a significant area of ongoing research and development. As highlighted 
through this analysis, there are multiple perspectives and approaches to understanding and 
addressing this topic. Continued research and collaboration among experts will be essential 
to advancing knowledge in this field.
""")
        
        return '\n'.join(sections)
    
    def _format_with_citations(self, article: str, articles: List[Dict]) -> str:
        """
        Add proper citations to article
        
        Args:
            article: Generated article text
            articles: Source articles with URLs
        
        Returns:
            Article with formatted citations
        """
        formatted = article
        
        # Add sources section at end
        sources_section = "\n\n## Sources\n\n"
        for i, article_info in enumerate(articles[:10], 1):
            sources_section += f"[{i}] {article_info.get('title', 'Unknown')}: {article_info.get('url', '#')}\n"
        
        formatted += sources_section
        return formatted
    
    def find_images(self, topic: str, count: int = 3) -> List[Dict]:
        """
        Find relevant images for article topic
        
        Args:
            topic: Article topic
            count: Number of images to find
        
        Returns:
            List of image dicts with 'url', 'title', 'source'
        """
        try:
            # Using Unsplash API (free, no key required)
            url = "https://unsplash.com/napi/search/photos"
            params = {
                'query': topic,
                'per_page': count,
                'order_by': 'relevant'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Image search failed: {response.status_code}")
                return []
            
            images = []
            try:
                data = response.json()
                for result in data.get('results', []):
                    images.append({
                        'url': result['urls']['regular'],
                        'title': result.get('description', 'Image'),
                        'source': 'Unsplash',
                        'author': result.get('user', {}).get('name', 'Unknown')
                    })
            except:
                pass
            
            logger.info(f"   Found {len(images)} images")
            return images
        
        except Exception as e:
            logger.warning(f"Image search error: {e}")
            return []
    
    def save_as_draft(self, topic: str, article: str, db_path: Optional[str] = None) -> bool:
        """
        Save generated article as draft in database
        
        Args:
            topic: Article topic (becomes title)
            article: Article content
            db_path: Optional custom database path
        
        Returns:
            Success status
        """
        try:
            db = db_path or self.db_path
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            
            # Insert into ai_drafts table
            cursor.execute('''
                INSERT INTO ai_drafts 
                (title, body_draft, summary, source_url, created_date, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                topic,
                article,
                article[:200] + '...',  # Summary
                f'research://{topic}',
                datetime.now(),
                'research'
            ))
            
            conn.commit()
            draft_id = cursor.lastrowid
            conn.close()
            
            logger.info(f"✅ Saved as draft ID: {draft_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save draft: {e}")
            return False
    
    def clear_cache(self):
        """Clear article cache"""
        self.article_cache.clear()
        logger.info("Cache cleared")
