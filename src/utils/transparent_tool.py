from PIL import Image
import os

def process_image(img_path):
    if not os.path.exists(img_path):
        return
        
    img = Image.open(img_path)
    img = img.convert("RGBA")
    datas = img.getdata()

    # 简单的去背逻辑：获取左上角像素颜色作为背景色
    # 注意：这假设背景是纯色的。如果是有噪点的（比如生成的图），可能需要容差。
    # 这里我们先尝试用左上角颜色
    bg_color = datas[0]
    
    new_data = []
    # 容差范围
    tolerance = 10 
    
    for item in datas:
        # 计算色差
        diff = sum([abs(item[i] - bg_color[i]) for i in range(3)])
        
        # 如果接近背景色，或者是灰色棋盘格（常见的情况）
        # 有时候生成的图会带有灰白相间的棋盘格来表示透明
        is_transparent_grid = False
        
        # 简单的背景色剔除
        if diff < tolerance:
            new_data.append((255, 255, 255, 0))
        # 针对灰白棋盘格的特殊处理 (如果是灰色或白色)
        # 往往是 (255, 255, 255) 或 (204, 204, 204)
        elif (item[0] > 200 and item[1] > 200 and item[2] > 200): 
            # 这是一个比较暴力的假设：假设所有高亮灰白都是背景
            # 为了防止误伤主体（白色衣服），我们最好还是只去掉纯色背景
            # 如果主体是白衣服，容易误伤。
            # 暂时先只处理左上角背景色。
            new_data.append(item) 
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save(img_path, "PNG")
    print(f"Processed {img_path}")

if __name__ == "__main__":
    # 处理 assets 下的所有 png
    # __file__ 是 src/utils/transparent_tool.py
    # dirname -> src/utils
    # dirname -> src
    # dirname -> root
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assets_dir = os.path.join(root_dir, 'assets')
    print(f"Scanning assets in: {assets_dir}")
    for f in os.listdir(assets_dir):
        if f.endswith('.png'):
            process_image(os.path.join(assets_dir, f))
