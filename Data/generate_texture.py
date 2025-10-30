#!/usr/bin/env python3
"""
Generate a texture image with dice numbers for the platonic solids
This creates a single image file with all numbers from 1-20 arranged in a grid
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_dice_texture():
    # Create a large image to hold all numbers
    # We need numbers 1-20 for the icosahedron
    img_width = 2048
    img_height = 2048
    img = Image.new('RGBA', (img_width, img_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fallback to default if not available
    try:
        # Try different font sizes and paths
        font_size = 200
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
    
    # Draw numbers in a grid
    # For simplicity, we'll create sections for different dice
    
    # Tetrahedron (4 numbers) - 2x2 grid in top-left quadrant
    numbers_4 = [1, 2, 3, 4]
    cell_width = img_width // 2
    cell_height = img_height // 2
    
    for i, num in enumerate(numbers_4):
        row = i // 2
        col = i % 2
        x = col * (cell_width // 2)
        y = row * (cell_height // 2)
        
        # Draw a colored background for visibility
        draw.rectangle([x, y, x + cell_width // 2, y + cell_height // 2], 
                      fill=(220, 220, 255, 255))
        
        # Draw the number centered
        text = str(num)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = x + (cell_width // 2 - text_width) // 2
        text_y = y + (cell_height // 2 - text_height) // 2
        draw.text((text_x, text_y), text, fill=(0, 0, 0, 255), font=font)
    
    # Cube (6 numbers) - 3x2 grid
    numbers_6 = [1, 2, 3, 4, 5, 6]
    cube_cell_w = img_width // 3
    cube_cell_h = img_height // 2
    
    for i, num in enumerate(numbers_6):
        row = i // 3
        col = i % 3
        x = col * cube_cell_w
        y = row * cube_cell_h
        
        draw.rectangle([x, y, x + cube_cell_w, y + cube_cell_h], 
                      fill=(255, 220, 220, 255))
        
        text = str(num)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = x + (cube_cell_w - text_width) // 2
        text_y = y + (cube_cell_h - text_height) // 2
        draw.text((text_x, text_y), text, fill=(0, 0, 0, 255), font=font)
    
    # Octahedron (8 numbers) - 4x2 grid
    numbers_8 = [1, 2, 3, 4, 5, 6, 7, 8]
    oct_cell_w = img_width // 4
    oct_cell_h = img_height // 2
    
    for i, num in enumerate(numbers_8):
        row = i // 4
        col = i % 4
        x = col * oct_cell_w
        y = row * oct_cell_h
        
        draw.rectangle([x, y, x + oct_cell_w, y + oct_cell_h], 
                      fill=(220, 255, 220, 255))
        
        text = str(num)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = x + (oct_cell_w - text_width) // 2
        text_y = y + (oct_cell_h - text_height) // 2
        draw.text((text_x, text_y), text, fill=(0, 0, 0, 255), font=font)
    
    # Dodecahedron (12 numbers) - 4x3 grid
    numbers_12 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    dod_cell_w = img_width // 4
    dod_cell_h = img_height // 3
    
    for i, num in enumerate(numbers_12):
        row = i // 4
        col = i % 4
        x = col * dod_cell_w
        y = row * dod_cell_h
        
        draw.rectangle([x, y, x + dod_cell_w, y + dod_cell_h], 
                      fill=(220, 220, 255, 255))
        
        text = str(num)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = x + (dod_cell_w - text_width) // 2
        text_y = y + (dod_cell_h - text_height) // 2
        draw.text((text_x, text_y), text, fill=(0, 0, 0, 255), font=font)
    
    # Icosahedron (20 numbers) - 5x4 grid
    numbers_20 = list(range(1, 21))
    ico_cell_w = img_width // 5
    ico_cell_h = img_height // 4
    
    for i, num in enumerate(numbers_20):
        row = i // 5
        col = i % 5
        x = col * ico_cell_w
        y = row * ico_cell_h
        
        draw.rectangle([x, y, x + ico_cell_w, y + ico_cell_h], 
                      fill=(255, 220, 255, 255))
        
        text = str(num)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = x + (ico_cell_w - text_width) // 2
        text_y = y + (ico_cell_h - text_height) // 2
        draw.text((text_x, text_y), text, fill=(0, 0, 0, 255), font=font)
    
    return img


if __name__ == "__main__":
    print("Generating dice texture...")
    img = create_dice_texture()
    
    # Save to the Data directory (capital D - matching starter code path)
    output_path = "../Data/dice_numbers.png"
    
    # Create Data directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    img.save(output_path)
    print(f"Texture saved to: {output_path}")
    print("Texture created successfully!")
    
    # Also save a copy in the current directory for easy viewing
    img.save("dice_numbers.png")
    print("Copy also saved to: dice_numbers.png")
