from fontTools.ttLib import TTFont
import numpy as np
from PIL import Image, ImageDraw
import os

def render_glyph_to_image(font_path, output_dir, image_size=32):
    # 加载字体
    font = TTFont(font_path)
    glyf_table = font['glyf']
    cmap = font['cmap'].getBestCmap()  # 获取 Unicode 映射
    
    # 检查输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 遍历每个字符
    for codepoint, glyph_name in cmap.items():
        glyph = glyf_table[glyph_name]
        if glyph.isComposite():
            continue  # 跳过复合字形

        # 获取字形轮廓
        coords_data = glyph.getCoordinates(font['glyf'])
        if not coords_data or len(coords_data[0]) == 0:
            print(f"字形 {glyph_name} ({chr(codepoint)}) 没有轮廓，跳过")
            continue  # 跳过空轮廓的字形

        coords, endPts, instructions = coords_data

        # 创建空白二值图
        img = Image.new("1", (image_size, image_size), 1)  # 二值图，默认白色背景
        draw = ImageDraw.Draw(img)

        # 坐标归一化到图像大小
        xmin, ymin = np.min(coords, axis=0)
        xmax, ymax = np.max(coords, axis=0)
        scale_x = (image_size - 2) / (xmax - xmin) if xmax > xmin else 1
        scale_y = (image_size - 2) / (ymax - ymin) if ymax > ymin else 1
        scale = min(scale_x, scale_y)  # 保持比例
        offset_x = (image_size - (xmax - xmin) * scale) / 2 if xmax > xmin else 0
        offset_y = (image_size - (ymax - ymin) * scale) / 2 if ymax > ymin else 0

        # 缩放和居中调整
        transformed_coords = [
            ((x - xmin) * scale + offset_x, (y - ymin) * scale + offset_y)
            for x, y in coords
        ]

        # 绘制路径
        start = 0
        for end in endPts:
            polygon = transformed_coords[start:end + 1]
            draw.polygon(polygon, fill=0)  # 填充黑色
            start = end + 1

        # 保存为 PNG 图像，文件名使用 Unicode 码点
        img.save(os.path.join(output_dir, f"{codepoint:04X}.png"))

    print(f"所有字形已保存为二值图像到: {output_dir}")

# 示例使用
font_path = './AlibabaPuHuiTi-3-55-Regular/AlibabaPuHuiTi-3-55-Regular.ttf'
output_dir = './vector_binary_images'
render_glyph_to_image(font_path, output_dir, image_size=32)
