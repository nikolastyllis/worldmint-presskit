"""Builds the Penal Penguins logos and page header.

- The logo (kept off the site): "PP" with a penguin peeping over it, from two headshots rendered by capture_logo.gd, one
  covered in blood and one clean, whose eyes are pasted over the bloody one so they still show.
- The letters logo: the "PP" alone on a square.
- The banner logo: the full name in the same lettering, without the penguin.
- The header: the aerial screenshot, zoomed in, with the banner logo over it.

Usage: python3 tools/compose_logo.py <bloody headshot.png> <clean headshot.png>
"""

import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

LOGO_SIZE = 2000
# Drawn this many times larger and scaled down, so the thin wire is smooth.
SUPERSAMPLE = 2
FONT_PATH = "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"
# The orange of the game's interface (themes/game_theme.tres).
LETTER_COLOR = (232, 99, 28, 255)
# The letters fade diagonally from this lighter orange at the top left to LETTER_COLOR at the bottom right.
LETTER_HIGHLIGHT_COLOR = (255, 170, 90, 255)
OUTLINE_COLOR = (15, 15, 25, 255)
WIRE_COLOR = (0, 0, 0, 255)
# The lettering was designed at this font size; the outline and wire scale with it.
DESIGN_FONT_SIZE = 1500
OUTLINE_WIDTH = 48
# A texture atlas of barbed wire strands, white on black. It is scaled so the strands span the letters
# from top to bottom, and tiled across them.
WIRE_TEXTURE_PATH = "tools/assets/barbed-wire.tif"

LOGO_TEXT = "PP"
LOGO_TEXT_TOP = 880
# Left, top and size of the square taken from the headshots, placing the eyes just above the letters.
HEADSHOT_CROP = (139, 193, 1642)
# Boxes around each eye in the headshots, where the clean eyes are pasted.
EYE_BOXES = [(555, 769, 745, 927), (1177, 738, 1367, 875)]
LOGO_PATH = "tools/assets/logo-penguin.png"

LETTERS_MARGIN = 80
LETTERS_PATH = "data/penal-penguins/images/logo-pp.png"

BANNER_TEXT = "PENAL PENGUINS"
BANNER_FONT_SIZE = 600
BANNER_MARGIN = 60
BANNER_PATH = "data/penal-penguins/images/logo-banner.png"

HEADER_SOURCE_PATH = "tools/assets/screenshots/01-prison-aerial.png"
HEADER_SIZE = (1920, 600)
HEADER_ZOOM = 1.35
# The banner logo's width as a share of the header's.
HEADER_BANNER_WIDTH = 0.7
HEADER_PATH = "data/penal-penguins/images/header.png"


