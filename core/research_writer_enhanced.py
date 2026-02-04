"""
Advanced Research Writer Module - AI-Powered Deep Research & Article Generation
✨ ENHANCED VERSION with Technical Analyzer Integration

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
- ⚡ Performance analysis (NEW!)
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

# Import Technical Analyzer
try:
    from core.technical_analyzer import TechnicalAnalyzer
    TECH_ANALYZER_AVAILABLE = True
except ImportError:
    TECH_ANALYZER_AVAILABLE = False
    logger.warning("⚠️ Technical Analyzer not available")

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
    """Advanced AI-powered research and article generation engine with internet access and technical analysis"""
    
    def __init__(self, db_path: str = 'nexuzy.db', cache_articles: bool = True, 
                 model_name: str = 'models/mistral-7b-instruct-v0.2.Q4_K_M.gguf'):
        global _CACHED_MODEL, _CACHED_SENTENCE_MODEL
        
        self.db_path = db_path
        self.cache_articles = cache_articles
        self.article_cache = {}
        self.session = self._create_session()
        self.model_name = model_name
        self._ensure_research_table()
        
        # Initialize Technical Analyzer
        if TECH_ANALYZER_AVAILABLE:
            self.tech_analyzer = TechnicalAnalyzer()
            logger.info("✅ Technical Analyzer enabled")
        else:
            self.tech_analyzer = None
            logger.warning("⚠️ Technical Analyzer disabled")
        
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
        
        logger.info(f"✅ Advanced Research Writer initialized (Internet: ✓, URL Input: ✓, AI: {'✓' if self.llm else '⚠️'}, Tech Analysis: {'✓' if self.tech_analyzer else '⚠️'})")
    
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
                             use_internet: bool = True,
                             technical_analysis: bool = False) -> Dict:
        """
        🚀 ADVANCED: Complete research workflow with internet access, optional URL sources, and technical analysis
        
        Args:
            topic: Research topic
            source_urls: Optional list of specific URLs to analyze
            word_count: Target article length (1000-2000)
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
            
            # Step 1.5: Technical Analysis (NEW!)
            technical_reports = []
            if technical_analysis and self.tech_analyzer:
                self._update_progress(15, "🔒 Running technical analysis...")
                for url in sources[:3]:  # Analyze first 3 URLs
                    try:
                        logger.info(f"   Analyzing: {url}")
                        tech_report = self.tech_analyzer.analyze_website(url, deep_scan=True)
                        technical_reports.append(tech_report)
                    except Exception as e:
                        logger.warning(f"   Technical analysis failed for {url}: {e}")
                
                logger.info(f"   ✅ Analyzed {len(technical_reports)} URLs")
            
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
            
            # Step 5.5: Add technical reports if available
            if technical_reports:
                formatted_article += "\n\n## 🔒 Technical Analysis\n\n"
                for i, report in enumerate(technical_reports, 1):
                    formatted_article += f"\n### Source {i}: {report.get('domain', 'Unknown')}\n"
                    formatted_article += self.tech_analyzer.format_report_for_article(report)
                    formatted_article += "\n"
            
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
                'technical_reports': technical_reports if technical_reports else None,
                'technical_analysis_enabled': technical_analysis,
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
    
    # [REST OF THE METHODS REMAIN THE SAME - Copy from original research_writer.py]
    # Including: _generate_cache_key, _check_cache, _save_to_cache, _advanced_web_search,
    # _search_duckduckgo, _search_google, _advanced_scrape_articles, _scrape_with_newspaper,
    # _scrape_with_bs4, _scrape_basic, _extract_key_points, _extract_facts, _extract_quotes,
    # _generate_article_with_ai, _prepare_research_context, _clean_generated_text,
    # _template_article, _format_with_citations, _calculate_quality_score, save_as_draft, clear_cache
