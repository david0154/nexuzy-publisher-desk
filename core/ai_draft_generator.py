""" 
AI Draft Generation Module - HUMAN-LIKE ARTICLES
Generates articles that bypass AI detectors (under 5% AI detection)

FEATURES:
✅ 450-2500 word flexible articles
✅ 95%+ human-like writing (sentence model integration)
✅ ULTRA-HIGH CONTRACTIONS (92% rate - human-level)
✅ EXTREME sentence length variation (burstiness)
✅ Natural conversational tone
✅ Unpredictable flow patterns
✅ Grammar checking with natural style
✅ Anti-AI-detection techniques
✅ Pre-writing angle selection
✅ Neutral tone enforcement
✅ Anti-plagiarism system
✅ Title uniqueness checking
✅ Research writer integration
✅ Local image download with watermark detection
✅ Clean output (no section headers)
✅ Retry logic for short articles
✅ Fragment validation + sentence improvement
✅ Proper sentence model error handling
✅ AI Humanizer integration (QuillBot-inspired 7-pass refinement)
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import random
import re
from datetime import datetime, timedelta
import json
import requests
from io import BytesIO
import os
import sys
import hashlib
from core.ai_humanizer import AIHumanizer

logger = logging.getLogger(__name__)

# GLOBAL MODEL CACHE - shared between AI Writer and Research Writer
_CACHED_MODEL = None
_CACHED_SENTENCE_MODEL = None
_GRAMMAR_CHECKER = None

# Enhanced synonym dictionary for uniqueness
SYNONYM_DICT = {
    'said': ['stated', 'mentioned', 'noted', 'explained', 'announced', 'revealed', 'reported', 'disclosed', 'expressed', 'conveyed', 'declared', 'affirmed', 'remarked'],
    'new': ['recent', 'latest', 'fresh', 'novel', 'emerging', 'modern', 'contemporary', 'current', 'up-to-date', 'innovative', 'groundbreaking'],
    'big': ['significant', 'substantial', 'considerable', 'major', 'large-scale', 'extensive', 'sizeable', 'massive', 'prominent', 'notable'],
    'important': ['crucial', 'vital', 'essential', 'critical', 'key', 'significant', 'pivotal', 'paramount', 'fundamental', 'pressing', 'imperative'],
    'show': ['demonstrate', 'illustrate', 'reveal', 'indicate', 'display', 'exhibit', 'present', 'showcase', 'reflect', 'manifest'],
    'many': ['numerous', 'multiple', 'several', 'various', 'countless', 'myriad', 'abundant', 'plentiful', 'manifold'],
    'good': ['positive', 'beneficial', 'favorable', 'advantageous', 'promising', 'valuable', 'constructive', 'productive', 'fruitful'],
    'bad': ['negative', 'adverse', 'unfavorable', 'detrimental', 'problematic', 'harmful', 'damaging', 'troublesome', 'concerning'],
    'make': ['create', 'produce', 'generate', 'develop', 'establish', 'form', 'construct', 'build', 'forge', 'craft'],
    'use': ['utilize', 'employ', 'apply', 'leverage', 'implement', 'adopt', 'deploy', 'harness', 'incorporate'],
    'get': ['obtain', 'acquire', 'receive', 'secure', 'gain', 'attain', 'procure', 'achieve', 'derive'],
    'very': ['extremely', 'highly', 'particularly', 'exceptionally', 'remarkably', 'significantly', 'notably', 'especially'],
    'problem': ['issue', 'challenge', 'concern', 'difficulty', 'complication', 'obstacle', 'hurdle', 'dilemma'],
    'change': ['transform', 'modify', 'alter', 'adjust', 'revise', 'adapt', 'evolve', 'shift', 'reshape'],
    'help': ['assist', 'aid', 'support', 'facilitate', 'contribute to', 'enable', 'empower', 'bolster'],
    'think': ['believe', 'consider', 'suggest', 'indicate', 'propose', 'maintain', 'posit', 'contend'],
    'see': ['observe', 'notice', 'witness', 'recognize', 'identify', 'detect', 'perceive', 'discern'],
    'know': ['understand', 'recognize', 'acknowledge', 'realize', 'comprehend', 'grasp'],
    'want': ['desire', 'seek', 'aim for', 'pursue', 'strive for', 'aspire to', 'yearn for'],
    'need': ['require', 'necessitate', 'demand', 'call for', 'warrant', 'entail'],
    'look': ['appear', 'seem', 'indicate', 'suggest', 'signal', 'point to'],
    'find': ['discover', 'uncover', 'identify', 'determine', 'ascertain', 'locate'],
    'give': ['provide', 'offer', 'supply', 'deliver', 'furnish', 'grant', 'bestow'],
    'tell': ['inform', 'notify', 'advise', 'communicate', 'convey', 'relay'],
    'work': ['function', 'operate', 'perform', 'serve', 'act', 'execute'],
    'call': ['designate', 'term', 'label', 'refer to', 'name', 'dub'],
    'try': ['attempt', 'endeavor', 'strive', 'seek', 'aim', 'undertake'],
    'ask': ['inquire', 'question', 'query', 'request', 'seek information'],
    'feel': ['sense', 'experience', 'perceive', 'detect', 'recognize'],
    'become': ['turn into', 'evolve into', 'transform into', 'develop into'],
    'leave': ['depart', 'exit', 'withdraw', 'abandon', 'vacate'],
    'put': ['place', 'position', 'set', 'situate', 'locate', 'install'],
    'however': ['but', 'yet', 'still', 'though', 'although'],
    'therefore': ['so', 'thus', 'hence', 'consequently'],
    'additionally': ['also', 'plus', 'and', 'furthermore'],
    'moreover': ['also', 'besides', 'what\'s more', 'on top of that'],
    'furthermore': ['besides', 'also', 'plus', 'what\'s more'],
}

# Neutral title templates (avoiding sensationalism)
NEUTRAL_TITLE_PATTERNS = [
    "{topic}: Analysis and Key Details",
    "{topic}: What to Know About Recent Developments",
    "{topic}: Overview of Current Situation",
    "Understanding {topic}: Facts and Context",
    "{topic}: Recent Updates and Information",
    "{topic}: Examining the Details",
    "{topic}: Current Status and Background",
    "{topic}: Key Points and Analysis",
    "{topic}: Developments and Implications",
    "{topic}: A Factual Review",
]

# Article angles for pre-writing step
ARTICLE_ANGLES = {
    'impact': 'Focus on the direct and indirect consequences for stakeholders',
    'analysis': 'Provide analytical breakdown of the situation with data and context',
    'public_reaction': 'Examine how different groups and communities are responding',
    'policy': 'Analyze policy implications and regulatory considerations',
    'symbolism': 'Explore the broader symbolic meaning and cultural significance',
    'expert': 'Present expert interpretations and professional perspectives'
}

class DraftGenerator:
    """Generate HUMAN-LIKE AI-rewritten articles (450-2500 words, 95%+ human score)"""
    
    def __init__(self, db_path: str, model_name: str = 'models/mistral-7b-instruct-v0.2.Q4_K_M.gguf'):
        global _CACHED_MODEL, _CACHED_SENTENCE_MODEL, _GRAMMAR_CHECKER
        
        self.db_path = db_path
        self.model_name = model_name
        self.model_file = Path(model_name).name
        self.translation_keywords = self._load_translation_keywords()
        
        # Use GLOBAL cached model (shared with Research Writer)
        if _CACHED_MODEL:
            logger.info("✅ Using GLOBAL cached AI model (shared with Research Writer)")
            self.llm = _CACHED_MODEL
        else:
            logger.info("⏳ Loading AI model for BOTH AI Writer and Research Writer...")
            self.llm = self._load_model()
            if self.llm:
                _CACHED_MODEL = self.llm
                logger.info("💾 Model cached GLOBALLY for AI Writer + Research Writer")
        
        # 🔥 LOAD SENTENCE MODEL for human-like accuracy
        if _CACHED_SENTENCE_MODEL:
            logger.info("✅ Using GLOBAL cached Sentence Model")
            self.sentence_model = _CACHED_SENTENCE_MODEL
        else:
            logger.info("⏳ Loading Sentence Model for human-like refinement...")
            self.sentence_model = self._load_sentence_model()
            if self.sentence_model:
                _CACHED_SENTENCE_MODEL = self.sentence_model
                logger.info("💾 Sentence Model cached GLOBALLY")
        
        # Initialize grammar checker
        if _GRAMMAR_CHECKER:
            self.grammar_checker = _GRAMMAR_CHECKER
        else:
            self.grammar_checker = self._load_grammar_checker()
            if self.grammar_checker:
                _GRAMMAR_CHECKER = self.grammar_checker
        
        if not self.llm:
            logger.error("❌ AI Writer FAILED - GGUF model not found")
        else:
            logger.info("✅ AI Writer LOADED (450-2500 words, 95%+ Human-Like, Enhanced Sentence Model)")
        
        # 🎯 Initialize AI Humanizer (QuillBot-inspired 7-pass refinement)
        try:
            logger.info("⏳ Loading AI Humanizer...")
            self.humanizer = AIHumanizer()
            logger.info("✅ AI Humanizer loaded (7-pass refinement)")
        except Exception as e:
            logger.warning(f"⚠️  AI Humanizer unavailable: {e}")
            self.humanizer = None
