"""Generate complete products.html with all 66 product cards."""
import os

BALUSTERS = [
    ("square-baluster","Square Baluster"),("round-baluster","Round Baluster"),
    ("twist-baluster","Twist Baluster"),("knuckle-baluster","Knuckle Baluster"),
    ("fluted-baluster","Fluted Baluster"),("basket-baluster","Basket Baluster"),
    ("spear-tip-baluster","Spear-tip Baluster"),("hollow-square-baluster","Hollow Square Baluster"),
    ("scroll-baluster","Scroll Baluster"),("ornate-baluster","Ornate Baluster"),
    ("flat-bar-baluster","Flat Bar Baluster"),("grooved-round-baluster","Grooved Round Baluster"),
    ("diamond-pattern-baluster","Diamond Pattern Baluster"),("ribbed-baluster","Ribbed Baluster"),
    ("tapered-baluster","Tapered Baluster"),("double-twist-baluster","Double Twist Baluster"),
    ("vine-scroll-baluster","Vine Scroll Baluster"),("classic-pillar-baluster","Classic Pillar Baluster"),
    ("square-twist-baluster","Square Twist Baluster"),("cage-baluster","Cage Baluster"),
    ("arrow-baluster","Arrow Baluster"),("hammered-baluster","Hammered Baluster"),
    ("colonial-baluster","Colonial Baluster"),("wave-baluster","Wave Baluster"),
    ("lotus-baluster","Lotus Baluster"),("finial-baluster","Finial Baluster"),
    ("stepped-baluster","Stepped Baluster"),("barrel-baluster","Barrel Baluster"),
    ("leaf-scroll-baluster","Leaf Scroll Baluster"),("gothic-baluster","Gothic Baluster"),
    ("hex-baluster","Hex Baluster"),("bold-fluted-baluster","Bold Fluted Baluster"),
    ("art-deco-baluster","Art Deco Baluster"),("wrought-iron-baluster","Wrought Iron Baluster"),
]

PARTITIONS = [
    ("DSC05776","Geometric Partition Screen"),("DSC05778","Floral Jali Panel"),
    ("DSC05780","Linear Strip Partition"),("DSC05784","Lattice Partition Panel"),
    ("DSC05795","Perforated Screen Panel"),("DSC05797","Ornamental Divider"),
    ("DSC05798","Arch Panel Partition"),("DSC05806","Chevron Screen"),
    ("DSC05810","Diamond Mesh Panel"),("DSC05818","Lotus Pattern Screen"),
    ("DSC05824","Classic Jali Divider"),("DSC05841","Scroll Border Panel"),
    ("DSC05850","Honeycomb Screen"),("DSC05852","Woven Pattern Panel"),
    ("DSC05864","Moroccan Jali Screen"),("DSC05871","Temple Pattern Divider"),
    ("DSC05872","Leaf Cluster Panel"),("DSC05875","Star Lattice Screen"),
    ("DSC05876","Arabesque Panel"),("DSC05901","Wave Pattern Divider"),
    ("DSC05914","Peacock Jali Screen"),("DSC05925","Fleur-de-Lis Panel"),
    ("DSC05932","Interlocking Ring Screen"),("DSC05940","Heritage Jali Panel"),
    ("DSC05941","Vine Trellis Screen"),("DSC05947","Parquet Pattern Panel"),
    ("DSC05956","Decorative Laser-cut Screen"),("DSC05958","Chevron Laser Panel"),
    ("DSC05961","Geometric Star Screen"),("DSC05965","Classic Medallion Panel"),
    ("DSC05969","Abstract Cut-out Screen"),("DSC05971","Trefoil Jali Divider"),
]

def card(slug, name, cat, img_path, ext="png"):
    return f'''            <div class="px-card" data-cat="{cat}" data-img="{img_path}" data-name="{name}" data-cat-label="{cat.title()}">
                <div class="px-card-img">
                    <img src="{img_path}" alt="{name}" loading="lazy">
                </div>
                <div class="px-card-overlay"><span class="px-enquire">Enquire</span></div>
                <div class="px-card-info">
                    <span class="px-card-category">{cat.title()}</span>
                    <div class="px-card-name">{name}</div>
                </div>
            </div>'''

cards_html = "\n"
for slug, name in BALUSTERS:
    cards_html += card(slug, name, "balusters",
                       f"images/products/balusters/{slug}.png") + "\n"
for dsc, name in PARTITIONS:
    cards_html += card(dsc, name, "partitions",
                       f"images/products/partitions/{dsc}.JPG", "jpg") + "\n"

# Read current file and insert cards
with open("products.html") as f:
    content = f.read()

MARKER = '<div class="products-grid" id="productsGrid">'
if MARKER in content:
    content = content.replace(MARKER, MARKER + cards_html, 1)
    with open("products.html", "w") as f:
        f.write(content)
    print(f"SUCCESS: {len(BALUSTERS)+len(PARTITIONS)} cards inserted")
else:
    print("MARKER NOT FOUND")
    print("Grid div variants in file:")
    import re
    for m in re.findall(r'<div[^>]*products-grid[^>]*>', content):
        print(" ", m)
