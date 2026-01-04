from PIL import Image
import os

path = "assets/cultivator_alchemy_high.png"
if os.path.exists(path):
    with Image.open(path) as img:
        print(f"{path}: {img.size} mode={img.mode}")
