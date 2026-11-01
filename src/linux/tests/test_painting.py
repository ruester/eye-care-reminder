import unittest

try:
    import cairo
    from eye_care_reminder import painting
except ImportError:  # pycairo is not installed: the app can't run either
    cairo = None

from eye_care_reminder import flags, languages


def pixel(surface, x, y):
    """0xRRGGBB at (x, y) of an ARGB32 surface (opaque pixels)."""
    surface.flush()
    data = surface.get_data()
    offset = y * surface.get_stride() + x * 4
    b, g, r = data[offset], data[offset + 1], data[offset + 2]
    return (r << 16) | (g << 8) | b


@unittest.skipIf(cairo is None, "pycairo is not installed")
class PaintingTests(unittest.TestCase):
    def test_horizontal_stripes(self):
        surface = painting.flag_surface(flags.GERMANY, 30, 20)
        self.assertEqual(0x000000, pixel(surface, 15, 3))
        self.assertEqual(0xDD0000, pixel(surface, 15, 10))
        self.assertEqual(0xFFCE00, pixel(surface, 15, 16))
        self.assertEqual(painting.FLAG_OUTLINE, pixel(surface, 0, 10))

    def test_vertical_stripes_with_weights(self):
        surface = painting.flag_surface(flags.FRANCE, 30, 20)
        self.assertEqual(0x0055A4, pixel(surface, 4, 10))
        self.assertEqual(0xFFFFFF, pixel(surface, 15, 10))
        self.assertEqual(0xEF4135, pixel(surface, 26, 10))

    def test_nordic_cross(self):
        surface = painting.flag_surface(flags.SWEDEN, 32, 20)
        self.assertEqual(0x006AA7, pixel(surface, 4, 4))
        self.assertEqual(0xFECC00, pixel(surface, 12, 4))
        self.assertEqual(0xFECC00, pixel(surface, 25, 10))

    def test_every_flag_renders(self):
        for language in languages.ALL:
            with self.subTest(language=language.code):
                surface = painting.flag_surface(language.flag, 36, 24)
                colors = {pixel(surface, x, y) for x in range(2, 34, 3) for y in range(2, 22, 3)}
                self.assertGreaterEqual(len(colors), 2)

    def test_icon(self):
        surface = painting.icon_surface(64)
        self.assertEqual(painting.ACCENT, pixel(surface, 32, 6))
        self.assertEqual(painting.DARK, pixel(surface, 32, 32))
        self.assertEqual(0, surface.get_data()[3])  # transparent corner

    def test_render_icons(self):
        import os
        import tempfile
        directory = tempfile.mkdtemp()
        painting.render_icons(directory)
        self.assertEqual(sorted("eye-care-reminder-%d.png" % s for s in painting.ICON_SIZES),
                         sorted(os.listdir(directory)))


if __name__ == "__main__":
    unittest.main()
