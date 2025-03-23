from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
# 读取文件内容并处理
with open("cjk_extensions.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

# '儿儿貝刂'

re_font_path = './AlibabaPuHuiTi-3-55-Regular/AlibabaPuHuiTi-3-55-Regular.ttf'
l3_font_path = './AlibabaPuHuiTi-3-55-RegularL3/AlibabaPuHuiTi-3-55-RegularL3.ttf'

font = TTFont('./AlibabaPuHuiTi-3-55-Regular/AlibabaPuHuiTi-3-55-Regular.ttf')
font_l3 = TTFont('./AlibabaPuHuiTi-3-55-RegularL3/AlibabaPuHuiTi-3-55-RegularL3.ttf')
unicode_map = font['cmap'].tables[0].ttFont.getBestCmap()
glyf_map = font['glyf']

unicode_map_l3 = font_l3['cmap'].tables[0].ttFont.getBestCmap()
glyf_map_l3 = font_l3['glyf']

image_size = 64
output_dir = 'font_images64'

output_dir = Path(output_dir)
output_dir.mkdir(parents=True, exist_ok=True)

try:
    pil_font = ImageFont.truetype(re_font_path, size=image_size - 5)
except Exception as e:
    print(f"加载字体失败: {e}")

try:
    pil_font_l3 = ImageFont.truetype(l3_font_path, size=image_size - 5)
except Exception as e:
    print(f"加载字体失败: {e}")

# 将每行的字符串解析为对应的 Unicode 字符
decoded_chars = []
for line in lines:
    # 去掉多余的字符，如换行符和 b' 前后缀
    word = int(line.strip(), 16)
    # 使用 `unicode_escape` 解码
    char = chr(word)
    if word in unicode_map and len(glyf_map[unicode_map[word]].getCoordinates(0)[0]) > 0:
        print(f'字体库中有：【{word}】这个字')
        img = Image.new("L", (image_size, image_size), color=255)
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), char, font=pil_font)
        if bbox:
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (image_size - text_width) // 2
            y = (image_size - text_height) // 2 - bbox[1]
            draw.text((x, y), char, fill=0, font=pil_font)
            img.save(output_dir / f"{ord(char):04X}.png")
    else:
        if word in unicode_map_l3 and len(glyf_map_l3[unicode_map_l3[word]].getCoordinates(0)[0]) > 0:
            print(f'字体库l3有：【{word}】这个字')
            img = Image.new("L", (image_size, image_size), color=255)
            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((0, 0), char, font=pil_font_l3)
            if bbox:
                text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                x = (image_size - text_width) // 2
                y = (image_size - text_height) // 2 - bbox[1]
                draw.text((x, y), char, fill=0, font=pil_font_l3)
                img.save(output_dir / f"{ord(char):04X}.png")
        else:
            print(f'字体库没有：【{word}】这个字')
