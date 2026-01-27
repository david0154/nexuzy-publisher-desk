"""
Vision AI Module - Image Analysis with Watermark Detection
Simplified and working version
"""

import logging
from typing import Dict, Optional
import hashlib

logger = logging.getLogger(__name__)

class VisionAI:
    """Analyze images with watermark detection"""
    
    def __init__(self):
        self.dependencies_available = self._check_dependencies()
    
    def _check_dependencies(self) -> bool:
        """Check if required libraries are available"""
        try:
            import PIL
            import numpy as np
            logger.info("✅ Vision AI dependencies available")
            return True
        except ImportError as e:
            logger.warning(f"⚠️ Vision AI dependencies missing: {e}")
            logger.warning("Install: pip install pillow numpy")
            return False
    
    def detect_watermark(self, image_path: str) -> Dict:
        """
        Detect watermarks in image
        
        Args:
            image_path: Path to local image file
        
        Returns:
            Dict with watermark detection results
        """
        if not self.dependencies_available:
            return {
                'watermark_detected': False,
                'confidence': 'N/A',
                'status': '❌ Vision AI not available. Install: pip install pillow numpy',
                'error': 'Dependencies missing'
            }
        
        try:
            from PIL import Image
            import numpy as np
            import os
            
            # Check file exists
            if not os.path.exists(image_path):
                return {
                    'watermark_detected': False,
                    'confidence': 'N/A',
                    'status': f'❌ File not found: {image_path}',
                    'error': 'File not found'
                }
            
            logger.info(f"🔍 Analyzing image: {image_path}")
            
            # Load image
            image = Image.open(image_path).convert('RGB')
            img_array = np.array(image)
            
            # Run detection algorithms
            text_result = self._detect_text_watermark(img_array)
            logo_result = self._detect_logo_watermark(img_array)
            overlay_result = self._detect_overlay_watermark(img_array)
            
            # Calculate overall detection
            detections = [text_result, logo_result, overlay_result]
            max_confidence = max([d['confidence'] for d in detections])
            watermark_detected = any([d['detected'] for d in detections])
            
            # Determine watermark type
            watermark_types = []
            if text_result['detected']:
                watermark_types.append('text')
            if logo_result['detected']:
                watermark_types.append('logo')
            if overlay_result['detected']:
                watermark_types.append('overlay')
            
            # Build status message
            if watermark_detected:
                if max_confidence > 0.7:
                    status = f"⚠️ HIGH CONFIDENCE watermark detected: {', '.join(watermark_types)}"
                elif max_confidence > 0.5:
                    status = f"⚠️ MEDIUM CONFIDENCE watermark detected: {', '.join(watermark_types)}"
                else:
                    status = f"🔍 LOW CONFIDENCE watermark detected: {', '.join(watermark_types)}"
            else:
                status = "✅ No watermark detected - Image is clear"
            
            logger.info(f"Detection result: {watermark_detected} (confidence: {max_confidence:.2f})")
            
            return {
                'watermark_detected': watermark_detected,
                'confidence': f"{max_confidence:.1%}",
                'status': status,
                'details': {
                    'text_watermark': text_result,
                    'logo_watermark': logo_result,
                    'overlay_watermark': overlay_result
                },
                'image_size': f"{image.width}x{image.height}",
                'file_size': f"{os.path.getsize(image_path) / 1024:.1f} KB"
            }
        
        except ImportError as e:
            return {
                'watermark_detected': False,
                'confidence': 'N/A',
                'status': f'❌ Missing dependency: {e}. Install: pip install pillow numpy',
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error detecting watermark: {e}")
            return {
                'watermark_detected': False,
                'confidence': 'N/A',
                'status': f'❌ Error: {str(e)}',
                'error': str(e)
            }
    
    def _detect_text_watermark(self, img_array) -> Dict:
        """
        Detect text-based watermarks using edge detection
        Text has high edge density and specific patterns
        """
        try:
            import numpy as np
            
            # Convert to grayscale
            gray = np.mean(img_array, axis=2)
            
            # Calculate horizontal and vertical edges
            h_edges = np.abs(np.diff(gray, axis=1))
            v_edges = np.abs(np.diff(gray, axis=0))
            
            # Calculate edge density
            h_density = np.mean(h_edges)
            v_density = np.mean(v_edges)
            avg_density = (h_density + v_density) / 2
            
            # Text has edge density typically > 12
            detected = avg_density > 12
            confidence = min(avg_density / 30, 1.0)
            
            logger.debug(f"Text detection: density={avg_density:.2f}, detected={detected}")
            
            return {
                'detected': detected,
                'confidence': float(confidence),
                'method': 'edge_density',
                'edge_density': float(avg_density)
            }
        
        except Exception as e:
            logger.debug(f"Text watermark detection failed: {e}")
            return {'detected': False, 'confidence': 0.0}
    
    def _detect_logo_watermark(self, img_array) -> Dict:
        """
        Detect logo watermarks in corners
        Logos typically appear in image corners with distinct colors
        """
        try:
            import numpy as np
            
            height, width, _ = img_array.shape
            
            # Check 4 corners (typical logo positions)
            corner_size = min(height // 5, width // 5)
            
            corners = [
                img_array[:corner_size, :corner_size],          # Top-left
                img_array[:corner_size, -corner_size:],         # Top-right
                img_array[-corner_size:, :corner_size],         # Bottom-left
                img_array[-corner_size:, -corner_size:]          # Bottom-right
            ]
            
            # Calculate variance in corners vs center
            center_y, center_x = height // 2, width // 2
            center_area = img_array[
                center_y - corner_size//2 : center_y + corner_size//2,
                center_x - corner_size//2 : center_x + corner_size//2
            ]
            
            corner_vars = [np.var(corner) for corner in corners]
            center_var = np.var(center_area)
            
            # Logo detected if corner variance significantly higher than center
            max_corner_var = max(corner_vars)
            variance_ratio = max_corner_var / (center_var + 1)  # Avoid div by zero
            
            detected = variance_ratio > 1.5 and max_corner_var > 300
            confidence = min(variance_ratio / 3, 1.0)
            
            logger.debug(f"Logo detection: ratio={variance_ratio:.2f}, detected={detected}")
            
            return {
                'detected': detected,
                'confidence': float(confidence),
                'method': 'corner_variance',
                'variance_ratio': float(variance_ratio)
            }
        
        except Exception as e:
            logger.debug(f"Logo watermark detection failed: {e}")
            return {'detected': False, 'confidence': 0.0}
    
    def _detect_overlay_watermark(self, img_array) -> Dict:
        """
        Detect semi-transparent overlay watermarks
        These create uniform color shifts across image
        """
        try:
            import numpy as np
            
            # Calculate color channel consistency
            # Overlays create abnormal color distribution
            r_std = np.std(img_array[:, :, 0])
            g_std = np.std(img_array[:, :, 1])
            b_std = np.std(img_array[:, :, 2])
            
            # Check if all channels have similar low variance (overlay signature)
            channel_stds = [r_std, g_std, b_std]
            avg_std = np.mean(channel_stds)
            std_variance = np.var(channel_stds)
            
            # Overlay: low overall std + low variance between channels
            detected = avg_std < 40 and std_variance < 50
            confidence = (60 - avg_std) / 60 if avg_std < 60 else 0
            confidence = max(0, min(confidence, 1.0))
            
            logger.debug(f"Overlay detection: avg_std={avg_std:.2f}, detected={detected}")
            
            return {
                'detected': detected,
                'confidence': float(confidence),
                'method': 'color_uniformity',
                'avg_std': float(avg_std)
            }
        
        except Exception as e:
            logger.debug(f"Overlay watermark detection failed: {e}")
            return {'detected': False, 'confidence': 0.0}
    
    def check_image_quality(self, image_path: str) -> Dict:
        """
        Check overall image quality
        Returns quality score and recommendations
        """
        try:
            from PIL import Image
            import numpy as np
            import os
            
            if not os.path.exists(image_path):
                return {'error': 'File not found'}
            
            image = Image.open(image_path)
            img_array = np.array(image)
            
            # Check resolution
            min_dim = min(image.width, image.height)
            resolution_score = min(min_dim / 1000, 1.0)  # Good if > 1000px
            
            # Check sharpness (Laplacian variance)
            if len(img_array.shape) == 3:
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array
            
            edges = np.abs(np.diff(gray))
            sharpness_score = min(np.mean(edges) / 15, 1.0)
            
            # Overall quality
            quality_score = (resolution_score * 0.5 + sharpness_score * 0.5)
            
            return {
                'quality_score': f"{quality_score:.1%}",
                'resolution': f"{image.width}x{image.height}",
                'resolution_score': f"{resolution_score:.1%}",
                'sharpness_score': f"{sharpness_score:.1%}",
                'file_size': f"{os.path.getsize(image_path) / 1024:.1f} KB",
                'status': '✅ Good quality' if quality_score > 0.7 else '⚠️ Low quality'
            }
        
        except Exception as e:
            return {'error': str(e)}
