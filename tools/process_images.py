import os
from PIL import Image
import collections

# 目标图片清单
TARGET_FILES = [
    "cultivator_alchemy_high.png",
    "cultivator_alchemy_low.png",
    "cultivator_alchemy_mid.png",
    "cultivator_cast.png",
    "cultivator_drag.png",
    "cultivator_idle.png",
    "cultivator_read.png",
    "cultivator_walk.png",
    "tribulation_0_foundation.png",
    "tribulation_1_goldcore.png",
    "tribulation_2_nascentsoul.png"
]

def remove_background(image_path, tolerance=30):
    """
    从图片四角开始泛洪填充，移除白色背景
    :param tolerance: 颜色容差 (0-255), 越大越容易把非纯白也当背景
    """
    try:
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size
        pixels = img.load()
        
        # 访问标记矩阵
        visited = set()
        queue = collections.deque()
        
        # 种子点：四个角
        seeds = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
        
        for x, y in seeds:
            if 0 <= x < width and 0 <= y < height:
                queue.append((x, y))
                visited.add((x, y))
        
        # 定义由于是白色背景，我们认为是接近 (255, 255, 255)
        # tolerance 处理 JPG 压缩噪点或抗锯齿灰边
        min_val = 255 - tolerance
        
        def is_background(r, g, b, a):
            # Alpha 已经透明的也是背景
            if a == 0: return True
            # RGB 接近白色
            return r >= min_val and g >= min_val and b >= min_val
        
        count = 0
        while queue:
            x, y = queue.popleft()
            r, g, b, a = pixels[x, y]
            
            if is_background(r, g, b, a):
                # 设为全透明
                pixels[x, y] = (0, 0, 0, 0)
                count += 1
                
                # 检查四周邻居
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append((nx, ny))
        
        print(f"Processed {image_path}: Cleared {count} pixels.")
        img.save(image_path, "PNG") # 覆盖原文件
        return True
        
    except Exception as e:
        print(f"Failed to process {image_path}: {e}")
        return False

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
    
    print(f"Target Assets Directory: {base_dir}")
    
    success_count = 0
    for filename in TARGET_FILES:
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            if remove_background(path):
                success_count += 1
        else:
            print(f"File not found: {filename}")
            
    print("-" * 30)
    print(f"Batch processing complete. Success: {success_count}/{len(TARGET_FILES)}")

if __name__ == "__main__":
    main()
