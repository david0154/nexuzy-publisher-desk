"""
Vision AI - Image Analysis and Watermark Detection
Uses CLIP or similar vision models for image understanding
"""

import logging
import os
from pathlib import Path

try:
    from PIL import Image
    import torch
    from transformers import CLIPProcessor, CLIPModel
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

logger = logging.getLogger(__name__)


class VisionAI:
    """Vision AI for image analysis and watermark detection"""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.model_name = "openai/clip-vit-large-patch14"
        self.model_loaded = False
    
    def load_model(self):
        """Load CLIP vision model for image analysis"""
        
        if not VISION_AVAILABLE:
            raise ImportError(
                "Vision AI requires: pip install torch transformers pillow"
            )
        
        if self.model_loaded:
            logger.info("Vision model already loaded")
            return True
        
        try:
            logger.info(f"Loading Vision AI model: {self.model_name}")
            
            # Load CLIP model (2.3GB)
            self.model = CLIPModel.from_pretrained(self.model_name)
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            
            # Set to eval mode
            self.model.eval()
            
            self.model_loaded = True
            logger.info("[OK] Vision AI model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading Vision AI model: {e}")
            return False
    
    def detect_watermark(self, image_path):
        """
        Detect watermarks, logos, and copyright marks in image
        
        Args:
            image_path: Path to image file
            
        Returns:
            dict: Analysis results with watermark detection scores
        """
        
        if not self.model_loaded:
            self.load_model()
        
        if not os.path.exists(image_path):
            return {"error": "Image file not found"}
        
        try:
            # Load image
            image = Image.open(image_path).convert("RGB")
            
            # Watermark detection prompts
            watermark_prompts = [
                "an image with a watermark",
                "an image with a logo",
                "an image with text overlay",
                "an image with copyright mark",
                "a clean image without watermarks",
                "an image with brand logo",
                "an image with Getty Images watermark",
                "an image with Shutterstock watermark"
            ]
            
            # Process image and text
            inputs = self.processor(
                text=watermark_prompts,
                images=image,
                return_tensors="pt",
                padding=True
            )
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            # Parse results
            results = {}
            for idx, prompt in enumerate(watermark_prompts):
                score = float(probs[0][idx])
                results[prompt] = score
            
            # Determine if watermark detected
            watermark_score = max(
                results["an image with a watermark"],
                results["an image with a logo"],
                results["an image with text overlay"],
                results["an image with copyright mark"]
            )
            
            clean_score = results["a clean image without watermarks"]
            
            watermark_detected = watermark_score > clean_score
            confidence = watermark_score if watermark_detected else clean_score
            
            return {
                "watermark_detected": watermark_detected,
                "confidence": f"{confidence * 100:.2f}%",
                "watermark_score": f"{watermark_score * 100:.2f}%",
                "clean_score": f"{clean_score * 100:.2f}%",
                "detailed_scores": results,
                "status": "Watermark detected" if watermark_detected else "Clean image"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {"error": str(e)}
    
    def analyze_image_quality(self, image_path):
        """
        Analyze general image quality and content
        
        Args:
            image_path: Path to image file
            
        Returns:
            dict: Image quality analysis
        """
        
        if not self.model_loaded:
            self.load_model()
        
        try:
            image = Image.open(image_path).convert("RGB")
            
            quality_prompts = [
                "a high quality professional photo",
                "a low quality blurry photo",
                "a sharp clear image",
                "a dark underexposed image",
                "a bright overexposed image",
                "a well composed photograph"
            ]
            
            inputs = self.processor(
                text=quality_prompts,
                images=image,
                return_tensors="pt",
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            results = {}
            for idx, prompt in enumerate(quality_prompts):
                score = float(probs[0][idx])
                results[prompt] = f"{score * 100:.2f}%"
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing image quality: {e}")
            return {"error": str(e)}
    
    def get_model_info(self):
        """Get information about the loaded model"""
        return {
            "model_name": "David AI Vision (CLIP)",
            "model_id": self.model_name,
            "size": "2.3GB",
            "purpose": "Image Watermark Detection",
            "loaded": self.model_loaded,
            "capabilities": [
                "Watermark detection",
                "Logo detection",
                "Copyright mark detection",
                "Text overlay detection",
                "Image quality analysis"
            ]
        }
