"""
Variation 2 — Warmer, lighter background, single centered baluster,
more luxury hotel/lobby feel. Also generates a partition version.
"""
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import os, random

OUT_DIR = "images/generated"
os.makedirs(OUT_DIR, exist_ok=True)

def remove_light_bg(img, threshold=200, feather=10):
    img = img.convert("RGBA")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            rv, gv, bv, av = pixels[x, y]
            brightness = (rv*0.299 + gv*0.587 + bv*0.114)
            if brightness > threshold:
                fade = min(255, int((brightness - threshold) / (255 - threshold) * 255))
                pixels[x, y] = (rv, gv, bv, max(0, 255 - fade))
    img = img.filter(ImageFilter.GaussianBlur(feather * 0.5))
    return img

def make_bg_warm(W, H, style='dark_luxury'):
    """Create premium background."""
    bg = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(bg)

    if style == 'dark_luxury':
        # Deep charcoal base
        for y in range(H):
            t = y / H
            r = int(14 + t * 12)
            g = int(11 + t * 9)
            b = int(8 + t * 7)
            draw.line([(0,y),(W,y)], fill=(r,g,b))

        # Strong warm key light — center top
        light = Image.new("RGBA", (W, H), (0,0,0,0))
        ld = ImageDraw.Draw(light)
        for rad in range(700, 0, -3):
            t = 1 - rad/700
            a = int(t**1.6 * 52)
            r_c = int(200 + t*30)
            g_c = int(150 + t*20)
            b_c = int(70 + t*10)
            cx, cy = W//2, int(H*0.1)
            ld.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=(r_c,g_c,b_c,a))
        bg = Image.alpha_composite(bg, light)

        # Rim light right side (cool)
        rim = Image.new("RGBA", (W, H), (0,0,0,0))
        rd = ImageDraw.Draw(rim)
        for rad in range(350, 0, -3):
            t = 1 - rad/350
            a = int(t**2 * 30)
            rd.ellipse([W-rad, int(H*0.3)-rad, W+rad, int(H*0.3)+rad],
                       fill=(80, 100, 130, a))
        bg = Image.alpha_composite(bg, rim)

    elif style == 'warm_beige':
        # Warm beige/cream background
        for y in range(H):
            t = y / H
            r = int(235 - t * 50)
            g = int(220 - t * 50)
            b = int(195 - t * 55)
            draw.line([(0,y),(W,y)], fill=(r,g,b))

        # Soft shadow from center
        shadow = Image.new("RGBA", (W, H), (0,0,0,0))
        sd = ImageDraw.Draw(shadow)
        for rad in range(500, 0, -3):
            t = 1 - rad/500
            a = int(t**2 * 25)
            sd.ellipse([W//2-rad, H//2-rad, W//2+rad, H//2+rad],
                       fill=(0,0,0,a))
        bg = Image.alpha_composite(bg, shadow)

    # Gold accent line
    gold = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(gold)
    ly = int(H * 0.72)
    for thick, alpha in [(8,25),(4,55),(2,100),(1,180)]:
        gd.line([(0,ly),(W,ly)], fill=(184,148,63,alpha), width=thick)
    bg = Image.alpha_composite(bg, gold)

    # Vignette
    vig = Image.new("RGBA", (W, H), (0,0,0,0))
    vd = ImageDraw.Draw(vig)
    for i in range(0, 280, 2):
        t = 1 - i/280
        a = int(t**2.2 * 180)
        vd.rectangle([i,i,W-i,H-i], outline=(0,0,0,a))
    bg = Image.alpha_composite(bg, vig)

    return bg.convert("RGB")


# ── IMAGE 1: 3 Balusters, Dark Luxury, Landscape ──────────────
def make_baluster_dark():
    W, H = 1920, 1080
    prod = remove_light_bg(
        Image.open("images/products/balusters/DSC05627.JPG"), threshold=198, feather=12)

    bg = make_bg_warm(W, H, 'dark_luxury')
    canvas = bg.convert("RGBA")

    pw, ph = prod.size
    target_h = int(H * 1.12)
    scale = target_h / ph
    nw, nh = int(pw * scale), target_h
    prod_r = prod.resize((nw, nh), Image.LANCZOS)

    configs = [
        (-0.22, 0.70, 1.2),   # left, depth 70%, bright 1.2 — further
        (0.0,   1.0,  1.0),   # center, full size
        (0.22,  0.72, 1.15),  # right
    ]

    offsets_x = [-int(W*0.18), 0, int(W*0.18)]
    base_x = W//2 - nw//2

    for i, (x_off, depth, bright) in enumerate(configs):
        x = base_x + int(W * x_off)
        y = int(H * -0.06)

        sz_w = int(nw * depth)
        sz_h = int(nh * depth)
        p = prod_r.resize((sz_w, sz_h), Image.LANCZOS)

        if bright != 1.0:
            p = ImageEnhance.Brightness(p).enhance(bright)
        if depth < 0.9:
            p = p.filter(ImageFilter.GaussianBlur(1.5))

        # Drop shadow
        sh = Image.new("RGBA", (W, H), (0,0,0,0))
        shd = ImageDraw.Draw(sh)
        for s in range(50, 0, -1):
            a = int((1-s/50)**1.5 * 70)
            shd.rectangle([x+sz_w//2-s*3, y, x+sz_w//2+s*3, y+sz_h],
                          fill=(0,0,0,a))
        canvas = Image.alpha_composite(canvas, sh)
        canvas.paste(p, (x, y), p)

    # Subtle floor reflection
    center_p = prod_r.copy()
    center_p = center_p.transpose(Image.FLIP_TOP_BOTTOM)
    r2,g2,b2,a2 = center_p.split()
    a2 = a2.point(lambda p: int(p * 0.07))
    center_p.putalpha(a2)
    center_p = center_p.filter(ImageFilter.GaussianBlur(5))
    ref_y = int(H * -0.06) + nh
    canvas.paste(center_p, (base_x, ref_y - int(H*0.02)), center_p)

    final = canvas.convert("RGB")
    final = ImageEnhance.Color(final).enhance(1.15)
    final = ImageEnhance.Contrast(final).enhance(1.06)
    out = "images/generated/baluster_dark_hero.jpg"
    final.save(out, "JPEG", quality=94)
    print(f"Saved: {out}")
    return out


# ── IMAGE 2: Single Baluster, Warm Beige, Square (for product page) ──
def make_baluster_warm():
    W, H = 1080, 1080
    prod = remove_light_bg(
        Image.open("images/products/balusters/DSC05627.JPG"), threshold=198, feather=12)

    bg = make_bg_warm(W, H, 'warm_beige')
    canvas = bg.convert("RGBA")

    pw, ph = prod.size
    target_h = int(H * 1.05)
    scale = target_h / ph
    nw, nh = int(pw * scale), target_h
    prod_r = prod.resize((nw, nh), Image.LANCZOS)

    x = W//2 - nw//2
    y = int(H * -0.03)

    # Drop shadow
    sh = Image.new("RGBA", (W, H), (0,0,0,0))
    shd = ImageDraw.Draw(sh)
    for s in range(60, 0, -1):
        a = int((1-s/60)**1.5 * 50)
        shd.rectangle([x+nw//2-s*2, y, x+nw//2+s*2, y+nh],
                      fill=(120,90,50,a))
    canvas = Image.alpha_composite(canvas, sh)
    canvas.paste(prod_r, (x, y), prod_r)

    final = canvas.convert("RGB")
    final = ImageEnhance.Color(final).enhance(1.1)
    out = "images/generated/baluster_warm_square.jpg"
    final.save(out, "JPEG", quality=94)
    print(f"Saved: {out}")
    return out


# ── IMAGE 3: Partition panel on dark bg ──────────────────────────
def make_partition_dark():
    W, H = 1920, 1080

    # Try first partition image
    try:
        prod = remove_light_bg(
            Image.open("images/products/partitions/DSC05776.JPG"), threshold=200, feather=10)
    except:
        print("Partition image not found, skipping")
        return

    bg = make_bg_warm(W, H, 'dark_luxury')
    canvas = bg.convert("RGBA")

    pw, ph = prod.size
    # Partition is likely landscape/square — fit to height
    target_h = int(H * 0.92)
    scale = target_h / ph
    nw, nh = int(pw * scale), target_h
    prod_r = prod.resize((nw, nh), Image.LANCZOS)

    x = W//2 - nw//2
    y = H//2 - nh//2 + int(H*0.03)

    # Glow behind panel (backlit partition effect)
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    for rad in range(min(nw, nh)//2 + 100, 0, -3):
        t = 1 - rad/(min(nw,nh)//2 + 100)
        a = int(t**2 * 35)
        gd.ellipse([x+nw//2-rad, y+nh//2-rad, x+nw//2+rad, y+nh//2+rad],
                   fill=(200,160,80,a))
    canvas = Image.alpha_composite(canvas, glow)

    # Drop shadow
    sh = Image.new("RGBA", (W, H), (0,0,0,0))
    shd = ImageDraw.Draw(sh)
    for s in range(60, 0, -1):
        a = int((1-s/60)**1.5 * 80)
        shd.rectangle([x-s*2, y, x+nw+s*2, y+nh], fill=(0,0,0,a))
    canvas = Image.alpha_composite(canvas, sh)
    canvas.paste(prod_r, (x, y), prod_r)

    final = canvas.convert("RGB")
    final = ImageEnhance.Color(final).enhance(1.12)
    final = ImageEnhance.Contrast(final).enhance(1.05)
    out = "images/generated/partition_dark_hero.jpg"
    final.save(out, "JPEG", quality=94)
    print(f"Saved: {out}")
    return out


# ── RUN ALL ──────────────────────────────────────────────────────
print("Generating composites...")
make_baluster_dark()
make_baluster_warm()
make_partition_dark()
print("\nAll done. View at: http://localhost:8081/images/generated/")
