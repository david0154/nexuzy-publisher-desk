"""
Translator Module - NLLB-200 Model Integration
Supports 200+ languages with proper language codes
"""

import sqlite3
import logging
from datetime import datetime

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
        self._load_model()
    
    def _load_model(self):
        """Load NLLB-200 model"""
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            import torch
            
            model_name = "facebook/nllb-200-distilled-600M"
            logger.info(f"Loading NLLB-200 model: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.translator = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            logger.info("NLLB-200 model loaded successfully")
            
        except ImportError:
            logger.warning("Transformers not installed. Translation will use template mode.")
            logger.warning("Install: pip install transformers torch")
        except Exception as e:
            logger.error(f"Error loading NLLB-200: {e}")
    
    def translate_text(self, text, target_language):
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Language name (e.g., 'Spanish', 'Hindi')
        
        Returns:
            Translated text
        """
        if not self.translator or not self.tokenizer:
            logger.warning("Using template translation (model not loaded)")
            return f"[Translation to {target_language}]\n\n{text}"
        
        # Get language code
        target_code = LANGUAGE_CODES.get(target_language)
        if not target_code:
            logger.error(f"Unsupported language: {target_language}")
            return f"[Unsupported language: {target_language}]\n\n{text}"
        
        try:
            # Set source language (English)
            self.tokenizer.src_lang = "eng_Latn"
            
            # Tokenize
            inputs = self.tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
            
            # Translate
            translated_tokens = self.translator.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(target_code),
                max_length=512
            )
            
            # Decode
            translated_text = self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
            
            logger.info(f"Translated to {target_language} successfully")
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return f"[Translation Error: {e}]\n\n{text}"
    
    def translate_draft(self, draft_id, target_language):
        """
        Translate a draft from database
        
        Args:
            draft_id: Draft ID from database
            target_language: Target language name
        
        Returns:
            dict with translation details
        """
        try:
            # Get draft
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT workspace_id, title, body_draft FROM ai_drafts WHERE id = ?', (draft_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.error(f"Draft {draft_id} not found")
                conn.close()
                return None
            
            workspace_id, title, body = result
            
            # Translate title
            logger.info(f"Translating title to {target_language}...")
            translated_title = self.translate_text(title, target_language)
            
            # Translate body
            logger.info(f"Translating body to {target_language}...")
            translated_body = self.translate_text(body, target_language)
            
            # Save translation
            cursor.execute('''
                INSERT INTO translations (draft_id, language, title, body, approved)
                VALUES (?, ?, ?, ?, 0)
            ''', (draft_id, target_language, translated_title, translated_body))
            
            translation_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Translation saved with ID: {translation_id}")
            
            return {
                'id': translation_id,
                'draft_id': draft_id,
                'language': target_language,
                'title': translated_title,
                'body': translated_body
            }
            
        except Exception as e:
            logger.error(f"Error translating draft: {e}")
            return None
    
    def get_translations(self, draft_id):
        """Get all translations for a draft"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, language, title, body, approved, translated_at
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
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        return sorted(LANGUAGE_CODES.keys())
