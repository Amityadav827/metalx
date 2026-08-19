"""Square-crop all partition JPGs — center crop, white background, 1200x1200."""
from PIL import Image, ImageFilter
import os

FOLDER  = "images/products/partitions"
SIZE    = 1200
PADDING = 0.08

def get_product_bbox(img, threshold=240):
    """Find bounding box of non-white content."""
    w, h = img.size
    pix = img.load()
    min_x, min_y = w, h
    max_x, max_y = 0, 0
    for y in range(h):
        for x in range(w):
            px = pix[x, y]
            r, g, b = px[0], px[1], px[2]
            brightness = (r*0.299 + g*0.587 + b*0.114)
            if brightness < threshold:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    if max_x > min_x and max_y > min_y:
        return (min_x, min_y, max_x, max_y)
    return None

def process(path, out_path, size=1200, padding=0.08):
    img = Image.open(path).convert("RGB")
    w, h = img.size

    # For partitions — product fills most of frame, just do center square crop
    # Find shorter dimension
    sq = min(w, h)
    cx, cy = w // 2, h // 2
    x0 = cx - sq // 2
    y0 = cy - sq // 2
    x1 = x0 + sq
    y1 = y0 + sq

    # Clamp
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    cropped = img.crop((x0, y0, x1, y1))
    cw, ch = cropped.size

    # Make perfect square canvas
    sq2 = max(cw, ch)
    canvas = Image.new("RGB", (sq2, sq2), (255, 255, 255))
    canvas.paste(cropped, ((sq2 - cw) // 2, (sq2 - ch) // 2))

    final = canvas.resize((size, size), Image.LANCZOS)
    final.save(out_path, "JPEG", quality=92, optimize=True)

files = sorted(f for f in os.listdir(FOLDER)
               if f.upper().endswith('.JPG') and not f.startswith('_'))

print(f"Processing {len(files)} partition images...\n")
for i, fname in enumerate(files, 1):
    src = os.path.join(FOLDER, fname)
    # Save as _sq.jpg (keep originals)
    out = os.path.join(FOLDER, fname.replace('.JPG', '_sq.JPG'))
    process(src, out)
    print(f"  [{i:02d}]  {fname}  →  {fname.replace('.JPG','_sq.JPG')}")

print(f"\n✓ Done. {len(files)} square crops saved.")
