"""
Vision AI Module - Advanced Image Analysis with Multi-Method Watermark Detection
Implements: Edge detection, Frequency analysis, Opacity detection, Text detection, Logo detection

FIXED: Removed db_path parameter from __init__() to prevent initialization errors
KEPT: All your comprehensive watermark detection methods and quality checking
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
        """Initialize Vision AI - FIXED: No db_path parameter needed"""
        self.dependencies_available = self._check_dependencies()
        self.detection_threshold = 0.5  # Configurable threshold
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
        """
        Detect watermarks using MULTIPLE methods
        
        Args:
            image_path: Path to local image file
        
        Returns:
            Dict with comprehensive watermark detection results
        """
        if not self.dependencies_available:
            return {
                'watermark_detected': False,
                'confidence': 'N/A',
                'status': '❌ Vision AI not available. Install: pip install pillow numpy scipy scikit-image',
                'error': 'Dependencies missing'
            }
        
        try:
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
            img_array = np.array(image, dtype=np.float32)
            
            # Run ALL detection methods
            text_result = self._detect_text_watermark(img_array)
            logo_result = self._detect_logo_watermark(img_array)
            overlay_result = self._detect_overlay_watermark(img_array)
            opacity_result = self._detect_opacity_watermark(img_array)
            frequency_result = self._detect_frequency_watermark(img_array)
            
            # Aggregate results
            detections = [
                text_result, 
                logo_result, 
                overlay_result, 
                opacity_result, 
                frequency_result
            ]
            
            confidences = [d['confidence'] for d in detections if d['detected']]
            max_confidence = max(confidences) if confidences else 0
            watermark_detected = any([d['detected'] for d in detections])
            
            # Determine watermark types
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
            
            # Build status message
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
        
        except ImportError as e:
            return {
                'watermark_detected': False,
                'confidence': 'N/A',
                'status': f'❌ Missing dependency: {e}. Install: pip install pillow numpy scipy scikit-image',
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
    
    def _detect_text_watermark(self, img_array: np.ndarray) -> Dict:
        """
        Detect text-based watermarks using edge detection
        Text watermarks have high edge density and specific patterns
        """
        try:
            # Convert to grayscale
            gray = np.mean(img_array, axis=2)
            
            # Compute edges in both directions
            h_edges = np.abs(np.diff(gray, axis=1))
            v_edges = np.abs(np.diff(gray, axis=0))
            
            # Calculate edge density
            h_density = np.mean(h_edges)
            v_density = np.mean(v_edges)
            edge_density = (h_density + v_density) / 2
            
            # Compute laplacian for sharpness
            laplacian_x = np.convolve(gray[0], [-1, 0, 1], mode='same')
            laplacian_y = np.convolve(gray[:, 0], [-1, 0, 1], mode='same')
            sharpness = np.std(laplacian_x) + np.std(laplacian_y)
            
            # Text has high edge density typically > 12 and high sharpness
            detected = edge_density > 12 and sharpness > 5
            confidence = min((edge_density / 30) * (sharpness / 20), 1.0)
            
            logger.debug(f"Text detection: edge_density={edge_density:.2f}, sharpness={sharpness:.2f}, detected={detected}")
            
            return {
                'detected': detected,
                'confidence': float(confidence),
                'method': 'edge_detection',
                'metrics': {
                    'edge_density': float(edge_density),
                    'sharpness': float(sharpness)
                }
            }
        
        except Exception as e:
            logger.debug(f"Text watermark detection failed: {e}")
            return {'detected': False, 'confidence': 0.0, 'method': 'edge_detection'}
    
    def _detect_logo_watermark(self, img_array: np.ndarray) -> Dict:
        """
        Detect logo watermarks in corners using variance analysis
        Logos typically appear in image corners with distinct colors
        """
        try:
            height, width, _ = img_array.shape
            
            # Check 4 corners (typical logo positions)
            corner_size = min(height // 5, width // 5)
            
            if corner_size < 20:
                return {'detected': False, 'confidence': 0.0, 'method': 'corner_variance'}
            
            corners = [
                img_array[:corner_size, :corner_size],                    # Top-left
                img_array[:corner_size, -corner_size:],                   # Top-right
                img_array[-corner_size:, :corner_size],                   # Bottom-left
                img_array[-corner_size:, -corner_size:]                    # Bottom-right
            ]
            
            # Calculate variance in corners vs center
            center_y, center_x = height // 2, width // 2
            center_area = img_array[
                max(0, center_y - corner_size//2): min(height, center_y + corner_size//2),
                max(0, center_x - corner_size//2): min(width, center_x + corner_size//2)
            ]
            
            corner_vars = [np.var(corner) for corner in corners]
            center_var = np.var(center_area)
            
            # Logo detected if corner variance significantly higher
            max_corner_var = max(corner_vars)
            variance_ratio = max_corner_var / (center_var + 1)
            
            detected = variance_ratio > 1.5 and max_corner_var > 300
            confidence = min(variance_ratio / 3, 1.0)
            
            logger.debug(f"Logo detection: ratio={variance_ratio:.2f}, max_var={max_corner_var:.2f}, detected={detected}")
            
            return {
                'detected': detected,
                'confidence': float(confidence),
                'method': 'corner_variance',
                'metrics': {
                    'variance_ratio': float(variance_ratio),
                    'max_corner_variance': float(max_corner_var)
                }
            }
        
        except Exception as e:
            logger.debug(f"Logo watermark detection failed: {e}")
            return {'detected': False, 'confidence': 0.0, 'method': 'corner_variance'}
    
    def _detect_overlay_watermark(self, img_array: np.ndarray) -> Dict:
        """
        Detect semi-transparent overlay watermarks
        Overlays create uniform color shifts across image
        """
        try:
            # Calculate color channel consistency
            r_std = np.std(img_array[:, :, 0])
            g_std = np.std(img_array[:, :, 1])
            b_std = np.std(img_array[:, :, 2])
            
            # Check if all channels have similar low variance (overlay signature)
            channel_stds = [r_std, g_std, b_std]
            avg_std = np.mean(channel_stds)
            std_variance = np.var(channel_stds)
            
            # Overlay creates uniform low std + balanced channels
            detected = avg_std < 40 and std_variance < 50
            confidence = max(0, (60 - avg_std) / 60) if avg_std < 60 else 0
            confidence = min(confidence, 1.0)
            
            logger.debug(f"Overlay detection: avg_std={avg_std:.2f}, std_var={std_variance:.2f}, detected={detected}")
            
            return {
                'detected': detected,
                'confidence': float(confidence),
                'method': 'color_uniformity',
                'metrics': {
                    'avg_std': float(avg_std),
                    'std_variance': float(std_variance)
                }
            }
        
        except Exception as e:
            logger.debug(f"Overlay watermark detection failed: {e}")
            return {'detected': False, 'confidence': 0.0, 'method': 'color_uniformity'}
    
    def _detect_opacity_watermark(self, img_array: np.ndarray) -> Dict:
        """
        Detect watermarks by opacity patterns
        Semi-transparent watermarks have specific pixel value distributions
        """
        try:
            # Convert to HSV for better opacity detection
            img_normalized = img_array / 255.0
            
            # Calculate brightness variation
            brightness = np.mean(img_normalized, axis=2)
            brightness_std = np.std(brightness)
            
            # Calculate saturation proxy
            max_channel = np.max(img_normalized, axis=2)
            min_channel = np.min(img_normalized, axis=2)
            saturation = (max_channel - min_channel) / (max_channel + 1e-8)
            saturation_mean = np.mean(saturation)
            
            # Opacity watermark: reduced brightness variation + specific saturation
            detected = brightness_std < 0.15 and saturation_mean < 0.3
            confidence = max(0, 1.0 - (brightness_std / 0.2))
            confidence = min(confidence, 1.0)
            
            logger.debug(f"Opacity detection: brightness_std={brightness_std:.3f}, saturation={saturation_mean:.3f}, detected={detected}")
            
            return {
                'detected': detected,
                'confidence': float(confidence),
                'method': 'opacity_pattern',
                'metrics': {
                    'brightness_std': float(brightness_std),
                    'saturation_mean': float(saturation_mean)
                }
            }
        
        except Exception as e:
            logger.debug(f"Opacity watermark detection failed: {e}")
            return {'detected': False, 'confidence': 0.0, 'method': 'opacity_pattern'}
    
    def _detect_frequency_watermark(self, img_array: np.ndarray) -> Dict:
        """
        Detect repeating patterns using frequency analysis (FFT)
        Watermarks often create periodic patterns in frequency domain
        """
        try:
            # Convert to grayscale
            gray = np.mean(img_array, axis=2)
            
            # Compute 2D FFT
            fft = np.fft.fft2(gray)
            fft_shifted = np.fft.fftshift(fft)
            magnitude = np.abs(fft_shifted)
            
            # Log scale for visualization
            magnitude_log = np.log1p(magnitude)
            
            # Analyze frequency spectrum
            height, width = gray.shape
            center_y, center_x = height // 2, width // 2
            
            # Extract center region (low frequencies)
            center_region = magnitude_log[
                max(0, center_y - height//4): min(height, center_y + height//4),
                max(0, center_x - width//4): min(width, center_x + width//4)
            ]
            
            # Extract periphery (high frequencies where watermarks often hide)
            periphery_mask = np.ones_like(magnitude_log, dtype=bool)
            periphery_mask[
                max(0, center_y - height//4): min(height, center_y + height//4),
                max(0, center_x - width//4): min(width, center_x + width//4)
            ] = False
            periphery = magnitude_log[periphery_mask]
            
            # Watermark signature: elevated high frequencies
            center_mean = np.mean(center_region) if center_region.size > 0 else 0
            periphery_mean = np.mean(periphery) if periphery.size > 0 else 0
            
            frequency_ratio = periphery_mean / (center_mean + 1e-8)
            
            # Watermark detected if high frequencies unusually strong
            detected = frequency_ratio > 1.3
            confidence = min((frequency_ratio - 1.0) / 0.5, 1.0) if frequency_ratio > 1.0 else 0
            confidence = min(confidence, 1.0)
            
            logger.debug(f"Frequency detection: ratio={frequency_ratio:.2f}, detected={detected}")
            
            return {
                'detected': detected,
                'confidence': float(confidence),
                'method': 'frequency_analysis',
                'metrics': {
                    'frequency_ratio': float(frequency_ratio),
                    'center_frequency': float(center_mean),
                    'periphery_frequency': float(periphery_mean)
                }
            }
        
        except Exception as e:
            logger.debug(f"Frequency watermark detection failed: {e}")
            return {'detected': False, 'confidence': 0.0, 'method': 'frequency_analysis'}
    
    def check_image_quality(self, image_path: str) -> Dict:
        """
        Check overall image quality and recommend optimizations
        
        Returns:
            Dict with quality metrics and recommendations
        """
        try:
            if not os.path.exists(image_path):
                return {'error': 'File not found'}
            
            image = Image.open(image_path)
            img_array = np.array(image, dtype=np.float32)
            
            # Check resolution
            min_dim = min(image.width, image.height)
            resolution_score = min(min_dim / 1000, 1.0)  # Good if > 1000px
            
            # Check sharpness using Laplacian
            if len(img_array.shape) == 3:
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array
            
            edges = np.abs(np.diff(gray))
            sharpness_score = min(np.mean(edges) / 15, 1.0)
            
            # Check for noise
            noise_level = np.std(img_array)
            noise_score = 1.0 if noise_level < 30 else max(0, 1.0 - (noise_level - 30) / 50)
            
            # Overall quality
            quality_score = (resolution_score * 0.4 + sharpness_score * 0.35 + noise_score * 0.25)
            
            # Recommendations
            recommendations = []
            if resolution_score < 0.7:
                recommendations.append("⚠️ Low resolution - consider upscaling or using higher quality source")
            if sharpness_score < 0.6:
                recommendations.append("⚠️ Image is blurry - consider using a clearer source")
            if noise_level > 30:
                recommendations.append("⚠️ High noise level - consider applying denoising filters")
            
            return {
                'quality_score': f"{quality_score:.1%}",
                'quality_value': float(quality_score),
                'resolution': f"{image.width}x{image.height}",
                'resolution_score': f"{resolution_score:.1%}",
                'sharpness_score': f"{sharpness_score:.1%}",
                'noise_level': f"{noise_level:.1f}",
                'file_size': f"{os.path.getsize(image_path) / 1024:.1f} KB",
                'status': '✅ Excellent quality' if quality_score > 0.8 else ('✅ Good quality' if quality_score > 0.6 else '⚠️ Low quality'),
                'recommendations': recommendations
            }
        
        except Exception as e:
            logger.error(f"Error checking image quality: {e}")
            return {'error': str(e)}
    
    def get_detection_summary(self, image_path: str) -> str:
        """
        Get human-readable summary of all detections
        """
        result = self.detect_watermark(image_path)
        quality = self.check_image_quality(image_path)
        
        summary = f"""
╔══════════════════════════════════════════╗
║        IMAGE ANALYSIS SUMMARY            ║
╚══════════════════════════════════════════╝

📊 WATERMARK DETECTION:
  Status: {result.get('status', 'N/A')}
  Confidence: {result.get('confidence', 'N/A')}
  Methods Used: {', '.join(result.get('methods', []))}

🖼️  IMAGE QUALITY:
  Score: {quality.get('quality_score', 'N/A')}
  Resolution: {quality.get('resolution', 'N/A')}
  Sharpness: {quality.get('sharpness_score', 'N/A')}
  Size: {quality.get('file_size', 'N/A')}
"""
        
        if quality.get('recommendations'):
            summary += "\n💡 RECOMMENDATIONS:\n"
            for rec in quality['recommendations']:
                summary += f"  {rec}\n"
        
        return summary
