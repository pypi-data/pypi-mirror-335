from fontTools.ttLib import TTFont

font = TTFont('./AlibabaPuHuiTi-3-55-Regular/AlibabaPuHuiTi-3-55-Regular.ttf')
unicode_map = font['cmap'].tables[0].ttFont.getBestCmap()
glyf_map = font['glyf']
words = '一二龍三四'
for word in words:
    print(ord(word))
    if ord(word) in unicode_map and len(glyf_map[unicode_map[ord(word)]].getCoordinates(0)[0]) > 0:
        print(f'字体库中有：【{word}】这个汉字')
        continue
    print(f'字体库没有：【{word}】这个汉字')

def list_all_characters_in_font(font_path, output_file):
    with open(output_file, '+a', encoding='utf-8') as char_file:
        font = TTFont(font_path)
        unicode_map = font['cmap'].tables[0].ttFont.getBestCmap()
        # 过滤 CJK 扩展 A-F 区间
        cjk_extensions = [
            (chr(codepoint), f"{codepoint:04X}")
            for codepoint in unicode_map.keys()
            if 0x3400 <= codepoint <= 0x9FFF or 0x20000 <= codepoint <= 0x2FFFF
        ]
        
        char_file.write("CJK扩展字符\tUnicode码点\n")
        char_file.write("==========\t============\n")
        for char, codepoint in cjk_extensions:
            char_file.write(f"{codepoint}\n")
    print(f"已将字体中的 CJK 扩展字符保存到 {output_file}")


# Example usage
list_all_characters_in_font('./AlibabaPuHuiTi-3-55-Regular/AlibabaPuHuiTi-3-55-Regular.ttf', 'cjk_extensions.txt')
list_all_characters_in_font('./AlibabaPuHuiTi-3-55-RegularL3/AlibabaPuHuiTi-3-55-RegularL3.ttf', 'cjk_extensions.txt')


# char_file = open('chat_file.txt', 'r')
