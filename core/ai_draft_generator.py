"""
AI Draft Generation Module
Generates news articles using Mistral-7B-GPTQ (quantized, 4GB) with fact-based prompts
"""

import sqlite3
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class DraftGenerator:
    """Generate AI-assisted news drafts using quantized model"""
    
    def __init__(self, db_path: str, model_name: str = 'TheBloke/Mistral-7B-Instruct-v0.2-GPTQ'):
        self.db_path = db_path
        self.model_name = model_name
        self.pipeline = self._load_model()
    
    def _load_model(self):
        """Load quantized Mistral model (GPTQ - 4GB instead of 14GB)"""
        try:
            from transformers import AutoTokenizer
            from auto_gptq import AutoGPTQForCausalLM
            
            logger.info(f"Loading quantized model: {self.model_name}")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Load GPTQ quantized model
            model = AutoGPTQForCausalLM.from_quantized(
                self.model_name,
                device="cuda:0" if self._has_gpu() else "cpu",
                use_safetensors=True,
                use_triton=False  # Better CPU compatibility
            )
            
            logger.info("✓ Mistral-7B-GPTQ loaded (4GB quantized)")
            return {'model': model, 'tokenizer': tokenizer}
        
        except ImportError:
            logger.error("auto-gptq not installed. Install with: pip install auto-gptq")
            return None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None
    
    @staticmethod
    def _has_gpu():
        """Check if GPU is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
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
            
            if not self.pipeline:
                logger.warning("Model not loaded, returning template draft")
                return self._template_draft(headline, summary, facts)
            
            # Generate with Mistral-GPTQ
            try:
                tokenizer = self.pipeline['tokenizer']
                model = self.pipeline['model']
                
                inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
                
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
                
                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            except Exception as e:
                logger.error(f"Generation error: {e}")
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
            
            logger.info(f"Generated draft for news_id {news_id}")
            return {**draft, 'id': draft_id}
        
        except Exception as e:
            logger.error(f"Error generating draft: {e}")
            return self._template_draft(headline, summary, [])
    
    def _build_prompt(self, headline: str, summary: str, facts: List[tuple]) -> str:
        """
        Build prompt for model
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
        # Extract article body (remove prompt)
        if '[/INST]' in text:
            parts = text.split('[/INST]')
            body = parts[-1].strip() if len(parts) > 1 else text
        else:
            body = text
        
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
        """Generate template draft when model unavailable"""
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
