"""
AI Draft Generation Module
Generates news articles using Mistral-7B-GGUF (quantized Q4_K_M, 4.1GB)
"""

import sqlite3
import logging
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)

class DraftGenerator:
    """Generate AI-assisted news drafts using GGUF quantized model"""
    
    def __init__(self, db_path: str, model_name: str = 'TheBloke/Mistral-7B-Instruct-v0.2-GGUF'):
        self.db_path = db_path
        self.model_name = model_name
        self.model_file = 'mistral-7b-instruct-v0.2.Q4_K_M.gguf'
        self.llm = self._load_model()
    
    def _load_model(self):
        """Load GGUF quantized Mistral model (4.1GB with llama-cpp-python)"""
        try:
            from llama_cpp import Llama
            
            logger.info(f"Loading GGUF model: {self.model_name}")
            
            # Construct model path
            model_dir = Path('models') / self.model_name.replace('/', '_')
            model_path = model_dir / self.model_file
            
            if not model_path.exists():
                logger.warning(f"Model not found at {model_path}, will use template generation")
                return None
            
            # Load GGUF model with llama-cpp-python
            llm = Llama(
                model_path=str(model_path),
                n_ctx=4096,  # Context window
                n_threads=4,  # CPU threads (adjust based on your CPU)
                n_gpu_layers=0,  # 0 for CPU, increase if GPU available
                verbose=False
            )
            
            logger.info("✓ Mistral-7B-GGUF Q4_K_M loaded (4.1GB, CPU-optimized)")
            return llm
        
        except ImportError:
            logger.error("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            return None
        except Exception as e:
            logger.error(f"Error loading GGUF model: {e}")
            return None
    
    def generate_draft(self, news_id: int) -> Dict:
        """
        Generate article draft for news item
        Uses facts from database to guide generation
        """
        try:
            # Get news details
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT headline, summary FROM news_queue WHERE id = ?
            ''', (news_id,))
            
            news = cursor.fetchone()
            if not news:
                return {}
            
            headline, summary = news
            
            # Get scraped facts
            cursor.execute('''
                SELECT fact_type, content FROM scraped_facts 
                WHERE news_id = ?
                ORDER BY confidence DESC
                LIMIT 20
            ''', (news_id,))
            
            facts = cursor.fetchall()
            conn.close()
            
            # Build prompt
            prompt = self._build_prompt(headline, summary, facts)
            
            if not self.llm:
                logger.warning("GGUF model not loaded, returning template draft")
                return self._template_draft(headline, summary, facts)
            
            # Generate with Mistral-GGUF
            try:
                output = self.llm(
                    prompt,
                    max_tokens=512,
                    temperature=0.7,
                    top_p=0.9,
                    stop=["</s>", "[/INST]"],
                    echo=False
                )
                
                generated_text = output['choices'][0]['text']
            
            except Exception as e:
                logger.error(f"GGUF generation error: {e}")
                return self._template_draft(headline, summary, facts)
            
            # Parse output
            draft = self._parse_output(generated_text, headline, summary)
            
            # Get workspace_id
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT workspace_id FROM news_queue WHERE id = ?', (news_id,))
            workspace_id = cursor.fetchone()[0]
            conn.close()
            
            # Store draft
            draft_id = self._store_draft(news_id, workspace_id, draft)
            
            logger.info(f"Generated draft for news_id {news_id} using GGUF model")
            return {**draft, 'id': draft_id}
        
        except Exception as e:
            logger.error(f"Error generating draft: {e}")
            return self._template_draft(headline, summary, [])
    
    def _build_prompt(self, headline: str, summary: str, facts: List[tuple]) -> str:
        """
        Build prompt for GGUF model
        Structured to guide neutral, fact-based generation
        """
        facts_str = "\n".join([f"- {fact_type}: {content}" for fact_type, content in facts])
        
        prompt = f"""<s>[INST] You are a professional news journalist. Write a neutral, fact-based news article.

Headline: {headline}
Summary: {summary}

Facts to include:
{facts_str}

Write a concise article (300-500 words):
1. Start with a compelling introduction (2-3 sentences)
2. Include verified facts from above
3. Add context and background
4. Keep neutral tone - avoid opinion
5. Conclude with implications

Article: [/INST]"""
        
        return prompt
    
    def _parse_output(self, text: str, headline: str, summary: str) -> Dict:
        """Parse model output into structured draft"""
        # Clean up generated text
        body = text.strip()
        
        # Generate headline suggestions
        headline_suggestions = [
            f"{headline}",
            f"Breaking: {headline}",
            f"{headline} - Latest Updates"
        ]
        
        return {
            'title': headline,
            'headline_suggestions': headline_suggestions,
            'body_draft': body[:1500],  # Truncate to reasonable length
            'summary': summary,
            'word_count': len(body.split())
        }
    
    def _template_draft(self, headline: str, summary: str, facts: List[tuple]) -> Dict:
        """Generate template draft when GGUF model unavailable"""
        body = f"""Breaking News: {headline}

{summary}

"""        
        if facts:
            body += "Key Details:\n"
            for fact_type, content in facts[:5]:
                body += f"• {content}\n"
        
        body += "\nMore details to follow as this story develops."
        
        return {
            'title': headline,
            'headline_suggestions': [headline, f"Breaking: {headline}"],
            'body_draft': body,
            'summary': summary,
            'word_count': len(body.split())
        }
    
    def _store_draft(self, news_id: int, workspace_id: int, draft: Dict) -> int:
        """Store draft in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ai_drafts 
                (workspace_id, news_id, title, headline_suggestions, body_draft, summary, word_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                workspace_id,
                news_id,
                draft['title'],
                str(draft['headline_suggestions']),
                draft['body_draft'],
                draft['summary'],
                draft['word_count']
            ))
            
            conn.commit()
            draft_id = cursor.lastrowid
            conn.close()
            
            return draft_id
        
        except Exception as e:
            logger.error(f"Error storing draft: {e}")
            return 0
