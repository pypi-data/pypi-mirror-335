from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os

def save_characters_as_images(font_path, output_dir, image_size=32):
    try:
        pil_font = ImageFont.truetype(font_path, size=image_size - 5)
    except Exception as e:
        print(f"加载字体失败: {e}")
        return

    font = TTFont(font_path)
    unicode_map = font['cmap'].tables[0].ttFont.getBestCmap()
    all_characters = [chr(codepoint) for codepoint in unicode_map.keys() if chr(codepoint).isprintable()]
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    def process_character(char):
        img = Image.new("L", (image_size, image_size), color=255)
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), char, font=pil_font)
        if bbox:
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (image_size - text_width) // 2
            y = (image_size - text_height) // 2 - bbox[1]
            draw.text((x, y), char, fill=0, font=pil_font)
            img.save(output_dir / f"{ord(char):04X}.png")

    with ThreadPoolExecutor() as executor:
        executor.map(process_character, all_characters)

    print(f"所有字符已保存到: {output_dir}")

image_size=64
# 示例调用
font_path = './AlibabaPuHuiTi-3-55-Regular/AlibabaPuHuiTi-3-55-Regular.ttf'
output_dir = f'./font_images{image_size}'
save_characters_as_images(font_path, output_dir, image_size=image_size)

font_path = './AlibabaPuHuiTi-3-55-RegularL3/AlibabaPuHuiTi-3-55-RegularL3.ttf'
save_characters_as_images(font_path, output_dir, image_size=image_size)
