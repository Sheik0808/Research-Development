#!/usr/bin/env python
# Script to create KGISL logo image
from PIL import Image, ImageDraw, ImageFont
import os

# Create image with transparent background
width, height = 300, 300
image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
draw = ImageDraw.Draw(image)

# Draw shield shape (blue background)
shield_x, shield_y = 50, 30
shield_w, shield_h = 200, 220

# Draw shield (main blue shape)
draw.rectangle([shield_x, shield_y, shield_x + shield_w, shield_y + shield_h], 
               fill=(0, 51, 102, 255), outline=(204, 153, 0, 255), width=4)

# Draw decorative stripe (gold)
draw.rectangle([shield_x, shield_y + shield_h - 60, shield_x + shield_w, shield_y + shield_h - 35],
               fill=(204, 153, 0, 255))

# Try to load fonts, fallback to default
try:
    font_title = ImageFont.truetype("arial.ttf", 52)
    font_subtitle = ImageFont.truetype("arial.ttf", 16)
    font_small = ImageFont.truetype("arial.ttf", 14)
except:
    try:
        font_title = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 52)
        font_subtitle = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 16)
        font_small = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_small = ImageFont.load_default()

# Add text
draw.text((150, 90), "KGISL", fill=(255, 255, 255, 255), font=font_title, anchor="mm")
draw.text((150, 160), "Institute of", fill=(255, 255, 255, 255), font=font_subtitle, anchor="mm")
draw.text((150, 185), "Technology", fill=(255, 255, 255, 255), font=font_subtitle, anchor="mm")
draw.text((150, 245), "KITE", fill=(0, 51, 102, 255), font=font_small, anchor="mm")

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Save as PNG
output_path = os.path.join(script_dir, 'kgisl_logo.png')
image.save(output_path)
print(f"✓ KGISL logo created successfully: {output_path}")
print(f"✓ Logo dimensions: {width}x{height} pixels")
print(f"✓ File size: {os.path.getsize(output_path) / 1024:.1f} KB")
