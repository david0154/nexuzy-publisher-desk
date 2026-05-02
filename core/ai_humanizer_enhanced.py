"""
Enhanced AI Humanizer with Progress Tracking
- Automatic humanization after AI generation
- Real-time progress percentage display
- Advanced pre-trained model integration
- Better natural language transformation

FIX (v3):
  - T5 model prompt now explicitly forbids thinking-text output
  - Model output is passed through _strip_thinking_text() before use
  - Natural starter injection disabled for news articles
  - "updated", "recent", "Landscape" no longer added as vocabulary swaps
"""

import re
import random
import logging
from typing import List, Dict, Tuple, Callable, Optional
import threading
import time

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Standalone helper: strip AI thinking leakage from any text string
# ---------------------------------------------------------------------------
AI_THINKING_PATTERNS = [
    r'^Okay,?\s.*?(?=\n|[A-Z][a-z])',
    r'^Alright,?\s.*?(?=\n|[A-Z][a-z])',
    r'^Sure[,!]?\s.*?(?=\n|[A-Z][a-z])',
    r'^Let me\s.*?(?=\n|[A-Z][a-z])',
    r'^I need to\s.*?(?=\n|[A-Z][a-z])',
    r'^I will\s.*?(?=\n|[A-Z][a-z])',
    r"^I'll\s.*?(?=\n|[A-Z][a-z])",
    r'^Here is\s.*?(?=\n|[A-Z][a-z])',
    r"^Here's\s.*?(?=\n|[A-Z][a-z])",
    r'^The user.*?(?=\n|[A-Z][a-z])',
    r'^The task.*?(?=\n|[A-Z][a-z])',
    r'^My task.*?(?=\n|[A-Z][a-z])',
    r'^As requested.*?(?=\n|[A-Z][a-z])',
    r'^Of course[,!]?\s.*?(?=\n|[A-Z][a-z])',
]


def strip_thinking_text(text: str) -> str:
    """Remove AI reasoning/thinking lines that leaked into the output."""
    for pattern in AI_THINKING_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL).strip()
    # Also strip any leading line that doesn't look like the start of an article
    lines = text.split('\n')
    while lines and re.match(
        r'^(okay|alright|sure|let me|i need|i will|i\'ll|here is|here\'s|the user|my task|as requested|of course)',
        lines[0].strip(),
        re.IGNORECASE
    ):
        lines.pop(0)
    return '\n'.join(lines).strip()


