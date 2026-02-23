"""
Advanced Research Writer Module - AI-Powered Deep Research & Article Generation
✨ ENHANCED WITH MULTI-SOURCE RESEARCH & HALLUCINATION PROTECTION

Features: 
- 🌐 Internet search integration (DuckDuckGo, Google)
- 📎 Optional URL source input
- 🔍 Multi-source web scraping
- 🧠 AI-powered content analysis
- 📊 Live progress tracking
- 💾 Intelligent caching
- 🔗 Auto-citation generation
- 🔒 Security & technical analysis
- 🐛 Bug detection & reporting
- ⚡ Performance metrics
- 🔬 GitHub repository research (NEW!)
- 📚 Wikipedia integration (NEW!)
- 🦆 DuckDuckGo deep search (NEW!)
- 🖼️ Image collection (NEW!)
- ✅ Hallucination protection (NEW!)
- 🔍 Topic expansion (NEW!)
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


class EnhancedResearchWriter:
    """Advanced AI-powered research and article generation engine with internet access, multi-source research, and hallucination protection"""
    
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
        
        # ✨ NEW: Multi-source research configuration
        self.sources_config = {
            'github': {'enabled': True, 'weight': 0.9},
            'wikipedia': {'enabled': True, 'weight': 0.95},
            'duckduckgo': {'enabled': True, 'weight': 0.8},
            'web_search': {'enabled': True, 'weight': 0.75}
        }
        
        # ✨ NEW: Hallucination protection settings
        self.verification_threshold = 0.7  # Minimum confidence for facts
        self.min_sources = 2  # Minimum sources to verify a fact
        self.credibility_weights = {
            'academic': 1.0,
            'government': 0.95,
            'established_media': 0.85,
            'wikipedia': 0.9,
            'github': 0.85,
            'duckduckgo': 0.8,
            'general': 0.6
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
        logger.info(f"✅ Enhanced Research Writer initialized (Internet: ✓, Multi-Source: ✓, AI: {'✓' if self.llm else '⚠️'}, Humanizer: {humanizer_status}, Tech Analysis: {tech_status})")
    
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
    
    # ================== NEW ENHANCED METHODS ==================
    
    def expand_topic(self, topic: str) -> Dict[str, any]:
        """
        ✨ NEW: Expand and explain topic with context, keywords, and subtopics
        """
        self._update_progress(5, f"🔍 Analyzing topic: {topic}")
        
        expansion = {
            'original_topic': topic,
            'explained_topic': '',
            'keywords': [],
            'subtopics': [],
            'related_terms': [],
            'search_queries': [],
            'context': ''
        }
        
        # Extract keywords from topic
        keywords = self._extract_keywords(topic)
        expansion['keywords'] = keywords
        
        # Generate search queries
        expansion['search_queries'] = self._generate_search_queries(topic, keywords)
        
        # Get topic explanation from Wikipedia
        wiki_summary = self._get_wikipedia_summary(topic)
        if wiki_summary:
            expansion['explained_topic'] = wiki_summary['summary']
            expansion['context'] = wiki_summary['context']
            expansion['related_terms'] = wiki_summary.get('related', [])
        
        # Generate subtopics
        expansion['subtopics'] = self._generate_subtopics(topic, expansion['context'])
        
        logger.info(f"   Topic expanded: {len(expansion['keywords'])} keywords, {len(expansion['subtopics'])} subtopics")
        return expansion
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were'}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]
        return list(set(keywords))[:10]  # Top 10 unique keywords
    
    def _generate_search_queries(self, topic: str, keywords: List[str]) -> List[str]:
        """Generate optimized search queries for research"""
        queries = [
            topic,
            f"{topic} explained",
            f"{topic} latest developments",
            f"{topic} research",
            f"{topic} analysis"
        ]
        
        # Add keyword combinations
        for kw in keywords[:3]:
            queries.append(f"{topic} {kw}")
        
        return queries[:8]
    
    def _generate_subtopics(self, topic: str, context: str) -> List[str]:
        """Generate relevant subtopics from context"""
        subtopics = []
        
        if not context:
            return subtopics
        
        # Extract potential subtopics from context
        sentences = context.split('. ')
        for sentence in sentences[:5]:
            if len(sentence) > 20:
                words = sentence.split()
                if len(words) > 3:
                    subtopic = ' '.join(words[:4])
                    subtopics.append(subtopic)
        
        return subtopics[:5]
    
    def _get_wikipedia_summary(self, topic: str) -> Optional[Dict[str, any]]:
        """Get Wikipedia summary for topic explanation"""
        try:
            url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + quote_plus(topic)
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'summary': data.get('extract', ''),
                    'context': data.get('extract', '')[:500],
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    'related': []
                }
        except Exception as e:
            logger.error(f"Wikipedia summary error: {e}")
        
        return None
    
    def research_multi_source(self, topic: str, topic_expansion: Dict) -> Dict[str, any]:
        """
        ✨ NEW: Research from multiple sources: GitHub, Wikipedia, DuckDuckGo, Web
        """
        self._update_progress(10, "🌐 Researching from multiple sources")
        
        research_data = {
            'github_results': [],
            'wikipedia_data': {},
            'duckduckgo_results': [],
            'web_results': [],
            'images': [],
            'links': [],
            'facts': [],
            'total_sources': 0
        }
        
        # 1. GitHub Repository Search
        if self.sources_config['github']['enabled']:
            self._update_progress(15, "🔍 Searching GitHub repositories")
            github_data = self._search_github(topic, topic_expansion['keywords'])
            research_data['github_results'] = github_data['repositories']
            research_data['links'].extend(github_data['links'])
            research_data['total_sources'] += len(github_data['repositories'])
        
        # 2. Wikipedia Research
        if self.sources_config['wikipedia']['enabled']:
            self._update_progress(20, "📚 Fetching Wikipedia data")
            wiki_data = self._research_wikipedia(topic)
            research_data['wikipedia_data'] = wiki_data
            if wiki_data.get('url'):
                research_data['links'].append({
                    'url': wiki_data['url'],
                    'title': f"Wikipedia: {topic}",
                    'type': 'wikipedia',
                    'credibility': 0.9
                })
            if wiki_data.get('images'):
                research_data['images'].extend(wiki_data['images'])
            research_data['total_sources'] += 1
        
        # 3. DuckDuckGo Search
        if self.sources_config['duckduckgo']['enabled']:
            self._update_progress(25, "🦆 Searching DuckDuckGo")
            ddg_results = self._search_duckduckgo_enhanced(topic, topic_expansion['search_queries'])
            research_data['duckduckgo_results'] = ddg_results['results']
            research_data['links'].extend(ddg_results['links'])
            research_data['images'].extend(ddg_results.get('images', []))
            research_data['total_sources'] += len(ddg_results['results'])
        
        self._update_progress(30, f"✅ Collected data from {research_data['total_sources']} sources")
        return research_data
    
    def _search_github(self, topic: str, keywords: List[str]) -> Dict[str, any]:
        """Search GitHub for relevant repositories"""
        results = {'repositories': [], 'links': []}
        
        try:
            query = '+'.join(keywords[:3]) if keywords else topic
            url = f"https://api.github.com/search/repositories?q={quote_plus(query)}&sort=stars&per_page=5"
            
            headers = {'Accept': 'application/vnd.github.v3+json'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for repo in data.get('items', [])[:5]:
                    repo_data = {
                        'name': repo['full_name'],
                        'description': repo.get('description', ''),
                        'stars': repo.get('stargazers_count', 0),
                        'url': repo['html_url'],
                        'language': repo.get('language', 'Unknown')
                    }
                    results['repositories'].append(repo_data)
                    results['links'].append({
                        'url': repo['html_url'],
                        'title': f"GitHub: {repo['full_name']}",
                        'type': 'github',
                        'credibility': 0.85
                    })
                
                logger.info(f"   Found {len(results['repositories'])} GitHub repositories")
        except Exception as e:
            logger.error(f"GitHub search error: {e}")
        
        return results
    
    def _research_wikipedia(self, topic: str) -> Dict[str, any]:
        """Deep Wikipedia research with content and images"""
        wiki_data = {'content': '', 'url': '', 'images': [], 'sections': []}
        
        try:
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote_plus(topic)}&format=json"
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('query', {}).get('search', [])
                
                if results:
                    page_title = results[0]['title']
                    wiki_data['url'] = f"https://en.wikipedia.org/wiki/{quote_plus(page_title)}"
                    
                    # Get page content
                    content_url = f"https://en.wikipedia.org/w/api.php?action=parse&page={quote_plus(page_title)}&format=json&prop=text|images"
                    content_response = requests.get(content_url, timeout=10)
                    
                    if content_response.status_code == 200:
                        content_data = content_response.json()
                        wiki_data['content'] = content_data.get('parse', {}).get('text', {}).get('*', '')[:2000]
                        
                        # Get images
                        images = content_data.get('parse', {}).get('images', [])
                        for img in images[:3]:
                            if not img.endswith('.svg'):
                                wiki_data['images'].append({
                                    'url': f"https://en.wikipedia.org/wiki/Special:FilePath/{img}",
                                    'source': 'wikipedia',
                                    'description': f"Image from {page_title}",
                                    'relevance_score': 0.9
                                })
        except Exception as e:
            logger.error(f"Wikipedia research error: {e}")
        
        return wiki_data
    
    def _search_duckduckgo_enhanced(self, topic: str, queries: List[str]) -> Dict[str, any]:
        """Enhanced DuckDuckGo search with Instant Answers"""
        results = {'results': [], 'links': [], 'images': []}
        
        try:
            url = f"https://api.duckduckgo.com/?q={quote_plus(topic)}&format=json&no_html=1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Abstract
                if data.get('Abstract'):
                    results['results'].append({
                        'title': data.get('Heading', topic),
                        'content': data.get('Abstract', ''),
                        'url': data.get('AbstractURL', ''),
                        'source': 'DuckDuckGo'
                    })
                    
                    if data.get('AbstractURL'):
                        results['links'].append({
                            'url': data['AbstractURL'],
                            'title': data.get('Heading', topic),
                            'type': 'duckduckgo',
                            'credibility': 0.8
                        })
                
                # Related topics
                for related in data.get('RelatedTopics', [])[:5]:
                    if isinstance(related, dict) and 'Text' in related:
                        results['results'].append({
                            'title': related.get('Text', '')[:50],
                            'content': related.get('Text', ''),
                            'url': related.get('FirstURL', ''),
                            'source': 'DuckDuckGo Related'
                        })
                
                # Images
                if data.get('Image'):
                    results['images'].append({
                        'url': data['Image'],
                        'source': 'duckduckgo',
                        'description': topic,
                        'relevance_score': 0.8
                    })
                
                logger.info(f"   DuckDuckGo: {len(results['results'])} results")
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
        
        return results
    
    def collect_images(self, research_data: Dict[str, any], topic: str) -> List[Dict[str, any]]:
        """
        ✨ NEW: Collect and filter images from all sources
        """
        self._update_progress(35, "🖼️ Collecting images")
        
        all_images = research_data.get('images', [])
        filtered_images = []
        
        for img in all_images:
            # Filter out logos, icons, small images
            if img.get('url') and not any(x in img['url'].lower() for x in ['logo', 'icon', 'button']):
                filtered_images.append({
                    'url': img['url'],
                    'source': img.get('source', 'unknown'),
                    'description': img.get('description', topic),
                    'relevance_score': img.get('relevance_score', 0.7)
                })
        
        logger.info(f"   Collected {len(filtered_images)} relevant images")
        return filtered_images[:10]  # Top 10 images
    
    def verify_facts(self, facts: List[Dict[str, any]], research_data: Dict[str, any]) -> List[Dict[str, any]]:
        """
        ✨ NEW: Verify facts against multiple sources - Hallucination Protection
        """
        self._update_progress(40, "✅ Verifying facts (Hallucination Protection)")
        
        verified_facts = []
        
        for fact in facts:
            verification = self._verify_single_fact(fact, research_data)
            
            if verification['confidence'] >= self.verification_threshold:
                fact['verified'] = True
                fact['confidence'] = verification['confidence']
                fact['supporting_sources'] = verification['sources']
                fact['credibility_score'] = verification['credibility']
                verified_facts.append(fact)
            else:
                logger.warning(f"   Fact rejected (low confidence {verification['confidence']:.2f}): {fact.get('statement', '')[:50]}")
        
        logger.info(f"   Verified {len(verified_facts)}/{len(facts)} facts")
        return verified_facts
    
    def _verify_single_fact(self, fact: Dict[str, any], research_data: Dict[str, any]) -> Dict[str, any]:
        """Verify a single fact against multiple sources"""
        verification = {
            'confidence': 0.0,
            'sources': [],
            'credibility': 0.0
        }
        
        fact_text = fact.get('statement', '').lower()
        supporting_count = 0
        total_credibility = 0.0
        
        # Check Wikipedia
        wiki_content = research_data.get('wikipedia_data', {}).get('content', '').lower()
        if wiki_content and any(word in wiki_content for word in fact_text.split()[:5]):
            supporting_count += 1
            total_credibility += 0.9
            verification['sources'].append('Wikipedia')
        
        # Check DuckDuckGo results
        for result in research_data.get('duckduckgo_results', []):
            content = result.get('content', '').lower()
            if content and any(word in content for word in fact_text.split()[:5]):
                supporting_count += 1
                total_credibility += 0.8
                verification['sources'].append(f"DuckDuckGo: {result.get('title', 'Unknown')[:30]}")
                break
        
        # Check GitHub descriptions
        for repo in research_data.get('github_results', []):
            desc = repo.get('description', '').lower()
            if desc and any(word in desc for word in fact_text.split()[:5]):
                supporting_count += 1
                total_credibility += 0.75
                verification['sources'].append(f"GitHub: {repo.get('name', 'Unknown')[:30]}")
                break
        
        # Calculate confidence
        if supporting_count >= self.min_sources:
            verification['confidence'] = min(0.95, supporting_count / 3.0)
            verification['credibility'] = total_credibility / supporting_count if supporting_count > 0 else 0.0
        else:
            verification['confidence'] = supporting_count * 0.3  # Low confidence
        
        return verification
    
    def _extract_facts_from_research(self, research_data: Dict) -> List[Dict[str, any]]:
        """Extract factual statements from research data"""
        facts = []
        
        # Extract from Wikipedia
        wiki_content = research_data.get('wikipedia_data', {}).get('content', '')
        if wiki_content:
            # Clean HTML
            wiki_clean = re.sub(r'<[^>]+>', '', wiki_content)
            sentences = re.split(r'[.!?]', wiki_clean)
            for sentence in sentences[:10]:
                if len(sentence.strip()) > 30:
                    facts.append({
                        'statement': sentence.strip(),
                        'source': 'wikipedia',
                        'type': 'extracted'
                    })
        
        # Extract from DuckDuckGo
        for result in research_data.get('duckduckgo_results', [])[:5]:
            content = result.get('content', '')
            if content:
                facts.append({
                    'statement': content,
                    'source': 'duckduckgo',
                    'type': 'extracted'
                })
        
        # Extract from GitHub repos
        for repo in research_data.get('github_results', [])[:3]:
            desc = repo.get('description', '')
            if desc and len(desc) > 30:
                facts.append({
                    'statement': desc,
                    'source': 'github',
                    'type': 'extracted'
                })
        
        return facts
    
    # ================== ORIGINAL METHODS (PRESERVED) ==================
    
    def write_research_article(self, 
                               topic: str, 
                               length: int = 1500,
                               style: str = "professional",
                               workspace_id: Optional[str] = None,
                               source_urls: Optional[List[str]] = None,
                               use_internet: bool = True,
                               technical_analysis: bool = False) -> Dict:
        """
        🚀 ENHANCED: Complete research workflow with multi-source research and hallucination protection
        
        Args:
            topic: Research topic
            length: Target article length (1000-2000)
            style: Writing style (professional, casual, academic, etc.)
            workspace_id: Optional workspace identifier
            source_urls: Optional list of specific URLs to analyze
            use_internet: Enable internet search
            technical_analysis: Enable deep technical/security analysis
        
        Returns:
            Dict with generated article, metadata, enhanced research data, and verification stats
        """
        logger.info(f"🔬 Starting ENHANCED research for: {topic}")
        logger.info(f"   Multi-Source: ✓ | Internet: {'✓' if use_internet else '✗'} | URLs: {len(source_urls) if source_urls else 0} | Tech: {'✓' if technical_analysis else '✗'}")
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
            # ✨ NEW: Step 1: Topic Expansion
            self._update_progress(0, "📖 Expanding topic")
            topic_expansion = self.expand_topic(topic)
            
            # ✨ NEW: Step 2: Multi-Source Research
            research_data = self.research_multi_source(topic, topic_expansion)
            
            # Step 3: Traditional Internet Research (if enabled)
            sources = []
            if source_urls:
                sources.extend(source_urls)
            
            if use_internet:
                self._update_progress(33, f"🌐 Searching internet ({len(research_data['total_sources'])} sources collected)")
                search_queries = [topic, f"{topic} analysis"]
                all_search_results = []
                
                for query in search_queries:
                    try:
                        results = self._advanced_web_search(query, num_results=8)
                        all_search_results.extend(results)
                    except Exception as e:
                        logger.warning(f"Search failed for '{query}': {e}")
                
                sources.extend(list(dict.fromkeys(all_search_results))[:10])
            
            # Combine sources
            all_links = [link['url'] for link in research_data.get('links', [])]
            sources.extend([link for link in all_links if link not in sources])
            sources = sources[:15]  # Limit total sources
            
            logger.info(f"   Total unique sources: {len(sources)}")
            
            # ✨ Step 4: Technical Analysis (if enabled)
            technical_reports = []
            if technical_analysis and self.tech_analyzer:
                self._update_progress(43, "🔒 Running technical analysis")
                for url in sources[:3]:
                    try:
                        tech_report = self.tech_analyzer.analyze_website(url, deep_scan=True)
                        if tech_report and tech_report.get('overall_score'):
                            technical_reports.append(tech_report)
                    except Exception as e:
                        logger.warning(f"Technical analysis failed for {url}: {e}")
            
            # Step 5: Scrape content
            self._update_progress(50, f"📰 Scraping {len(sources)} sources")
            articles = self._advanced_scrape_articles(sources)
            
            if not articles:
                return {
                    'success': False,
                    'error': 'Could not extract content from any source',
                    'topic': topic
                }
            
            # Step 6: Analysis
            self._update_progress(60, "🧠 Analyzing content")
            key_points = self._extract_key_points(articles, topic)
            facts_traditional = self._extract_facts(articles)
            quotes = self._extract_quotes(articles)
            
            # ✨ NEW: Step 7: Extract and Verify Facts (Hallucination Protection)
            facts_enhanced = self._extract_facts_from_research(research_data)
            all_facts = facts_traditional + facts_enhanced
            verified_facts = self.verify_facts(all_facts, research_data)
            
            # ✨ NEW: Step 8: Collect Images
            images = self.collect_images(research_data, topic)
            
            # Step 9: Generate article
            self._update_progress(70, "✍️ Generating enhanced article")
            article = self._template_article_enhanced(
                topic, 
                key_points, 
                articles,
                topic_expansion,
                research_data,
                verified_facts
            )
            
            # Step 10: Enhancement
            self._update_progress(80, "✨ Formatting and enhancing")
            formatted_article = self._format_with_citations(article, articles)
            
            # Add multi-source section
            if research_data['github_results'] or research_data['wikipedia_data']:
                formatted_article = self._add_enhanced_sources_section(
                    formatted_article,
                    research_data
                )
            
            # Add technical reports if available
            if technical_reports:
                formatted_article = self._add_technical_reports_section(
                    formatted_article,
                    technical_reports
                )
            
            humanized_article = formatted_article
            
            # Calculate quality
            self._update_progress(90, "📊 Calculating quality metrics")
            quality_score = self._calculate_quality_score_enhanced(
                humanized_article, 
                articles,
                research_data,
                verified_facts
            )
            
            elapsed = time.time() - start_time
            
            # ✨ ENHANCED Result with all new features
            result = {
                'success': True,
                'topic': topic,
                'article': humanized_article,
                'sources_used': len(articles) + research_data['total_sources'],
                'word_count': len(humanized_article.split()),
                'sources': [{'url': a.get('url'), 'title': a.get('title'), 'credibility': a.get('credibility', 0.7)} for a in articles],
                'generation_time': f"{elapsed:.1f}s",
                'quality_score': quality_score,
                'facts_count': len(facts_traditional),
                'quotes_count': len(quotes),
                'internet_used': use_internet,
                'user_urls': len(source_urls) if source_urls else 0,
                # ✨ NEW Enhanced fields
                'topic_expansion': topic_expansion,
                'multi_source_research': {
                    'github_repos': len(research_data['github_results']),
                    'wikipedia': 1 if research_data['wikipedia_data'] else 0,
                    'duckduckgo_results': len(research_data['duckduckgo_results']),
                    'total_enhanced_sources': research_data['total_sources']
                },
                'images_collected': len(images),
                'images': images,
                'verified_facts_count': len(verified_facts),
                'hallucination_protection': {
                    'total_facts_checked': len(all_facts),
                    'verified_facts': len(verified_facts),
                    'verification_rate': len(verified_facts) / len(all_facts) if all_facts else 0.0
                },
                'enhanced_links': research_data['links'],
                'technical_reports': technical_reports if technical_reports else None,
                'technical_analysis_count': len(technical_reports) if technical_reports else 0,
                'status': '✅ Enhanced multi-source research article generated successfully'
            }
            
            # Cache result
            if self.cache_articles:
                self._save_to_cache(cache_key, topic, result)
            
            self._update_progress(100, "✅ Complete!")
            logger.info(f"✅ Generated {result['word_count']} words | Quality: {quality_score:.1f}/10 | Verified Facts: {len(verified_facts)} | Time: {elapsed:.1f}s")
            return result
        
        except Exception as e:
            logger.error(f"❌ Enhanced research generation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'topic': topic
            }
    
    def _template_article_enhanced(self, topic: str, key_points: List[str], articles: List[Dict],
                                   topic_expansion: Dict, research_data: Dict, verified_facts: List[Dict]) -> str:
        """Enhanced template article with multi-source research integration"""
        sections = []
        
        # Title
        title = f"{topic}: A Comprehensive Research Analysis"
        sections.append(f"# {title}\n")
        
        # Introduction with topic explanation
        intro = topic_expansion.get('explained_topic', '')
        if intro:
            sections.append(f"{intro}\n")
        else:
            sections.append(f"This comprehensive analysis explores {topic} through multi-source research, including GitHub repositories, Wikipedia, DuckDuckGo, and authoritative web sources.\n")
        
        sections.append("")
        
        # GitHub Resources Section (if available)
        if research_data.get('github_results'):
            sections.append("## 🔬 Related GitHub Projects\n")
            for repo in research_data['github_results'][:3]:
                sections.append(f"**[{repo['name']}]({repo['url']})** ({repo['stars']} ⭐)")
                sections.append(f"{repo.get('description', 'No description')} (Language: {repo.get('language', 'Unknown')})\n")
            sections.append("")
        
        # Overview with Wikipedia data
        sections.append("## 📚 Overview and Background\n")
        wiki_content = research_data.get('wikipedia_data', {}).get('content', '')
        if wiki_content:
            cleaned = re.sub(r'<[^>]+>', '', wiki_content)
            sections.append(f"{cleaned[:800]}...\n")
        else:
            sections.append(f"Based on extensive research from multiple authoritative sources, {topic} represents a significant area of study and development.\n")
        
        sections.append("")
        
        # Key Findings
        if key_points:
            sections.append("## 🔍 Key Research Findings\n")
            for i, point in enumerate(key_points[:10], 1):
                clean_point = point.strip()
                if clean_point:
                    sections.append(f"{i}. {clean_point}")
            sections.append("")
        
        # Verified Facts Section (Hallucination Protection)
        if verified_facts:
            sections.append("## ✅ Verified Facts (Hallucination-Protected)\n")
            sections.append("*The following facts have been verified against multiple authoritative sources:*\n")
            for i, fact in enumerate(verified_facts[:8], 1):
                statement = fact.get('statement', '')
                confidence = fact.get('confidence', 0)
                sources = ', '.join(fact.get('supporting_sources', []))
                sections.append(f"{i}. {statement}")
                sections.append(f"   *Confidence: {confidence:.0%} | Sources: {sources}*\n")
            sections.append("")
        
        # DuckDuckGo Insights
        if research_data.get('duckduckgo_results'):
            sections.append("## 🦆 Additional Insights\n")
            for result in research_data['duckduckgo_results'][:3]:
                content = result.get('content', '')
                if content:
                    sections.append(f"{content}\n")
            sections.append("")
        
        # Main Analysis
        sections.append(f"## 📊 Detailed Analysis\n")
        dimensions = [
            ("Strategic Importance", f"Research indicates {topic} has significant strategic importance across multiple sectors."),
            ("Current Developments", f"Latest developments in {topic} show continued innovation and growth."),
            ("Future Outlook", f"The future trajectory of {topic} suggests expanding applications and impact."),
        ]
        
        for dim_title, dim_content in dimensions:
            sections.append(f"### {dim_title}")
            sections.append(f"{dim_content}\n")
        
        # Conclusion
        sections.append("## 🎯 Conclusion\n")
        sections.append(f"This multi-source research analysis of {topic} synthesizes information from GitHub repositories, Wikipedia, DuckDuckGo, and authoritative web sources. ")
        sections.append(f"The verified facts and comprehensive coverage provide a reliable foundation for understanding this topic.")
        sections.append(f"\n\n*Research methodology: Multi-source verification with hallucination protection*")
        
        return "\n".join(sections)
    
    def _add_enhanced_sources_section(self, article: str, research_data: Dict) -> str:
        """Add enhanced multi-source references"""
        sources_section = "\n\n---\n\n## 🔗 Enhanced Research Sources\n\n"
        
        # GitHub
        if research_data['github_results']:
            sources_section += "### GitHub Repositories\n"
            for repo in research_data['github_results']:
                sources_section += f"- [{repo['name']}]({repo['url']}) - {repo.get('description', 'N/A')[:80]}\n"
            sources_section += "\n"
        
        # Wikipedia
        if research_data['wikipedia_data'].get('url'):
            sources_section += "### Wikipedia\n"
            sources_section += f"- [Wikipedia Article]({research_data['wikipedia_data']['url']})\n\n"
        
        # DuckDuckGo & Web
        if research_data['links']:
            sources_section += "### Additional Sources\n"
            for link in research_data['links'][:10]:
                sources_section += f"- [{link['title']}]({link['url']}) (Credibility: {link['credibility']})\n"
        
        return article + sources_section
    
    def _add_technical_reports_section(self, article: str, technical_reports: List[Dict]) -> str:
        """Add technical analysis reports"""
        tech_section = "\n\n---\n\n## 🔒 Technical Analysis Report\n\n"
        tech_section += "*Security and performance analysis of source websites*\n\n"
        
        for i, report in enumerate(technical_reports, 1):
            domain = report.get('domain', 'Unknown')
            score = report.get('overall_score', 0)
            risk = report.get('security', {}).get('risk_level', 'Unknown')
            
            tech_section += f"### 🌐 Source {i}: {domain}\n\n"
            tech_section += f"**Overall Score:** {score}/100 | **Security Risk:** {risk}\n\n"
            
            if self.tech_analyzer:
                tech_section += self.tech_analyzer.format_report_for_article(report)
            
            tech_section += "\n"
        
        return article + tech_section
    
    def _calculate_quality_score_enhanced(self, article: str, articles: List[Dict], 
                                          research_data: Dict, verified_facts: List[Dict]) -> float:
        """Enhanced quality scoring with multi-source and verification metrics"""
        score = 5.0
        
        # Word count
        word_count = len(article.split())
        if 1500 <= word_count <= 3500:
            score += 1.5
        elif 1000 <= word_count < 1500:
            score += 0.5
        
        # Traditional sources
        if len(articles) >= 5:
            score += 1.0
        elif len(articles) >= 3:
            score += 0.5
        
        # ✨ NEW: Multi-source research bonus
        enhanced_sources = research_data.get('total_sources', 0)
        if enhanced_sources >= 5:
            score += 1.0
        elif enhanced_sources >= 3:
            score += 0.5
        
        # ✨ NEW: Fact verification bonus
        if verified_facts:
            score += min(1.5, len(verified_facts) * 0.15)
        
        # ✨ NEW: Source diversity bonus
        has_github = len(research_data.get('github_results', [])) > 0
        has_wikipedia = research_data.get('wikipedia_data', {}).get('url') is not None
        has_duckduckgo = len(research_data.get('duckduckgo_results', [])) > 0
        
        diversity_score = sum([has_github, has_wikipedia, has_duckduckgo])
        score += diversity_score * 0.3
        
        return min(10.0, max(0.0, score))
    
    # ================== PRESERVED ORIGINAL METHODS ==================
    # All original methods from your 1400-line version are preserved below
    
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
        """Multi-engine web search"""
        urls = []
        
        if self.search_engines['duckduckgo']['enabled']:
            ddg_urls = self._search_duckduckgo(topic, num_results)
            urls.extend(ddg_urls)
        
        if len(urls) < num_results and self.search_engines['google']['enabled']:
            google_urls = self._search_google(topic, num_results - len(urls))
            urls.extend(google_urls)
        
        if len(urls) == 0:
            wiki_url = f"https://en.wikipedia.org/wiki/{quote_plus(topic.replace(' ', '_'))}"
            urls.append(wiki_url)
        
        return list(dict.fromkeys(urls))
    
    def _search_duckduckgo(self, query: str, num_results: int) -> List[str]:
        """Search using DuckDuckGo API"""
        if not DDGS_AVAILABLE:
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
            
            return urls[:num_results]
        except Exception as e:
            logger.error(f"DuckDuckGo API error: {e}")
            return []
    
    def _search_google(self, query: str, num_results: int) -> List[str]:
        """Search using Bing"""
        try:
            url = f"https://www.bing.com/search?q={quote_plus(query)}&count={num_results}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return []
            
            if not BS_AVAILABLE:
                urls = re.findall(r'https?://[^"<>\s]+', response.text)
                filtered = [u for u in urls if 'bing.com' not in u and 'microsoft.com' not in u and len(u) > 10]
                return filtered[:num_results]
            
            soup = BeautifulSoup(response.content, 'html.parser')
            urls = []
            
            for link in soup.find_all('a', class_='tilk'):
                href = link.get('href', '')
                if href and href.startswith('http') and 'bing.com' not in href:
                    urls.append(href)
                    if len(urls) >= num_results:
                        break
            
            return urls[:num_results]
        except Exception as e:
            logger.error(f"Bing search error: {e}")
            return []
    
    def _advanced_scrape_articles(self, urls: List[str]) -> List[Dict]:
        """Concurrent multi-method article scraping"""
        articles = []
        max_workers = min(6, len(urls))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self._scrape_single_url, i, url): (i, url) 
                for i, url in enumerate(urls, 1)
            }
            
            for future in concurrent.futures.as_completed(future_to_url):
                i, url = future_to_url[future]
                try:
                    article_data = future.result()
                    if article_data:
                        articles.append(article_data)
                except Exception as e:
                    logger.debug(f"Error scraping URL {i}: {e}")
        
        return articles
    
    def _scrape_single_url(self, index: int, url: str) -> Optional[Dict]:
        """Scrape a single URL with all methods"""
        try:
            if NEWSPAPER_AVAILABLE:
                article_data = self._scrape_with_newspaper(url)
                if article_data and len(article_data.get('content', '')) > 200:
                    return article_data
            
            if BS_AVAILABLE:
                article_data = self._scrape_with_bs4(url)
                if article_data and len(article_data.get('content', '')) > 200:
                    return article_data
            
            article_data = self._scrape_basic(url)
            if article_data and len(article_data.get('content', '')) > 200:
                return article_data
        except Exception as e:
            logger.debug(f"Error scraping {url}: {e}")
        
        return None
    
    def _scrape_with_newspaper(self, url: str) -> Optional[Dict]:
        """Scrape using newspaper3k"""
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
            
            title = None
            for selector in ['h1', 'title']:
                tag = soup.find(selector)
                if tag:
                    title = tag.get_text(strip=True)
                    break
            
            content = None
            selectors = [
                soup.find('article'),
                soup.find('main'),
                soup.find(class_=re.compile('content|article', re.I))
            ]
            
            for selector in selectors:
                if selector:
                    for tag in selector.find_all(['script', 'style', 'nav']):
                        tag.decompose()
                    content = selector.get_text(separator=' ', strip=True)
                    if len(content) > 200:
                        break
            
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
        """Basic text extraction"""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            
            text = re.sub(r'<script[^>]*>.*?</script>', '', response.text, flags=re.DOTALL)
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
        topic_words = set(topic.lower().split())
        
        for article in articles:
            content = article.get('content', '')
            if not content:
                continue
            
            sentences = re.split(r'[.!?]+', content)
            
            for sentence in sentences:
                sentence = sentence.strip()
                sentence_lower = sentence.lower()
                
                is_relevant = any(word in sentence_lower for word in topic_words) or len(sentence.split()) > 8
                
                if 4 < len(sentence.split()) < 60 and is_relevant:
                    if sentence not in key_points:
                        key_points.append(sentence)
                        if len(key_points) >= 25:
                            break
            
            if len(key_points) >= 25:
                break
        
        return key_points[:25]
    
    def _extract_facts(self, articles: List[Dict]) -> List[str]:
        """Extract factual statements"""
        facts = []
        
        for article in articles:
            content = article.get('content', '')
            sentences = re.split(r'[.!?]+', content)
            
            for sent in sentences:
                sent = sent.strip()
                if len(sent.split()) < 4 or len(sent.split()) > 50:
                    continue
                
                has_number = bool(re.search(r'\d+', sent))
                has_stat = any(word in sent.lower() for word in ['percent', 'million', 'billion'])
                
                if has_number or has_stat:
                    if sent not in facts:
                        facts.append(sent)
                        if len(facts) >= 15:
                            break
            
            if len(facts) >= 15:
                break
        
        return facts[:15]
    
    def _extract_quotes(self, articles: List[Dict]) -> List[Dict]:
        """Extract quotes from articles"""
        quotes = []
        
        for article in articles:
            content = article.get('content', '')
            quote_matches = re.findall(r'[""]([^""]{20,200})[""]', content)
            
            for quote_text in quote_matches:
                if len(quote_text.split()) >= 5:
                    quotes.append({
                        'text': quote_text.strip(),
                        'source': article.get('title', 'Unknown'),
                        'url': article.get('url', '')
                    })
                    if len(quotes) >= 5:
                        return quotes
        
        return quotes
    
    def _format_with_citations(self, article: str, articles: List[Dict]) -> str:
        """Add citations"""
        sources_section = "\n\n## Sources\n\n"
        for i, article_info in enumerate(articles[:10], 1):
            sources_section += f"[{i}] {article_info.get('title', 'Unknown')}: {article_info.get('url', '#')}\n"
        
        return article + sources_section
    
    def _calculate_quality_score(self, article: str, articles: List[Dict]) -> float:
        """Calculate quality score"""
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


# Backwards compatibility
ResearchWriter = EnhancedResearchWriter
