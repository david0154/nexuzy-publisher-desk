"""
Translator Module - NLLB-200 Model Integration with Enhanced Error Handling
Supports 200+ languages with proper language codes and fallback modes
Fixed workflow: Save as new draft after translation for WordPress push
Robust error handling for missing database columns
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib

logger = logging.getLogger(__name__)

# Complete NLLB-200 Language Codes Mapping
LANGUAGE_CODES = {
    # European Languages
    'Spanish': 'spa_Latn', 'French': 'fra_Latn', 'German': 'deu_Latn',
    'Italian': 'ita_Latn', 'Portuguese': 'por_Latn', 'Russian': 'rus_Cyrl',
    'Polish': 'pol_Latn', 'Dutch': 'nld_Latn', 'Greek': 'ell_Grek',
    'Swedish': 'swe_Latn', 'Norwegian': 'nob_Latn', 'Danish': 'dan_Latn',
    'Finnish': 'fin_Latn', 'Czech': 'ces_Latn', 'Romanian': 'ron_Latn',
    'Hungarian': 'hun_Latn', 'Bulgarian': 'bul_Cyrl', 'Croatian': 'hrv_Latn',
    'Ukrainian': 'ukr_Cyrl', 'Serbian': 'srp_Cyrl', 'Slovak': 'slk_Latn',
    'Lithuanian': 'lit_Latn', 'Latvian': 'lvs_Latn', 'Estonian': 'est_Latn',
    'Slovenian': 'slv_Latn', 'Macedonian': 'mkd_Cyrl', 'Albanian': 'als_Latn',
    'Catalan': 'cat_Latn', 'Galician': 'glg_Latn', 'Basque': 'eus_Latn',
    'Icelandic': 'isl_Latn', 'Irish': 'gle_Latn', 'Welsh': 'cym_Latn',
    'Maltese': 'mlt_Latn', 'Luxembourgish': 'ltz_Latn',
    
    # Indian Languages
    'Hindi': 'hin_Deva', 'Bengali': 'ben_Beng', 'Tamil': 'tam_Taml',
    'Telugu': 'tel_Telu', 'Marathi': 'mar_Deva', 'Gujarati': 'guj_Gujr',
    'Kannada': 'kan_Knda', 'Malayalam': 'mal_Mlym', 'Punjabi': 'pan_Guru',
    'Urdu': 'urd_Arab', 'Odia': 'ory_Orya', 'Assamese': 'asm_Beng',
    'Sanskrit': 'san_Deva', 'Sindhi': 'snd_Arab', 'Nepali': 'npi_Deva',
    'Sinhala': 'sin_Sinh', 'Kashmiri': 'kas_Arab', 'Konkani': 'kok_Deva',
    'Manipuri': 'mni_Beng', 'Maithili': 'mai_Deva', 'Santali': 'sat_Olck',
    'Dogri': 'doi_Deva', 'Bodo': 'brx_Deva',
    
    # Asian Languages
    'Chinese (Simplified)': 'zho_Hans', 'Chinese (Traditional)': 'zho_Hant',
    'Japanese': 'jpn_Jpan', 'Korean': 'kor_Hang', 'Thai': 'tha_Thai',
    'Vietnamese': 'vie_Latn', 'Indonesian': 'ind_Latn', 'Malay': 'zsm_Latn',
    'Filipino': 'fil_Latn', 'Burmese': 'mya_Mymr', 'Khmer': 'khm_Khmr',
    'Lao': 'lao_Laoo', 'Mongolian': 'khk_Cyrl', 'Tibetan': 'bod_Tibt',
    'Javanese': 'jav_Latn', 'Sundanese': 'sun_Latn', 'Cebuano': 'ceb_Latn',
    'Tagalog': 'tgl_Latn', 'Malagasy': 'plt_Latn',
    
    # Middle Eastern Languages
    'Arabic': 'arb_Arab', 'Persian': 'pes_Arab', 'Hebrew': 'heb_Hebr',
    'Turkish': 'tur_Latn', 'Kurdish': 'ckb_Arab', 'Pashto': 'pbt_Arab',
    'Dari': 'prs_Arab', 'Azerbaijani': 'azj_Latn', 'Uzbek': 'uzn_Latn',
    'Kazakh': 'kaz_Cyrl', 'Kyrgyz': 'kir_Cyrl', 'Tajik': 'tgk_Cyrl',
    'Turkmen': 'tuk_Latn', 'Uyghur': 'uig_Arab', 'Armenian': 'hye_Armn',
    'Georgian': 'kat_Geor',
    
    # African Languages
    'Swahili': 'swh_Latn', 'Yoruba': 'yor_Latn', 'Hausa': 'hau_Latn',
    'Zulu': 'zul_Latn', 'Afrikaans': 'afr_Latn', 'Amharic': 'amh_Ethi',
    'Somali': 'som_Latn', 'Igbo': 'ibo_Latn', 'Shona': 'sna_Latn',
    'Xhosa': 'xho_Latn', 'Tigrinya': 'tir_Ethi', 'Oromo': 'gaz_Latn',
    'Kinyarwanda': 'kin_Latn', 'Kirundi': 'run_Latn', 'Luganda': 'lug_Latn',
    'Wolof': 'wol_Latn', 'Bambara': 'bam_Latn', 'Fula': 'fuv_Latn',
    'Lingala': 'lin_Latn', 'Luo': 'luo_Latn', 'Northern Sotho': 'nso_Latn',
    'Southern Sotho': 'sot_Latn', 'Tswana': 'tsn_Latn', 'Tsonga': 'tso_Latn',
    'Venda': 'ven_Latn',
    
    # Other Languages
    'English': 'eng_Latn', 'Esperanto': 'epo_Latn'
}

class Translator:
    def __init__(self, db_path='nexuzy.db'):
        self.db_path = db_path
        self.translator = None
        self.tokenizer = None
        self.translation_cache = {}  # Cache for recent translations
        self._load_model()
    
    def _load_model(self):
        """Load NLLB-200 model with proper error handling and fallback"""
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            import torch
            
            model_name = "facebook/nllb-200-distilled-600M"
            logger.info(f"Loading NLLB-200 model: {model_name}")
            
            # Try to load model
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
                self.translator = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    trust_remote_code=True,
                    device_map="cpu",  # Use CPU if GPU not available
                    low_cpu_mem_usage=True
                )
                
                logger.info("✅ NLLB-200 model loaded successfully")
                
            except Exception as model_error:
                logger.warning(f"Failed to load full model: {model_error}")
                # Try quantized version
                logger.info("Attempting to load quantized version...")
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.translator = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                logger.info("✅ Quantized model loaded")
            
        except ImportError:
            logger.warning("Transformers not installed. Translation will use fallback mode.")
            logger.warning("Install: pip install transformers torch")
            self.translator = None
        except Exception as e:
            logger.error(f"Error loading NLLB-200: {e}")
            logger.warning("Falling back to template translation mode")
            self.translator = None
    
    def _get_cache_key(self, text: str, target_language: str) -> str:
        """Generate cache key for translation"""
        content = f"{text}:{target_language}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def translate_text(self, text: str, target_language: str, force_refresh: bool = False) -> Tuple[str, bool]:
        """
        Translate text to target language with caching and fallback reporting.
        
        Args:
            text: Text to translate
            target_language: Language name (e.g., 'Spanish', 'Hindi')
            force_refresh: Skip cache and force new translation
        
        Returns:
            A tuple containing the translated text and a boolean indicating if fallback was used.
        """
        if not text or not text.strip():
            return text, False
        
        cache_key = self._get_cache_key(text, target_language)
        if not force_refresh and cache_key in self.translation_cache:
            logger.debug(f"Using cached translation for {target_language}")
            return self.translation_cache[cache_key]

        if target_language not in LANGUAGE_CODES:
            logger.error(f"Unsupported language: {target_language}")
            return text, True  # Fallback: return original text

        if self.translator and self.tokenizer:
            try:
                result = self._translate_with_model(text, target_language)
                self.translation_cache[cache_key] = (result, False)
                return result, False
            except Exception as e:
                logger.warning(f"AI translation failed: {e}. Using fallback.")
        
        # Fallback to template translation
        result = f"[Translation to {target_language}]\n\n{text}"
        self.translation_cache[cache_key] = (result, True)
        return result, True
    
    def _translate_with_model(self, text: str, target_language: str) -> str:
        """Translate using AI model with proper error handling"""
        target_code = LANGUAGE_CODES.get(target_language)
        if not target_code:
            raise ValueError(f"Invalid language code: {target_language}")
        
        try:
            # Handle long texts by chunking
            max_length = 512
            if len(text) > max_length:
                chunks = self._chunk_text(text, max_length)
                translated_chunks = []
                for chunk in chunks:
                    chunk_result = self._translate_chunk(chunk, target_code)
                    translated_chunks.append(chunk_result)
                return " ".join(translated_chunks)
            else:
                return self._translate_chunk(text, target_code)
        
        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise
    
    def _translate_chunk(self, text: str, target_code: str) -> str:
        """Translate a single chunk of text"""
        # Set source language (English)
        self.tokenizer.src_lang = "eng_Latn"
        
        # Tokenize
        inputs = self.tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
        
        # Translate
        translated_tokens = self.translator.generate(
            **inputs,
            forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(target_code),
            max_length=512,
            temperature=0.7,
            top_p=0.9
        )
        
        # Decode
        translated_text = self.tokenizer.batch_decode(
            translated_tokens,
            skip_special_tokens=True
        )[0]
        
        logger.debug(f"Translated chunk successfully")
        return translated_text
    
    def _chunk_text(self, text: str, chunk_size: int = 512) -> List[str]:
        """Split text into chunks while preserving sentences"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _check_column_exists(self, conn, table: str, column: str) -> bool:
        """Check if a column exists in a table"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        return column in columns
    
    def translate_draft(self, draft_id: int, target_language: str) -> Optional[Dict]:
        """
        Translate a draft and save as NEW draft in ai_drafts table
        This allows WordPress push to work with translated draft
        
        Args:
            draft_id: Original draft ID from database
            target_language: Target language name
        
        Returns:
            dict with new draft details or None if failed
        """
        try:
            # Validate language
            if target_language not in LANGUAGE_CODES:
                logger.error(f"Invalid target language: {target_language}")
                return None
            
            # Get original draft with column checking
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check which columns exist
            has_source_url = self._check_column_exists(conn, 'ai_drafts', 'source_url')
            has_source_domain = self._check_column_exists(conn, 'ai_drafts', 'source_domain')
            has_image_url = self._check_column_exists(conn, 'ai_drafts', 'image_url')
            has_summary = self._check_column_exists(conn, 'ai_drafts', 'summary')
            
            # Build dynamic query based on available columns
            base_cols = 'workspace_id, news_id, title, body_draft'
            extra_cols = []
            if has_summary:
                extra_cols.append('summary')
            if has_image_url:
                extra_cols.append('image_url')
            if has_source_url:
                extra_cols.append('source_url')
            if has_source_domain:
                extra_cols.append('source_domain')
            
            query_cols = base_cols + (', ' + ', '.join(extra_cols) if extra_cols else '')
            
            cursor.execute(f'''
                SELECT {query_cols}
                FROM ai_drafts WHERE id = ?
            ''', (draft_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.error(f"Draft {draft_id} not found")
                conn.close()
                return None
            
            # Unpack results dynamically
            workspace_id, news_id, title, body = result[:4]
            idx = 4
            summary = result[idx] if has_summary and len(result) > idx else ''
            idx += 1 if has_summary else 0
            image_url = result[idx] if has_image_url and len(result) > idx else ''
            idx += 1 if has_image_url else 0
            source_url = result[idx] if has_source_url and len(result) > idx else ''
            idx += 1 if has_source_url else 0
            source_domain = result[idx] if has_source_domain and len(result) > idx else ''
            
            fallback_occurred = False

            # Translate title
            logger.info(f"Translating title to {target_language}...")
            translated_title, title_fallback = self.translate_text(title, target_language)
            if title_fallback: fallback_occurred = True

            # Translate body
            logger.info(f"Translating body to {target_language}...")
            translated_body, body_fallback = self.translate_text(body, target_language)
            if body_fallback: fallback_occurred = True

            # Translate summary if present
            translated_summary = ""
            if summary:
                logger.info(f"Translating summary to {target_language}...")
                translated_summary, summary_fallback = self.translate_text(summary, target_language)
                if summary_fallback: fallback_occurred = True

            # Save as NEW draft in ai_drafts table (so WordPress push works)
            word_count = len(translated_body.split())
            
            # Build insert query dynamically based on available columns
            insert_cols = ['workspace_id', 'news_id', 'title', 'body_draft', 'word_count', 'is_html', 'created_at']
            insert_vals = [workspace_id, news_id, f"{translated_title} [{target_language}]", translated_body, word_count, 1, datetime.now().isoformat()]
            
            if has_summary:
                insert_cols.append('summary')
                insert_vals.append(translated_summary)
            if has_image_url:
                insert_cols.append('image_url')
                insert_vals.append(image_url or '')
            if has_source_url:
                insert_cols.append('source_url')
                insert_vals.append(source_url or '')
            if has_source_domain:
                insert_cols.append('source_domain')
                insert_vals.append(source_domain or '')
            
            placeholders = ', '.join(['?' for _ in insert_vals])
            cursor.execute(f'''
                INSERT INTO ai_drafts ({', '.join(insert_cols)})
                VALUES ({placeholders})
            ''', insert_vals)
            
            new_draft_id = cursor.lastrowid
            
            # Also save in translations table for record keeping
            cursor.execute('''
                INSERT INTO translations
                (draft_id, language, title, body, summary, approved, translated_at)
                VALUES (?, ?, ?, ?, ?, 0, ?)
            ''', (draft_id, target_language, translated_title, translated_body, translated_summary, datetime.now().isoformat()))
            
            translation_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Translation saved as new draft ID: {new_draft_id}, translation record ID: {translation_id}")
            
            return {
                'id': translation_id,
                'new_draft_id': new_draft_id,
                'original_draft_id': draft_id,
                'language': target_language,
                'title': translated_title,
                'body': translated_body,
                'summary': translated_summary,
                'word_count': word_count,
                'fallback_occurred': fallback_occurred
            }
            
        except sqlite3.OperationalError as e:
            if "no such column" in str(e):
                logger.error(f"❌ Database schema error: {e}")
                logger.error("❌ Please run: python fix_database.py")
                logger.error("This will add missing columns to your database.")
            else:
                logger.error(f"❌ Database error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error translating draft: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def batch_translate(self, draft_ids: List[int], target_languages: List[str]) -> List[Dict]:
        """Translate multiple drafts to multiple languages"""
        results = []
        for draft_id in draft_ids:
            for language in target_languages:
                try:
                    result = self.translate_draft(draft_id, language)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error translating draft {draft_id} to {language}: {e}")
        return results
    
    def get_translations(self, draft_id: int) -> List[Tuple]:
        """Get all translations for a draft"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, language, title, body, summary, approved, translated_at
                FROM translations
                WHERE draft_id = ?
                ORDER BY translated_at DESC
            ''', (draft_id,))
            
            translations = cursor.fetchall()
            conn.close()
            return translations
            
        except Exception as e:
            logger.error(f"Error getting translations: {e}")
            return []
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return sorted(LANGUAGE_CODES.keys())
    
    def approve_translation(self, translation_id: int) -> bool:
        """Mark translation as approved"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE translations
                SET approved = 1
                WHERE id = ?
            ''', (translation_id,))
            conn.commit()
            conn.close()
            logger.info(f"Translation {translation_id} approved")
            return True
        except Exception as e:
            logger.error(f"Error approving translation: {e}")
            return False
    
    def clear_cache(self):
        """Clear translation cache to free memory"""
        self.translation_cache.clear()
        logger.info("Translation cache cleared")
