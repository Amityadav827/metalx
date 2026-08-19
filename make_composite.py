"""
MetalX — Premium Product Composite Generator
Creates a realistic installed-context image from a product studio shot.

Concept for DSC05627 (baluster, portrait ~1908x3978):
- Background: elegant dark marble staircase scene (generated via gradients + texture)
- Product: extracted from white bg, placed as vertical railing element
- Lighting: warm golden ambient from top-left, cool shadow right
- Gold accent light strip simulating premium interior lighting
- Final: 1920x1080 landscape — hero-ready
"""

from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageChops
import math, os

OUT_DIR = "images/generated"
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1920, 1080   # output size

# ─── Load product ───────────────────────────────────────────────
prod_path = "images/products/balusters/DSC05627.JPG"
prod_orig = Image.open(prod_path).convert("RGBA")
pw, ph = prod_orig.size

# ─── Step 1: Remove white/light background ──────────────────────
def remove_light_bg(img, threshold=210, feather=12):
    """Replace near-white pixels with transparency, feather edges."""
    r, g, b, a = img.split()
    # Build mask: pixel is bg if all channels > threshold
    mask = Image.new("L", img.size, 0)
    pixels_in  = img.load()
    mask_px    = mask.load()
    for y in range(img.height):
        for x in range(img.width):
            rv, gv, bv, av = pixels_in[x, y]
            brightness = (rv + gv + bv) / 3
            if brightness > threshold:
                # how close to white → more transparent
                alpha_val = max(0, int((255 - brightness) * 2.5))
                mask_px[x, y] = alpha_val
            else:
                mask_px[x, y] = 255

    # Feather / smooth edges
    mask = mask.filter(ImageFilter.GaussianBlur(feather))
    img.putalpha(mask)
    return img

prod_cut = remove_light_bg(prod_orig.copy(), threshold=205, feather=8)

# ─── Step 2: Build premium background ───────────────────────────

bg = Image.new("RGB", (W, H), (18, 14, 10))   # near-black base

draw = ImageDraw.Draw(bg)

# -- Dark marble floor (bottom third) --
floor_y = int(H * 0.68)
for y in range(floor_y, H):
    t = (y - floor_y) / (H - floor_y)
    # dark warm tone, slight reflection
    r = int(28 + t * 18)
    g = int(22 + t * 14)
    b = int(16 + t * 10)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# -- Add subtle marble veining to floor --
for i in range(12):
    import random
    random.seed(i * 7 + 42)
    x1 = random.randint(0, W)
    x2 = x1 + random.randint(-200, 200)
    y1 = floor_y + random.randint(0, H - floor_y)
    y2 = y1 + random.randint(-30, 30)
    opacity_line = random.randint(18, 45)
    draw.line([(x1, y1), (x2, y2)],
              fill=(opacity_line + 20, opacity_line + 14, opacity_line + 8),
              width=random.randint(1, 2))

# -- Warm ambient light from upper-left (golden) --
light_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ld = ImageDraw.Draw(light_layer)
# Large radial gradient — simulate warm studio/room light
cx, cy = int(W * 0.28), int(H * 0.22)
for radius in range(600, 0, -4):
    t = 1 - (radius / 600)
    alpha = int(t * t * 38)
    r_c = int(180 + t * 40)
    g_c = int(130 + t * 30)
    b_c = int(60 + t * 20)
    ld.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
               fill=(r_c, g_c, b_c, alpha))

bg_rgba = bg.convert("RGBA")
bg_rgba = Image.alpha_composite(bg_rgba, light_layer)

# -- Secondary cooler light from right edge --
light2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
l2d = ImageDraw.Draw(light2)
cx2, cy2 = int(W * 0.88), int(H * 0.35)
for radius in range(400, 0, -4):
    t = 1 - (radius / 400)
    alpha = int(t * t * 18)
    l2d.ellipse([cx2-radius, cy2-radius, cx2+radius, cy2+radius],
                fill=(90, 110, 140, alpha))

bg_rgba = Image.alpha_composite(bg_rgba, light2)

# -- Thin gold accent line (horizontal, premium feel) --
gold_strip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(gold_strip)
line_y = int(H * 0.67)
for thickness, alpha in [(6, 40), (3, 80), (1, 160)]:
    gd.line([(0, line_y), (W, line_y)],
            fill=(184, 148, 63, alpha), width=thickness)
