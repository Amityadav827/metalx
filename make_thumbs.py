"""Generate tiny 120x120 JPEG thumbnails for the image sorter."""
import os
from PIL import Image

SRC  = "images/products"
DEST = "images/thumbs"
SIZE = (120, 120)
QUALITY = 40   # very low quality — fast load, still recognisable

os.makedirs(DEST, exist_ok=True)

files = sorted(f for f in os.listdir(SRC) if f.upper().endswith(".JPG"))
total = len(files)

for i, fname in enumerate(files, 1):
    src_path  = os.path.join(SRC, fname)
    dest_path = os.path.join(DEST, fname)
    if os.path.exists(dest_path):
        continue
    try:
        img = Image.open(src_path)
        img.thumbnail(SIZE, Image.LANCZOS)
        # paste on white square background
        bg = Image.new("RGB", SIZE, (245, 242, 236))
        offset = ((SIZE[0] - img.width) // 2, (SIZE[1] - img.height) // 2)
        bg.paste(img, offset)
        bg.save(dest_path, "JPEG", quality=QUALITY, optimize=True)
    except Exception as e:
        print(f"  skip {fname}: {e}")

    if i % 50 == 0 or i == total:
        print(f"  {i}/{total} done")

print(f"\nThumbnails saved to: {DEST}")
