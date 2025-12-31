import os
import subprocess
import shutil

def create_icns(source_png, output_icns):
    iconset_dir = "assets/icon.iconset"
    if os.path.exists(iconset_dir):
        shutil.rmtree(iconset_dir)
    os.makedirs(iconset_dir)

    # Define sizes
    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png")
    ]

    for size, name in sizes:
        out_path = os.path.join(iconset_dir, name)
        cmd = ["sips", "-z", str(size), str(size), source_png, "--out", out_path]
        subprocess.run(cmd, check=True)

    # Convert
    cmd_convert = ["iconutil", "-c", "icns", iconset_dir, "-o", output_icns]
    try:
        subprocess.run(cmd_convert, check=True)
        print(f"Successfully created {output_icns}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create icns: {e}")
    finally:
        shutil.rmtree(iconset_dir)

if __name__ == "__main__":
    create_icns("assets/tray_icon.png", "assets/icon.icns")
