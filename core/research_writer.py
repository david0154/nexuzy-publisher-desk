"""
Advanced Research Writer Module - AI-Powered Deep Research & Article Generation
Features: 
- 🌐 Internet search integration (DuckDuckGo, Google)
- 📎 Optional URL source input
- 🔍 Multi-source web scraping
- 🧠 AI-powered content analysis
- 📊 Live progress tracking
- 💾 Intelligent caching
- 🔗 Auto-citation generation
"""

import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime
import sqlite3
from pathlib import Path
import re
import time
import random
import json
from urllib.parse import urlparse, quote_plus
import hashlib

try:
    from bs4 import BeautifulSoup
    BS_AVAILABLE = True
except ImportError:
    BS_AVAILABLE = False
    BeautifulSoup = None

try:
    import newspaper
    from newspaper import Article as NewsArticle
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

logger = logging.getLogger(__name__)

# GLOBAL MODEL CACHE - shared with AI Draft Generator
_CACHED_MODEL = None
_CACHED_SENTENCE_MODEL = None

# Import synonym dictionary from ai_draft_generator
try:
    from core.ai_draft_generator import SYNONYM_DICT, TITLE_PATTERNS
except:
    SYNONYM_DICT = {
        'said': ['stated', 'mentioned', 'noted', 'explained', 'announced', 'declared', 'reported'],
        'new': ['recent', 'latest', 'fresh', 'novel', 'emerging', 'contemporary'],
        'important': ['crucial', 'vital', 'essential', 'critical', 'key', 'significant'],
        'shows': ['indicates', 'demonstrates', 'reveals', 'suggests', 'illustrates'],
        'found': ['discovered', 'identified', 'uncovered', 'revealed', 'detected'],
        'big': ['large', 'substantial', 'significant', 'considerable', 'major'],
        'good': ['beneficial', 'positive', 'favorable', 'advantageous', 'promising'],
        'bad': ['negative', 'adverse', 'unfavorable', 'detrimental', 'problematic'],
    }
    TITLE_PATTERNS = ["{topic}: What This Means", "{topic}: Analysis"]

