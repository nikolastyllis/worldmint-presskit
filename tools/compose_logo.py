"""Builds the Penal Penguins logo and favicons from the headshot rendered by capture_logo.gd.

Usage: python3 tools/compose_logo.py <headshot.png>
"""

import math
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

SIZE = 2000
# Drawn this many times larger and scaled down, so the thin wire is smooth.
SUPERSAMPLE = 2
FONT_PATH = "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"
FONT_SIZE = 880
TEXT = "PP"
TEXT_TOP = 1020
OUTLINE_WIDTH = 30
OUTLINE_COLOR = (15, 15, 25, 255)
WIRE_COLOR = (0, 0, 0, 255)
# Each strand runs across the letters at this height, rising or falling by this many pixels from left to right.
STRANDS = [(1330, 0)]
LOGO_PATH = "data/penal-penguins/images/logo.png"
FAVICON_PATHS = ["data/images/favicon.ico", "data/penal-penguins/images/favicon.ico"]


def crop_headshot(path):
    headshot = Image.open(path).convert("RGBA")
    crop_size, centre_x, top = 1400, 1590, 300
    logo = headshot.crop((centre_x - crop_size // 2, top, centre_x + crop_size // 2, top + crop_size))
    logo = logo.resize((SIZE, SIZE), Image.LANCZOS)
    # Fades the cut-off body into transparency.
    fade = Image.new("L", (1, SIZE))
    for y in range(SIZE):
        fade.putpixel((0, y), 255 if y < 1400 else max(0, int(255 * (1 - (y - 1400) / 520))))
    logo.putalpha(ImageChops.multiply(logo.getchannel("A"), fade.resize(logo.size)))
    return logo


def text_position(draw, font):
    box = draw.textbbox((0, 0), TEXT, font=font)
    return ((SIZE * SUPERSAMPLE - (box[2] - box[0])) // 2 - box[0], TEXT_TOP * SUPERSAMPLE - box[1])


def draw_razor_wire(draw, start_y, tilt):
    """A coil of razor wire seen from the side, from the left edge to the right: overlapping rings
    with sharp blades around each one."""
    scale = SUPERSAMPLE
    width = SIZE * scale
    ring_width = 150 * scale
    ring_height = 210 * scale
    ring_spacing = 85 * scale
    blades_per_ring = 6
    blade_length = 34 * scale
    blade_width = 9 * scale
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
        draw.line(points, fill=WIRE_COLOR, width=9 * scale, joint="curve")
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
    logo = crop_headshot(sys.argv[1])
    big_size = (SIZE * SUPERSAMPLE, SIZE * SUPERSAMPLE)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE * SUPERSAMPLE)

    lettering = Image.new("RGBA", big_size, (0, 0, 0, 0))
    lettering_draw = ImageDraw.Draw(lettering)
    position = text_position(lettering_draw, font)
    lettering_draw.text(position, TEXT, font=font, fill=(255, 255, 255, 255), stroke_width=OUTLINE_WIDTH * SUPERSAMPLE, stroke_fill=OUTLINE_COLOR)

    # The wire only shows over the white inside of the letters, not their outline.
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
