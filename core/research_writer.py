"""
Advanced Research Writer Module - AI-Powered Deep Research & Article Generation
✨ NOW WITH TECHNICAL ANALYSIS INTEGRATION

Features: 
- 🌐 Internet search integration (DuckDuckGo, Google)
- 📎 Optional URL source input
- 🔍 Multi-source web scraping
- 🧠 AI-powered content analysis
- 📊 Live progress tracking
- 💾 Intelligent caching
- 🔗 Auto-citation generation
- 🔒 Security & technical analysis (NEW!)
- 🐛 Bug detection & reporting (NEW!)
- ⚡ Performance metrics (NEW!)
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
import concurrent.futures
import threading

try:
    from bs4 import BeautifulSoup
    BS_AVAILABLE = True
except ImportError:
    BS_AVAILABLE = False
    BeautifulSoup = None

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

try:
    from newspaper import Article as NewsArticle
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False
    NewsArticle = None

# ✨ NEW: Import Technical Analyzer
try:
    from core.technical_analyzer import TechnicalAnalyzer
    TECH_ANALYZER_AVAILABLE = True
except ImportError:
    TECH_ANALYZER_AVAILABLE = False

logger = logging.getLogger(__name__)

# GLOBAL MODEL CACHE - shared with AI Draft Generator
_CACHED_MODEL = None
_CACHED_SENTENCE_MODEL = None
_CACHED_HUMANIZER_MODEL = None

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
    """Advanced AI-powered research and article generation engine with internet access and technical analysis"""
    
    def __init__(self, db_path: str = 'nexuzy.db', cache_articles: bool = True, 
                 model_name: str = 'models/mistral-7b-instruct-v0.2.Q4_K_M.gguf'):
        global _CACHED_MODEL, _CACHED_SENTENCE_MODEL, _CACHED_HUMANIZER_MODEL
        
        self.db_path = db_path
        self.cache_articles = cache_articles
        self.article_cache = {}
        self.session = self._create_session()
        self.model_name = model_name
        self._ensure_research_table()
        
        # ✨ NEW: Initialize Technical Analyzer
        if TECH_ANALYZER_AVAILABLE:
            try:
                self.tech_analyzer = TechnicalAnalyzer()
                logger.info("✅ Technical Analyzer enabled")
            except Exception as e:
                logger.warning(f"⚠️ Technical Analyzer initialization failed: {e}")
                self.tech_analyzer = None
        else:
            self.tech_analyzer = None
            logger.info("ℹ️ Technical Analyzer not available (optional feature)")
        
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
        
        # Load Humanizer Model
        if _CACHED_HUMANIZER_MODEL:
            logger.info("✅ Research Writer using GLOBAL cached Humanizer model")
            self.humanizer_model = _CACHED_HUMANIZER_MODEL
        else:
            logger.info("⏳ Loading Humanizer AI model...")
            self.humanizer_model = self._load_humanizer_model()
            if self.humanizer_model:
                _CACHED_HUMANIZER_MODEL = self.humanizer_model
                logger.info("💾 Humanizer model cached GLOBALLY")
        
        tech_status = '✓' if self.tech_analyzer else '○'
        humanizer_status = '✓' if self.humanizer_model else '○'
        logger.info(f"✅ Advanced Research Writer initialized (Internet: ✓, URL Input: ✓, AI: {'✓' if self.llm else '⚠️'}, Humanizer: {humanizer_status}, Tech Analysis: {tech_status})")
    
    @property
    def model(self):
        """Compatibility property: returns self.llm for code checking .model attribute"""
        return self.llm
    
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
    
    def _load_humanizer_model(self):
        """Load small AI model for humanizing articles"""
        try:
            from transformers import pipeline
            logger.info("Loading humanizer AI model...")
            
            # Use a small, fast model for text generation/humanization
            model = pipeline(
                "text-generation",
                model="distilgpt2",
                device=-1,
                pad_token_id=50256  # GPT-2 pad token
            )
            logger.info("✅ Humanizer model loaded (distilgpt2)")
            return model
        except Exception as e:
            logger.warning(f"⚠️ Humanizer model unavailable: {e}")
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
        """Ensure research cache table exists with all required columns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if table exists and has the right structure
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='research_cache'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                # Check if topic_hash column exists
                cursor.execute("PRAGMA table_info(research_cache)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'topic_hash' not in columns:
                    logger.info("Recreating research_cache table with missing topic_hash column")
                    # Drop and recreate table
                    cursor.execute("DROP TABLE research_cache")
                    cursor.execute('''
                        CREATE TABLE research_cache (
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
            else:
                # Create table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE research_cache (
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
            logger.warning(f"Could not create/update research table: {e}")
    
    def write_research_article(self, 
                               topic: str, 
                               length: int = 1500,
                               style: str = "professional",
                               workspace_id: Optional[str] = None,
                               source_urls: Optional[List[str]] = None,
                               use_internet: bool = True,
                               technical_analysis: bool = False) -> Dict:
        """
        🚀 ADVANCED: Complete research workflow with internet access, optional URL sources, and technical analysis
        
        Args:
            topic: Research topic
            length: Target article length (1000-2000)
            style: Writing style (professional, casual, academic, etc.)
            workspace_id: Optional workspace identifier for multi-workspace support
            source_urls: Optional list of specific URLs to analyze
            use_internet: Enable internet search
            technical_analysis: Enable deep technical/security analysis of URLs (NEW!)
        
        Returns:
            Dict with generated article, metadata, and optional technical reports
        """
        logger.info(f"🔬 Starting ADVANCED research for: {topic}")
        logger.info(f"   Internet: {'✓' if use_internet else '✗'} | URL Sources: {len(source_urls) if source_urls else 0} | Tech Analysis: {'✓' if technical_analysis else '✗'}")
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
            
            # Internet search if enabled - OPTIMIZED SEARCH
            if use_internet:
                # Reduced to 2 key searches for better performance
                search_queries = [
                    topic,  # Main topic
                    f"{topic} analysis",  # In-depth analysis
                ]
                
                all_search_results = []
                for query in search_queries:
                    try:
                        results = self._advanced_web_search(query, num_results=10)  # Reduced from 12
                        all_search_results.extend(results)
                        logger.info(f"   Query '{query}': {len(results)} results")
                    except Exception as e:
                        logger.warning(f"   Search failed for '{query}': {e}")
                
                # Remove duplicates and limit to reasonable number
                sources.extend(list(dict.fromkeys(all_search_results))[:15])  # Reduced from 20
                logger.info(f"   Found {len(all_search_results)} URLs from optimized internet search (using {len(sources)} unique)")
            
            if not sources:
                return {
                    'success': False,
                    'error': 'No sources found. Enable internet search or provide URLs.',
                    'topic': topic
                }
            
            # Prioritize and limit sources for efficient research
            prioritized_sources = []
            
            # Always include user-provided URLs first
            user_urls = source_urls or []
            prioritized_sources.extend(user_urls)
            
            # Add diverse sources from search results (limit to 8 for speed)
            remaining_slots = 8 - len(prioritized_sources)
            if remaining_slots > 0:
                # Filter out duplicates and low-quality sources
                search_sources = [s for s in sources if s not in user_urls and 
                                not any(domain in s.lower() for domain in ['facebook.com', 'twitter.com', 'instagram.com', 'youtube.com', 'tiktok.com'])]
                prioritized_sources.extend(search_sources[:remaining_slots])
            
            sources = prioritized_sources
            logger.info(f"   Total prioritized sources: {len(sources)} (optimized for speed)")
            
            # ✨ NEW: Step 1.5: Technical Analysis
            technical_reports = []
            if technical_analysis and self.tech_analyzer:
                self._update_progress(15, "🔒 Running technical analysis...")
                urls_to_analyze = sources[:3]  # Analyze first 3 URLs
                logger.info(f"   Analyzing {len(urls_to_analyze)} URLs for security & performance...")
                
                for idx, url in enumerate(urls_to_analyze, 1):
                    try:
                        logger.info(f"   [{idx}/{len(urls_to_analyze)}] Analyzing: {url[:60]}...")
                        tech_report = self.tech_analyzer.analyze_website(url, deep_scan=True)
                        if tech_report and tech_report.get('overall_score'):
                            technical_reports.append(tech_report)
                            logger.info(f"      Score: {tech_report.get('overall_score')}/100 | Risk: {tech_report.get('security', {}).get('risk_level', 'Unknown')}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Technical analysis failed for {url}: {str(e)[:50]}")
                
                logger.info(f"   ✅ Completed technical analysis on {len(technical_reports)} URLs")
            elif technical_analysis and not self.tech_analyzer:
                logger.warning("   ⚠️ Technical analysis requested but TechnicalAnalyzer not available")
            
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
            
            # Step 4: Generate article using high-quality template
            self._update_progress(65, "✍️ Generating article with template synthesis...")
            
            # Use template-based generation for consistent, high-quality output
            article = self._template_article(topic, key_points, articles)
            
            # Step 5: Enhancement
            self._update_progress(85, "✨ Enhancing and formatting...")
            formatted_article = self._format_with_citations(article, articles)
            
            # Step 5.2: Humanize article (skip for template-based articles - they're already high quality)
            self._update_progress(90, "✨ Finalizing article...")
            humanized_article = formatted_article  # Use as-is, don't humanize
            
            # ✨ NEW: Step 5.5: Add technical reports if available
            if technical_reports:
                logger.info(f"   Adding {len(technical_reports)} technical reports to article...")
                humanized_article += "\n\n---\n\n## 🔒 Technical Analysis Report\n\n"
                humanized_article += "*Security and performance analysis of source websites*\n\n"
                
                for i, report in enumerate(technical_reports, 1):
                    domain = report.get('domain', 'Unknown')
                    score = report.get('overall_score', 0)
                    risk = report.get('security', {}).get('risk_level', 'Unknown')
                    
                    humanized_article += f"### 🌐 Source {i}: {domain}\n\n"
                    humanized_article += f"**Overall Score:** {score}/100 | **Security Risk:** {risk}\n\n"
                    
                    # Add formatted report sections
                    humanized_article += self.tech_analyzer.format_report_for_article(report)
                    humanized_article += "\n\n---\n\n"
            
            quality_score = self._calculate_quality_score(humanized_article, articles)
            
            # Step 6: Cache result
            self._update_progress(95, "💾 Caching results...")
            
            elapsed = time.time() - start_time
            
            result = {
                'success': True,
                'topic': topic,
                'article': humanized_article,
                'sources_used': len(articles),
                'word_count': len(humanized_article.split()),
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
                'technical_reports': technical_reports if technical_reports else None,
                'technical_analysis_count': len(technical_reports) if technical_reports else 0,
                'status': '✅ Advanced research article generated successfully'
            }
            
            # Cache result
            if self.cache_articles:
                self._save_to_cache(cache_key, topic, result)
            
            self._update_progress(100, "✅ Complete!")
            logger.info(f"✅ Generated {result['word_count']} words | Quality: {quality_score:.1f}/10 | Time: {elapsed:.1f}s")
            if technical_reports:
                logger.info(f"   🔒 Technical reports: {len(technical_reports)} URLs analyzed")
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
    
    def _advanced_web_search(self, topic: str, num_results: int = 15) -> List[str]:
        """
        🌐 COMPREHENSIVE: Multi-engine web search with extensive coverage
        
        Args:
            topic: Search query
            num_results: Number of results (increased for comprehensive research)
        
        Returns:
            List of URLs
        """
        urls = []
        
        # Try DuckDuckGo first
        if self.search_engines['duckduckgo']['enabled']:
            ddg_urls = self._search_duckduckgo(topic, num_results)
            urls.extend(ddg_urls)
            logger.info(f"   DuckDuckGo: {len(ddg_urls)} results")
        
        # Try Google/Bing if needed
        if len(urls) < num_results and self.search_engines['google']['enabled']:
            google_urls = self._search_google(topic, num_results - len(urls))
            urls.extend(google_urls)
            logger.info(f"   Bing: {len(google_urls)} results")
        
        # Fallback: Add Wikipedia if no results
        if len(urls) == 0:
            wiki_url = f"https://en.wikipedia.org/wiki/{quote_plus(topic.replace(' ', '_'))}"
            urls.append(wiki_url)
            logger.info(f"   Wikipedia fallback: 1 result")
        
        return list(dict.fromkeys(urls))  # Remove duplicates
    
    def _search_duckduckgo(self, query: str, num_results: int) -> List[str]:
        """Search using DuckDuckGo API"""
        if not DDGS_AVAILABLE:
            logger.warning("DuckDuckGo search library not available")
            return []
        
        try:
            urls = []
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=num_results)
                for result in results:
                    if 'href' in result:
                        url = result['href']
                        if url and url.startswith('http') and 'duckduckgo.com' not in url:
                            urls.append(url)
            
            logger.info(f"DuckDuckGo API returned {len(urls)} results")
            return urls[:num_results]
        
        except Exception as e:
            logger.error(f"DuckDuckGo API search error: {e}")
            return []
    
    def _search_google(self, query: str, num_results: int) -> List[str]:
        """Search using Bing (more reliable than Google scraping)"""
        try:
            # Use Bing search as it's more scraper-friendly than Google
            url = f"https://www.bing.com/search?q={quote_plus(query)}&count={num_results}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Bing search failed: {response.status_code}")
                return []
            
            if not BS_AVAILABLE:
                # Fallback: regex extraction
                urls = re.findall(r'https?://[^"<>\s]+', response.text)
                # Filter out Bing's own URLs
                filtered = [u for u in urls if 'bing.com' not in u and 'microsoft.com' not in u and len(u) > 10]
                return filtered[:num_results]
            
            soup = BeautifulSoup(response.content, 'html.parser')
            urls = []
            
            # Bing search results - try different selectors
            for link in soup.find_all('a', class_='tilk'):
                href = link.get('href', '')
                if href and href.startswith('http') and 'bing.com' not in href:
                    urls.append(href)
                    if len(urls) >= num_results:
                        break
            
            # Also try h2 results
            if len(urls) < num_results:
                for h2 in soup.find_all('h2'):
                    link = h2.find('a')
                    if link:
                        href = link.get('href', '')
                        if href and href.startswith('http') and 'bing.com' not in href:
                            urls.append(href)
                            if len(urls) >= num_results:
                                break
            
            logger.info(f"Bing search returned {len(urls)} results")
            return urls[:num_results]
        
        except Exception as e:
            logger.error(f"Bing search error: {e}")
            return []
    
    def _advanced_scrape_articles(self, urls: List[str]) -> List[Dict]:
        """
        ⚡ HIGH-PERFORMANCE: Concurrent multi-method article scraping with newspaper3k fallback
        
        Args:
            urls: List of URLs to scrape
        
        Returns:
            List of article dicts with metadata
        """
        articles = []
        
        # Limit concurrent requests to avoid being blocked
        max_workers = min(6, len(urls))  # Max 6 concurrent requests
        
        logger.info(f"🚀 Starting concurrent scraping of {len(urls)} URLs with {max_workers} workers")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scraping tasks
            future_to_url = {
                executor.submit(self._scrape_single_url, i, url): (i, url) 
                for i, url in enumerate(urls, 1)
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_url):
                i, url = future_to_url[future]
                try:
                    article_data = future.result()
                    if article_data:
                        articles.append(article_data)
                        logger.debug(f"   ✅ [{i}/{len(urls)}] Scraped: {len(article_data.get('content', ''))} chars")
                    else:
                        logger.debug(f"   ❌ [{i}/{len(urls)}] Failed to extract content")
                        
                except Exception as e:
                    logger.debug(f"   ❌ [{i}/{len(urls)}] Error: {str(e)[:50]}")
        
        scraped_count = len([a for a in articles if a.get('content')])
        logger.info(f"   Successfully scraped: {scraped_count}/{len(urls)} (concurrent processing)")
        
        return articles
    
    def _scrape_single_url(self, index: int, url: str) -> Optional[Dict]:
        """Scrape a single URL with all methods"""
        try:
            # Update progress (thread-safe)
            progress = 25 + (index * 15 // 12)  # Assuming max 12 URLs
            # Note: Progress updates in threads need to be handled carefully
            
            # Method 1: newspaper3k (best for news articles)
            if NEWSPAPER_AVAILABLE:
                article_data = self._scrape_with_newspaper(url)
                if article_data and len(article_data.get('content', '')) > 200:
                    return article_data
            
            # Method 2: BeautifulSoup (fallback)
            if BS_AVAILABLE:
                article_data = self._scrape_with_bs4(url)
                if article_data and len(article_data.get('content', '')) > 200:
                    return article_data
            
            # Method 3: Basic regex (last resort)
            article_data = self._scrape_basic(url)
            if article_data and len(article_data.get('content', '')) > 200:
                return article_data
                
        except Exception as e:
            logger.debug(f"Error scraping {url}: {e}")
        
        return None
    
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
        """Extract comprehensive key points from multiple articles"""
        key_points = []
        topic_words = set(topic.lower().split())
        
        for article in articles:
            content = article.get('content', '')
            if not content:
                continue
            
            sentences = re.split(r'[.!?]+', content)
            
            for sentence in sentences:
                sentence = sentence.strip()
                sentence_lower = sentence.lower()
                
                # More comprehensive matching - include related terms
                relevant_words = ['overview', 'introduction', 'background', 'history', 
                                'development', 'current', 'latest', 'new', 'important',
                                'key', 'main', 'primary', 'significant', 'major']
                
                is_relevant = (
                    any(word in sentence_lower for word in topic_words) or
                    any(word in sentence_lower for word in relevant_words) or
                    len(sentence.split()) > 8  # Include longer informative sentences
                )
                
                if len(sentence.split()) > 4 and len(sentence.split()) < 60 and is_relevant:
                    if sentence not in key_points:  # Avoid duplicates
                        key_points.append(sentence)
                        if len(key_points) >= 25:  # Extract more points
                            break
            
            if len(key_points) >= 25:
                break
        
        return key_points[:25]  # Return up to 25 key points
    
    def _extract_facts(self, articles: List[Dict]) -> List[str]:
        """Extract comprehensive factual statements from articles"""
        facts = []
        
        for article in articles:
            content = article.get('content', '')
            sentences = re.split(r'[.!?]+', content)
            
            for sent in sentences:
                sent = sent.strip()
                if len(sent.split()) < 4 or len(sent.split()) > 50:
                    continue
                
                # More comprehensive fact detection
                has_number = bool(re.search(r'\d+', sent))
                has_date = bool(re.search(r'\b(20\d{2}|\d{4}|\d{1,2}\s+(january|february|march|april|may|june|july|august|september|october|november|december|year|month|day))', sent, re.IGNORECASE))
                has_stat = any(word in sent.lower() for word in ['percent', '%', 'million', 'billion', 'thousand', 'according', 'data', 'study', 'research', 'report'])
                has_specific = any(word in sent.lower() for word in ['version', 'release', 'update', 'feature', 'function', 'method', 'technique'])
                
                if has_number or has_date or has_stat or has_specific:
                    if sent not in facts:  # Avoid duplicates
                        facts.append(sent)
                        if len(facts) >= 15:  # Extract more facts
                            break
            
            if len(facts) >= 15:
                break
        
        return facts[:15]
    
    def _extract_quotes(self, articles: List[Dict]) -> List[Dict]:
        """Extract quotes from articles"""
        quotes = []
        
        for article in articles:
            content = article.get('content', '')
            
            # Find quoted text
            quote_matches = re.findall(r'["\"\""]([^\"\"\"]{20,200})["\"\""]', content)
            
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
                                  articles: List[Dict], length: int,
                                  facts: List[str], quotes: List[Dict]) -> str:
        """
        🔥 Generate article using AI MODEL
        DISABLED: Always uses template for reliable, high-quality output
        """
        logger.info("🔄 AI generation disabled - using reliable template method")
        return self._template_article(topic, key_points, articles)
    
    def _prepare_research_context(self, key_points: List[str], articles: List[Dict],
                                  facts: List[str], quotes: List[Dict]) -> str:
        """Prepare CONCISE research context from multiple sources for AI (within token limits)"""
        context_parts = []
        
        # Add brief topic overview
        context_parts.append(f"RESEARCH TOPIC: {len(articles)} sources analyzed")
        context_parts.append("")
        
        # Include only essential source info (limit to 3 sources)
        if articles:
            context_parts.append("Key Sources:")
            for article in articles[:3]:  # Only first 3 sources
                title = article.get('title', 'Unknown')[:30]
                context_parts.append(f"• {title}")
            context_parts.append("")
        
        # Limit key points to 6 most important
        if key_points:
            context_parts.append("Key Findings:")
            for i, point in enumerate(key_points[:6], 1):
                # Truncate long points to stay within token limits
                truncated_point = point[:150] + "..." if len(point) > 150 else point
                context_parts.append(f"{i}. {truncated_point}")
            context_parts.append("")
        
        # Limit facts to 4 most important
        if facts:
            context_parts.append("Important Facts:")
            for fact in facts[:4]:
                truncated_fact = fact[:120] + "..." if len(fact) > 120 else fact
                context_parts.append(f"• {truncated_fact}")
            context_parts.append("")
        
        # Include only 2 quotes max
        if quotes:
            context_parts.append("Expert Insights:")
            for quote in quotes[:2]:
                text = quote.get('text', '')[:80]
                context_parts.append(f'• "{text}"')
            context_parts.append("")
        
        # Brief synthesis instruction
        context_parts.append("SYNTHESIS: Create a comprehensive article covering multiple perspectives from these sources.")
        
        # Ensure total context stays under 1000 characters to be safe
        full_context = "\n".join(context_parts)
        if len(full_context) > 1000:
            full_context = full_context[:1000] + "\n\n[Context truncated for length]"
        
        return full_context
    
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
        """Generate high-quality template article from research data - NO raw content extraction"""
        sections = []
        
        # Title
        title_templates = [
            f"{topic}: A Comprehensive Overview",
            f"Understanding {topic}: Key Insights and Developments",
            f"{topic}: Impact, Trends, and Future Outlook",
            f"Exploring {topic}: What You Need to Know",
            f"{topic}: The Complete Guide",
        ]
        title = random.choice(title_templates)
        sections.append(f"# {title}\n")
        
        # Introduction
        intro_templates = [
            f"{topic} has become increasingly important in contemporary discourse. Based on research from multiple authoritative sources, this article provides a comprehensive analysis of its key aspects, current state, and future trajectory.",
            
            f"In today's evolving landscape, {topic} plays a crucial role across multiple sectors. Understanding its various dimensions, challenges, and opportunities is essential for professionals and stakeholders seeking to stay informed.",
            
            f"{topic} represents a significant area of focus for researchers, practitioners, and organizations worldwide. This detailed examination synthesizes insights from leading experts and authoritative sources to provide a holistic understanding.",
        ]
        sections.append(random.choice(intro_templates))
        sections.append("")
        
        # Overview Section
        sections.append("## Overview and Background\n")
        overview_text = f"""
The concept of {topic} has evolved significantly over time. Today, it encompasses multiple interconnected dimensions that impact various aspects of modern society, business, and technology.

Key aspects include:
- Foundational principles and core concepts
- Historical development and evolution
- Current applications and use cases
- Stakeholders and communities involved
- Strategic importance across sectors
"""
        sections.append(overview_text.strip())
        sections.append("")
        
        # Key Findings
        if key_points:
            sections.append("## Key Research Findings\n")
            for i, point in enumerate(key_points[:10], 1):
                # Clean up the point if needed
                clean_point = point.strip()
                if clean_point:
                    sections.append(f"{i}. {clean_point}")
            sections.append("")
        
        # Main Dimensions
        sections.append(f"## Main Dimensions of {topic}\n")
        dimensions = [
            ("Strategic Importance", f"{topic} has strategic importance due to its wide-ranging applications and implications."),
            ("Current Trends", f"Recent developments in {topic} show increasing focus on innovation and improvement."),
            ("Future Outlook", f"The future of {topic} will likely be shaped by technological advances and market dynamics."),
            ("Challenges and Opportunities", f"While {topic} presents significant opportunities, it also faces challenges that require strategic approaches."),
        ]
        
        for dim_title, dim_content in dimensions:
            sections.append(f"### {dim_title}")
            sections.append(dim_content)
            sections.append("")
        
        # Impact Section
        sections.append("## Broader Impact and Implications\n")
        impact_text = f"""
The implications of {topic} extend across multiple domains:

**Organizational Level:** Companies and institutions are increasingly recognizing the importance of understanding and implementing strategies related to {topic}.

**Sectoral Impact:** Multiple sectors - including technology, business, education, and government - are being influenced by developments in {topic}.

**Societal Implications:** The broader societal impact includes considerations of sustainability, ethical implications, and stakeholder engagement.

**Future Considerations:** As {topic} continues to evolve, ongoing research and adaptation will be essential for organizations and individuals.
"""
        sections.append(impact_text.strip())
        sections.append("")
        
        # Conclusion
        conclusion = f"""## Conclusion

{topic} represents a complex and evolving field that requires continuous attention and research. Key takeaways from this analysis include:
"""
        sections.append(conclusion)
        
        if key_points:
            for point in key_points[:3]:
                sections.append(f"- {point}")
        
        sections.append(f"""
The landscape of {topic} continues to change, with new developments and innovations emerging regularly. Stakeholders across all sectors should remain engaged with developments in this field to ensure informed decision-making and strategic planning.

Continued research, collaboration, and knowledge sharing will be essential for advancing understanding and realizing the full potential of {topic} in addressing contemporary challenges and opportunities.
""")
        
        return "\n".join(sections)
    
    def _format_with_citations(self, article: str, articles: List[Dict]) -> str:
        """Add citations to article"""
        formatted = article
        
        sources_section = "\n\n## Sources\n\n"
        for i, article_info in enumerate(articles[:10], 1):
            sources_section += f"[{i}] {article_info.get('title', 'Unknown')}: {article_info.get('url', '#')}\n"
        
        formatted += sources_section
        return formatted
    
    def _humanize_article(self, article: str) -> str:
        """Humanize article using AI to make it sound more natural and human-like"""
        if not self.humanizer_model:
            logger.warning("⚠️ Humanizer model not available, returning original article")
            return article
        
        try:
            logger.info("🤖 Humanizing article with AI...")
            
            # Split article into paragraphs for better processing
            paragraphs = article.split('\n\n')
            humanized_paragraphs = []
            
            for i, para in enumerate(paragraphs):
                if len(para.strip()) < 50:  # Skip short paragraphs (titles, etc.)
                    humanized_paragraphs.append(para)
                    continue
                
                # Create prompt for humanization
                prompt = f"Rewrite this text to sound more natural and human-like, keeping the same meaning and facts:\n\n{para[:1000]}"  # Limit input length
                
                # Generate humanized version
                result = self.humanizer_model(
                    prompt,
                    max_new_tokens=100,  # Generate up to 100 new tokens
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=50256
                )
                
                if result and len(result) > 0:
                    humanized_text = result[0]['generated_text']
                    # Remove the prompt from the response
                    if humanized_text.startswith(prompt):
                        humanized_text = humanized_text[len(prompt):].strip()
                    
                    # Clean up the response - remove extra content after the rewritten text
                    # Look for common stop patterns
                    stop_patterns = ['\n\n##', '\n\n###', '\n\nSources:', '\n\n---']
                    for pattern in stop_patterns:
                        if pattern in humanized_text:
                            humanized_text = humanized_text.split(pattern)[0]
                            break
                    
                    humanized_paragraphs.append(humanized_text.strip())
                else:
                    humanized_paragraphs.append(para)  # Fallback to original
            
            humanized_article = '\n\n'.join(humanized_paragraphs)
            logger.info("✅ Article humanized successfully")
            return humanized_article
            
        except Exception as e:
            logger.warning(f"⚠️ Humanization failed: {e}, returning original article")
            return article
    
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
