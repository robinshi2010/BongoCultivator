import sys
import os
from PIL import Image
from collections import deque

def remove_background(image_path, tolerance=30):
    try:
        img = Image.open(image_path).convert("RGBA")
        datas = img.load()
        width, height = img.size
        
        # Get background color from top-left corner
        bg_color = datas[0, 0]
        
        # If already transparent, maybe skip? But AI sometimes generates transparent pixels as white/checkerboard visually but not alpha.
        # Assuming we are removing a solid color background (likely white).
        
        # Function to check if a pixel is similar to bg color
        def is_similar(c1, c2, tol):
            return (abs(c1[0] - c2[0]) <= tol and
                    abs(c1[1] - c2[1]) <= tol and
                    abs(c1[2] - c2[2]) <= tol)

        # Flood fill algorithm
        queue = deque([(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]) # Start from corners
        visited = set(queue)
        
        # Check if corners are actually background-ish 
        # (If artwork touches corner, this might be bad, but usually sprite sheets have padding)
        # We process queue items only if they match bg_color
        
        # Refined queue initialization: only add corners that look like bg
        queue = deque()
        corners = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
        for x, y in corners:
            if is_similar(datas[x, y], bg_color, tolerance):
                queue.append((x, y))
                visited.add((x, y))
        
        if not queue:
            print(f"Skipping {image_path}: Corners do not match background or no convenient background found.")
            return

        while queue:
            x, y = queue.popleft()
            
            # Set pixel to transparent
            # Keep RGB but set Alpha to 0
            r, g, b, a = datas[x, y]
            datas[x, y] = (r, g, b, 0)
            
            # Check neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if (nx, ny) not in visited:
                        idx_color = datas[nx, ny]
                        if is_similar(idx_color, bg_color, tolerance) and idx_color[3] != 0:
                            visited.add((nx, ny))
                            queue.append((nx, ny))
                            
        img.save(image_path, "PNG")
        print(f"Processed: {image_path}")

    except Exception as e:
        print(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    targets = [

        "assets/cultivator_drag.png"

    ]
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming script is in src/tools/ or valid relative path
    # But user runs valid python, let's just make paths absolute based on current CWD which is project root
    project_root = os.getcwd() # USER CWD is /Volumes/home/mac/robin/bongo
    
    for rel_path in targets:
        full_path = os.path.join(project_root, rel_path)
        if os.path.exists(full_path):
            remove_background(full_path)
        else:
            print(f"File not found: {full_path}")
