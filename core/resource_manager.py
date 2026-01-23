"""
Resource Manager Module
Handles application resources like icons, logos, and assets
"""

import logging
from pathlib import Path
import base64
from typing import Optional, Dict
import os

logger = logging.getLogger(__name__)

class ResourceManager:
    """Manage application resources (icons, logos, images)"""
    
    def __init__(self, resources_dir: str = 'resources'):
        self.resources_dir = Path(resources_dir)
        self.cache = {}
        self._ensure_resources_dir()
    
    def _ensure_resources_dir(self):
        """Ensure resources directory exists"""
        if not self.resources_dir.exists():
            logger.warning(f"Resources directory not found: {self.resources_dir}")
            self.resources_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created resources directory: {self.resources_dir}")
    
    def get_icon_path(self, icon_name: str = 'application') -> Optional[Path]:
        """
        Get path to application icon
        
        Args:
            icon_name: Icon name (without extension)
        
        Returns:
            Path to icon file or None
        """
        # Try different icon locations and formats
        possible_paths = [
            self.resources_dir / f"{icon_name}.ico",
            self.resources_dir / f"{icon_name}.png",
            self.resources_dir / f"{icon_name}.jpg",
            Path(f"{icon_name}.ico"),
            Path(f"{icon_name}.png"),
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found icon at: {path}")
                return path
        
        logger.warning(f"Icon not found: {icon_name}")
        return None
    
    def get_logo_path(self, logo_name: str = 'logo') -> Optional[Path]:
        """
        Get path to application logo
        
        Args:
            logo_name: Logo name (without extension)
        
        Returns:
            Path to logo file or None
        """
        # Try different logo locations and formats
        possible_paths = [
            self.resources_dir / f"{logo_name}.png",
            self.resources_dir / f"{logo_name}.jpg",
            self.resources_dir / f"{logo_name}.svg",
            Path(f"{logo_name}.png"),
            Path(f"{logo_name}.jpg"),
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found logo at: {path}")
                return path
        
        logger.warning(f"Logo not found: {logo_name}")
        return None
    
    def load_resource_as_base64(self, resource_path: str) -> Optional[str]:
        """
        Load resource file as base64 string
        
        Args:
            resource_path: Path to resource file
        
        Returns:
            Base64 encoded string or None
        """
        try:
            full_path = self.resources_dir / resource_path
            if not full_path.exists():
                logger.error(f"Resource not found: {full_path}")
                return None
            
            with open(full_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        
        except Exception as e:
            logger.error(f"Error loading resource as base64: {e}")
            return None
    
    def get_icon_base64(self, icon_name: str = 'application') -> Optional[str]:
        """
        Get icon as base64 string for web display
        
        Args:
            icon_name: Icon name
        
        Returns:
            Base64 encoded icon or None
        """
        # Check cache first
        cache_key = f"icon_{icon_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        icon_path = self.get_icon_path(icon_name)
        if not icon_path:
            return None
        
        try:
            with open(icon_path, 'rb') as f:
                base64_data = base64.b64encode(f.read()).decode('utf-8')
                self.cache[cache_key] = base64_data
                return base64_data
        
        except Exception as e:
            logger.error(f"Error encoding icon: {e}")
            return None
    
    def get_logo_base64(self, logo_name: str = 'logo') -> Optional[str]:
        """
        Get logo as base64 string for web display
        
        Args:
            logo_name: Logo name
        
        Returns:
            Base64 encoded logo or None
        """
        # Check cache first
        cache_key = f"logo_{logo_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        logo_path = self.get_logo_path(logo_name)
        if not logo_path:
            return None
        
        try:
            with open(logo_path, 'rb') as f:
                base64_data = base64.b64encode(f.read()).decode('utf-8')
                self.cache[cache_key] = base64_data
                return base64_data
        
        except Exception as e:
            logger.error(f"Error encoding logo: {e}")
            return None
    
    def get_icon_html(self, icon_name: str = 'application', size: str = '32x32') -> str:
        """
        Get HTML img tag for icon
        
        Args:
            icon_name: Icon name
            size: Icon size (e.g., '32x32')
        
        Returns:
            HTML img tag
        """
        base64_data = self.get_icon_base64(icon_name)
        if not base64_data:
            logger.warning(f"Could not load icon: {icon_name}")
            return f'<span title="Icon: {icon_name}">📎</span>'
        
        # Detect image type from magic bytes
        image_type = self._detect_image_type(base64_data)
        return f'<img src="data:{image_type};base64,{base64_data}" alt="{icon_name}" width="{size.split("x")[0]}" height="{size.split("x")[1]}" />'
    
    def get_logo_html(self, logo_name: str = 'logo', max_width: str = '200px') -> str:
        """
        Get HTML img tag for logo
        
        Args:
            logo_name: Logo name
            max_width: Maximum width for logo
        
        Returns:
            HTML img tag
        """
        base64_data = self.get_logo_base64(logo_name)
        if not base64_data:
            logger.warning(f"Could not load logo: {logo_name}")
            return f'<span title="Logo: {logo_name}">🔷</span>'
        
        # Detect image type
        image_type = self._detect_image_type(base64_data)
        return f'<img src="data:{image_type};base64,{base64_data}" alt="{logo_name}" style="max-width: {max_width}; height: auto;" />'
    
    def _detect_image_type(self, base64_data: str) -> str:
        """
        Detect image MIME type from base64 data
        
        Args:
            base64_data: Base64 encoded image data
        
        Returns:
            MIME type string
        """
        # Magic bytes detection
        if base64_data.startswith('/9j/') or base64_data.startswith('iVBOR'):
            if base64_data.startswith('/9j/'):
                return 'image/jpeg'
            else:
                return 'image/png'
        
        # Try to decode first bytes
        try:
            import base64
            first_bytes = base64.b64decode(base64_data[:50])
            
            # PNG
            if first_bytes.startswith(b'\x89PNG'):
                return 'image/png'
            # JPEG
            elif first_bytes.startswith(b'\xff\xd8\xff'):
                return 'image/jpeg'
            # GIF
            elif first_bytes.startswith(b'GIF8'):
                return 'image/gif'
            # WebP
            elif b'WEBP' in first_bytes:
                return 'image/webp'
            # SVG (text-based)
            elif b'svg' in first_bytes.lower():
                return 'image/svg+xml'
        except:
            pass
        
        # Default to PNG
        return 'image/png'
    
    def verify_resources(self) -> Dict[str, bool]:
        """
        Verify that critical resources exist
        
        Returns:
            Dictionary of resource verification results
        """
        results = {
            'icon': bool(self.get_icon_path()),
            'logo': bool(self.get_logo_path())
        }
        
        logger.info(f"Resource verification: {results}")
        return results
    
    def create_default_resources(self):
        """
        Create default/placeholder resources if they don't exist
        """
        try:
            from PIL import Image, ImageDraw
            
            # Create placeholder icon if missing
            icon_path = self.resources_dir / 'application.ico'
            if not icon_path.exists():
                logger.info("Creating placeholder icon...")
                img = Image.new('RGB', (256, 256), color=(73, 109, 137))
                draw = ImageDraw.Draw(img)
                draw.text((90, 110), 'NPD', fill=(255, 255, 255))
                img.save(icon_path)
            
            # Create placeholder logo if missing
            logo_path = self.resources_dir / 'logo.png'
            if not logo_path.exists():
                logger.info("Creating placeholder logo...")
                img = Image.new('RGB', (400, 200), color=(255, 255, 255))
                draw = ImageDraw.Draw(img)
                draw.text((150, 80), 'Nexuzy', fill=(73, 109, 137))
                img.save(logo_path)
            
            logger.info("Default resources created")
        
        except ImportError:
            logger.warning("PIL not available for creating default resources")
        except Exception as e:
            logger.error(f"Error creating default resources: {e}")
    
    def clear_cache(self):
        """Clear resource cache"""
        self.cache.clear()
        logger.info("Resource cache cleared")