bg_rgba = Image.alpha_composite(bg_rgba, gold_strip)

# -- Soft vignette --
vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
vd = ImageDraw.Draw(vignette)
for r in range(max(W, H), 0, -4):
    cx_v, cy_v = W // 2, H // 2
    t = r / max(W, H)
    alpha = int((1 - t) * (1 - t) * 120)
    vd.ellipse([cx_v-r, cy_v-r, cx_v+r, cy_v+r],
               fill=(0, 0, 0, 0),
               outline=(0, 0, 0, alpha) if alpha > 2 else None)

# Simpler vignette — corners dark
vig2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
v2d = ImageDraw.Draw(vig2)
for i in range(200):
    t = i / 200
    a = int((1 - t) ** 1.8 * 160)
    v2d.rectangle([i, i, W-i, H-i], outline=(0, 0, 0, a))
bg_rgba = Image.alpha_composite(bg_rgba, vig2)

# ─── Step 3: Scale & position product ───────────────────────────

# Baluster is tall/narrow — place as repeating railing
# Scale product to fit ~65% of canvas height
target_h = int(H * 1.05)
scale = target_h / ph
prod_w_new = int(pw * scale)
prod_h_new = target_h
prod_resized = prod_cut.resize((prod_w_new, prod_h_new), Image.LANCZOS)

# Place 3 balusters side by side — simulate installed railing
n_balusters = 3
spacing = int(prod_w_new * 0.82)   # slight overlap / tight spacing

# Start x so the group is roughly centered
total_width = prod_w_new + spacing * (n_balusters - 1)
start_x = (W - total_width) // 2 - int(prod_w_new * 0.1)
paste_y = int(H * -0.03)   # slightly above frame = installed look

for i in range(n_balusters):
    x = start_x + i * spacing

    # Each baluster gets slightly different brightness (depth illusion)
    depth_factor = 1.0 if i == 1 else 0.78   # center brightest
    b_img = prod_resized.copy()

    # Darken side balusters
    if depth_factor < 1.0:
        enhancer = ImageEnhance.Brightness(b_img)
        b_img = enhancer.enhance(depth_factor)

        # Also slightly blur them (depth of field)
        blur_r = 1.5 if i == 0 else 1.2
        b_img = b_img.filter(ImageFilter.GaussianBlur(blur_r))

    # Cast soft shadow on background before pasting
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_x = x + int(prod_w_new * 0.15)
    shadow_w = int(prod_w_new * 0.25)
    for s in range(40, 0, -1):
        a_s = int((1 - s/40) ** 2 * 55)
        shadow_draw.rectangle(
            [shadow_x - s*2, paste_y,
             shadow_x + shadow_w + s*2, paste_y + prod_h_new],
            fill=(0, 0, 0, a_s))
    bg_rgba = Image.alpha_composite(bg_rgba, shadow)

    # Paste baluster
    bg_rgba.paste(b_img, (x, paste_y), b_img)

# ─── Step 4: Add warm reflection on floor ───────────────────────
# Flip product, place below floor line, very faint
if n_balusters >= 1:
    center_prod = prod_resized.copy()
    center_prod = center_prod.transpose(Image.FLIP_TOP_BOTTOM)

    # Make very faint
    r2, g2, b2, a2 = center_prod.split()
    a2 = a2.point(lambda p: int(p * 0.08))
    center_prod.putalpha(a2)

    # Blur reflection
    center_prod = center_prod.filter(ImageFilter.GaussianBlur(4))
    ref_y = paste_y + prod_h_new - int(H * 0.04)
    ref_x = start_x + spacing
    bg_rgba.paste(center_prod, (ref_x, ref_y), center_prod)

# ─── Step 5: Final adjustments ──────────────────────────────────
final = bg_rgba.convert("RGB")

# Slight warm tone overall
enhancer = ImageEnhance.Color(final)
final = enhancer.enhance(1.12)

enhancer = ImageEnhance.Contrast(final)
final = enhancer.enhance(1.08)

enhancer = ImageEnhance.Brightness(final)
final = enhancer.enhance(0.96)

# ─── Save ────────────────────────────────────────────────────────
out_path = os.path.join(OUT_DIR, "baluster_installed_hero.jpg")
final.save(out_path, "JPEG", quality=93, optimize=True)
print(f"Saved: {out_path}")
print(f"Size: {final.size}")
