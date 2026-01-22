"""
Multi-Language Translator Module
Translates articles using NLLB-200 model
"""

import sqlite3
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class Translator:
    """Translate content to multiple languages"""
    
    SUPPORTED_LANGUAGES = {
        'english': 'eng_Latn',
        'hindi': 'hin_Deva',
        'bengali': 'ben_Beng',
        'spanish': 'spa_Latn',
        'french': 'fra_Latn',
        'german': 'deu_Latn',
        'arabic': 'arb_Arab',
        'chinese': 'zho_Hans',
        'japanese': 'jpn_Jpan',
        'portuguese': 'por_Latn'
    }
    
    def __init__(self, db_path: str, model_name: str = 'facebook/nllb-200-distilled-600M'):
        self.db_path = db_path
        self.model_name = model_name
        self.translator = self._load_model()
    
    def _load_model(self):
        """Load NLLB translator"""
        try:
            from transformers import pipeline
            translator = pipeline(
                'translation',
                model=self.model_name,
                device=0 if self._has_gpu() else -1
            )
            logger.info("NLLB-200 model loaded successfully")
            return translator
        
        except Exception as e:
            logger.error(f"Error loading NLLB model: {e}")
            return None
    
    @staticmethod
    def _has_gpu():
        """Check GPU availability"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def translate_draft(self, draft_id: int, target_language: str) -> Dict:
        """
        Translate draft to target language
        """
        try:
            if target_language.lower() not in self.SUPPORTED_LANGUAGES:
                logger.error(f"Unsupported language: {target_language}")
                return {}
            
            # Get draft content
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT title, body_draft FROM ai_drafts WHERE id = ?
            ''', (draft_id,))
            
            result = cursor.fetchone()
            if not result:
                return {}
            
            original_title, original_body = result
            conn.close()
            
            if not self.translator:
                logger.warning("Model not loaded, returning template")
                return self._template_translation(target_language, original_title, original_body)
            
            # Translate
            target_code = self.SUPPORTED_LANGUAGES[target_language.lower()]
            
            translated_title = self._translate_text(original_title, target_code)
            translated_body = self._translate_text(original_body, target_code, chunk_size=200)
            
            translation = {
                'language': target_language,
                'title': translated_title,
                'body': translated_body
            }
            
            # Store translation
            self._store_translation(draft_id, translation)
            
            logger.info(f"Translated draft {draft_id} to {target_language}")
            return translation
        
        except Exception as e:
            logger.error(f"Error translating draft: {e}")
            return {}
    
    def _translate_text(self, text: str, target_code: str, chunk_size: int = 400) -> str:
        """
        Translate text, breaking into chunks for long content
        """
        try:
            if len(text) <= chunk_size:
                result = self.translator(text, target_lang=target_code, max_length=512)
                return result[0]['translation_text']
            
            # Split into sentences and chunks
            sentences = text.split('. ')
            chunks = []
            current_chunk = []
            chunk_length = 0
            
            for sentence in sentences:
                if chunk_length + len(sentence) > chunk_size and current_chunk:
                    chunks.append('. '.join(current_chunk) + '.')
                    current_chunk = []
                    chunk_length = 0
                
                current_chunk.append(sentence)
                chunk_length += len(sentence)
            
            if current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
            
            # Translate chunks
            translations = []
            for chunk in chunks:
                try:
                    result = self.translator(chunk, target_lang=target_code, max_length=512)
                    translations.append(result[0]['translation_text'])
                except:
                    translations.append(chunk)  # Keep original on error
            
            return ' '.join(translations)
        
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return text
    
    def _store_translation(self, draft_id: int, translation: Dict):
        """
        Store translation in database
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO translations 
                (draft_id, language, title, body, approved)
                VALUES (?, ?, ?, ?, 0)
            ''', (
                draft_id,
                translation['language'],
                translation['title'],
                translation['body']
            ))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            logger.error(f"Error storing translation: {e}")
    
    @staticmethod
    def _template_translation(language: str, title: str, body: str) -> Dict:
        """
        Generate template translation when model unavailable
        """
        # Simple placeholder - in production would use translation API
        return {
            'language': language,
            'title': f"[{language.upper()}] {title}",
            'body': f"[Translated to {language} - Original follows]\n\n{body}"
        }
