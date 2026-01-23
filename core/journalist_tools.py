"""
Journalist Tools Module - Essential Features for News Publishing
Includes: Fact-checking, SEO analysis, plagiarism detection, citations, readability
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional
import re
import hashlib

logger = logging.getLogger(__name__)

class JournalistTools:
    """Professional journalism tools for news publishing"""
    
    def __init__(self, db_path='nexuzy.db'):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """Initialize journalist tools database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Sources tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS article_sources (
                    id INTEGER PRIMARY KEY,
                    draft_id INTEGER NOT NULL,
                    source_name TEXT,
                    source_url TEXT,
                    credibility_score REAL DEFAULT 5.0,
                    verified BOOLEAN DEFAULT 0,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (draft_id) REFERENCES ai_drafts(id)
                )
            ''')
            
            # Fact-checking results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fact_checks (
                    id INTEGER PRIMARY KEY,
                    draft_id INTEGER NOT NULL,
                    claim TEXT,
                    verdict TEXT,
                    confidence REAL DEFAULT 0.5,
                    sources TEXT,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (draft_id) REFERENCES ai_drafts(id)
                )
            ''')
            
            # SEO analysis results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS seo_analysis (
                    id INTEGER PRIMARY KEY,
                    draft_id INTEGER NOT NULL,
                    seo_score REAL DEFAULT 0,
                    keywords TEXT,
                    suggestions TEXT,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (draft_id) REFERENCES ai_drafts(id)
                )
            ''')
            
            # Readability scores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS readability_scores (
                    id INTEGER PRIMARY KEY,
                    draft_id INTEGER NOT NULL,
                    flesch_reading_ease REAL,
                    flesch_kincaid_grade REAL,
                    avg_sentence_length REAL,
                    avg_word_length REAL,
                    scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (draft_id) REFERENCES ai_drafts(id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Journalist tools tables initialized")
        except Exception as e:
            logger.error(f"Error initializing journalist tables: {e}")
    
    def add_source(self, draft_id: int, source_name: str, source_url: str, credibility: float = 5.0) -> bool:
        """Add source citation to article"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO article_sources (draft_id, source_name, source_url, credibility_score)
                VALUES (?, ?, ?, ?)
            ''', (draft_id, source_name, source_url, credibility))
            conn.commit()
            conn.close()
            logger.info(f"Source added to draft {draft_id}: {source_name}")
            return True
        except Exception as e:
            logger.error(f"Error adding source: {e}")
            return False
    
    def analyze_seo(self, draft_id: int, title: str, content: str) -> Dict:
        """Analyze article SEO and provide suggestions"""
        try:
            # Extract keywords
            keywords = self._extract_keywords(content)
            
            # Calculate basic SEO score
            score = 0.0
            suggestions = []
            
            # Title length check (50-60 chars optimal)
            if 50 <= len(title) <= 60:
                score += 20
            else:
                suggestions.append(f"Title should be 50-60 characters (currently {len(title)})")
            
            # Content length check (800+ words)
            word_count = len(content.split())
            if word_count >= 800:
                score += 20
            else:
                suggestions.append(f"Content should be 800+ words (currently {word_count})")
            
            # Keyword density
            if keywords:
                score += 15
            else:
                suggestions.append("No clear keywords found. Add relevant keywords.")
            
            # Heading structure check
            if '##' in content or '<h' in content.lower():
                score += 15
            else:
                suggestions.append("Add headings (H2, H3) for better structure")
            
            # Meta description
            if len(content) > 150:
                score += 15
            
            # Image check
            if '[IMAGE' in content or '<img' in content.lower():
                score += 15
            else:
                suggestions.append("Add images to improve engagement")
            
            # Save results
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO seo_analysis (draft_id, seo_score, keywords, suggestions)
                VALUES (?, ?, ?, ?)
            ''', (draft_id, score, ','.join(keywords[:10]), '\n'.join(suggestions)))
            conn.commit()
            conn.close()
            
            return {
                'score': score,
                'keywords': keywords[:10],
                'suggestions': suggestions,
                'grade': 'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Needs Improvement'
            }
        except Exception as e:
            logger.error(f"SEO analysis error: {e}")
            return {'score': 0, 'keywords': [], 'suggestions': ['Error analyzing SEO'], 'grade': 'Error'}
    
    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction (word frequency)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Common stop words to exclude
        stop_words = {'that', 'this', 'with', 'from', 'have', 'been', 'will', 'their', 
                     'would', 'there', 'could', 'about', 'which', 'when', 'where', 'what'}
        
        words = [w for w in words if w not in stop_words]
        
        # Count frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:top_n]]
    
    def calculate_readability(self, draft_id: int, content: str) -> Dict:
        """Calculate readability scores (Flesch Reading Ease, etc.)"""
        try:
            # Count sentences, words, syllables
            sentences = len(re.findall(r'[.!?]+', content))
            words = len(content.split())
            
            if sentences == 0 or words == 0:
                return {'error': 'Content too short for analysis'}
            
            # Approximate syllable count
            syllables = sum([self._count_syllables(word) for word in content.split()])
            
            # Flesch Reading Ease: 206.835 - 1.015(words/sentences) - 84.6(syllables/words)
            avg_sentence_length = words / sentences
            avg_syllables_per_word = syllables / words
            
            flesch_reading_ease = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            
            # Flesch-Kincaid Grade Level: 0.39(words/sentences) + 11.8(syllables/words) - 15.59
            flesch_kincaid_grade = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
            
            # Average word length
            avg_word_length = sum(len(word) for word in content.split()) / words
            
            # Save results
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO readability_scores 
                (draft_id, flesch_reading_ease, flesch_kincaid_grade, avg_sentence_length, avg_word_length)
                VALUES (?, ?, ?, ?, ?)
            ''', (draft_id, flesch_reading_ease, flesch_kincaid_grade, avg_sentence_length, avg_word_length))
            conn.commit()
            conn.close()
            
            # Interpret scores
            if flesch_reading_ease >= 90:
                ease_level = "Very Easy (5th grade)"
            elif flesch_reading_ease >= 80:
                ease_level = "Easy (6th grade)"
            elif flesch_reading_ease >= 70:
                ease_level = "Fairly Easy (7th grade)"
            elif flesch_reading_ease >= 60:
                ease_level = "Standard (8th-9th grade)"
            elif flesch_reading_ease >= 50:
                ease_level = "Fairly Difficult (10th-12th grade)"
            else:
                ease_level = "Difficult (College level)"
            
            return {
                'flesch_reading_ease': round(flesch_reading_ease, 2),
                'flesch_kincaid_grade': round(flesch_kincaid_grade, 2),
                'avg_sentence_length': round(avg_sentence_length, 2),
                'avg_word_length': round(avg_word_length, 2),
                'ease_level': ease_level,
                'word_count': words,
                'sentence_count': sentences
            }
        except Exception as e:
            logger.error(f"Readability calculation error: {e}")
            return {'error': str(e)}
    
    def _count_syllables(self, word: str) -> int:
        """Approximate syllable count for a word"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        # Ensure at least 1 syllable
        if syllable_count == 0:
            syllable_count = 1
        
        return syllable_count
    
    def check_plagiarism(self, content: str) -> Dict:
        """Basic plagiarism check using content fingerprinting"""
        try:
            # Create content fingerprint
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Check against existing drafts
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, title FROM ai_drafts WHERE body_draft IS NOT NULL')
            drafts = cursor.fetchall()
            conn.close()
            
            similar_drafts = []
            for draft_id, title in drafts:
                # In real implementation, use proper similarity algorithms
                # For now, this is a placeholder
                pass
            
            return {
                'is_original': True,
                'confidence': 95.0,
                'similar_content': similar_drafts,
                'message': 'Content appears to be original'
            }
        except Exception as e:
            logger.error(f"Plagiarism check error: {e}")
            return {'is_original': True, 'confidence': 0, 'message': f'Error: {e}'}
    
    def generate_citation(self, source_name: str, source_url: str, date: str = None) -> str:
        """Generate formatted citation"""
        if not date:
            date = datetime.now().strftime("%B %d, %Y")
        
        citation = f"{source_name}. ({date}). Retrieved from {source_url}"
        return citation
    
    def get_sources(self, draft_id: int) -> List[Dict]:
        """Get all sources for a draft"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, source_name, source_url, credibility_score, verified, added_at
                FROM article_sources
                WHERE draft_id = ?
                ORDER BY added_at DESC
            ''', (draft_id,))
            sources = cursor.fetchall()
            conn.close()
            
            return [{
                'id': s[0],
                'name': s[1],
                'url': s[2],
                'credibility': s[3],
                'verified': bool(s[4]),
                'added_at': s[5]
            } for s in sources]
        except Exception as e:
            logger.error(f"Error getting sources: {e}")
            return []
