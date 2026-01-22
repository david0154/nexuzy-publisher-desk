"""
Content Scraper Module
Safely scrapes facts, names, dates, quotes from source URLs
"""

import sqlite3
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import re

logger = logging.getLogger(__name__)

class ContentScraper:
    """Scrape facts and data from news articles"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_article(self, url: str, news_id: int) -> Dict:
        """
        Scrape article content and extract facts
        Safe mode: extract only facts, names, dates, quotes - no full article
        """
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            extracted = {
                'facts': [],
                'names': [],
                'dates': [],
                'quotes': [],
                'entities': []
            }
            
            # Extract main content
            article = soup.find('article') or soup.find('div', class_=re.compile('content|article|story', re.I))
            if not article:
                article = soup.body
            
            # Extract paragraphs
            paragraphs = article.find_all('p')
            text = ' '.join([p.get_text() for p in paragraphs])
            
            # Extract dates
            dates = self._extract_dates(text)
            for date in dates:
                self._store_fact(news_id, 'date', date, url)
                extracted['dates'].append(date)
            
            # Extract names/entities
            names = self._extract_proper_nouns(text)
            for name in names:
                self._store_fact(news_id, 'entity', name, url)
                extracted['names'].append(name)
            
            # Extract quotes
            quotes = self._extract_quotes(article)
            for quote in quotes[:5]:  # Limit to 5 quotes
                self._store_fact(news_id, 'quote', quote, url)
                extracted['quotes'].append(quote)
            
            # Extract key facts (sentences with numbers or key words)
            facts = self._extract_facts(text)
            for fact in facts[:10]:  # Limit to 10 facts
                self._store_fact(news_id, 'fact', fact, url)
                extracted['facts'].append(fact)
            
            logger.info(f"Scraped {url}: {len(extracted['facts'])} facts, {len(extracted['names'])} names")
            return extracted
        
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {}
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        date_patterns = [
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}/\d{1,2}/\d{4}'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        return list(set(dates))
    
    def _extract_proper_nouns(self, text: str) -> List[str]:
        """Extract proper nouns (names, organizations)"""
        # Simple extraction: words starting with capital letters
        words = text.split()
        proper_nouns = []
        
        for i, word in enumerate(words):
            # Check if word starts with capital letter
            if word and word[0].isupper() and len(word) > 2:
                # Check if it's not after sentence start
                if i > 0 and words[i-1][-1] not in '.!?':
                    proper_nouns.append(word.strip('.,;:'))
        
        return list(set(proper_nouns))[:20]  # Limit to 20
    
    def _extract_quotes(self, soup) -> List[str]:
        """Extract quotes from article"""
        quotes = []
        
        # Look for blockquotes
        for blockquote in soup.find_all('blockquote'):
            text = blockquote.get_text().strip()
            if text:
                quotes.append(text)
        
        # Look for quoted text patterns
        text = soup.get_text()
        quote_pattern = r'["\u201c]([^"\u201d]{20,200})["\u201d]'
        matches = re.findall(quote_pattern, text)
        quotes.extend(matches)
        
        return quotes[:5]
    
    def _extract_facts(self, text: str) -> List[str]:
        """Extract key facts (sentences with numbers, important keywords)"""
        facts = []
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 300:
                continue
            
            # Check for numbers or key indicators
            has_number = bool(re.search(r'\d+', sentence))
            has_keyword = any(kw in sentence.lower() for kw in [
                'said', 'announced', 'confirmed', 'reported', 'found',
                'according', 'however', 'yesterday', 'today', 'showed'
            ])
            
            if has_number or has_keyword:
                facts.append(sentence)
        
        return facts[:10]
    
    def _store_fact(self, news_id: int, fact_type: str, content: str, source_url: str):
        """Store extracted fact in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO scraped_facts (news_id, fact_type, content, source_url, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (news_id, fact_type, content, source_url, 0.8))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            logger.error(f"Error storing fact: {e}")
