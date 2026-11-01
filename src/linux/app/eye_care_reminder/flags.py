"""Simplified national flags of the language switcher (same as the Windows app's Flag.cs),
drawn by flag_painter.py: flag emoji need a color emoji font, which many systems lack."""

import enum
from dataclasses import dataclass
from typing import Optional, Tuple


class Pattern(enum.Enum):
    HORIZONTAL_STRIPES = 1  # top to bottom, weights = relative heights
    VERTICAL_STRIPES = 2  # left to right, weights = relative widths
    # colors[0] background with a cross; weights / cross_weights_y split the width /
    # height: (field, cross, field) or (field, border, cross, border, field);
    # colors[1] is the cross (or its border), colors[2] the inner cross.
    NORDIC_CROSS = 3
    UNION_JACK = 4  # colors: (blue field, white, red)
    CZECHIA = 5  # colors: (white, red, blue triangle at the hoist)


class Emblem(enum.Enum):
    NONE = 0
    PORTUGAL = 1  # simplified armillary sphere and shield on the green/red border
    CROATIA = 2  # red and white checkerboard shield in the center


@dataclass(frozen=True)
class Flag:
    pattern: Pattern
    colors: Tuple[int, ...]  # 0xRRGGBB
    weights: Optional[Tuple[float, ...]] = None  # default: equal parts
    cross_weights_y: Optional[Tuple[float, ...]] = None
    emblem: Emblem = Emblem.NONE

    @property
    def part_weights(self):
        return self.weights or (1,) * len(self.colors)


BELGIUM = Flag(Pattern.VERTICAL_STRIPES, (0x000000, 0xFDDA24, 0xEF3340))
CROATIA = Flag(Pattern.HORIZONTAL_STRIPES, (0xFF0000, 0xFFFFFF, 0x171796), emblem=Emblem.CROATIA)
CZECHIA = Flag(Pattern.CZECHIA, (0xFFFFFF, 0xD7141A, 0x11457E))
FINLAND = Flag(Pattern.NORDIC_CROSS, (0xFFFFFF, 0x002F6C), (5, 3, 10), (4, 3, 4))
FRANCE = Flag(Pattern.VERTICAL_STRIPES, (0x0055A4, 0xFFFFFF, 0xEF4135))
GERMANY = Flag(Pattern.HORIZONTAL_STRIPES, (0x000000, 0xDD0000, 0xFFCE00))
ITALY = Flag(Pattern.VERTICAL_STRIPES, (0x009246, 0xFFFFFF, 0xCE2B37))
NETHERLANDS = Flag(Pattern.HORIZONTAL_STRIPES, (0xAE1C28, 0xFFFFFF, 0x21468B))
NORWAY = Flag(Pattern.NORDIC_CROSS, (0xBA0C2F, 0xFFFFFF, 0x00205B), (6, 1, 2, 1, 12), (6, 1, 2, 1, 6))
POLAND = Flag(Pattern.HORIZONTAL_STRIPES, (0xFFFFFF, 0xDC143C))
PORTUGAL = Flag(Pattern.VERTICAL_STRIPES, (0x006600, 0xFF0000), (2, 3), emblem=Emblem.PORTUGAL)
SPAIN = Flag(Pattern.HORIZONTAL_STRIPES, (0xAA151B, 0xF1BF00, 0xAA151B), (1, 2, 1))
SWEDEN = Flag(Pattern.NORDIC_CROSS, (0x006AA7, 0xFECC00), (5, 2, 9), (4, 2, 4))
UNITED_KINGDOM = Flag(Pattern.UNION_JACK, (0x012169, 0xFFFFFF, 0xC8102E))
