"""
Logo and Icon Generator
Creates logo.png and icon.ico automatically
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_logo():
    """Create Nexuzy logo"""
    # Create 512x512 logo
    img = Image.new('RGB', (512, 512), color='#3498db')
    draw = ImageDraw.Draw(img)
    
    # Draw 'N' letter
    draw.polygon([
        (100, 100), (150, 100), (150, 350),
        (300, 150), (300, 100), (350, 100),
        (350, 412), (300, 412), (300, 262),
        (150, 412), (100, 412)
    ], fill='white')
    
    # Save as PNG
    img.save('logo.png', 'PNG')
    print("✅ Created: logo.png")
    
    # Create smaller versions for icon
    sizes = [256, 128, 64, 48, 32, 16]
    images = []
    
    for size in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        images.append(resized)
    
    # Save as ICO
    images[0].save('icon.ico', format='ICO', sizes=[(s, s) for s in sizes])
    print("✅ Created: icon.ico")

if __name__ == '__main__':
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    create_logo()
    print("\n🎨 Logo and icon created successfully!")
