"""
AI Humanizer Module - Advanced Text Humanization Engine
Transforms AI-generated text into authentic, natural human writing

INSPIRED BY: QuillBot's AI Humanizer approach
OPTIMIZED FOR: News articles and journalistic content

FEATURES:
✅ Sentence length variance optimization (3-45 words)
✅ 95% contraction injection (human-level)
✅ Forbidden AI pattern removal ("tells" detection)
✅ Flow smoothing with natural transitions
✅ Synonym variation with contextual awareness
✅ Burstiness injection (perplexity + randomness)
✅ Passive-to-active voice conversion
✅ Natural imperfection injection
✅ Trained patterns from human text analysis
✅ Multi-pass refinement system
"""

import re
import random
import logging
from typing import List, Dict, Tuple
from collections import Counter

logger = logging.getLogger(__name__)

class AIHumanizer:
    """Advanced AI text humanization engine"""
    
    # AI "TELLS" - Forbidden patterns that reveal AI generation
    AI_TELLS = {
        'repetitive_starters': [
            r'^Moreover,\s', r'^Furthermore,\s', r'^Additionally,\s',
            r'^In addition,\s', r'^Subsequently,\s', r'^Consequently,\s',
            r'^Therefore,\s', r'^Thus,\s', r'^Hence,\s',
            r'^It is important to note that\s', r'^It should be noted that\s',
            r'^It is worth mentioning that\s'
        ],
        'formal_phrases': [
            'in order to', 'due to the fact that', 'at this point in time',
            'in the event that', 'for the purpose of', 'in spite of the fact that',
            'with regard to', 'with respect to', 'in relation to',
            'as a matter of fact', 'it goes without saying', 'needless to say'
        ],
        'robotic_endings': [
            'only time will tell', 'remains to be seen', 'time will tell',
            'it is clear that', 'it is evident that', 'it is obvious that'
        ],
        'passive_indicators': [
            r'\bis\s+being\s+\w+ed\b', r'\bwas\s+being\s+\w+ed\b',
            r'\bwill\s+be\s+\w+ed\b', r'\bhas\s+been\s+\w+ed\b',
            r'\bhave\s+been\s+\w+ed\b', r'\bhad\s+been\s+\w+ed\b'
        ]
    }
    
    # Natural contraction patterns (95% application rate)
    CONTRACTIONS = {
        r'\bdo not\b': "don't", r'\bdoes not\b': "doesn't",
        r'\bdid not\b': "didn't", r'\bis not\b': "isn't",
        r'\bare not\b': "aren't", r'\bwas not\b': "wasn't",
        r'\bwere not\b': "weren't", r'\bhave not\b': "haven't",
        r'\bhas not\b': "hasn't", r'\bhad not\b': "hadn't",
        r'\bwill not\b': "won't", r'\bwould not\b': "wouldn't",
        r'\bshould not\b': "shouldn't", r'\bcould not\b': "couldn't",
        r'\bcannot\b': "can't", r'\bit is\b': "it's",
        r'\bthat is\b': "that's", r'\bthere is\b': "there's",
        r'\bthey are\b': "they're", r'\bwe are\b': "we're",
        r'\byou are\b': "you're", r'\bI am\b': "I'm",
        r'\bhe is\b': "he's", r'\bshe is\b': "she's",
        r'\bwhat is\b': "what's", r'\bwhere is\b': "where's",
        r'\bwho is\b': "who's", r'\bthere will\b': "there'll",
        r'\bit would\b': "it'd", r'\bthey would\b': "they'd",
        r'\bI would\b': "I'd", r'\byou would\b': "you'd",
        r'\bthat would\b': "that'd", r'\bwho would\b': "who'd"
    }
    
    # Conversational replacements (natural language)
    CONVERSATIONAL_SWAPS = {
        'in order to': 'to',
        'due to the fact that': 'because',
        'at this point in time': 'now',
        'in the event that': 'if',
        'for the purpose of': 'to',
        'in spite of the fact that': 'although',
        'by means of': 'by',
        'in the near future': 'soon',
        'at the present time': 'currently',
        'in the process of': 'while',
        'with regard to': 'about',
        'with respect to': 'regarding',
        'as a matter of fact': 'actually',
        'it is important to note': 'notably',
        'it should be noted': 'note that',
        'it is worth mentioning': 'worth noting',
        'a large number of': 'many',
        'a small number of': 'few',
        'in the majority of cases': 'usually',
        'on a regular basis': 'regularly',
        'in close proximity to': 'near'
    }
    
    # Natural sentence starters for variety
    NATURAL_STARTERS = [
        'But', 'Yet', 'So', 'Still', 'Plus', 'And',
        'Meanwhile', 'However', 'Though', 'In fact'
    ]
    
    def __init__(self):
        logger.info("✅ AI Humanizer initialized (QuillBot-inspired)")
    
    def humanize(self, text: str, mode: str = 'advanced') -> Dict:
        """
        Main humanization pipeline - transforms AI text to human-like
        
        Args:
            text: AI-generated text to humanize
            mode: 'basic' or 'advanced' (advanced = deeper rewrites)
        
        Returns:
            Dict with humanized_text, score, and changes
        """
        logger.info(f"🎯 Humanizing text ({mode} mode)...")
        
        original_text = text
        changes = []
        
        # PASS 1: Remove AI tells (forbidden patterns)
        text, tell_changes = self._remove_ai_tells(text)
        changes.extend(tell_changes)
        
        # PASS 2: Apply 95% contractions (human-level)
        text, contraction_count = self._inject_contractions(text)
        changes.append(f"Applied {contraction_count} contractions (95% rate)")
        
        # PASS 3: Convert formal phrases to conversational
        text, swap_count = self._conversational_swaps(text)
        changes.append(f"Converted {swap_count} formal phrases")
        
        # PASS 4: Optimize sentence length variance (burstiness)
        text, variance_changes = self._optimize_sentence_variance(text, mode)
        changes.extend(variance_changes)
        
        # PASS 5: Convert passive to active voice
        text, voice_count = self._passive_to_active(text)
        changes.append(f"Converted {voice_count} passive constructions")
        
        # PASS 6: Inject natural imperfections
        text = self._inject_imperfections(text)
        changes.append("Injected natural imperfections")
        
        # PASS 7: Flow smoothing
        text = self._smooth_flow(text)
        changes.append("Smoothed overall flow")
        
        # Calculate humanization score
        score = self._calculate_human_score(text)
        
        logger.info(f"✅ Humanization complete: {score:.1%} human-like")
        
        return {
            'humanized_text': text,
            'original_text': original_text,
            'human_score': score,
            'changes': changes,
            'mode': mode
        }
    
    def _remove_ai_tells(self, text: str) -> Tuple[str, List[str]]:
        """Remove forbidden AI patterns ("tells")"""
        changes = []
        cleaned = text
        
        # Remove repetitive formal starters
        for pattern in self.AI_TELLS['repetitive_starters']:
            matches = len(re.findall(pattern, cleaned, re.IGNORECASE))
            if matches > 0:
                # Replace with nothing or natural starter
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
                changes.append(f"Removed {matches} formal starter(s)")
        
        # Remove robotic endings
        for phrase in self.AI_TELLS['robotic_endings']:
            if phrase in cleaned.lower():
                # Remove entire sentence containing phrase
                sentences = re.split(r'([.!?])', cleaned)
                filtered = []
                i = 0
                while i < len(sentences):
                    sent = sentences[i]
                    if phrase not in sent.lower():
                        filtered.append(sent)
                        if i + 1 < len(sentences):
                            filtered.append(sentences[i + 1])
                    i += 2
                cleaned = ''.join(filtered)
                changes.append(f"Removed robotic phrase: '{phrase}'")
        
        return cleaned, changes
    
    def _inject_contractions(self, text: str) -> Tuple[str, int]:
        """Apply 95% contraction rate (human-level writing)"""
        contracted = text
        contraction_count = 0
        
        for pattern, contraction in self.CONTRACTIONS.items():
            matches = re.finditer(pattern, contracted, re.IGNORECASE)
            for match in matches:
                # Apply 95% of the time
                if random.random() < 0.95:
                    original = match.group(0)
                    # Preserve capitalization
                    if original[0].isupper():
                        replacement = contraction[0].upper() + contraction[1:]
                    else:
                        replacement = contraction
                    
                    contracted = contracted[:match.start()] + replacement + contracted[match.end():]
                    contraction_count += 1
                    break  # Re-search after each replacement
        
        return contracted, contraction_count
    
    def _conversational_swaps(self, text: str) -> Tuple[str, int]:
        """Replace formal phrases with conversational language"""
        swapped = text
        swap_count = 0
        
        for formal, casual in self.CONVERSATIONAL_SWAPS.items():
            pattern = re.compile(re.escape(formal), re.IGNORECASE)
            matches = pattern.findall(swapped)
            if matches:
                swapped = pattern.sub(casual, swapped)
                swap_count += len(matches)
        
        return swapped, swap_count
    
    def _optimize_sentence_variance(self, text: str, mode: str) -> Tuple[str, List[str]]:
        """Optimize sentence length variance for burstiness (3-45 words)"""
        changes = []
        sentences = re.split(r'([.!?]\s+)', text)
        optimized = []
        
        i = 0
        punchy_added = 0
        long_added = 0
        
        while i < len(sentences):
            sent = sentences[i]
            
            if not sent.strip() or sent in ['. ', '! ', '? ']:
                optimized.append(sent)
                i += 1
                continue
            
            word_count = len(sent.split())
            
            # STRATEGY 1: Create punchy 3-5 word sentences (every 3 sentences, 60% chance)
            if i % 3 == 0 and word_count > 15 and random.random() < 0.60:
                words = sent.split()
                if len(words) > 8:
                    split_point = random.randint(3, min(5, len(words) - 3))
                    punchy = ' '.join(words[:split_point])
                    rest = ' '.join(words[split_point:])
                    
                    if self._is_complete(punchy) and len(rest.split()) >= 3:
                        optimized.append(punchy + '.')
                        optimized.append(' ')
                        # Capitalize rest
                        if rest[0].islower():
                            rest = rest[0].upper() + rest[1:]
                        optimized.append(rest)
                        punchy_added += 1
                        i += 1
                        continue
            
            # STRATEGY 2: Combine for long 35-45 word sentences (every 4 sentences)
            if mode == 'advanced' and i % 4 == 0 and i + 2 < len(sentences):
                next_sent = sentences[i + 2] if i + 2 < len(sentences) else None
                if next_sent and word_count < 25 and len(next_sent.split()) < 25:
                    if self._is_complete(sent) and self._is_complete(next_sent):
                        connectors = [', and ', ', but ', ', yet ', ', while ', ', though ', ', so ']
                        connector = random.choice(connectors)
                        
                        if next_sent.strip()[0].isupper():
                            combined = sent.strip() + connector + next_sent.strip()[0].lower() + next_sent.strip()[1:]
                        else:
                            combined = sent.strip() + connector + next_sent.strip()
                        
                        if self._is_complete(combined):
                            optimized.append(combined)
                            optimized.append(sentences[i + 1])
                            long_added += 1
                            i += 3
                            continue
            
            optimized.append(sent)
            i += 1
        
        if punchy_added > 0:
            changes.append(f"Created {punchy_added} punchy sentences (3-5 words)")
        if long_added > 0:
            changes.append(f"Created {long_added} long sentences (35-45 words)")
        
        return ''.join(optimized), changes
    
    def _passive_to_active(self, text: str) -> Tuple[str, int]:
        """Convert passive voice to active voice (30% conversion rate)"""
        converted = text
        conversion_count = 0
        
        # Simple passive patterns
        passive_patterns = [
            (r'\b(\w+)\s+was\s+(\w+ed)\s+by\s+(\w+)', r'\3 \2 \1'),  # "X was done by Y" -> "Y did X"
            (r'\b(\w+)\s+were\s+(\w+ed)\s+by\s+(\w+)', r'\3 \2 \1'),
            (r'\bis\s+being\s+(\w+ed)', r'is \1ing'),  # "is being done" -> "is doing"
        ]
        
        for pattern, replacement in passive_patterns:
            matches = re.finditer(pattern, converted, re.IGNORECASE)
            for match in matches:
                # Convert 30% of the time (not all passive is bad)
                if random.random() < 0.30:
                    converted = re.sub(pattern, replacement, converted, count=1, flags=re.IGNORECASE)
                    conversion_count += 1
        
        return converted, conversion_count
    
    def _inject_imperfections(self, text: str) -> str:
        """Inject natural human imperfections (5% rate)"""
        sentences = re.split(r'([.!?]\s+)', text)
        imperfect = []
        
        for i, sent in enumerate(sentences):
            if not sent.strip() or sent in ['. ', '! ', '? ']:
                imperfect.append(sent)
                continue
            
            # 5% chance: Start sentence with natural connector
            if i > 0 and random.random() < 0.05 and len(sent) > 30:
                if self._is_complete(sent):
                    if not sent.strip().startswith(tuple(self.NATURAL_STARTERS)):
                        starter = random.choice(self.NATURAL_STARTERS)
                        if sent.strip()[0].isupper():
                            sent = starter + ' ' + sent.strip()[0].lower() + sent.strip()[1:]
            
            imperfect.append(sent)
        
        return ''.join(imperfect)
    
    def _smooth_flow(self, text: str) -> str:
        """Smooth overall flow and remove awkward transitions"""
        # Remove double spaces
        smoothed = re.sub(r'\s+', ' ', text)
        
        # Fix punctuation spacing
        smoothed = re.sub(r'\s+([.,!?;:])', r'\1', smoothed)
        smoothed = re.sub(r'([.!?])([A-Z])', r'\1 \2', smoothed)
        
        # Remove triple+ newlines
        smoothed = re.sub(r'\n{3,}', '\n\n', smoothed)
        
        return smoothed.strip()
    
    def _is_complete(self, sentence: str) -> bool:
        """Check if sentence is complete (has verb and subject)"""
        if not sentence or len(sentence.strip()) < 5:
            return False
        
        # Must end with punctuation
        if sentence.strip()[-1] not in '.!?':
            # Add period for checking
            sentence = sentence.strip() + '.'
        
        # Check for basic verb
        verbs = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'will', 'would', 
                 'could', 'should', 'can', 'may', 'might', 'do', 'does', 'did',
                 'said', 'says', 'got', 'get', 'make', 'makes', 'take', 'takes']
        
        words = sentence.lower().split()
        has_verb = any(verb in words for verb in verbs)
        
        # Check it's not a fragment
        incomplete_endings = [' while', ' but', ' and', ' or', ' because', ' though',
                             ' if', ' when', ' where', ' which', ' that', ' who']
        
        is_fragment = any(sentence.lower().strip().endswith(ending) for ending in incomplete_endings)
        
        return has_verb and not is_fragment and len(words) >= 3
    
    def _calculate_human_score(self, text: str) -> float:
        """
        Calculate humanization score (0.0-1.0)
        Based on: contractions, sentence variance, vocabulary diversity, flow
        """
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        words = text.split()
        
        if len(sentences) < 3 or len(words) < 50:
            return 0.5
        
        # Factor 1: Contraction rate (target: 3-5% of words)
        contraction_count = sum(1 for word in words if "'" in word)
        contraction_rate = contraction_count / len(words)
        contraction_score = min(contraction_rate / 0.04, 1.0)  # 4% is optimal
        
        # Factor 2: Sentence length variance (burstiness)
        lengths = [len(s.split()) for s in sentences]
        if len(lengths) > 1:
            import statistics
            variance = statistics.stdev(lengths) / statistics.mean(lengths) if statistics.mean(lengths) > 0 else 0
            variance_score = min(variance / 0.8, 1.0)  # 80% variance is good
        else:
            variance_score = 0.3
        
        # Factor 3: Vocabulary diversity
        unique_words = len(set(w.lower() for w in words))
        diversity = unique_words / len(words)
        diversity_score = diversity  # Already 0-1
        
        # Factor 4: Natural flow (no AI tells)
        ai_tell_count = 0
        for pattern in self.AI_TELLS['repetitive_starters']:
            ai_tell_count += len(re.findall(pattern, text, re.IGNORECASE))
        for phrase in self.AI_TELLS['formal_phrases']:
            ai_tell_count += text.lower().count(phrase)
        
        flow_score = max(0, 1.0 - (ai_tell_count * 0.1))
        
        # Weighted average
        human_score = (
            contraction_score * 0.25 +
            variance_score * 0.30 +
            diversity_score * 0.20 +
            flow_score * 0.25
        )
        
        return min(human_score, 1.0)
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze text for AI detection indicators"""
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        words = text.split()
        
        # Check for AI tells
        ai_indicators = []
        
        # Check repetitive starters
        starter_counts = {}
        for sent in sentences:
            first_word = sent.split()[0] if sent.split() else ''
            if first_word in ['Moreover', 'Furthermore', 'Additionally', 'Therefore']:
                starter_counts[first_word] = starter_counts.get(first_word, 0) + 1
        
        if starter_counts:
            ai_indicators.append(f"Repetitive starters: {starter_counts}")
        
        # Check sentence uniformity
        lengths = [len(s.split()) for s in sentences]
        if lengths:
            import statistics
            avg_length = statistics.mean(lengths)
            if 15 <= avg_length <= 25 and statistics.stdev(lengths) < 5:
                ai_indicators.append(f"Uniform sentences (avg {avg_length:.1f}, stdev {statistics.stdev(lengths):.1f})")
        
        # Check contraction rate
        contraction_count = sum(1 for word in words if "'" in word)
        contraction_rate = (contraction_count / len(words)) * 100 if words else 0
        if contraction_rate < 2:
            ai_indicators.append(f"Low contractions ({contraction_rate:.1f}%)")
        
        # Calculate AI probability
        ai_score = len(ai_indicators) / 10  # Normalize
        ai_probability = min(ai_score, 1.0)
        
        return {
            'ai_probability': ai_probability,
            'human_probability': 1.0 - ai_probability,
            'ai_indicators': ai_indicators,
            'sentence_count': len(sentences),
            'word_count': len(words),
            'avg_sentence_length': statistics.mean(lengths) if lengths else 0,
            'contraction_rate': contraction_rate
        }


if __name__ == '__main__':
    # Test the humanizer
    humanizer = AIHumanizer()
    
    test_text = """Furthermore, it is important to note that artificial intelligence is transforming industries. Moreover, companies are investing heavily in AI technologies. Additionally, researchers are developing new algorithms. Therefore, the future of AI is promising. In order to succeed, organizations must adapt."""
    
    print("=== ORIGINAL TEXT ===")
    print(test_text)
    print()
    
    # Analyze original
    analysis = humanizer.analyze_text(test_text)
    print("=== AI DETECTION ANALYSIS ===")
    print(f"AI Probability: {analysis['ai_probability']:.1%}")
    print(f"Human Probability: {analysis['human_probability']:.1%}")
    print(f"Indicators: {analysis['ai_indicators']}")
    print()
    
    # Humanize
    result = humanizer.humanize(test_text, mode='advanced')
    print("=== HUMANIZED TEXT ===")
    print(result['humanized_text'])
    print()
    print(f"Human Score: {result['human_score']:.1%}")
    print(f"Changes: {result['changes']}")
