"""Builds the WorldMint Games banner logo, the mint leaves beside the full name, and the company page
header, the snowball fight screenshot with the banner over it. The leaves are tools/assets/mint.svg,
rendered to tools/assets/mint.png.

Usage: python3 tools/compose_company_banner.py
"""

from PIL import Image, ImageDraw, ImageFont

MINT_PATH = "tools/assets/mint.png"
FONT_PATH = "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"
FONT_SIZE = 600
# The white of the "WM" on the logo, then the bright green of the leaves.
WORDS = [("WorldMint ", (255, 255, 255, 255)), ("Games", (145, 189, 41, 255))]
# The leaves' height as a share of the capital letters' height.
LEAF_HEIGHT = 1.7
LEAF_GAP = 60
MARGIN = 40
BANNER_PATH = "data/images/logo-banner.png"

HEADER_SOURCE_PATH = "data/penal-penguins/images/04-snowball-fight.png"
HEADER_SIZE = (1920, 600)
HEADER_ZOOM = 1.2
# The banner logo's width as a share of the header's.
HEADER_BANNER_WIDTH = 0.7
# A dark band behind the banner, so the white lettering stands out from the snow.
HEADER_SHADE = (0, 0, 0, 110)
HEADER_PATH = "data/images/header.png"


def banner_logo():
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    measure = ImageDraw.Draw(Image.new("L", (1, 1)))
    text = "".join(word for word, _ in WORDS)
    text_box = measure.textbbox((0, 0), text, font=font)
    capital_height = measure.textbbox((0, 0), "W", font=font)
    capital_height = capital_height[3] - capital_height[1]

    leaves = Image.open(MINT_PATH).convert("RGBA")
    leaves = leaves.crop(leaves.getbbox())
    leaf_height = round(capital_height * LEAF_HEIGHT)
    leaves = leaves.resize((round(leaves.width * leaf_height / leaves.height), leaf_height), Image.LANCZOS)

    text_width = text_box[2] - text_box[0]
    size = (MARGIN * 2 + leaves.width + LEAF_GAP + text_width, MARGIN * 2 + leaf_height)
    banner = Image.new("RGBA", size, (0, 0, 0, 0))
    banner.alpha_composite(leaves, (MARGIN, MARGIN))

    draw = ImageDraw.Draw(banner)
    x = MARGIN + leaves.width + LEAF_GAP - text_box[0]
    # The capitals are centred on the leaves.
    y = MARGIN + (leaf_height - capital_height) // 2 - measure.textbbox((0, 0), "W", font=font)[1]
    for word, color in WORDS:
        draw.text((x, y), word, font=font, fill=color)
        x += draw.textlength(word, font=font)
    return banner


def header(banner):
    source = Image.open(HEADER_SOURCE_PATH).convert("RGBA")
    width = round(HEADER_SIZE[0] / HEADER_ZOOM)
    height = round(HEADER_SIZE[1] / HEADER_ZOOM)
    left = (source.width - width) // 2
    top = (source.height - height) // 2
    image = source.crop((left, top, left + width, top + height)).resize(HEADER_SIZE, Image.LANCZOS)

    banner_width = round(HEADER_SIZE[0] * HEADER_BANNER_WIDTH)
    banner = banner.resize((banner_width, round(banner.height * banner_width / banner.width)), Image.LANCZOS)
    position = ((HEADER_SIZE[0] - banner.width) // 2, (HEADER_SIZE[1] - banner.height) // 2)
    shade = Image.new("RGBA", HEADER_SIZE, (0, 0, 0, 0))
    ImageDraw.Draw(shade).rectangle((0, position[1], HEADER_SIZE[0], position[1] + banner.height), fill=HEADER_SHADE)
    image.alpha_composite(shade)
    image.alpha_composite(banner, position)
    return image.convert("RGB")


banner = banner_logo()
banner.save(BANNER_PATH)
header(banner).save(HEADER_PATH)
