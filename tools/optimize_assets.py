from PIL import Image
import os
import sys

def optimize_images(directory):
    total_saved = 0
    print(f"Optimizing images in {directory}...")
    
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(directory, filename)
            try:
                original_size = os.path.getsize(filepath)
                
                # Skip small files (< 200KB) to avoid quality loss on icons/ui elements
                if original_size < 200 * 1024:
                    print(f"Skipping {filename}: too small ({original_size/1024:.1f}KB)")
                    continue

                with Image.open(filepath) as img:
                    # Optimize content
                    # Identify if image has transparency
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        # For PNGs with transparency, we can use optimize=True
                        # reducing colors/palette is risky for visuals without manual check, 
                        # so we rely on zlib compression level optimization by PIL
                        img.save(filepath, optimize=True, quality=85)
                    else:
                        img.save(filepath, optimize=True, quality=85)
                
                new_size = os.path.getsize(filepath)
                saved = original_size - new_size
                total_saved += saved
                
                print(f"Optimized {filename}: {original_size/1024:.1f}KB -> {new_size/1024:.1f}KB (Saved {saved/1024:.1f}KB)")
                
            except Exception as e:
                print(f"Error optimizing {filename}: {e}")

    print(f"\nTotal space saved: {total_saved / (1024*1024):.2f} MB")

if __name__ == "__main__":
    assets_dir = os.path.join(os.getcwd(), 'assets')
    if len(sys.argv) > 1:
        assets_dir = sys.argv[1]
    
    if not os.path.exists(assets_dir):
        print(f"Directory {assets_dir} not found!")
        sys.exit(1)
        
    optimize_images(assets_dir)
