"""
Vision AI Module - Image Analysis with Watermark Detection
Verifies images, detects watermarks, optimizes for web publishing
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Tuple
import hashlib
from datetime import datetime
import base64
import io
from pathlib import Path

logger = logging.getLogger(__name__)

class VisionAI:
    """Analyze images using Vision AI with watermark detection"""
    
    def __init__(self, db_path: str = 'nexuzy.db'):
        self.db_path = db_path
        self.vision_model = self._load_vision_model()
        self.image_cache = {}  # Cache analyzed images
    
    def _load_vision_model(self):
        """Load Vision AI model for image analysis"""
        try:
            from transformers import AutoImageProcessor, AutoModelForImageClassification
            from PIL import Image
            import torch
            
            logger.info("Loading Vision AI model...")
            
            # Try to load a lightweight vision model
            try:
                processor = AutoImageProcessor.from_pretrained(
                    "google/vit-base-patch16-224",
                    local_files_only=True,
                    trust_remote_code=True
                )
                model = AutoModelForImageClassification.from_pretrained(
                    "google/vit-base-patch16-224",
                    local_files_only=True,
                    trust_remote_code=True,
                    device_map="cpu"
                )
                logger.info("[OK] Vision AI model loaded successfully")
                return {'processor': processor, 'model': model}
            except Exception as e:
                logger.warning(f"Could not load vision model: {e}")
                logger.info("Will use fallback image analysis mode")
                return None
        
        except ImportError:
            logger.warning("Vision AI dependencies not installed")
            logger.warning("Install: pip install transformers pillow torch")
            return None
        except Exception as e:
            logger.error(f"Error loading Vision AI: {e}")
            return None
    
    def analyze_image(self, image_path: str, draft_id: int) -> Dict:
        """
        Comprehensive image analysis including watermark detection
        
        Args:
            image_path: Path to image file or URL
            draft_id: Associated draft ID
        
        Returns:
            Analysis results dictionary
        """
        try:
            logger.info(f"Analyzing image: {image_path}")
            
            # Load image
            image_data = self._load_image(image_path)
            if not image_data:
                return {'status': 'failed', 'error': 'Could not load image'}
            
            # Generate image hash for duplicate detection
            image_hash = self._generate_image_hash(image_data['path'])
            
            # Check for duplicates
            duplicate_check = self._check_duplicate_image(image_hash)
            if duplicate_check['is_duplicate']:
                logger.warning(f"Duplicate image detected: {duplicate_check['original_id']}")
            
            # Detect watermarks
            watermark_result = self._detect_watermark(image_data['path'])
            
            # Extract image metadata
            metadata = self._extract_metadata(image_data['path'])
            
            # Assess image quality
            quality_score = self._assess_image_quality(image_data['path'])
            
            # Optimize image
            optimized_path = self._optimize_image(image_data['path'])
            
            # Convert to base64 for direct embedding
            image_base64 = self._convert_to_base64(optimized_path or image_data['path'])
            
            # Compile analysis results
            analysis = {
                'status': 'success',
                'image_path': image_path,
                'image_hash': image_hash,
                'watermark_detected': watermark_result['has_watermark'],
                'watermark_confidence': watermark_result['confidence'],
                'watermark_type': watermark_result['type'],
                'quality_score': quality_score,
                'metadata': metadata,
                'duplicate_detected': duplicate_check['is_duplicate'],
                'image_base64': image_base64,
                'optimized_size': len(image_base64),
                'recommendations': self._generate_recommendations(watermark_result, quality_score),
                'notifications': self._generate_notifications(watermark_result, duplicate_check, quality_score)
            }
            
            # Store analysis in database
            self._store_analysis(draft_id, analysis)
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _load_image(self, image_path: str) -> Optional[Dict]:
        """Load image from file or URL"""
        try:
            from PIL import Image
            import requests
            from io import BytesIO
            
            if image_path.startswith('http'):
                # Load from URL
                response = requests.get(image_path, timeout=10)
                image = Image.open(BytesIO(response.content))
                temp_path = f"/tmp/image_{hashlib.md5(image_path.encode()).hexdigest()}.png"
                image.save(temp_path)
            else:
                # Load from file
                image = Image.open(image_path)
                temp_path = image_path
            
            return {
                'path': temp_path,
                'image': image,
                'format': image.format,
                'size': image.size
            }
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
    
    def _detect_watermark(self, image_path: str) -> Dict:
        """
        Detect watermarks in image using multiple techniques
        """
        try:
            from PIL import Image
            import numpy as np
            
            image = Image.open(image_path).convert('RGB')
            img_array = np.array(image)
            
            # Check for text watermarks
            text_watermark = self._detect_text_watermark(img_array)
            
            # Check for logo watermarks
            logo_watermark = self._detect_logo_watermark(img_array)
            
            # Check for gradient watermarks
            gradient_watermark = self._detect_gradient_watermark(img_array)
            
            # Compile results
            has_watermark = any([text_watermark['detected'], logo_watermark['detected'], gradient_watermark['detected']])
            
            confidence = max([text_watermark['confidence'], logo_watermark['confidence'], gradient_watermark['confidence']])
            
            watermark_type = []
            if text_watermark['detected']:
                watermark_type.append('text')
            if logo_watermark['detected']:
                watermark_type.append('logo')
            if gradient_watermark['detected']:
                watermark_type.append('gradient')
            
            logger.info(f"Watermark detection: {has_watermark} (confidence: {confidence})")
            
            return {
                'has_watermark': has_watermark,
                'confidence': confidence,
                'type': ', '.join(watermark_type) if watermark_type else 'none',
                'details': {
                    'text': text_watermark,
                    'logo': logo_watermark,
                    'gradient': gradient_watermark
                }
            }
        
        except Exception as e:
            logger.error(f"Error detecting watermark: {e}")
            return {
                'has_watermark': False,
                'confidence': 0,
                'type': 'unknown',
                'error': str(e)
            }
    
    def _detect_text_watermark(self, img_array) -> Dict:
        """Detect text-based watermarks"""
        try:
            import numpy as np
            
            # Convert to grayscale for text detection
            gray = np.mean(img_array, axis=2)
            
            # Calculate edge density (text has high edges)
            edges = np.abs(np.diff(gray))
            edge_density = np.mean(edges)
            
            # Threshold-based detection
            text_detected = edge_density > 15  # Adjust threshold based on testing
            confidence = min(edge_density / 50, 1.0)  # Normalize to 0-1
            
            return {
                'detected': text_detected,
                'confidence': float(confidence),
                'edge_density': float(edge_density)
            }
        except Exception as e:
            logger.debug(f"Error in text watermark detection: {e}")
            return {'detected': False, 'confidence': 0}
    
    def _detect_logo_watermark(self, img_array) -> Dict:
        """Detect logo-based watermarks in corners"""
        try:
            import numpy as np
            
            height, width, _ = img_array.shape
            
            # Check corners where logos typically appear
            corner_size = min(height // 4, width // 4)
            corners = [
                img_array[:corner_size, :corner_size],  # Top-left
                img_array[:corner_size, -corner_size:],  # Top-right
                img_array[-corner_size:, :corner_size],  # Bottom-left
                img_array[-corner_size:, -corner_size:]   # Bottom-right
            ]
            
            # Calculate color variance in corners
            corner_variances = [np.var(corner) for corner in corners]
            avg_corner_variance = np.mean(corner_variances)
            
            # High variance suggests distinct logo
            logo_detected = avg_corner_variance > 500  # Adjust threshold
            confidence = min(avg_corner_variance / 2000, 1.0)
            
            return {
                'detected': logo_detected,
                'confidence': float(confidence),
                'variance': float(avg_corner_variance)
            }
        except Exception as e:
            logger.debug(f"Error in logo watermark detection: {e}")
            return {'detected': False, 'confidence': 0}
    
    def _detect_gradient_watermark(self, img_array) -> Dict:
        """Detect gradient or overlay watermarks"""
        try:
            import numpy as np
            
            # Check for semi-transparent overlays
            # Analyze color distribution
            color_std = np.std(img_array, axis=(0, 1))
            avg_color_std = np.mean(color_std)
            
            # Low color std suggests overlay
            overlay_detected = avg_color_std < 30  # Adjust threshold
            confidence = (50 - avg_color_std) / 50 if avg_color_std < 50 else 0
            confidence = max(0, min(confidence, 1.0))
            
            return {
                'detected': overlay_detected,
                'confidence': float(confidence),
                'color_variance': float(avg_color_std)
            }
        except Exception as e:
            logger.debug(f"Error in gradient watermark detection: {e}")
            return {'detected': False, 'confidence': 0}
    
    def _extract_metadata(self, image_path: str) -> Dict:
        """Extract EXIF and other metadata"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            image = Image.open(image_path)
            metadata = {
                'format': image.format,
                'size': image.size,
                'width': image.width,
                'height': image.height,
                'mode': image.mode,
                'exif_data': {}
            }
            
            # Extract EXIF data if available
            try:
                exif_data = image.getexif()
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    metadata['exif_data'][tag_name] = str(value)[:100]  # Limit to 100 chars
            except:
                pass
            
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}
    
    def _assess_image_quality(self, image_path: str) -> float:
        """Assess overall image quality (0-1 scale)"""
        try:
            from PIL import Image
            import numpy as np
            
            image = Image.open(image_path)
            img_array = np.array(image)
            
            # Check dimensions
            min_dimension = min(image.width, image.height)
            size_score = min(min_dimension / 1920, 1.0)  # Good quality if > 1920px
            
            # Check color depth
            if image.mode == 'RGB':
                color_score = 1.0
            elif image.mode == 'RGBA':
                color_score = 0.9
            else:
                color_score = 0.7
            
            # Check blur (using Laplacian variance)
            if image.mode != 'RGB':
                img_array = Image.new('RGB', image.size, color=image.getexif().get(274, 1))
            
            # Simple blur detection
            gray = np.mean(img_array, axis=2) if len(img_array.shape) == 3 else img_array
            edges = np.abs(np.diff(gray))
            blur_score = min(np.mean(edges) / 20, 1.0)
            
            # Combined quality score
            quality = (size_score * 0.3 + color_score * 0.3 + blur_score * 0.4)
            
            return float(max(0, min(quality, 1.0)))
        
        except Exception as e:
            logger.error(f"Error assessing image quality: {e}")
            return 0.5
    
    def _optimize_image(self, image_path: str) -> Optional[str]:
        """Optimize image for web publishing"""
        try:
            from PIL import Image
            
            image = Image.open(image_path)
            
            # Resize if too large
            max_dimension = 1920
            if max(image.width, image.height) > max_dimension:
                ratio = max_dimension / max(image.width, image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Save optimized version
            optimized_path = f"{image_path[:-4]}_optimized.jpg"
            image.save(optimized_path, 'JPEG', quality=85, optimize=True)
            
            logger.info(f"Image optimized: {optimized_path}")
            return optimized_path
        
        except Exception as e:
            logger.warning(f"Error optimizing image: {e}")
            return None
    
    def _convert_to_base64(self, image_path: str) -> str:
        """Convert image to base64 for direct embedding"""
        try:
            with open(image_path, 'rb') as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            return ""
    
    def _generate_image_hash(self, image_path: str) -> str:
        """Generate perceptual hash of image for duplicate detection"""
        try:
            from PIL import Image
            import numpy as np
            
            image = Image.open(image_path).resize((8, 8)).convert('L')
            pixels = np.array(image)
            avg_pixel = np.mean(pixels)
            hash_string = ''.join(['1' if p > avg_pixel else '0' for p in pixels.flatten()])
            return hash_string
        except Exception as e:
            logger.error(f"Error generating image hash: {e}")
            return hashlib.md5(str(image_path).encode()).hexdigest()
    
    def _check_duplicate_image(self, image_hash: str) -> Dict:
        """Check if similar image already exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Look for matching hash
            cursor.execute('''
                SELECT id, draft_id, similarity_score FROM image_analysis
                WHERE image_hash = ? LIMIT 1
            ''', (image_hash,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'is_duplicate': True,
                    'original_id': result[0],
                    'draft_id': result[1],
                    'similarity': result[2]
                }
            
            return {'is_duplicate': False}
        
        except Exception as e:
            logger.error(f"Error checking duplicates: {e}")
            return {'is_duplicate': False}
    
    def _generate_recommendations(self, watermark_result: Dict, quality_score: float) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if watermark_result['has_watermark']:
            if watermark_result['confidence'] > 0.7:
                recommendations.append(f"Replace image - Strong {watermark_result['type']} watermark detected")
            else:
                recommendations.append(f"Consider replacing - Possible {watermark_result['type']} watermark detected")
        
        if quality_score < 0.6:
            recommendations.append("Image quality is low - Consider using a higher resolution version")
        elif quality_score < 0.8:
            recommendations.append("Image quality could be improved")
        
        if not recommendations:
            recommendations.append("Image looks good for publishing")
        
        return recommendations
    
    def _generate_notifications(self, watermark_result: Dict, duplicate_check: Dict, quality_score: float) -> List[Dict]:
        """Generate user notifications"""
        notifications = []
        
        if watermark_result['has_watermark']:
            notifications.append({
                'type': 'warning',
                'severity': 'high' if watermark_result['confidence'] > 0.7 else 'medium',
                'message': f"Watermark detected ({watermark_result['type']}) with {int(watermark_result['confidence']*100)}% confidence",
                'action': 'Consider replacing the image'
            })
        
        if duplicate_check.get('is_duplicate'):
            notifications.append({
                'type': 'info',
                'severity': 'low',
                'message': f"Similar image already used in draft {duplicate_check['draft_id']}",
                'action': 'Verify this is intentional'
            })
        
        if quality_score < 0.6:
            notifications.append({
                'type': 'warning',
                'severity': 'medium',
                'message': f"Low image quality score ({int(quality_score*100)}%)",
                'action': 'Use a higher resolution version if available'
            })
        
        return notifications
    
    def _store_analysis(self, draft_id: int, analysis: Dict):
        """Store analysis results in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO image_analysis
                (draft_id, image_path, image_hash, watermark_detected, watermark_confidence, 
                 quality_score, metadata, analysis_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                draft_id,
                analysis['image_path'],
                analysis['image_hash'],
                analysis['watermark_detected'],
                analysis['watermark_confidence'],
                analysis['quality_score'],
                str(analysis.get('metadata', {})),
                str(analysis),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Analysis stored for draft {draft_id}")
        
        except Exception as e:
            logger.error(f"Error storing analysis: {e}")
