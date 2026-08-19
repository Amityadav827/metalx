"""
Rename + Square-crop all baluster images.
- Detects the product area (non-white pixels)
- Crops tight around product
- Places on 1:1 white square canvas with padding
- Saves as clean PNG with proper name
"""
from PIL import Image, ImageChops
import os, shutil

FOLDER  = "images/products/balusters"
SIZE    = 1200          # output square size
PADDING = 0.10          # 10% padding around product
BG      = (255, 255, 255, 255)   # white bg

# ── 34 unique baluster names (in order of timestamp) ──────────
NAMES = [
    "square-baluster",
    "round-baluster",
    "twist-baluster",
    "knuckle-baluster",
    "fluted-baluster",
    "basket-baluster",
    "spear-tip-baluster",
    "hollow-square-baluster",
    "scroll-baluster",
    "ornate-baluster",
    "flat-bar-baluster",
    "grooved-round-baluster",
    "diamond-pattern-baluster",
    "ribbed-baluster",
    "tapered-baluster",
    "double-twist-baluster",
    "vine-scroll-baluster",
    "classic-pillar-baluster",
    "square-twist-baluster",
    "cage-baluster",
    "arrow-baluster",
    "hammered-baluster",
    "colonial-baluster",
    "wave-baluster",
    "lotus-baluster",
    "finial-baluster",
    "stepped-baluster",
    "barrel-baluster",
    "leaf-scroll-baluster",
    "gothic-baluster",
    "hex-baluster",
    "bold-fluted-baluster",
    "art-deco-baluster",
    "wrought-iron-baluster",
]

def get_product_bbox(img_rgba, threshold=245):
    """Find bounding box of non-white content."""
    r, g, b, a = img_rgba.split()
    # Pixel is 'product' if any channel < threshold OR alpha < 200
    from PIL import ImageFilter
    # Create mask where product exists
    mask = Image.new("L", img_rgba.size, 0)
    pw, ph = img_rgba.size
    pix = img_rgba.load()
    mpix = mask.load()
    for y in range(ph):
        for x in range(pw):
            rv, gv, bv, av = pix[x, y]
            if av < 200:                          # transparent → background
                mpix[x, y] = 0
            elif (rv + gv + bv) / 3 < threshold:  # dark enough → product
                mpix[x, y] = 255
            else:
                mpix[x, y] = 0

    # Find bounding box of non-zero mask
    bbox = mask.getbbox()
    return bbox

def square_crop_product(img_path, out_path, size=1200, padding=0.10):
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size

    # Try to find product bounding box
    bbox = get_product_bbox(img, threshold=240)

    if bbox:
        x0, y0, x1, y1 = bbox
        # Add padding
        pw = x1 - x0
        ph_prod = y1 - y0
        pad_x = int(pw * padding)
        pad_y = int(ph_prod * padding)
        x0 = max(0, x0 - pad_x)
        y0 = max(0, y0 - pad_y)
        x1 = min(w, x1 + pad_x)
        y1 = min(h, y1 + pad_y)
        cropped = img.crop((x0, y0, x1, y1))
    else:
        # No detection — use full image
        cropped = img

    cw, ch = cropped.size

    # Make square: use max dimension
    sq = max(cw, ch)
    canvas = Image.new("RGBA", (sq, sq), (255, 255, 255, 255))

    # Center paste
    px = (sq - cw) // 2
    py = (sq - ch) // 2
    canvas.paste(cropped, (px, py), cropped)

    # Resize to target
    out_img = canvas.resize((size, size), Image.LANCZOS)

    # Save as PNG (keeps transparency if needed, but bg is white anyway)
    out_img.convert("RGB").save(out_path, "PNG", optimize=True)

# ── Process ────────────────────────────────────────────────────
files = sorted(f for f in os.listdir(FOLDER) if f.lower().endswith('.png')
               and f.startswith('ChatGPT'))

print(f"Processing {len(files)} images...\n")

renamed = []
for i, (fname, name) in enumerate(zip(files, NAMES), 1):
    src = os.path.join(FOLDER, fname)
    dst = os.path.join(FOLDER, f"{name}.png")

    print(f"  [{i:02d}/34]  {fname[:35]}...")
    print(f"           → {name}.png")

    square_crop_product(src, dst, size=SIZE, padding=PADDING)
    renamed.append((fname, name + ".png"))

print(f"\n✓ Done. {len(renamed)} images processed.")
print("\nNew filenames:")
for old, new in renamed:
    print(f"  {new}")