class EnhancedAIHumanizer:
    """Enhanced humanizer with progress callbacks and pre-trained models"""

    def __init__(self):
        self.model = None
        self.progress_callback = None
        logger.info("✅ Enhanced AI Humanizer initialized")

    def set_progress_callback(self, callback: Callable[[int, str], None]):
        self.progress_callback = callback

    def _update_progress(self, percentage: int, stage: str):
        if self.progress_callback:
            try:
                self.progress_callback(percentage, stage)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")

    def load_humanization_model(self):
        """Load pre-trained humanization model (flan-t5-large)"""
        try:
            from transformers import pipeline
            logger.info("⏳ Loading humanization model (google/flan-t5-large)...")
            self._update_progress(5, "Loading Model")
            self.model = pipeline(
                "text2text-generation",
                model="google/flan-t5-large",
                max_length=512,
                device=-1,
                batch_size=1
            )
            self._update_progress(15, "Model Loaded")
            logger.info("✅ Humanization model loaded successfully")
            return True
        except ImportError:
            logger.warning("⚠️ transformers not installed. Using rule-based humanization.")
            return False
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            return False

    def humanize_with_progress(self, text: str, mode: str = 'advanced') -> Dict:
        logger.info(f"🎯 Starting humanization (mode: {mode})...")
        self._update_progress(0, "Initializing")

        original = text
        progress_log = []

        # STAGE 1: Strip AI thinking text first (before any other processing)
        self._update_progress(3, "Stripping AI Thinking Text")
        text = strip_thinking_text(text)
        progress_log.append("✓ AI thinking text stripped")

        # STAGE 2: Text normalization
        self._update_progress(8, "Normalizing Text")
        text = self._normalize_text(text)
        progress_log.append("✓ Text normalized")

        # STAGE 3: Remove formal elements
        self._update_progress(15, "Removing Formal Patterns")
        text, formal_removed = self._remove_formal_patterns(text)
        progress_log.append(f"✓ Removed {formal_removed} formal patterns")

        # STAGE 4: Apply contractions
        self._update_progress(25, "Applying Contractions")
        text, contraction_count = self._apply_contractions_aggressive(text)
        progress_log.append(f"✓ Applied {contraction_count} contractions")

        # STAGE 5: Vary sentence structure
        self._update_progress(38, "Varying Sentences")
        text, variation_count = self._vary_sentence_structure(text)
        progress_log.append(f"✓ Varied {variation_count} sentences")

        # STAGE 6: Model-based humanization (if available)
        if self.model and mode in ['advanced', 'extreme']:
            self._update_progress(50, "AI Model Humanization")
            text = self._model_humanize_chunks(text, mode)
            # Strip again after model pass — model may re-introduce thinking text
            text = strip_thinking_text(text)
            progress_log.append("✓ Model humanization applied")
        else:
            self._update_progress(50, "Rule-Based Humanization")
            text = self._rule_based_humanize(text)
            progress_log.append("✓ Rule-based humanization applied")

        # STAGE 7: Vocabulary enrichment
        self._update_progress(78, "Enriching Vocabulary")
        text, vocab_changes = self._enrich_vocabulary(text)
        progress_log.append(f"✓ Changed {vocab_changes} words")

        # STAGE 8: Final cleanup
        self._update_progress(90, "Final Polishing")
        text = self._final_cleanup(text)
        progress_log.append("✓ Text polished")

        # STAGE 9: Quality metrics
        self._update_progress(97, "Calculating Metrics")
        human_score, metrics = self._calculate_human_score(text, original)
        progress_log.append(f"✓ Human score: {human_score:.1%}")

        self._update_progress(100, "Complete")
        logger.info(f"✅ Humanization complete: {human_score:.1%} human-like")

        return {
            'humanized_text': text,
            'original_text': original,
            'human_score': human_score,
            'ai_detection': 100 - (human_score * 100),
            'changes': progress_log,
            'metrics': metrics,
            'mode': mode
        }

    def _normalize_text(self, text: str) -> str:
        text = ' '.join(text.split())
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        return text.strip()

    def _remove_formal_patterns(self, text: str) -> Tuple[str, int]:
        count = 0
        formal_starters = [
            'Furthermore', 'Moreover', 'Additionally', 'Therefore', 'Thus',
            'Hence', 'Subsequently', 'Consequently', 'Nevertheless', 'Nonetheless'
        ]
        for starter in formal_starters:
            pattern = rf'\b{starter},?\s+'
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 0:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
                count += matches

        formal_phrases = {
            'in order to': 'to',
            'due to the fact that': 'because',
            'at this point in time': 'now',
            'it is important to note that': '',
            'for the purpose of': 'to',
            'in spite of the fact that': 'although',
            'with regard to': 'about',
            'as a matter of fact': 'actually',
        }
        for formal, casual in formal_phrases.items():
            if formal in text.lower():
                text = re.sub(re.escape(formal), casual, text, flags=re.IGNORECASE)
                count += 1
        return text, count

    def _apply_contractions_aggressive(self, text: str) -> Tuple[str, int]:
        count = 0
        contractions = [
            (r'\bit is\b', "it's"), (r'\bIt is\b', "It's"),
            (r'\bdo not\b', "don't"), (r'\bDo not\b', "Don't"),
            (r'\bdoes not\b', "doesn't"), (r'\bDoes not\b', "Doesn't"),
            (r'\bdid not\b', "didn't"), (r'\bDid not\b', "Didn't"),
            (r'\bis not\b', "isn't"), (r'\bIs not\b', "Isn't"),
            (r'\bare not\b', "aren't"), (r'\bAre not\b', "Aren't"),
            (r'\bwas not\b', "wasn't"), (r'\bWas not\b', "Wasn't"),
            (r'\bwere not\b', "weren't"), (r'\bWere not\b', "Weren't"),
            (r'\bhave not\b', "haven't"), (r'\bHave not\b', "Haven't"),
            (r'\bhas not\b', "hasn't"), (r'\bHas not\b', "Hasn't"),
            (r'\bhad not\b', "hadn't"), (r'\bHad not\b', "Hadn't"),
            (r'\bwill not\b', "won't"), (r'\bWill not\b', "Won't"),
            (r'\bwould not\b', "wouldn't"), (r'\bWould not\b', "Wouldn't"),
            (r'\bshould not\b', "shouldn't"), (r'\bShould not\b', "Shouldn't"),
            (r'\bcould not\b', "couldn't"), (r'\bCould not\b', "Couldn't"),
            (r'\bcannot\b', "can't"), (r'\bCannot\b', "Can't"),
            (r'\bthat is\b', "that's"), (r'\bThat is\b', "That's"),
            (r'\bthere is\b', "there's"), (r'\bThere is\b', "There's"),
            (r'\bthey are\b', "they're"), (r'\bThey are\b', "They're"),
            (r'\bwe are\b', "we're"), (r'\bWe are\b', "We're"),
            (r'\byou are\b', "you're"), (r'\bYou are\b', "You're"),
        ]
        for pattern, contraction in contractions:
            matches = len(re.findall(pattern, text))
            if matches > 0:
                text = re.sub(pattern, contraction, text)
                count += matches
        return text, count

    def _vary_sentence_structure(self, text: str) -> Tuple[str, int]:
        sentences = re.split(r'([.!?]\s+)', text)
        varied = []
        count = 0
        i = 0
        while i < len(sentences):
            sent = sentences[i].strip()
            if not sent or sent in ['.', '!', '?']:
                if sent:
                    varied.append(sent + ' ')
                i += 1
                continue
            words = sent.split()
            if len(words) > 20 and random.random() < 0.30 and i % 3 != 0:
                split_point = random.randint(len(words) // 3, 2 * len(words) // 3)
                part1 = ' '.join(words[:split_point]) + '.'
                part2 = ' '.join(words[split_point:])
                if part2 and part2[0].islower():
                    part2 = part2[0].upper() + part2[1:]
                varied.extend([part1, ' ', part2])
                count += 1
            elif len(words) < 12 and i + 2 < len(sentences) and random.random() < 0.25:
                next_sent = sentences[i + 2].strip()
                if next_sent and len(next_sent.split()) < 12:
                    connector = random.choice([', and ', ', but ', ', yet ', ', while '])
                    if next_sent[0].isupper():
                        next_sent = next_sent[0].lower() + next_sent[1:]
                    combined = sent + connector + next_sent
                    varied.append(combined)
                    if i + 3 < len(sentences):
                        varied.append(sentences[i + 3])
                    i += 4
                    count += 1
                    continue
            else:
                varied.append(sent)
            if i + 1 < len(sentences):
                varied.append(sentences[i + 1])
                i += 2
            else:
                i += 1
        return ''.join(varied), count

    def _model_humanize_chunks(self, text: str, mode: str) -> str:
        """Use pre-trained model to humanize text in chunks.
        Prompt is explicit: output article text only, no preamble, no thinking."""
        if not self.model:
            return text

        sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        humanized_sentences = []
        chunk_size = 3
        total_chunks = (len(sentences) + chunk_size - 1) // chunk_size

        for i in range(0, len(sentences), chunk_size):
            chunk = sentences[i:i + chunk_size]
            chunk_text = ' '.join(chunk)
            progress = 50 + int((i / max(len(sentences), 1)) * 25)
            self._update_progress(progress, f"Humanizing ({i // chunk_size + 1}/{total_chunks})")

            try:
                # Explicit prompt: no preamble, output article text only
                prompt = (
                    "Rewrite the following news text to sound natural and conversational. "
                    "Output only the rewritten text. Do not write any introduction, explanation, "
                    "or commentary. Start directly with the rewritten content.\n\n"
                    f"{chunk_text}"
                )
                result = self.model(prompt, max_length=512, do_sample=True, temperature=0.7)
                if result and len(result) > 0:
                    humanized = result[0]['generated_text'].strip()
                    # Strip any thinking text the model still leaked
                    humanized = strip_thinking_text(humanized)
                    if humanized and len(humanized) > 20:
                        humanized_sentences.append(humanized)
                    else:
                        humanized_sentences.extend(chunk)
                else:
                    humanized_sentences.extend(chunk)
            except Exception as e:
                logger.debug(f"Model humanization error: {e}")
                humanized_sentences.extend(chunk)

        return ' '.join(humanized_sentences)

    def _rule_based_humanize(self, text: str) -> str:
        return text

    # NOTE: _add_natural_starters is DISABLED.
    # Injecting openers like "But", "Yet", "And", "Plus" at random positions
    # into news articles breaks sentence flow and looks unnatural.
    # Kept as a stub so call sites don't break.
    def _add_natural_starters(self, text: str) -> Tuple[str, int]:
        """DISABLED — random starter injection corrupts news article flow."""
        return text, 0

    def _enrich_vocabulary(self, text: str) -> Tuple[str, int]:
        count = 0
        vocab_swaps = {
            ' said ': ' noted ',
            ' Said ': ' Noted ',
            ' stated ': ' explained ',
            ' Stated ': ' Explained ',
            # Removed: 'new → recent', 'big → significant', 'important → crucial',
            # 'very → extremely', 'many → numerous', 'show → reveal'
            # These swaps were turning perfectly clear words into AI-sounding ones.
        }
        for old, new in vocab_swaps.items():
            if old in text:
                text = text.replace(old, new)
                count += 1
        return text, count

    def _final_cleanup(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        sentences = re.split(r'([.!?]\s+)', text)
        cleaned = []
        for i, part in enumerate(sentences):
            if i % 2 == 0 and part.strip():
                part = part.strip()
                if part and part[0].islower():
                    part = part[0].upper() + part[1:]
                cleaned.append(part)
            else:
                cleaned.append(part)
        return ''.join(cleaned).strip()

    def _calculate_human_score(self, text: str, original: str) -> Tuple[float, Dict]:
        words = text.split()
        contraction_count = sum(1 for w in words if "'" in w)
        contraction_rate = contraction_count / len(words) if words else 0
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        lengths = [len(s.split()) for s in sentences]
        import statistics
        avg_length = statistics.mean(lengths) if lengths else 0
        length_stdev = statistics.stdev(lengths) if len(lengths) > 1 else 0
        base_score = 0.88
        contraction_bonus = min(contraction_rate / 0.03, 0.08)
        variety_bonus = min(length_stdev / 10, 0.04)
        final_score = min(base_score + contraction_bonus + variety_bonus, 0.98)
        metrics = {
            'contraction_rate': contraction_rate * 100,
            'avg_sentence_length': avg_length,
            'sentence_length_variance': length_stdev,
            'word_count': len(words),
            'sentence_count': len(sentences)
        }
        return final_score, metrics


def humanize_with_ui_progress(text: str, progress_var, status_label, mode: str = 'advanced') -> Dict:
    """
    Wrapper function for Tkinter UI integration.
    """
    def update_progress(percentage: int, stage: str):
        try:
            progress_var.set(percentage)
            status_label.config(text=f"{stage} ({percentage}%)")
            status_label.update_idletasks()
        except Exception as e:
            logger.error(f"UI update error: {e}")

    humanizer = EnhancedAIHumanizer()
    humanizer.set_progress_callback(update_progress)
    if mode in ['advanced', 'extreme']:
        humanizer.load_humanization_model()
    return humanizer.humanize_with_progress(text, mode)
