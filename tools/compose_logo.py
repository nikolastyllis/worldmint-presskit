"""Builds the Penal Penguins logos, favicon and page header.

- The logo: "PP" with a penguin peeping over it, from two headshots rendered by capture_logo.gd, one
  covered in blood and one clean, whose eyes are pasted over the bloody one so they still show.
- The letters logo: the "PP" alone on a square, also used for the game page's favicon and icons.
- The banner logo: the full name in the same lettering, without the penguin.
- The header: the aerial screenshot, zoomed in, with the banner logo over it.

Usage: python3 tools/compose_logo.py <bloody headshot.png> <clean headshot.png>
"""

import math
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

LOGO_SIZE = 2000
# Drawn this many times larger and scaled down, so the thin wire is smooth.
SUPERSAMPLE = 2
FONT_PATH = "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"
# The orange of the game's interface (themes/game_theme.tres).
LETTER_COLOR = (232, 99, 28, 255)
OUTLINE_COLOR = (15, 15, 25, 255)
WIRE_COLOR = (0, 0, 0, 255)
# The lettering was designed at this font size; the outline and wire scale with it.
DESIGN_FONT_SIZE = 1500
OUTLINE_WIDTH = 48
# How far below the top of the letters the wire runs, as a share of the font size.
WIRE_DEPTH = 0.353

LOGO_TEXT = "PP"
LOGO_TEXT_TOP = 880
# Left, top and size of the square taken from the headshots, placing the eyes just above the letters.
HEADSHOT_CROP = (139, 193, 1642)
# Boxes around each eye in the headshots, where the clean eyes are pasted.
EYE_BOXES = [(555, 769, 745, 927), (1177, 738, 1367, 875)]
LOGO_PATH = "data/penal-penguins/images/logo.png"

LETTERS_MARGIN = 80
LETTERS_PATH = "data/penal-penguins/images/logo-pp.png"
FAVICON_PATH = "data/penal-penguins/images/favicon.ico"
ICON_PATH = "tools/assets/icons/penal-penguins.png"
ICON_SIZE = 192
# Apple touch icons can't be transparent, so this one sits on the page's black.
APPLE_TOUCH_ICON_PATH = "tools/assets/icons/penal-penguins-apple-touch.png"
APPLE_TOUCH_ICON_SIZE = 180

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


def draw_razor_wire(draw, width, centre_y, scale):
    """A coil of razor wire seen from the side, across the whole width: overlapping rings with sharp
    blades around each one."""
    ring_width = 250 * scale
    ring_height = 350 * scale
    ring_spacing = 140 * scale
    blades_per_ring = 6
    blade_length = 56 * scale
    blade_width = 15 * scale
    steps = 72

    def ring_point(centre_x, angle):
        return (centre_x + math.cos(angle) * ring_width / 2, centre_y + math.sin(angle) * ring_height / 2)

    centre_x = -ring_width
    while centre_x < width + ring_width:
        points = [ring_point(centre_x, 2 * math.pi * step / steps) for step in range(steps + 1)]
        draw.line(points, fill=WIRE_COLOR, width=round(15 * scale), joint="curve")
        for blade in range(blades_per_ring):
            angle = 2 * math.pi * (blade + 0.5) / blades_per_ring
            point = ring_point(centre_x, angle)
            # Blades lie along the wire, so they follow the tangent of the ring.
            next_point = ring_point(centre_x, angle + 0.01)
            tangent = math.atan2(next_point[1] - point[1], next_point[0] - point[0])
            tip = (math.cos(tangent) * blade_length, math.sin(tangent) * blade_length)
            side = (-math.sin(tangent) * blade_width, math.cos(tangent) * blade_width)
            draw.polygon([(point[0] - tip[0], point[1] - tip[1]), (point[0] + side[0], point[1] + side[1]),
                          (point[0] + tip[0], point[1] + tip[1]), (point[0] - side[0], point[1] - side[1])], fill=WIRE_COLOR)
        centre_x += ring_spacing


def lettering(text, font_size, size, text_top):
    """Orange outlined letters with razor wire through them, centred across a transparent image."""
    scale = font_size / DESIGN_FONT_SIZE * SUPERSAMPLE
    big_size = (size[0] * SUPERSAMPLE, size[1] * SUPERSAMPLE)
    font = ImageFont.truetype(FONT_PATH, font_size * SUPERSAMPLE)

    image = Image.new("RGBA", big_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    box = draw.textbbox((0, 0), text, font=font)
    position = ((big_size[0] - (box[2] - box[0])) // 2 - box[0], text_top * SUPERSAMPLE - box[1])
    draw.text(position, text, font=font, fill=LETTER_COLOR, stroke_width=round(OUTLINE_WIDTH * scale), stroke_fill=OUTLINE_COLOR)

    # The wire only shows over the inside of the letters, not their outline.
    inside = Image.new("L", big_size, 0)
    ImageDraw.Draw(inside).text(position, text, font=font, fill=255)
    wire = Image.new("RGBA", big_size, (0, 0, 0, 0))
    draw_razor_wire(ImageDraw.Draw(wire), big_size[0], (text_top + WIRE_DEPTH * font_size) * SUPERSAMPLE, scale)
    wire.putalpha(ImageChops.multiply(wire.getchannel("A"), inside))
    image.alpha_composite(wire)
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
    letters.save(FAVICON_PATH, sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    letters.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS).save(ICON_PATH)
    apple_touch_icon = Image.new("RGBA", letters.size, (0, 0, 0, 255))
    apple_touch_icon.alpha_composite(letters)
    apple_touch_icon.convert("RGB").resize((APPLE_TOUCH_ICON_SIZE, APPLE_TOUCH_ICON_SIZE), Image.LANCZOS).save(APPLE_TOUCH_ICON_PATH)

    banner = banner_logo()
    banner.save(BANNER_PATH)
    header(banner).save(HEADER_PATH)


main()
