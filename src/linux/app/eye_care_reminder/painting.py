"""Cairo drawing of the app icon and the flags (needs pycairo, not GTK).

`python3 -m eye_care_reminder.painting DIR` renders the PNG icons in DIR
(src/linux/app/icons, used for the menu entry).
"""

import math
import os
import sys

import cairo

from .flags import Emblem, Pattern

ICON_SIZES = (16, 22, 24, 32, 48, 64, 128, 256)

ACCENT = 0x00897B
ACCENT_LIGHT = 0x26A69A
DARK = 0x142128
COUNTDOWN_TRACK = 0xD6ECE9
FLAG_OUTLINE = 0xA0A0A0


def _rgb(cr, color, alpha=1.0):
    cr.set_source_rgba(((color >> 16) & 0xFF) / 255, ((color >> 8) & 0xFF) / 255, (color & 0xFF) / 255, alpha)


def _rounded_rect(cr, x, y, w, h, r):
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()


def paint_icon(cr, size):
    """The app icon (same shapes as site/logo.svg and the Windows .ico) in a size x size square."""
    cr.save()
    cr.scale(size / 1024, size / 1024)
    _rounded_rect(cr, 40, 40, 944, 944, 220)
    _rgb(cr, ACCENT)
    cr.fill_preserve()
    cr.clip()
    # Eye: two arcs (radius 620) between (-41.2, 512) and (1065.2, 512).
    half_chord = (1065.2 + 41.2) / 2
    offset = math.sqrt(620 ** 2 - half_chord ** 2)
    angle = math.atan2(offset, half_chord)
    cr.arc(512, 512 + offset, 620, -math.pi + angle, -angle)
    cr.arc(512, 512 - offset, 620, angle, math.pi - angle)
    cr.close_path()
    _rgb(cr, 0xFFFFFF)
    cr.fill()
    for x, y, r, color in ((512, 512, 190, ACCENT_LIGHT), (512, 512, 95, DARK), (569.5, 429.5, 37.5, 0xFFFFFF)):
        cr.arc(x, y, r, 0, 2 * math.pi)
        _rgb(cr, color)
        cr.fill()
    cr.restore()


def icon_surface(size):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    paint_icon(cairo.Context(surface), size)
    return surface


def _edges(start, length, weights):
    """Positions of the borders between parts with the given relative sizes."""
    total = float(sum(weights))
    edges = [start]
    for weight in weights:
        edges.append(edges[-1] + length * weight / total)
    return edges


def _fill(cr, color, x, y, w, h):
    _rgb(cr, color)
    cr.rectangle(x, y, w, h)
    cr.fill()


def _fill_cross(cr, color, x, y, w, h, left, right, top, bottom):
    _fill(cr, color, left, y, right - left, h)
    _fill(cr, color, x, top, w, bottom - top)


def paint_flag(cr, x, y, w, h, flag):
    """Draws flag into the rectangle, with a thin gray outline."""
    cr.save()
    cr.rectangle(x, y, w, h)
    cr.clip()
    colors = flag.colors
    if flag.pattern in (Pattern.HORIZONTAL_STRIPES, Pattern.VERTICAL_STRIPES):
        horizontal = flag.pattern is Pattern.HORIZONTAL_STRIPES
        edges = _edges(y if horizontal else x, h if horizontal else w, flag.part_weights)
        for i, color in enumerate(colors):
            if horizontal:
                _fill(cr, color, x, edges[i], w, edges[i + 1] - edges[i])
            else:
                _fill(cr, color, edges[i], y, edges[i + 1] - edges[i], h)
    elif flag.pattern is Pattern.NORDIC_CROSS:
        xs = _edges(x, w, flag.part_weights)
        ys = _edges(y, h, flag.cross_weights_y)
        _fill(cr, colors[0], x, y, w, h)
        last = len(xs) - 2  # outer cross: everything between the first and the last field
        _fill_cross(cr, colors[1], x, y, w, h, xs[1], xs[last], ys[1], ys[last])
        if len(colors) > 2:
            _fill_cross(cr, colors[2], x, y, w, h, xs[2], xs[3], ys[2], ys[3])
    elif flag.pattern is Pattern.UNION_JACK:
        _fill(cr, colors[0], x, y, w, h)
        unit = h / 30.0  # the real flag is 30 units high
        for color, width in ((colors[1], 6), (colors[2], 2)):
            _rgb(cr, color)
            cr.set_line_width(width * unit)
            cr.move_to(x, y)
            cr.line_to(x + w, y + h)
            cr.move_to(x, y + h)
            cr.line_to(x + w, y)
            cr.stroke()
        cx, cy = x + w / 2, y + h / 2
        _fill_cross(cr, colors[1], x, y, w, h, cx - 5 * unit, cx + 5 * unit, cy - 5 * unit, cy + 5 * unit)
        _fill_cross(cr, colors[2], x, y, w, h, cx - 3 * unit, cx + 3 * unit, cy - 3 * unit, cy + 3 * unit)
    elif flag.pattern is Pattern.CZECHIA:
        _fill(cr, colors[0], x, y, w, h / 2)
        _fill(cr, colors[1], x, y + h / 2, w, h / 2)
        _rgb(cr, colors[2])
        cr.move_to(x, y)
        cr.line_to(x + w / 2, y + h / 2)
        cr.line_to(x, y + h)
        cr.close_path()
        cr.fill()

    if flag.emblem is Emblem.PORTUGAL:
        cx, cy, radius = x + w * 2 / 5, y + h / 2, h * 0.3
        _rgb(cr, 0xFFFF00)
        cr.arc(cx, cy, radius, 0, 2 * math.pi)
        cr.fill()
        sw, sh = radius * 1.1, radius * 1.3
        _fill(cr, 0xFF0000, cx - sw / 2, cy - sh / 2, sw, sh)
        _fill(cr, 0xFFFFFF, cx - sw / 4, cy - sh / 4, sw / 2, sh / 2)
    elif flag.emblem is Emblem.CROATIA:
        cell = h * 0.55 / 3  # checkerboard shield, 3 x 3 squares, starting with red
        left, top = x + w / 2 - 1.5 * cell, y + h / 2 - 1.5 * cell
        for row in range(3):
            for column in range(3):
                color = colors[0] if (row + column) % 2 == 0 else 0xFFFFFF
                _fill(cr, color, left + column * cell, top + row * cell, cell, cell)
    cr.restore()

    _rgb(cr, FLAG_OUTLINE)
    cr.set_line_width(1)
    cr.rectangle(x + 0.5, y + 0.5, w - 1, h - 1)
    cr.stroke()


def flag_surface(flag, width, height):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    paint_flag(cairo.Context(surface), 0, 0, width, height, flag)
    return surface


def render_icons(directory):
    os.makedirs(directory, exist_ok=True)
    for size in ICON_SIZES:
        icon_surface(size).write_to_png(os.path.join(directory, "eye-care-reminder-%d.png" % size))


if __name__ == "__main__":
    render_icons(sys.argv[1] if len(sys.argv) > 1 else ".")
