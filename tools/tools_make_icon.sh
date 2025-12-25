#!/bin/bash
# Generate icon.icns from assets/cultivator_idle.png

SRC="assets/cultivator_idle.png"
ICONSET="assets/icon.iconset"

if [ ! -f "$SRC" ]; then
    echo "Source image not found!"
    exit 1
fi

mkdir -p "$ICONSET"

# Resize to required standard sizes
sips -z 16 16     "$SRC" --out "${ICONSET}/icon_16x16.png"
sips -z 32 32     "$SRC" --out "${ICONSET}/icon_16x16@2x.png"
sips -z 32 32     "$SRC" --out "${ICONSET}/icon_32x32.png"
sips -z 64 64     "$SRC" --out "${ICONSET}/icon_32x32@2x.png"
sips -z 128 128   "$SRC" --out "${ICONSET}/icon_128x128.png"
sips -z 256 256   "$SRC" --out "${ICONSET}/icon_128x128@2x.png"
sips -z 256 256   "$SRC" --out "${ICONSET}/icon_256x256.png"
sips -z 512 512   "$SRC" --out "${ICONSET}/icon_256x256@2x.png"
sips -z 512 512   "$SRC" --out "${ICONSET}/icon_512x512.png"
sips -z 1024 1024 "$SRC" --out "${ICONSET}/icon_512x512@2x.png"

# Convert to icns
iconutil -c icns "$ICONSET" -o assets/icon.icns

# Clean up
rm -rf "$ICONSET"

echo "Generated assets/icon.icns"
