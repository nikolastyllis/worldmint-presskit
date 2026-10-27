"""Builds the Penal Penguins logo and its favicon from two headshots rendered by capture_logo.gd: one
covered in blood and one clean, whose eyes are pasted over the bloody one so they still show.

Usage: python3 tools/compose_logo.py <bloody headshot.png> <clean headshot.png>
"""

import math
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

SIZE = 2000
# Drawn this many times larger and scaled down, so the thin wire is smooth.
SUPERSAMPLE = 2
FONT_PATH = "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"
FONT_SIZE = 1500
TEXT = "PP"
TEXT_TOP = 880
# The orange of the game's interface (themes/game_theme.tres).
LETTER_COLOR = (232, 99, 28, 255)
OUTLINE_WIDTH = 48
OUTLINE_COLOR = (15, 15, 25, 255)
WIRE_COLOR = (0, 0, 0, 255)
# Each strand runs across the letters at this height, rising or falling by this many pixels from left to right.
STRANDS = [(1410, 0)]
# Left, top and size of the square taken from the headshots, placing the eyes just above the letters.
HEADSHOT_CROP = (139, 193, 1642)
# Boxes around each eye in the headshots, where the clean eyes are pasted.
EYE_BOXES = [(555, 769, 745, 927), (1177, 738, 1367, 875)]
LOGO_PATH = "data/penal-penguins/images/logo.png"
FAVICON_PATHS = ["data/penal-penguins/images/favicon.ico"]


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
    return headshot.crop((left, top, left + crop_size, top + crop_size)).resize((SIZE, SIZE), Image.LANCZOS)


def text_position(draw, font):
    box = draw.textbbox((0, 0), TEXT, font=font)
    return ((SIZE * SUPERSAMPLE - (box[2] - box[0])) // 2 - box[0], TEXT_TOP * SUPERSAMPLE - box[1])


def draw_razor_wire(draw, start_y, tilt):
    """A coil of razor wire seen from the side, from the left edge to the right: overlapping rings
    with sharp blades around each one."""
    scale = SUPERSAMPLE
    width = SIZE * scale
    ring_width = 250 * scale
    ring_height = 350 * scale
    ring_spacing = 140 * scale
    blades_per_ring = 6
    blade_length = 56 * scale
    blade_width = 15 * scale
    steps = 72
    direction = math.atan2(tilt, SIZE)
    along = (math.cos(direction), math.sin(direction))
    across = (-along[1], along[0])

    def ring_point(centre, angle):
        offset_along = math.cos(angle) * ring_width / 2
        offset_across = math.sin(angle) * ring_height / 2
        return (centre[0] + along[0] * offset_along + across[0] * offset_across,
                centre[1] + along[1] * offset_along + across[1] * offset_across)

    distance = -ring_width
    while distance < width / math.cos(direction) + ring_width:
        centre = (along[0] * distance, start_y * scale + along[1] * distance)
        points = [ring_point(centre, 2 * math.pi * step / steps) for step in range(steps + 1)]
        draw.line(points, fill=WIRE_COLOR, width=15 * scale, joint="curve")
        for blade in range(blades_per_ring):
            angle = 2 * math.pi * (blade + 0.5) / blades_per_ring
            point = ring_point(centre, angle)
            # Blades lie along the wire, so they follow the tangent of the ring.
            next_point = ring_point(centre, angle + 0.01)
            tangent = math.atan2(next_point[1] - point[1], next_point[0] - point[0])
            tip = (math.cos(tangent) * blade_length, math.sin(tangent) * blade_length)
            side = (-math.sin(tangent) * blade_width, math.cos(tangent) * blade_width)
            draw.polygon([(point[0] - tip[0], point[1] - tip[1]), (point[0] + side[0], point[1] + side[1]),
                          (point[0] + tip[0], point[1] + tip[1]), (point[0] - side[0], point[1] - side[1])], fill=WIRE_COLOR)
        distance += ring_spacing


def main():
    logo = peeping_penguin(sys.argv[1], sys.argv[2])
    big_size = (SIZE * SUPERSAMPLE, SIZE * SUPERSAMPLE)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE * SUPERSAMPLE)

    lettering = Image.new("RGBA", big_size, (0, 0, 0, 0))
    lettering_draw = ImageDraw.Draw(lettering)
    position = text_position(lettering_draw, font)
    lettering_draw.text(position, TEXT, font=font, fill=LETTER_COLOR, stroke_width=OUTLINE_WIDTH * SUPERSAMPLE, stroke_fill=OUTLINE_COLOR)

    # The wire only shows over the inside of the letters, not their outline.
    inside = Image.new("L", big_size, 0)
    ImageDraw.Draw(inside).text(position, TEXT, font=font, fill=255)
    wire = Image.new("RGBA", big_size, (0, 0, 0, 0))
    wire_draw = ImageDraw.Draw(wire)
    for start_y, tilt in STRANDS:
        draw_razor_wire(wire_draw, start_y, tilt)
    wire.putalpha(ImageChops.multiply(wire.getchannel("A"), inside))
    lettering.alpha_composite(wire)

    logo.alpha_composite(lettering.resize((SIZE, SIZE), Image.LANCZOS))
    logo.save(LOGO_PATH)
    for path in FAVICON_PATHS:
        logo.save(path, sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])


main()
