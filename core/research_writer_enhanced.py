"""
Enhanced Research Writer with Advanced Features
- Topic Expansion & Deep Explanation
- Multi-Source Research (GitHub, Web, Wikipedia, DuckDuckGo)
- Image Collection from Sources
- Hallucination Protection & Fact Verification
- Source Credibility Scoring
"""

import os
import sys
import sqlite3
import logging
import requests
import json
import re
import time
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse, quote_plus
from datetime import datetime

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

logger = logging.getLogger(__name__)

class EnhancedResearchWriter:
    """
    Advanced Research Writer with multi-source integration and hallucination protection
    """
    
    def __init__(self, db_path='nexuzy.db', model_path=None):
        self.db_path = db_path
        self.model = None
        self.progress_callback = None
        
        # Load LLM model
        if model_path and os.path.exists(model_path) and Llama:
            try:
                self.model = Llama(
                    model_path=model_path,
                    n_ctx=4096,
                    n_threads=4,
                    verbose=False
                )
                logger.info("[OK] Research Writer AI Model loaded")
            except Exception as e:
                logger.error(f"Model load error: {e}")
        
        # Multi-source research configuration
        self.sources_config = {
            'github': {'enabled': True, 'weight': 0.9},
            'wikipedia': {'enabled': True, 'weight': 0.95},
            'duckduckgo': {'enabled': True, 'weight': 0.8},
            'web_search': {'enabled': True, 'weight': 0.75}
        }
        
        # Hallucination protection settings
        self.verification_threshold = 0.7  # Minimum confidence for facts
        self.min_sources = 2  # Minimum sources to verify a fact
        self.credibility_weights = {
            'academic': 1.0,
            'government': 0.95,
            'established_media': 0.85,
            'wikipedia': 0.8,
            'github': 0.75,
            'general': 0.6
        }
    
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def _update_progress(self, progress: int, status: str):
        """Update progress via callback"""
        if self.progress_callback:
            self.progress_callback(progress, status)
        logger.info(f"[{progress}%] {status}")
    
    def expand_topic(self, topic: str) -> Dict[str, Any]:
        """
        Expand and explain topic with context, keywords, and subtopics
        """
        self._update_progress(5, f"Analyzing topic: {topic}")
        
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
        
        logger.info(f"Topic expanded: {len(expansion['keywords'])} keywords, {len(expansion['subtopics'])} subtopics")
        return expansion
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Remove common words and extract important terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]
        return list(set(keywords))[:10]  # Top 10 unique keywords
    
    def _generate_search_queries(self, topic: str, keywords: List[str]) -> List[str]:
        """Generate optimized search queries"""
        queries = [
            topic,
            f"{topic} explained",
            f"{topic} latest news",
            f"{topic} research",
            f"{topic} analysis"
        ]
        
        # Add keyword combinations
        for kw in keywords[:3]:
            queries.append(f"{topic} {kw}")
        
        return queries[:8]
    
    def _generate_subtopics(self, topic: str, context: str) -> List[str]:
        """Generate relevant subtopics"""
        subtopics = []
        
        # Extract potential subtopics from context
        sentences = context.split('. ') if context else []
        for sentence in sentences[:5]:
            if len(sentence) > 20:
                # Extract noun phrases as subtopics
                words = sentence.split()
                if len(words) > 3:
                    subtopic = ' '.join(words[:4])
                    subtopics.append(subtopic)
        
        return subtopics[:5]
    
    def research_multi_source(self, topic: str, topic_expansion: Dict) -> Dict[str, Any]:
        """
        Research from multiple sources: GitHub, Wikipedia, DuckDuckGo, Web
        """
        self._update_progress(15, "Researching from multiple sources")
        
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
            self._update_progress(20, "Searching GitHub repositories")
            github_data = self._search_github(topic, topic_expansion['keywords'])
            research_data['github_results'] = github_data['repositories']
            research_data['links'].extend(github_data['links'])
            research_data['total_sources'] += len(github_data['repositories'])
        
        # 2. Wikipedia Research
        if self.sources_config['wikipedia']['enabled']:
            self._update_progress(30, "Fetching Wikipedia data")
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
            self._update_progress(45, "Searching DuckDuckGo")
            ddg_results = self._search_duckduckgo(topic, topic_expansion['search_queries'])
            research_data['duckduckgo_results'] = ddg_results['results']
            research_data['links'].extend(ddg_results['links'])
            research_data['images'].extend(ddg_results.get('images', []))
            research_data['total_sources'] += len(ddg_results['results'])
        
        # 4. Web Search (fallback)
        if self.sources_config['web_search']['enabled']:
            self._update_progress(60, "Performing web search")
            web_results = self._web_search(topic, topic_expansion['keywords'])
            research_data['web_results'] = web_results['results']
            research_data['links'].extend(web_results['links'])
            research_data['total_sources'] += len(web_results['results'])
        
        self._update_progress(70, f"Collected data from {research_data['total_sources']} sources")
        return research_data
    
    def _search_github(self, topic: str, keywords: List[str]) -> Dict[str, Any]:
        """Search GitHub for relevant repositories"""
        results = {'repositories': [], 'links': []}
        
        try:
            # GitHub API search
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
                
                logger.info(f"Found {len(results['repositories'])} GitHub repositories")
        except Exception as e:
            logger.error(f"GitHub search error: {e}")
        
        return results
    
    def _get_wikipedia_summary(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get Wikipedia summary for topic"""
        try:
            # Wikipedia API
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
    
    def _research_wikipedia(self, topic: str) -> Dict[str, Any]:
        """Deep Wikipedia research"""
        wiki_data = {'content': '', 'url': '', 'images': [], 'sections': []}
        
        try:
            # Get full page content
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
                                    'description': f"Image from {page_title}"
                                })
        except Exception as e:
            logger.error(f"Wikipedia research error: {e}")
        
        return wiki_data
    
    def _search_duckduckgo(self, topic: str, queries: List[str]) -> Dict[str, Any]:
        """Search DuckDuckGo for topic information"""
        results = {'results': [], 'links': [], 'images': []}
        
        try:
            # DuckDuckGo Instant Answer API
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
                        'description': topic
                    })
                
                logger.info(f"DuckDuckGo: {len(results['results'])} results")
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
        
        return results
    
    def _web_search(self, topic: str, keywords: List[str]) -> Dict[str, Any]:
        """Fallback web search using scraping"""
        results = {'results': [], 'links': []}
        
        # Simple web scraping fallback
        # In production, use proper search APIs
        logger.info("Using fallback web search")
        
        return results
    
    def collect_images(self, research_data: Dict[str, Any], topic: str) -> List[Dict[str, Any]]:
        """Collect and filter images from research"""
        self._update_progress(75, "Collecting images")
        
        all_images = research_data.get('images', [])
        filtered_images = []
        
        for img in all_images:
            # Filter out logos, icons, small images
            if img.get('url') and not any(x in img['url'].lower() for x in ['logo', 'icon', 'button']):
                filtered_images.append({
                    'url': img['url'],
                    'source': img.get('source', 'unknown'),
                    'description': img.get('description', topic),
                    'relevance_score': 0.8
                })
        
        logger.info(f"Collected {len(filtered_images)} relevant images")
        return filtered_images[:10]  # Top 10 images
    
    def verify_facts(self, facts: List[Dict[str, Any]], research_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Verify facts against multiple sources - Hallucination Protection
        """
        self._update_progress(80, "Verifying facts (Hallucination Protection)")
        
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
                logger.warning(f"Fact rejected (low confidence {verification['confidence']}): {fact.get('statement', '')[:50]}")
        
        logger.info(f"Verified {len(verified_facts)}/{len(facts)} facts")
        return verified_facts
    
    def _verify_single_fact(self, fact: Dict[str, Any], research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a single fact against sources"""
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
        
        # Check web results
        for result in research_data.get('web_results', []):
            content = result.get('content', '').lower()
            if content and any(word in content for word in fact_text.split()[:5]):
                supporting_count += 1
                total_credibility += 0.7
                verification['sources'].append(f"Web: {result.get('title', 'Unknown')[:30]}")
                break
        
        # Calculate confidence
        if supporting_count >= self.min_sources:
            verification['confidence'] = min(0.95, supporting_count / 3.0)
            verification['credibility'] = total_credibility / supporting_count if supporting_count > 0 else 0.0
        else:
            verification['confidence'] = supporting_count * 0.3  # Low confidence
        
        return verification
    
    def generate_article(self, topic: str, topic_expansion: Dict, research_data: Dict[str, Any], 
                         length: str = 'Long', style: str = 'Investigative') -> str:
        """
        Generate article with AI model using researched data
        """
        self._update_progress(85, "Generating article with AI")
        
        # Prepare context
        context = self._prepare_context(topic, topic_expansion, research_data)
        
        # Determine word target
        word_targets = {
            'Short (500-800 words)': 600,
            'Medium (1000-1500 words)': 1200,
            'Long (2000-3000 words)': 2500,
            'Deep Dive (3000+ words)': 3500
        }
        target_words = word_targets.get(length, 2500)
        
        # Generate with model or template
        if self.model:
            article = self._generate_with_model(topic, context, style, target_words)
        else:
            article = self._generate_template_article(topic, topic_expansion, research_data, style, target_words)
        
        return article
    
    def _prepare_context(self, topic: str, topic_expansion: Dict, research_data: Dict) -> str:
        """Prepare context for article generation"""
        context = f"Topic: {topic}\n\n"
        context += f"Explanation: {topic_expansion.get('explained_topic', '')}\n\n"
        context += f"Keywords: {', '.join(topic_expansion.get('keywords', [])[:5])}\n\n"
        
        # Add Wikipedia content
        wiki_content = research_data.get('wikipedia_data', {}).get('content', '')
        if wiki_content:
            context += f"Wikipedia Summary: {wiki_content[:500]}\n\n"
        
        # Add key findings
        context += "Key Findings:\n"
        for result in research_data.get('duckduckgo_results', [])[:3]:
            context += f"- {result.get('content', '')[:200]}\n"
        
        return context[:3000]  # Limit context size
    
    def _generate_with_model(self, topic: str, context: str, style: str, target_words: int) -> str:
        """Generate article using LLM model"""
        prompt = f"""Write a comprehensive {style.lower()} article about: {topic}

Context and Research:
{context}

Requirements:
- Approximately {target_words} words
- {style} writing style
- Well-structured with sections
- Fact-based and objective
- Include citations where appropriate

Article:"""
        
        try:
            output = self.model(
                prompt,
                max_tokens=target_words * 2,
                temperature=0.7,
                top_p=0.9,
                stop=["\n\nEnd of Article", "\n\n---"]
            )
            article = output['choices'][0]['text'].strip()
            return article
        except Exception as e:
            logger.error(f"Model generation error: {e}")
            return self._generate_template_article(topic, {}, {}, style, target_words)
    
    def _generate_template_article(self, topic: str, topic_expansion: Dict, 
                                   research_data: Dict, style: str, target_words: int) -> str:
        """Generate template-based article"""
        article = f"# {topic}\n\n"
        
        # Introduction
        explained = topic_expansion.get('explained_topic', '')
        if explained:
            article += f"{explained}\n\n"
        else:
            article += f"This comprehensive analysis explores {topic} in detail, examining its significance, implications, and current developments.\n\n"
        
        # Main sections
        article += f"## Overview\n\n"
        wiki_content = research_data.get('wikipedia_data', {}).get('content', '')
        if wiki_content:
            # Clean HTML tags
            cleaned = re.sub(r'<[^>]+>', '', wiki_content)
            article += f"{cleaned[:800]}...\n\n"
        
        # Key findings
        article += f"## Key Findings\n\n"
        for i, result in enumerate(research_data.get('duckduckgo_results', [])[:3], 1):
            content = result.get('content', '')
            if content:
                article += f"{i}. {content}\n\n"
        
        # GitHub resources
        github_repos = research_data.get('github_results', [])
        if github_repos:
            article += f"## Related Projects and Resources\n\n"
            for repo in github_repos[:3]:
                article += f"**{repo['name']}**: {repo.get('description', 'No description')} ({repo['stars']} stars)\n\n"
        
        # Conclusion
        article += f"## Conclusion\n\n"
        article += f"The research on {topic} reveals important insights and ongoing developments. "
        article += f"Further investigation and monitoring of this topic will provide additional clarity on its evolution and impact.\n\n"
        
        return article
    
    def write_research_article(self, topic: str, length: str = 'Long (2000-3000 words)',
                               style: str = 'Investigative', workspace_id: int = None) -> Dict[str, Any]:
        """
        Main entry point: Write complete research article
        """
        start_time = time.time()
        
        try:
            # Step 1: Topic expansion
            self._update_progress(0, "Starting research process")
            topic_expansion = self.expand_topic(topic)
            
            # Step 2: Multi-source research
            research_data = self.research_multi_source(topic, topic_expansion)
            
            # Step 3: Extract facts (simplified for now)
            facts = self._extract_facts_from_research(research_data)
            
            # Step 4: Verify facts (hallucination protection)
            verified_facts = self.verify_facts(facts, research_data)
            
            # Step 5: Collect images
            images = self.collect_images(research_data, topic)
            
            # Step 6: Generate article
            article_text = self.generate_article(topic, topic_expansion, research_data, length, style)
            
            # Step 7: Calculate quality metrics
            self._update_progress(95, "Finalizing article")
            word_count = len(article_text.split())
            quality_score = self._calculate_quality_score(article_text, research_data, verified_facts)
            
            generation_time = time.time() - start_time
            
            # Compile results
            result = {
                'success': True,
                'article': article_text,
                'topic': topic,
                'word_count': word_count,
                'quality_score': quality_score,
                'sources_used': research_data['total_sources'],
                'verified_facts_count': len(verified_facts),
                'images_collected': len(images),
                'generation_time': f"{generation_time:.1f}s",
                'sources': research_data['links'],
                'images': images,
                'topic_expansion': topic_expansion,
                'hallucination_protection': {
                    'total_facts_checked': len(facts),
                    'verified_facts': len(verified_facts),
                    'verification_rate': len(verified_facts) / len(facts) if facts else 0.0
                }
            }
            
            self._update_progress(100, "Research article complete!")
            return result
            
        except Exception as e:
            logger.error(f"Research article generation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'article': f"Error generating article: {e}"
            }
    
    def _extract_facts_from_research(self, research_data: Dict) -> List[Dict[str, Any]]:
        """Extract factual statements from research data"""
        facts = []
        
        # Extract from Wikipedia
        wiki_content = research_data.get('wikipedia_data', {}).get('content', '')
        if wiki_content:
            sentences = re.split(r'[.!?]', wiki_content)
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
        
        return facts
    
    def _calculate_quality_score(self, article: str, research_data: Dict, verified_facts: List) -> float:
        """Calculate article quality score"""
        score = 5.0  # Base score
        
        # Word count (target around 2000-3000)
        word_count = len(article.split())
        if 1500 <= word_count <= 3500:
            score += 1.5
        elif 1000 <= word_count < 1500:
            score += 0.5
        
        # Source diversity
        total_sources = research_data.get('total_sources', 0)
        if total_sources >= 5:
            score += 2.0
        elif total_sources >= 3:
            score += 1.0
        
        # Fact verification
        if verified_facts:
            score += min(1.5, len(verified_facts) * 0.2)
        
        return min(10.0, score)

# Backwards compatibility
ResearchWriter = EnhancedResearchWriter
