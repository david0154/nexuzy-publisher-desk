"""
Vision AI Module - Advanced Image Analysis with Multi-Method Watermark Detection
Implements: Edge detection, Frequency analysis, Opacity detection, Text detection, Logo detection
FIXED: Removed db_path dependency from __init__ to prevent initialization errors
"""

import logging
from typing import Dict, Optional, List, Tuple
import hashlib
import numpy as np
from PIL import Image
import os

logger = logging.getLogger(__name__)

class VisionAI:
    """Advanced image analysis with comprehensive watermark detection"""
    
    def __init__(self):
        """Initialize Vision AI - no parameters needed"""
        self.dependencies_available = self._check_dependencies()
        self.detection_threshold = 0.5
        logger.info("✅ VisionAI initialized successfully")
    
    def _check_dependencies(self) -> bool:
        """Check if required libraries are available"""
        try:
            import PIL
            import numpy as np
            logger.info("✅ Vision AI dependencies available")
            return True
        except ImportError as e:
            logger.warning(f"⚠️ Vision AI dependencies missing: {e}")
            logger.warning("Install: pip install pillow numpy scipy scikit-image")
            return False
    
    def detect_watermark(self, image_path: str) -> Dict:
        """Detect watermarks using MULTIPLE methods"""
        if not self.dependencies_available:
            return {
                'watermark_detected': False,
                'confidence': 'N/A',
                'status': '❌ Vision AI not available',
                'error': 'Dependencies missing'
            }
        
        try:
            if not os.path.exists(image_path):
                return {
                    'watermark_detected': False,
                    'confidence': 'N/A',
                    'status': f'❌ File not found: {image_path}',
                    'error': 'File not found'
                }
            
            logger.info(f"🔍 Analyzing image: {image_path}")
            
            image = Image.open(image_path).convert('RGB')
            img_array = np.array(image, dtype=np.float32)
            
            # Run ALL detection methods
            text_result = self._detect_text_watermark(img_array)
            logo_result = self._detect_logo_watermark(img_array)
            overlay_result = self._detect_overlay_watermark(img_array)
            opacity_result = self._detect_opacity_watermark(img_array)
            frequency_result = self._detect_frequency_watermark(img_array)
            
            detections = [text_result, logo_result, overlay_result, opacity_result, frequency_result]
            confidences = [d['confidence'] for d in detections if d['detected']]
            max_confidence = max(confidences) if confidences else 0
            watermark_detected = any([d['detected'] for d in detections])
            
            watermark_types = []
            detection_methods = []
            
            if text_result['detected']:
                watermark_types.append('text')
                detection_methods.append(f"text({text_result['confidence']:.0%})")
            if logo_result['detected']:
                watermark_types.append('logo')
                detection_methods.append(f"logo({logo_result['confidence']:.0%})")
            if overlay_result['detected']:
                watermark_types.append('overlay')
                detection_methods.append(f"overlay({overlay_result['confidence']:.0%})")
            if opacity_result['detected']:
                watermark_types.append('opacity')
                detection_methods.append(f"opacity({opacity_result['confidence']:.0%})")
            if frequency_result['detected']:
                watermark_types.append('frequency')
                detection_methods.append(f"frequency({frequency_result['confidence']:.0%})")
            
            if watermark_detected:
                methods_str = " + ".join(detection_methods)
                if max_confidence > 0.8:
                    status = f"🔴 HIGH CONFIDENCE watermark: {', '.join(watermark_types)} [{methods_str}]"
                elif max_confidence > 0.6:
                    status = f"🟡 MEDIUM CONFIDENCE watermark: {', '.join(watermark_types)} [{methods_str}]"
                else:
                    status = f"🟢 LOW CONFIDENCE watermark: {', '.join(watermark_types)} [{methods_str}]"
            else:
                status = "✅ No watermark detected - Image is clean"
            
            logger.info(f"Detection complete. Found: {watermark_detected} (confidence: {max_confidence:.1%})")
            
            return {
                'watermark_detected': watermark_detected,
                'confidence': f"{max_confidence:.1%}",
                'confidence_value': float(max_confidence),
                'status': status,
                'methods': detection_methods,
                'details': {
                    'text_watermark': text_result,
                    'logo_watermark': logo_result,
                    'overlay_watermark': overlay_result,
                    'opacity_watermark': opacity_result,
                    'frequency_watermark': frequency_result
                },
                'image_size': f"{image.width}x{image.height}",
                'file_size': f"{os.path.getsize(image_path) / 1024:.1f} KB"
            }
        
        except Exception as e:
            logger.error(f"Error detecting watermark: {e}")
            return {
                'watermark_detected': False,
                'confidence': 'N/A',
                'status': f'❌ Error: {str(e)}',
                'error': str(e)
            }
    
    def _detect_text_watermark(self, img_array: np.ndarray) -> Dict:
        try:
            gray = np.mean(img_array, axis=2)
            h_edges = np.abs(np.diff(gray, axis=1))
            v_edges = np.abs(np.diff(gray, axis=0))
            edge_density = (np.mean(h_edges) + np.mean(v_edges)) / 2
            detected = edge_density > 12
            confidence = min(edge_density / 30, 1.0)
            return {'detected': detected, 'confidence': float(confidence), 'method': 'edge_detection'}
        except:
            return {'detected': False, 'confidence': 0.0, 'method': 'edge_detection'}
    
    def _detect_logo_watermark(self, img_array: np.ndarray) -> Dict:
        try:
            height, width, _ = img_array.shape
            corner_size = min(height // 5, width // 5)
            if corner_size < 20:
                return {'detected': False, 'confidence': 0.0, 'method': 'corner_variance'}
            corners = [
                img_array[:corner_size, :corner_size],
                img_array[:corner_size, -corner_size:],
                img_array[-corner_size:, :corner_size],
                img_array[-corner_size:, -corner_size:]
            ]
            corner_vars = [np.var(corner) for corner in corners]
            max_corner_var = max(corner_vars)
            detected = max_corner_var > 300
            confidence = min(max_corner_var / 1000, 1.0)
            return {'detected': detected, 'confidence': float(confidence), 'method': 'corner_variance'}
        except:
            return {'detected': False, 'confidence': 0.0, 'method': 'corner_variance'}
    
    def _detect_overlay_watermark(self, img_array: np.ndarray) -> Dict:
        try:
            avg_std = np.mean([np.std(img_array[:, :, i]) for i in range(3)])
            detected = avg_std < 40
            confidence = max(0, (60 - avg_std) / 60) if avg_std < 60 else 0
            return {'detected': detected, 'confidence': float(confidence), 'method': 'color_uniformity'}
        except:
            return {'detected': False, 'confidence': 0.0, 'method': 'color_uniformity'}
    
    def _detect_opacity_watermark(self, img_array: np.ndarray) -> Dict:
        try:
            brightness = np.mean(img_array / 255.0, axis=2)
            brightness_std = np.std(brightness)
            detected = brightness_std < 0.15
            confidence = max(0, 1.0 - (brightness_std / 0.2))
            return {'detected': detected, 'confidence': float(confidence), 'method': 'opacity_pattern'}
        except:
            return {'detected': False, 'confidence': 0.0, 'method': 'opacity_pattern'}
    
    def _detect_frequency_watermark(self, img_array: np.ndarray) -> Dict:
        try:
            gray = np.mean(img_array, axis=2)
            fft = np.fft.fft2(gray)
            magnitude = np.abs(np.fft.fftshift(fft))
            center_mean = np.mean(magnitude)
            detected = center_mean > 1000
            confidence = min(center_mean / 5000, 1.0)
            return {'detected': detected, 'confidence': float(confidence), 'method': 'frequency_analysis'}
        except:
            return {'detected': False, 'confidence': 0.0, 'method': 'frequency_analysis'}
