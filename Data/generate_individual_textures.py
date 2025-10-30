#!/usr/bin/env python3
"""
Generate individual texture images for dice numbers 1-20
Creates separate files: 1.png, 2.png, 3.png, ... 20.png
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_individual_number_textures():
    """Create 20 separate image files, one for each number"""
    
    # Image size for each number
    img_size = 512  # 512x512 pixels per number
    
    # Try to use a nice font, fallback to default if not available
    try:
        font_size = 350
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "arial.ttf"
        ]
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Create output directory if it doesn't exist
    output_dir = "../Data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate each number as a separate file
    for number in range(1, 21):
        # Create a new image for this number
        img = Image.new('RGBA', (img_size, img_size), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Choose a background color (light color for contrast)
        bg_color = (240, 240, 255, 255)  # Light blue
        draw.rectangle([0, 0, img_size, img_size], fill=bg_color)
        
        # Draw the number centered
        text = str(number)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (img_size - text_width) // 2
        text_y = (img_size - text_height) // 2
        
        # Draw black text
        draw.text((text_x, text_y), text, fill=(0, 0, 0, 255), font=font)
        
        # Save the image
        filename = f"{output_dir}/{number}.png"
        img.save(filename)
        print(f"Created: {filename}")
    
    print(f"\n✓ Successfully created 20 texture files in {output_dir}/")
    print("Files: 1.png, 2.png, 3.png, ..., 20.png")


if __name__ == "__main__":
    print("Generating individual dice number textures...")
    create_individual_number_textures()
    print("\nDone!")
