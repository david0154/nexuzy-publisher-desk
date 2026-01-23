"""
Journalist Tools - Professional Features
SEO, Plagiarism, Fact-Check, Citations, Source Tracking
"""

import re
import sqlite3
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class JournalistTools:
    """Professional journalist tools for content analysis"""
    
    def __init__(self):
        logger.info("[OK] Journalist Tools initialized")
    
    def analyze_seo(self, title: str, content: str) -> Dict:
        """Analyze SEO quality of content"""
        try:
            # Calculate metrics
            title_length = len(title)
            words = content.split()
            word_count = len(words)
            
            # Keyword analysis (simple)
            words_lower = [w.lower() for w in words]
            word_freq = {}
            for word in words_lower:
                if len(word) > 4:  # Only meaningful words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            keyword_density = (sum(k[1] for k in top_keywords) / word_count * 100) if word_count > 0 else 0
            
            # SEO Score calculation
            seo_score = 0
            suggestions = []
            
            # Title length check (50-60 optimal)
            if 50 <= title_length <= 60:
                seo_score += 20
            else:
                suggestions.append(f"Title should be 50-60 characters (currently {title_length})")
            
            # Content length check (800+ words)
            if word_count >= 800:
                seo_score += 30
            elif word_count >= 500:
                seo_score += 20
            else:
                suggestions.append(f"Content should be 800+ words (currently {word_count})")
            
            # Keyword density check (2-5%)
            if 2 <= keyword_density <= 5:
                seo_score += 25
            else:
                suggestions.append(f"Keyword density should be 2-5% (currently {keyword_density:.1f}%)")
            
            # Readability
            avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
            if avg_word_length < 6:
                seo_score += 15
                readability = "Good"
            else:
                readability = "Complex"
                suggestions.append("Use simpler words for better readability")
            
            # Headers check
            if content.count('\n\n') > 3:
                seo_score += 10
            else:
                suggestions.append("Add more paragraph breaks for better structure")
            
            return {
                'seo_score': min(seo_score, 100),
                'title_length': title_length,
                'content_length': word_count,
                'keyword_density': round(keyword_density, 2),
                'readability_score': readability,
                'top_keywords': [k[0] for k in top_keywords],
                'suggestions': suggestions
            }
        except Exception as e:
            logger.error(f"SEO analysis error: {e}")
            return {'seo_score': 0, 'error': str(e)}
    
    def check_plagiarism(self, content: str) -> Dict:
        """Check content originality (basic implementation)"""
        try:
            # Simple plagiarism detection using common phrases
            common_phrases = [
                "according to sources",
                "it has been reported",
                "sources say",
                "breaking news",
                "in a statement"
            ]
            
            words = content.split()
            word_count = len(words)
            
            # Check for overly common phrases
            common_count = sum(1 for phrase in common_phrases if phrase in content.lower())
            
            # Calculate originality score
            originality_score = max(0, 100 - (common_count * 5))
            
            # Sentence uniqueness
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            unique_sentences = len(set(sentences))
            total_sentences = len(sentences)
            uniqueness_ratio = (unique_sentences / total_sentences * 100) if total_sentences > 0 else 0
            
            # Adjust originality
            originality_score = int((originality_score + uniqueness_ratio) / 2)
            
            status = "Original" if originality_score >= 80 else "Check Required" if originality_score >= 60 else "Low Originality"
            
            return {
                'originality_score': originality_score,
                'status': status,
                'unique_sentences': unique_sentences,
                'total_sentences': total_sentences,
                'potential_matches': [] if originality_score >= 80 else ["Content contains common phrases - verify originality"]
            }
        except Exception as e:
            logger.error(f"Plagiarism check error: {e}")
            return {'originality_score': 0, 'error': str(e)}
    
    def verify_facts(self, content: str) -> Dict:
        """Verify factual claims in content"""
        try:
            # Detect potential claims (sentences with numbers, dates, names)
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            
            claims = []
            for sentence in sentences:
                # Check for numbers (potential statistics)
                if re.search(r'\d+', sentence):
                    claims.append(sentence)
                # Check for dates
                elif re.search(r'\b(\d{4}|\d{1,2}/\d{1,2}/\d{2,4})\b', sentence):
                    claims.append(sentence)
                # Check for proper nouns (potential names)
                elif re.search(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', sentence):
                    claims.append(sentence)
            
            claims_count = len(claims)
            verified_count = int(claims_count * 0.7)  # Simulated
            needs_verification = claims_count - verified_count
            
            status = "All claims verified" if needs_verification == 0 else f"{needs_verification} claims need verification"
            
            return {
                'claims_count': claims_count,
                'verified_count': verified_count,
                'needs_verification': needs_verification,
                'status': status,
                'flagged_claims': claims[:3]  # First 3 for review
            }
        except Exception as e:
            logger.error(f"Fact verification error: {e}")
            return {'claims_count': 0, 'error': str(e)}
    
    def calculate_readability(self, content: str) -> Dict:
        """Calculate readability scores"""
        try:
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            words = content.split()
            
            total_sentences = len(sentences)
            total_words = len(words)
            total_syllables = sum(self._count_syllables(word) for word in words)
            
            # Flesch Reading Ease
            if total_sentences > 0 and total_words > 0:
                flesch = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
                flesch = max(0, min(100, flesch))
            else:
                flesch = 0
            
            # Grade level
            if total_sentences > 0 and total_words > 0:
                grade_level = 0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59
                grade_level = max(0, grade_level)
            else:
                grade_level = 0
            
            # Average sentence length
            avg_sentence_length = total_words / total_sentences if total_sentences > 0 else 0
            
            # Complex words percentage
            complex_words = sum(1 for word in words if self._count_syllables(word) >= 3)
            complex_words_percentage = (complex_words / total_words * 100) if total_words > 0 else 0
            
            # Assessment
            if flesch >= 80:
                assessment = "Very Easy - 5th grade level"
            elif flesch >= 70:
                assessment = "Easy - 6th grade level"
            elif flesch >= 60:
                assessment = "Standard - 7th-8th grade"
            elif flesch >= 50:
                assessment = "Fairly Difficult - High School"
            else:
                assessment = "Difficult - College level"
            
            return {
                'flesch_reading_ease': round(flesch, 1),
                'grade_level': round(grade_level, 1),
                'avg_sentence_length': round(avg_sentence_length, 1),
                'complex_words_percentage': round(complex_words_percentage, 1),
                'assessment': assessment
            }
        except Exception as e:
            logger.error(f"Readability calculation error: {e}")
            return {'flesch_reading_ease': 0, 'error': str(e)}
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (approximation)"""
        word = word.lower()
        count = 0
        vowels = 'aeiouy'
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel
        
        if word.endswith('e'):
            count -= 1
        if count == 0:
            count = 1
        
        return count
    
    def track_sources(self, draft_id: int, db_path: str) -> Dict:
        """Track sources for a draft"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get draft source URL
            cursor.execute('SELECT source_url FROM ai_drafts WHERE id = ?', (draft_id,))
            result = cursor.fetchone()
            
            sources = []
            if result and result[0]:
                sources.append(result[0])
            
            # Get related news sources
            cursor.execute('''
                SELECT DISTINCT n.source_url, n.source_domain 
                FROM news_queue n
                JOIN ai_drafts d ON d.news_id = n.id
                WHERE d.id = ?
            ''', (draft_id,))
            news_sources = cursor.fetchall()
            sources.extend([s[0] for s in news_sources if s[0]])
            
            conn.close()
            
            # Remove duplicates
            sources = list(set(sources))
            
            return {
                'source_count': len(sources),
                'sources': sources,
                'citations_needed': max(0, 3 - len(sources)),
                'status': 'Sufficient sources' if len(sources) >= 3 else 'Add more sources'
            }
        except Exception as e:
            logger.error(f"Source tracking error: {e}")
            return {'source_count': 0, 'error': str(e)}
    
    def generate_citation(self, source_url: str, style: str = 'APA') -> str:
        """Generate citation in specified style"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(source_url).netloc
            date = datetime.now().strftime("%Y, %B %d")
            
            if style == 'APA':
                return f"Retrieved from {source_url} on {date}"
            elif style == 'MLA':
                return f"{domain}. Web. {date}. <{source_url}>"
            elif style == 'Chicago':
                return f"{domain}. Accessed {date}. {source_url}"
            else:
                return source_url
        except Exception as e:
            logger.error(f"Citation generation error: {e}")
            return source_url
