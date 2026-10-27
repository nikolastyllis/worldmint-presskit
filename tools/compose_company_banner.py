"""Builds the WorldMint Games banner logo, the full name over the mint leaves, and the company page
header, the snowball fight screenshot with the banner over it. The leaves are tools/assets/mint.svg,
rendered to tools/assets/mint.png.

Usage: python3 tools/compose_company_banner.py
"""

from PIL import Image, ImageDraw, ImageFont

MINT_PATH = "tools/assets/mint.png"
FONT_PATH = "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"
FONT_SIZE = 600
NAME = "WorldMint"
# Set beneath the name, sized so it lines up with the name at both ends.
SUBTITLE = "GAMES"
LINE_GAP = 70
TEXT_COLOR = (255, 255, 255, 255)
# Keeps the white letters readable over the leaves and the screenshot.
OUTLINE_WIDTH = 14
OUTLINE_COLOR = (15, 15, 25, 255)
# The leaves sit behind the text, this much taller than it.
LEAF_HEIGHT = 1.45
MARGIN = 40
BANNER_PATH = "data/images/logo-banner.png"

HEADER_SOURCE_PATH = "data/penal-penguins/images/04-snowball-fight.png"
HEADER_SIZE = (1920, 600)
HEADER_ZOOM = 1.2
# The banner logo's height as a share of the header's.
HEADER_BANNER_HEIGHT = 0.85
HEADER_PATH = "data/images/header.png"


def ink_box(text, font):
    return ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=font)


def banner_logo():
    name_font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    name_box = ink_box(NAME, name_font)
    name_width = name_box[2] - name_box[0]
    # Text width grows almost exactly with font size, so one correction lines it up.
    subtitle_size = FONT_SIZE
    for attempt in range(2):
        subtitle_box = ink_box(SUBTITLE, ImageFont.truetype(FONT_PATH, subtitle_size))
        subtitle_size = round(subtitle_size * name_width / (subtitle_box[2] - subtitle_box[0]))
    subtitle_font = ImageFont.truetype(FONT_PATH, subtitle_size)
    subtitle_box = ink_box(SUBTITLE, subtitle_font)

    name_height = name_box[3] - name_box[1]
    text_height = name_height + LINE_GAP + subtitle_box[3] - subtitle_box[1]
    leaves = Image.open(MINT_PATH).convert("RGBA")
    leaves = leaves.crop(leaves.getbbox())
    leaf_height = round(text_height * LEAF_HEIGHT)
    leaves = leaves.resize((round(leaves.width * leaf_height / leaves.height), leaf_height), Image.LANCZOS)

    padding = MARGIN + OUTLINE_WIDTH
    size = (max(name_width, leaves.width) + padding * 2, leaf_height + padding * 2)
    banner = Image.new("RGBA", size, (0, 0, 0, 0))
    banner.alpha_composite(leaves, ((size[0] - leaves.width) // 2, padding))

    draw = ImageDraw.Draw(banner)
    left = (size[0] - name_width) // 2
    top = (size[1] - text_height) // 2
    draw.text((left - name_box[0], top - name_box[1]), NAME, font=name_font, fill=TEXT_COLOR,
              stroke_width=OUTLINE_WIDTH, stroke_fill=OUTLINE_COLOR)
    draw.text((left - subtitle_box[0], top + name_height + LINE_GAP - subtitle_box[1]), SUBTITLE, font=subtitle_font,
              fill=TEXT_COLOR, stroke_width=OUTLINE_WIDTH, stroke_fill=OUTLINE_COLOR)
    return banner


def header(banner):
    source = Image.open(HEADER_SOURCE_PATH).convert("RGBA")
    width = round(HEADER_SIZE[0] / HEADER_ZOOM)
    height = round(HEADER_SIZE[1] / HEADER_ZOOM)
    left = (source.width - width) // 2
    top = (source.height - height) // 2
    image = source.crop((left, top, left + width, top + height)).resize(HEADER_SIZE, Image.LANCZOS)

    banner_height = round(HEADER_SIZE[1] * HEADER_BANNER_HEIGHT)
    banner = banner.resize((round(banner.width * banner_height / banner.height), banner_height), Image.LANCZOS)
    image.alpha_composite(banner, ((HEADER_SIZE[0] - banner.width) // 2, (HEADER_SIZE[1] - banner.height) // 2))
    return image.convert("RGB")


banner = banner_logo()
banner.save(BANNER_PATH)
header(banner).save(HEADER_PATH)
