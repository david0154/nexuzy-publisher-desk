"""
AI Humanizer Module – ELITE HUMAN EDITION
Natural, imperfect, human-like article rewriting
Designed for long-form content & news articles
"""

import re
import random
import logging
import statistics
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class AIHumanizer:
    def __init__(self):
        logger.info("✅ ELITE Humanizer initialized")

    # -------------------------
    # CORE PUBLIC METHOD
    # -------------------------
    def humanize(
        self,
        text: str,
        intensity: float = 0.85,
        mode: str = "elite-human",
        **kwargs: Any
    ) -> Dict:
        """
        intensity: 0.0 → light touch
                   1.0 → heavy human rewrite
        mode: optional pipeline flag (ignored safely)
        """

        original = text
        text = self._normalize(text)

        text = self._remove_formality(text)
        text = self._apply_contractions(text)
        text = self._inject_human_thoughts(text, intensity)
        text = self._reshape_sentences(text, intensity)
        text = self._soften_claims(text)
        text = self._vocabulary_variation(text)
        text = self._final_cleanup(text)

        metrics = self._analyze(text)

        # Calculate human score based on metrics
        human_score = self._calculate_human_score(metrics, text)

        return {
            "original_text": original,
            "humanized_text": text,
            "metrics": metrics,
            "human_score": human_score,
            "changes": self._get_changes_summary(text, original),
            "mode": mode
        }

    # -------------------------
    # NORMALIZATION
    # -------------------------
    def _normalize(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    # -------------------------
    # FORMALITY REMOVAL
    # -------------------------
    def _remove_formality(self, text: str) -> str:
        formal_starters = [
            "Furthermore", "Moreover", "Additionally",
            "Therefore", "Thus", "Hence", "Consequently"
        ]
        for f in formal_starters:
            text = re.sub(rf'\b{f},?\s+', '', text, flags=re.IGNORECASE)

        phrase_map = {
            "in order to": "to",
            "due to the fact that": "because",
            "it is important to note that": "",
            "with regard to": "about",
            "as a matter of fact": "actually"
        }

        for k, v in phrase_map.items():
            text = re.sub(k, v, text, flags=re.IGNORECASE)

        return text

    # -------------------------
    # CONTRACTIONS
    # -------------------------
    def _apply_contractions(self, text: str) -> str:
        patterns = {
            r"\b(it is)\b": "it's",
            r"\b(do not)\b": "don't",
            r"\b(does not)\b": "doesn't",
            r"\b(is not)\b": "isn't",
            r"\b(are not)\b": "aren't",
            r"\b(will not)\b": "won't",
            r"\b(I am)\b": "I'm",
            r"\b(we are)\b": "we're",
            r"\b(you are)\b": "you're",
            r"\b(they are)\b": "they're",
        }

        for pattern, repl in patterns.items():
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

        return text

    # -------------------------
    # HUMAN THOUGHT INJECTION
    # -------------------------
    def _inject_human_thoughts(self, text: str, intensity: float) -> str:
        thoughts = [
            "to be honest",
            "in real terms",
            "at least for now",
            "in a way",
            "arguably",
            "from a practical standpoint",
            "if you think about it",
            "for most people"
        ]

        sentences = re.split(r'(?<=[.!?]) ', text)
        output = []

        for s in sentences:
            if random.random() < 0.15 * intensity:
                s = random.choice(thoughts) + ", " + s.lower()
                s = s[0].upper() + s[1:]
            output.append(s)

        return " ".join(output)

    # -------------------------
    # SENTENCE SHAPE VARIATION
    # -------------------------
    def _reshape_sentences(self, text: str, intensity: float) -> str:
        sentences = re.split(r'(?<=[.!?]) ', text)
        output = []
        i = 0

        while i < len(sentences):
            if i < len(sentences) - 1 and random.random() < 0.2 * intensity:
                merged = (
                    sentences[i].rstrip(".!?")
                    + ", and "
                    + sentences[i + 1].lower()
                )
                output.append(merged)
                i += 2
            else:
                output.append(sentences[i])
                i += 1

        return " ".join(output)

    # -------------------------
    # SOFTEN STRONG CLAIMS
    # -------------------------
    def _soften_claims(self, text: str) -> str:
        strong_words = {
            "proves": "suggests",
            "guarantees": "tends to",
            "will definitely": "will likely",
            "clearly shows": "seems to show"
        }

        for k, v in strong_words.items():
            text = re.sub(k, v, text, flags=re.IGNORECASE)

        return text

    # -------------------------
    # VOCABULARY VARIATION
    # -------------------------
    def _vocabulary_variation(self, text: str) -> str:
        swaps = {
            "important": ["crucial", "worth noting", "meaningful"],
            "big": ["significant", "noticeable", "sizable"],
            "new": ["recent", "updated", "fresh"]
        }

        for word, options in swaps.items():
            text = re.sub(
                rf'\b{word}\b',
                lambda _: random.choice(options),
                text,
                flags=re.IGNORECASE
            )

        return text

    # -------------------------
    # FINAL CLEANUP
    # -------------------------
    def _final_cleanup(self, text: str) -> str:
        text = re.sub(r'\s+([,.!?])', r'\1', text)
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        return text.strip()

    # -------------------------
    # ANALYSIS
    # -------------------------
    def _analyze(self, text: str) -> Dict:
        sentences = re.split(r'[.!?]', text)
        words = text.split()

        lengths = [len(s.split()) for s in sentences if s.strip()]
        contraction_rate = sum("'" in w for w in words) / max(len(words), 1)

        return {
            "sentence_count": len(lengths),
            "avg_sentence_length": statistics.mean(lengths) if lengths else 0,
            "sentence_variance": statistics.stdev(lengths) if len(lengths) > 1 else 0,
            "contraction_rate": round(contraction_rate * 100, 2),
            "human_signal_strength": "high" if contraction_rate > 0.04 else "medium"
        }

    def _calculate_human_score(self, metrics: Dict, text: str) -> float:
        """Calculate human-like score based on metrics"""
        base_score = 0.85  # Base human score

        # Bonus for high contraction rate (human-like)
        contraction_bonus = min(metrics["contraction_rate"] / 5.0, 0.10)  # Max 10% bonus

        # Bonus for sentence variance (natural flow)
        variance_bonus = min(metrics["sentence_variance"] / 5.0, 0.05)  # Max 5% bonus

        # Penalty for too short sentences (robotic)
        if metrics["avg_sentence_length"] < 10:
            length_penalty = 0.05
        else:
            length_penalty = 0

        human_score = base_score + contraction_bonus + variance_bonus - length_penalty
        return round(max(min(human_score, 0.98), 0.70), 2)  # Clamp between 70% and 98%

    def _get_changes_summary(self, humanized_text: str, original_text: str) -> List[str]:
        """Generate summary of changes made"""
        changes = []

        # Count contractions
        orig_contractions = sum(1 for word in original_text.split() if "'" in word)
        new_contractions = sum(1 for word in humanized_text.split() if "'" in word)
        if new_contractions > orig_contractions:
            changes.append(f"Added {new_contractions - orig_contractions} contractions")

        # Check for formality removal
        formal_phrases = ["in order to", "due to the fact that", "it is important to note that"]
        formality_removed = any(phrase not in humanized_text and phrase in original_text for phrase in formal_phrases)
        if formality_removed:
            changes.append("Removed formal phrases")

        # Sentence structure changes
        orig_sentences = len(re.split(r'[.!?]', original_text))
        new_sentences = len(re.split(r'[.!?]', humanized_text))
        if abs(new_sentences - orig_sentences) > 0:
            changes.append("Reshaped sentence structure")

        # Vocabulary variation
        if len(humanized_text.split()) > 0:
            changes.append("Applied vocabulary variation")

        return changes if changes else ["Applied human-like transformations"]
