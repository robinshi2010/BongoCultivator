from PIL import Image, ImageDraw, ImageFilter

def create_tray_icon():
    size = (128, 128)
    # 创建透明背景
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 颜色定义
    gold_core = (255, 223, 0, 255) # 金色
    gold_highlight = (255, 255, 200, 255) # 高光
    aura_purple = (147, 112, 219, 150) # 紫气
    
    center = (size[0] // 2, size[1] // 2)
    radius = 40
    
    # 画光晕 (多层圆)
    for r in range(radius + 15, radius, -1):
        alpha = int(150 * (1 - (r - radius) / 15))
        draw.ellipse([center[0]-r, center[1]-r, center[0]+r, center[1]+r], 
                     fill=(147, 112, 219, alpha), outline=None)

    # 画金丹主体
    draw.ellipse([center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius], 
                 fill=gold_core, outline=(218, 165, 32, 255), width=2)
    
    # 画太极风格的阴影/高光 (简单的弧线暗示)
    # 左上高光
    draw.chord([center[0]-radius+5, center[1]-radius+5, center[0]+radius-5, center[1]+radius-5],
               135, 225, fill=gold_highlight, outline=None)
    
    # 画一些神秘符文 (简化为点)
    dot_radius = 3
    positions = [
        (center[0], center[1] - radius + 10),
        (center[0] - radius + 10, center[1] + 10),
        (center[0] + radius - 10, center[1] + 10),
    ]
    for pos in positions:
        draw.ellipse([pos[0]-dot_radius, pos[1]-dot_radius, pos[0]+dot_radius, pos[1]+dot_radius],
                     fill=(255, 255, 255, 200))

    # 保存
    output_path = "assets/tray_icon.png"
    image.save(output_path, "PNG")
    print(f"Icon generated at {output_path}")

if __name__ == "__main__":
    create_tray_icon()
