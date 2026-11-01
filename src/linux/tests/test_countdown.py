import unittest

from eye_care_reminder import countdown


class CountdownTests(unittest.TestCase):
    def test_remaining_fraction(self):
        self.assertEqual(1.0, countdown.remaining_fraction(0, 1000))
        self.assertEqual(0.75, countdown.remaining_fraction(250, 1000))
        self.assertEqual(0.0, countdown.remaining_fraction(1000, 1000))
        self.assertEqual(0.0, countdown.remaining_fraction(5000, 1000))
        self.assertEqual(1.0, countdown.remaining_fraction(-10, 1000))
        self.assertEqual(0.0, countdown.remaining_fraction(0, 0))

    def test_bar_width(self):
        self.assertEqual(300, countdown.bar_width(300, 0, 60000))
        self.assertEqual(150, countdown.bar_width(300, 30000, 60000))
        self.assertEqual(0, countdown.bar_width(300, 60000, 60000))


if __name__ == "__main__":
    unittest.main()