class ResearchWriter:
    """Advanced AI-powered research and article generation engine with internet access"""
    
    def __init__(self, db_path: str = 'nexuzy.db', cache_articles: bool = True, 
                 model_name: str = 'models/mistral-7b-instruct-v0.2.Q4_K_M.gguf'):
        global _CACHED_MODEL, _CACHED_SENTENCE_MODEL
        
        self.db_path = db_path
        self.cache_articles = cache_articles
        self.article_cache = {}
        self.session = self._create_session()
        self.model_name = model_name
        self._ensure_research_table()
        
        # Progress tracking
        self.progress_callback = None
        self.current_progress = 0
        
        # Search engines configuration
        self.search_engines = {
            'duckduckgo': {'enabled': True, 'priority': 1},
            'google': {'enabled': True, 'priority': 2},
        }
        
        # Use GLOBAL cached model
        if _CACHED_MODEL:
            logger.info("✅ Research Writer using GLOBAL cached AI model")
            self.llm = _CACHED_MODEL
        else:
            logger.info("⏳ Loading AI model for Research Writer...")
            self.llm = self._load_model()
            if self.llm:
                _CACHED_MODEL = self.llm
                logger.info("💾 Model cached GLOBALLY")
        
        if _CACHED_SENTENCE_MODEL:
            self.sentence_model = _CACHED_SENTENCE_MODEL
        else:
            self.sentence_model = self._load_sentence_model()
            if self.sentence_model:
                _CACHED_SENTENCE_MODEL = self.sentence_model
        
        logger.info(f"✅ Advanced Research Writer initialized (Internet: ✓, URL Input: ✓, AI: {'✓' if self.llm else '⚠️'})")
    
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def _update_progress(self, progress: int, status: str):
        """Update progress and call callback if set"""
        self.current_progress = progress
        if self.progress_callback:
            self.progress_callback(progress, status)
        logger.info(f"[{progress}%] {status}")
    
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
        """Load GGUF model"""
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
        """Load sentence improvement model"""
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
        """Create configured requests session with better headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        return session
    
    def _ensure_research_table(self):
        """Ensure research cache table exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS research_cache (
                    id INTEGER PRIMARY KEY,
                    topic TEXT,
                    topic_hash TEXT UNIQUE,
                    article_content TEXT,
                    sources TEXT,
                    created_date TIMESTAMP,
                    word_count INTEGER,
                    quality_score REAL
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Could not create research table: {e}")
    
    def research_and_generate(self, 
                             topic: str, 
                             source_urls: Optional[List[str]] = None,
                             word_count: int = 1500,
                             use_internet: bool = True) -> Dict:
        """
        🚀 ADVANCED: Complete research workflow with internet access and optional URL sources
        
        Args:
            topic: Research topic
            source_urls: Optional list of specific URLs to analyze (NEW!)
            word_count: Target article length (1000-2000)
            use_internet: Enable internet search (NEW!)
        
        Returns:
            Dict with generated article and comprehensive metadata
        """
        logger.info(f"🔬 Starting ADVANCED research for: {topic}")
        logger.info(f"   Internet: {'✓' if use_internet else '✗'} | URL Sources: {len(source_urls) if source_urls else 0}")
        start_time = time.time()
        
        # Generate cache key
        cache_key = self._generate_cache_key(topic, source_urls)
        
        # Check cache
        if self.cache_articles:
            cached = self._check_cache(cache_key)
            if cached:
                self._update_progress(100, "Using cached article")
                return cached
        
        try:
            # Step 1: Gather sources
            self._update_progress(10, "🌐 Gathering sources...")
            sources = []
            
            # Add user-provided URLs first
            if source_urls:
                sources.extend(source_urls)
                logger.info(f"   Added {len(source_urls)} user-provided URLs")
            
            # Internet search if enabled
            if use_internet:
                search_results = self._advanced_web_search(topic, num_results=8)
                sources.extend(search_results)
                logger.info(f"   Found {len(search_results)} URLs from internet search")
            
            if not sources:
                return {
                    'success': False,
                    'error': 'No sources found. Enable internet search or provide URLs.',
                    'topic': topic
                }
            
            # Remove duplicates
            sources = list(dict.fromkeys(sources))
            logger.info(f"   Total unique sources: {len(sources)}")
            
            # Step 2: Advanced scraping
            self._update_progress(25, f"📰 Scraping {len(sources)} sources...")
            articles = self._advanced_scrape_articles(sources)
            scraped_count = len([a for a in articles if a.get('content')])
            logger.info(f"   Successfully scraped: {scraped_count}/{len(sources)}")
            
            if not articles:
                return {
                    'success': False,
                    'error': 'Could not extract content from any source',
                    'topic': topic
                }
            
            # Step 3: Deep analysis
            self._update_progress(45, "🧠 Analyzing content...")
            key_points = self._extract_key_points(articles, topic)
            facts = self._extract_facts(articles)
            quotes = self._extract_quotes(articles)
            
            # Step 4: AI generation
            self._update_progress(65, "✍️ Generating article with AI...")
            article = self._generate_article_with_ai(topic, key_points, articles, word_count, facts, quotes)
            
            # Step 5: Enhancement
            self._update_progress(85, "✨ Enhancing and formatting...")
            formatted_article = self._format_with_citations(article, articles)
            quality_score = self._calculate_quality_score(formatted_article, articles)
            
            # Step 6: Cache result
            self._update_progress(95, "💾 Caching results...")
            
            elapsed = time.time() - start_time
            
            result = {
                'success': True,
                'topic': topic,
                'article': formatted_article,
                'sources_used': len(articles),
                'word_count': len(formatted_article.split()),
                'sources': [{
                    'url': a.get('url'), 
                    'title': a.get('title'),
                    'credibility': a.get('credibility', 0.7)
                } for a in articles],
                'generation_time': f"{elapsed:.1f}s",
                'quality_score': quality_score,
                'facts_count': len(facts),
                'quotes_count': len(quotes),
                'internet_used': use_internet,
                'user_urls': len(source_urls) if source_urls else 0,
                'status': '✅ Advanced research article generated successfully'
            }
            
            # Cache result
            if self.cache_articles:
                self._save_to_cache(cache_key, topic, result)
            
            self._update_progress(100, "✅ Complete!")
            logger.info(f"✅ Generated {result['word_count']} words | Quality: {quality_score:.1f}/10 | Time: {elapsed:.1f}s")
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
    
    def _generate_cache_key(self, topic: str, urls: Optional[List[str]]) -> str:
        """Generate unique cache key"""
        key_data = topic.lower()
        if urls:
            key_data += '|' + '|'.join(sorted(urls))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[Dict]:
        """Check database cache for existing research"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT article_content, sources, word_count, quality_score, created_date
                FROM research_cache
                WHERE topic_hash = ?
                AND created_date > datetime('now', '-7 days')
            ''', (cache_key,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                logger.info("📦 Using cached research article")
                return {
                    'success': True,
                    'article': row[0],
                    'sources': json.loads(row[1]) if row[1] else [],
                    'word_count': row[2],
                    'quality_score': row[3],
                    'cached': True,
                    'cache_date': row[4]
                }
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
        
        return None
    
    def _save_to_cache(self, cache_key: str, topic: str, result: Dict):
        """Save research result to cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO research_cache
                (topic_hash, topic, article_content, sources, created_date, word_count, quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                cache_key,
                topic,
                result['article'],
                json.dumps(result['sources']),
                datetime.now(),
                result['word_count'],
                result.get('quality_score', 0)
            ))
            
            conn.commit()
            conn.close()
            logger.info("💾 Research cached to database")
        except Exception as e:
            logger.warning(f"Failed to cache: {e}")
    
    def _advanced_web_search(self, topic: str, num_results: int = 8) -> List[str]:
        """
        🌐 ADVANCED: Multi-engine web search with fallbacks
        
        Args:
            topic: Search query
            num_results: Number of results
        
        Returns:
            List of URLs
        """
        urls = []
        
        # Try DuckDuckGo first
        if self.search_engines['duckduckgo']['enabled']:
            ddg_urls = self._search_duckduckgo(topic, num_results)
            urls.extend(ddg_urls)
            logger.info(f"   DuckDuckGo: {len(ddg_urls)} results")
        
        # Try Google if needed
        if len(urls) < num_results and self.search_engines['google']['enabled']:
            google_urls = self._search_google(topic, num_results - len(urls))
            urls.extend(google_urls)
            logger.info(f"   Google: {len(google_urls)} results")
        
        return list(dict.fromkeys(urls))  # Remove duplicates
    
    def _search_duckduckgo(self, query: str, num_results: int) -> List[str]:
        """Search using DuckDuckGo"""
        try:
            # DuckDuckGo HTML search
            url = "https://html.duckduckgo.com/html/"
            data = {'q': query}
            
            response = self.session.post(url, data=data, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"DuckDuckGo search failed: {response.status_code}")
                return []
            
            if not BS_AVAILABLE:
                # Fallback: regex extraction
                urls = re.findall(r'uddg=([^"&]+)', response.text)
                from urllib.parse import unquote
                return [unquote(url) for url in urls[:num_results] if 'http' in url]
            
            soup = BeautifulSoup(response.content, 'html.parser')
            urls = []
            
            for result in soup.find_all('a', class_='result__url', limit=num_results * 2):
                href = result.get('href', '')
                if href.startswith('//'):
                    href = 'https:' + href
                elif not href.startswith('http'):
                    continue
                
                # Extract actual URL from DuckDuckGo redirect
                if 'uddg=' in href:
                    from urllib.parse import parse_qs, urlparse
                    parsed = urlparse(href)
                    params = parse_qs(parsed.query)
                    if 'uddg' in params:
                        href = params['uddg'][0]
                
                if href and href.startswith('http'):
                    urls.append(href)
                
                if len(urls) >= num_results:
                    break
            
            return urls
        
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def _search_google(self, query: str, num_results: int) -> List[str]:
        """Search using Google (basic HTML parsing)"""
        try:
            # Google search URL
            url = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}"
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Google search failed: {response.status_code}")
                return []
            
            if not BS_AVAILABLE:
                # Fallback: regex extraction
                urls = re.findall(r'https?://[^"<>\s]+', response.text)
                # Filter out Google's own URLs
                filtered = [u for u in urls if 'google.com' not in u and 'gstatic.com' not in u]
                return filtered[:num_results]
            
            soup = BeautifulSoup(response.content, 'html.parser')
            urls = []
            
            for link in soup.find_all('a'):
                href = link.get('href', '')
                
                # Extract URL from Google's redirect format
                if '/url?q=' in href:
                    try:
                        from urllib.parse import parse_qs, urlparse
                        parsed = urlparse(href)
                        params = parse_qs(parsed.query)
                        if 'q' in params:
                            actual_url = params['q'][0]
                            if actual_url.startswith('http') and 'google.com' not in actual_url:
                                urls.append(actual_url)
                    except:
                        pass
                
                if len(urls) >= num_results:
                    break
            
            return urls
        
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return []
    
    def _advanced_scrape_articles(self, urls: List[str]) -> List[Dict]:
        """
        🔍 ADVANCED: Multi-method article scraping with newspaper3k fallback
        
        Args:
            urls: List of URLs to scrape
        
        Returns:
            List of article dicts with metadata
        """
        articles = []
        
        for i, url in enumerate(urls, 1):
            self._update_progress(25 + (i * 15 // len(urls)), f"Scraping source {i}/{len(urls)}")
            
            try:
                logger.debug(f"   [{i}/{len(urls)}] {url[:60]}...")
                
                # Method 1: newspaper3k (best for news articles)
                if NEWSPAPER_AVAILABLE:
                    article_data = self._scrape_with_newspaper(url)
                    if article_data:
                        articles.append(article_data)
                        logger.debug(f"   ✅ newspaper3k: {len(article_data.get('content', ''))} chars")
                        continue
                
                # Method 2: BeautifulSoup (fallback)
                if BS_AVAILABLE:
                    article_data = self._scrape_with_bs4(url)
                    if article_data:
                        articles.append(article_data)
                        logger.debug(f"   ✅ BeautifulSoup: {len(article_data.get('content', ''))} chars")
                        continue
                
                # Method 3: Basic regex (last resort)
                article_data = self._scrape_basic(url)
                if article_data:
                    articles.append(article_data)
                    logger.debug(f"   ✅ Basic scrape: {len(article_data.get('content', ''))} chars")
                else:
                    logger.debug(f"   ⚠️ Failed to extract content")
            
            except Exception as e:
                logger.debug(f"   ❌ Error: {str(e)[:50]}")
                continue
            
            time.sleep(0.3)  # Rate limiting
        
        return articles
    
    def _scrape_with_newspaper(self, url: str) -> Optional[Dict]:
        """Scrape using newspaper3k library"""
        try:
            article = NewsArticle(url)
            article.download()
            article.parse()
            
            if len(article.text) < 200:
                return None
            
            return {
                'url': url,
                'title': article.title or url,
                'content': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'top_image': article.top_image,
                'credibility': 0.8
            }
        except:
            return None
    
    def _scrape_with_bs4(self, url: str) -> Optional[Dict]:
        """Scrape using BeautifulSoup"""
        try:
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = None
            for selector in ['h1', 'title', 'meta[property="og:title"]']:
                if '[' in selector:
                    tag = soup.find('meta', property='og:title')
                    if tag:
                        title = tag.get('content')
                else:
                    tag = soup.find(selector)
                    if tag:
                        title = tag.get_text(strip=True)
                if title:
                    break
            
            # Extract content
            content = None
            selectors = [
                soup.find('article'),
                soup.find('main'),
                soup.find(class_=re.compile('content|article|post|entry', re.I)),
                soup.find('div', {'id': re.compile('content|article|post', re.I)})
            ]
            
            for selector in selectors:
                if selector:
                    # Remove unwanted elements
                    for tag in selector.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header']):
                        tag.decompose()
                    
                    content = selector.get_text(separator=' ', strip=True)
                    if len(content) > 200:
                        break
            
            if not content or len(content) < 200:
                body = soup.find('body')
                if body:
                    for tag in body.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header']):
                        tag.decompose()
                    content = body.get_text(separator=' ', strip=True)
            
            if content and len(content) > 200:
                return {
                    'url': url,
                    'title': title or url,
                    'content': ' '.join(content.split())[:6000],
                    'credibility': 0.7
                }
        except:
            pass
        
        return None
    
    def _scrape_basic(self, url: str) -> Optional[Dict]:
        """Basic text extraction as last resort"""
        try:
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return None
            
            # Remove HTML tags
            text = re.sub(r'<script[^>]*>.*?</script>', '', response.text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = ' '.join(text.split())
            
            if len(text) > 200:
                return {
                    'url': url,
                    'title': url,
                    'content': text[:5000],
                    'credibility': 0.5
                }
        except:
            pass
        
        return None
    
    def _extract_key_points(self, articles: List[Dict], topic: str) -> List[str]:
        """Extract key points from articles"""
        key_points = []
        
        for article in articles:
            content = article.get('content', '')
            if not content:
                continue
            
            sentences = re.split(r'[.!?]+', content)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence.split()) > 5 and len(sentence.split()) < 50:
                    if any(word in sentence.lower() for word in topic.lower().split()):
                        key_points.append(sentence)
                        if len(key_points) >= 15:
                            break
            
            if len(key_points) >= 15:
                break
        
        return key_points[:15]
    
    def _extract_facts(self, articles: List[Dict]) -> List[str]:
        """Extract factual statements from articles"""
        facts = []
        
        for article in articles:
            content = article.get('content', '')
            sentences = re.split(r'[.!?]+', content)
            
            for sent in sentences:
                sent = sent.strip()
                if len(sent.split()) < 5 or len(sent.split()) > 40:
                    continue
                
                has_number = bool(re.search(r'\d+', sent))
                has_date = bool(re.search(r'\b(20\d{2}|\d{1,2}\s+\w+|\w+\s+\d{1,2})', sent))
                has_stat = any(word in sent.lower() for word in ['percent', '%', 'million', 'billion', 'thousand'])
                
                if has_number or has_date or has_stat:
                    facts.append(sent)
                    if len(facts) >= 10:
                        return facts
        
        return facts
    
    def _extract_quotes(self, articles: List[Dict]) -> List[Dict]:
        """Extract quotes from articles"""
        quotes = []
        
        for article in articles:
            content = article.get('content', '')
            
            # Find quoted text
            quote_matches = re.findall(r'[""""]([^"""]{20,200})[""""]', content)
            
            for quote_text in quote_matches:
                quote_text = quote_text.strip()
                if len(quote_text.split()) >= 5:
                    quotes.append({
                        'text': quote_text,
                        'source': article.get('title', 'Unknown'),
                        'url': article.get('url', '')
                    })
                    
                    if len(quotes) >= 5:
                        return quotes
        
        return quotes
    
    def _generate_article_with_ai(self, topic: str, key_points: List[str], 
                                  articles: List[Dict], target_words: int,
                                  facts: List[str], quotes: List[Dict]) -> str:
        """
        🔥 Generate article using AI MODEL
        Falls back to template if AI unavailable
        """
        if not self.llm:
            logger.warning("⚠️ AI model not available, using template generation")
            return self._template_article(topic, key_points, articles)
        
        try:
            research_context = self._prepare_research_context(key_points, articles, facts, quotes)
            
            writing_styles = [
                "Write like an experienced researcher with expertise in this field",
                "Write in a clear, accessible style that educates readers",
                "Write with authority backed by research and data",
                "Write comprehensively, exploring multiple perspectives",
            ]
            
            style_instruction = random.choice(writing_styles)
            
            prompt = f"""You are a professional researcher and writer. {style_instruction}

Topic: {topic}

Research Context:
{research_context}

Write a comprehensive research article ({target_words} words). Requirements:

WRITING STYLE:
1. Write naturally with varied sentence structure
2. Use active voice
3. Include specific details and evidence
4. Use smooth logical transitions
5. Vary paragraph length (2-5 sentences)

UNIQUENESS REQUIREMENTS:
1. Use original phrasing
2. Present unique analytical angles
3. Include deep analysis

DO NOT:
- Include section labels
- Use repetitive sentence starters
- Include meta-commentary

Write the article now:

"""
            
            logger.info("⏳ Generating with AI model (60-90 seconds)...")
            
            generated_text = self.llm(
                prompt,
                max_new_tokens=1500,
                temperature=0.90,
                top_p=0.95,
                repetition_penalty=1.35,
                stop=["\n\n\n\n", "Article:", "Summary:"],
                stream=False
            )
            
            if not generated_text or not isinstance(generated_text, str):
                generated_text = str(generated_text) if generated_text else ""
            
            generated_text = generated_text.strip()
            
            if len(generated_text) < 500:
                logger.error(f"❌ Generated text too short: {len(generated_text)} chars")
                return self._template_article(topic, key_points, articles)
            
            cleaned_text = self._clean_generated_text(generated_text)
            word_count = len(cleaned_text.split())
            logger.info(f"✅ AI generated {word_count} words")
            
            return cleaned_text
        
        except Exception as e:
            logger.error(f"❌ AI generation failed: {e}, using template")
            return self._template_article(topic, key_points, articles)
    
    def _prepare_research_context(self, key_points: List[str], articles: List[Dict],
                                  facts: List[str], quotes: List[Dict]) -> str:
        """Prepare research context summary for AI"""
        context_parts = []
        
        if key_points:
            context_parts.append("Key Research Findings:")
            for i, point in enumerate(key_points[:8], 1):
                context_parts.append(f"• {point}")
        
        if facts:
            context_parts.append("\nKey Facts:")
            for fact in facts[:5]:
                context_parts.append(f"• {fact}")
        
        if articles:
            context_parts.append(f"\nBased on {len(articles)} authoritative sources")
        
        return "\n".join(context_parts)
    
    def _clean_generated_text(self, text: str) -> str:
        """Clean AI-generated text"""
        unwanted_phrases = [
            "Note: This article", "Disclaimer:", "Generated by", "AI-generated",
            "[This article", "As an AI", "I cannot", "I apologize",
            "In conclusion,", "To summarize,", "In summary:",
        ]
        
        cleaned = text
        
        for phrase in unwanted_phrases:
            if phrase in cleaned:
                pos = cleaned.find(phrase)
                if pos > 500:
                    cleaned = cleaned[:pos].strip()
                    break
        
        section_patterns = [
            r'^\s*(?:Introduction|Background|Analysis|Conclusion):\s*',
            r'\n\s*(?:Introduction|Background|Analysis|Conclusion):\s*',
        ]
        
        for pattern in section_patterns:
            cleaned = re.sub(pattern, '\n\n', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _template_article(self, topic: str, key_points: List[str], articles: List[Dict]) -> str:
        """Generate article using template (fallback)"""
        sections = []
        
        intro = f"""# {topic}

This article explores the key aspects and recent developments in {topic}. Based on research from multiple sources, we examine the most important points and implications.

{topic} has become increasingly important. This analysis draws from current research and expert perspectives."""
        
        sections.append(intro)
        
        if key_points:
            sections.append("\n## Key Findings\n")
            for i, point in enumerate(key_points[:8], 1):
                sections.append(f"{i}. {point}")
        
        sections.append(f"""

## Analysis

The research indicates several important trends in {topic}:

- Growing recognition of importance across sectors
- New opportunities and challenges emerging
- Stakeholders focused on understanding key issues
- Future developments shaped by evolving factors

## Conclusion

{topic} represents a significant area of ongoing research. Multiple perspectives exist for understanding this topic. Continued research and collaboration will advance knowledge in this field.
""")
        
        return '\n'.join(sections)
    
    def _format_with_citations(self, article: str, articles: List[Dict]) -> str:
        """Add citations to article"""
        formatted = article
        
        sources_section = "\n\n## Sources\n\n"
        for i, article_info in enumerate(articles[:10], 1):
            sources_section += f"[{i}] {article_info.get('title', 'Unknown')}: {article_info.get('url', '#')}\n"
        
        formatted += sources_section
        return formatted
    
    def _calculate_quality_score(self, article: str, articles: List[Dict]) -> float:
        """Calculate article quality score (0-10)"""
        score = 5.0
        
        word_count = len(article.split())
        if 800 <= word_count <= 2000:
            score += 1.0
        elif word_count >= 500:
            score += 0.5
        
        if len(articles) >= 5:
            score += 1.0
        elif len(articles) >= 3:
            score += 0.5
        
        unique_words = len(set(article.lower().split()))
        if unique_words / word_count > 0.5:
            score += 1.0
        
        paragraphs = article.count('\n\n')
        if paragraphs >= 5:
            score += 0.5
        
        has_numbers = bool(re.search(r'\d+', article))
        if has_numbers:
            score += 0.5
        
        avg_credibility = sum(a.get('credibility', 0.5) for a in articles) / len(articles) if articles else 0.5
        score += avg_credibility * 1.0
        
        return min(10.0, max(0.0, score))
    
    def save_as_draft(self, topic: str, article: str, db_path: Optional[str] = None) -> bool:
        """Save article as draft"""
        try:
            db = db_path or self.db_path
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ai_drafts 
                (title, body_draft, summary, source_url, created_date, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                topic,
                article,
                article[:200] + '...',
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
