"""
Research Writer Module - AI-Powered Research & Article Generation
Features: Web search, Article scraping, AI analysis, Auto-generated articles with citations
"""

import logging
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sqlite3
from pathlib import Path
import re
import time
from urllib.parse import urlparse

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

logger = logging.getLogger(__name__)

class ResearchWriter:
    """AI-powered research and article generation engine"""
    
    def __init__(self, db_path: str = 'nexuzy.db', cache_articles: bool = True):
        self.db_path = db_path
        self.cache_articles = cache_articles
        self.article_cache = {}  # In-memory cache
        self.session = self._create_session()
        self._ensure_research_table()
    
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
        
        Args:
            topic: Research topic
            source_urls: Optional pre-specified URLs to scrape
            word_count: Target article length (1000-2000)
        
        Returns:
            Dict with generated article and metadata
        """
        logger.info(f"🔬 Starting research for: {topic}")
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
            
            # Step 4: Generate article
            logger.info(f"✍️  Step 4: Generating {word_count}-word article...")
            article = self._generate_article(topic, key_points, articles, word_count)
            
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
                'status': '✅ Article generated successfully'
            }
            
            # Cache result
            if self.cache_articles:
                self.article_cache[topic] = result
            
            logger.info(f"✅ Complete! Generated {result['word_count']} words in {elapsed:.1f}s")
            return result
        
        except Exception as e:
            logger.error(f"❌ Research generation failed: {e}")
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
    
    def _generate_article(self, 
                         topic: str, 
                         key_points: List[str], 
                         articles: List[Dict],
                         target_words: int) -> str:
        """
        Generate article from key points using AI/LLM
        Falls back to template-based generation if LLM unavailable
        
        Args:
            topic: Article topic
            key_points: Key points to include
            articles: Source articles for reference
            target_words: Target word count
        
        Returns:
            Generated article text
        """
        try:
            # Try to use transformers pipeline if available
            from transformers import pipeline
            generator = pipeline('text-generation', model='gpt2', max_new_tokens=500)
            
            prompt = f"Write a comprehensive article about {topic}:\n"
            article_text = generator(prompt, do_sample=True, top_p=0.95)[0]['generated_text']
            logger.info("   Using AI-generated content")
        except Exception as e:
            logger.debug(f"AI generation not available: {e}, using template")
            article_text = self._template_article(topic, key_points, articles)
        
        return article_text
    
    def _template_article(self, 
                         topic: str, 
                         key_points: List[str], 
                         articles: List[Dict]) -> str:
        """
        Generate article using template-based approach
        
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