def peeping_penguin(bloody_path, clean_path):
    headshot = Image.open(bloody_path).convert("RGBA")
    clean = Image.open(clean_path).convert("RGBA")
    # The whites of the clean eyes, closed up so the pupils inside them are included.
    eyes = Image.new("L", headshot.size, 0)
    for box in EYE_BOXES:
        whites = clean.crop(box).convert("L").point(lambda value: 255 if value > 140 else 0)
        eyes.paste(whites.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.MinFilter(15)), box[:2])
    headshot.paste(clean, (0, 0), eyes)

    left, top, crop_size = HEADSHOT_CROP
    return headshot.crop((left, top, left + crop_size, top + crop_size)).resize((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS)


def wire_overlay(size, letters_box):
    """Black barbed wire over the letters' box, the strands lined up with its top and bottom."""
    texture = Image.open(WIRE_TEXTURE_PATH).convert("L")
    strands_top, strands_bottom = texture.getbbox()[1], texture.getbbox()[3]
    scale = (letters_box[3] - letters_box[1]) / (strands_bottom - strands_top)
    tile = texture.resize((round(texture.width * scale), round(texture.height * scale)), Image.LANCZOS)
    alpha = Image.new("L", size, 0)
    top = round(letters_box[1] - strands_top * scale)
    for left in range(letters_box[0], letters_box[2], tile.width):
        alpha.paste(tile, (left, top))
    wire = Image.new("RGBA", size, WIRE_COLOR)
    wire.putalpha(alpha)
    return wire


def diagonal_gradient(size, box):
    """LETTER_HIGHLIGHT_COLOR at the top left of the box, fading to LETTER_COLOR at the bottom right."""
    width, height = box[2] - box[0], box[3] - box[1]
    small = Image.new("RGBA", (256, 256))
    pixels = small.load()
    for y in range(256):
        for x in range(256):
            t = (x + y) / 510
            pixels[x, y] = tuple(round(a + (b - a) * t) for a, b in zip(LETTER_HIGHLIGHT_COLOR, LETTER_COLOR))
    gradient = Image.new("RGBA", size, LETTER_COLOR)
    gradient.paste(small.resize((width, height), Image.BILINEAR), box[:2])
    return gradient


def lettering(text, font_size, size, text_top):
    """Outlined letters filled with an orange gradient, with barbed wire across them, centred on a
    transparent image."""
    scale = font_size / DESIGN_FONT_SIZE * SUPERSAMPLE
    big_size = (size[0] * SUPERSAMPLE, size[1] * SUPERSAMPLE)
    font = ImageFont.truetype(FONT_PATH, font_size * SUPERSAMPLE)

    image = Image.new("RGBA", big_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    box = draw.textbbox((0, 0), text, font=font)
    position = ((big_size[0] - (box[2] - box[0])) // 2 - box[0], text_top * SUPERSAMPLE - box[1])
    draw.text(position, text, font=font, fill=LETTER_COLOR, stroke_width=round(OUTLINE_WIDTH * scale), stroke_fill=OUTLINE_COLOR)

    # The fill and the wire only cover the inside of the letters, not their outline.
    inside = Image.new("L", big_size, 0)
    ImageDraw.Draw(inside).text(position, text, font=font, fill=255)
    letters_box = inside.getbbox()
    fill = diagonal_gradient(big_size, letters_box)
    fill.alpha_composite(wire_overlay(big_size, letters_box))
    image.paste(fill, (0, 0), inside)
    return image.resize(size, Image.LANCZOS)


def fitted_lettering(text, font_size, margin):
    """The lettering on an image just big enough to hold it, with the margin all round."""
    font = ImageFont.truetype(FONT_PATH, font_size)
    box = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=font)
    outline = round(OUTLINE_WIDTH * font_size / DESIGN_FONT_SIZE)
    padding = margin + outline
    size = (box[2] - box[0] + padding * 2, box[3] - box[1] + padding * 2)
    return lettering(text, font_size, size, padding)


def letters_logo():
    letters = fitted_lettering(LOGO_TEXT, DESIGN_FONT_SIZE, LETTERS_MARGIN)
    side = max(letters.size)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.alpha_composite(letters, ((side - letters.width) // 2, (side - letters.height) // 2))
    return square.resize((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS)


def banner_logo():
    return fitted_lettering(BANNER_TEXT, BANNER_FONT_SIZE, BANNER_MARGIN)


def header(banner):
    source = Image.open(HEADER_SOURCE_PATH).convert("RGBA")
    width = round(HEADER_SIZE[0] / HEADER_ZOOM)
    height = round(HEADER_SIZE[1] / HEADER_ZOOM)
    left = (source.width - width) // 2
    top = (source.height - height) // 2
    image = source.crop((left, top, left + width, top + height)).resize(HEADER_SIZE, Image.LANCZOS)

    banner_width = round(HEADER_SIZE[0] * HEADER_BANNER_WIDTH)
    banner = banner.resize((banner_width, round(banner.height * banner_width / banner.width)), Image.LANCZOS)
    image.alpha_composite(banner, ((HEADER_SIZE[0] - banner.width) // 2, (HEADER_SIZE[1] - banner.height) // 2))
    return image.convert("RGB")


def main():
    logo = peeping_penguin(sys.argv[1], sys.argv[2])
    logo.alpha_composite(lettering(LOGO_TEXT, DESIGN_FONT_SIZE, (LOGO_SIZE, LOGO_SIZE), LOGO_TEXT_TOP))
    logo.save(LOGO_PATH)

    letters = letters_logo()
    letters.save(LETTERS_PATH)

    banner = banner_logo()
    banner.save(BANNER_PATH)
    header(banner).save(HEADER_PATH)


if __name__ == "__main__":
    main()
