import datetime
import unittest

from eye_care_reminder import timeformat, translations


class TimeFormatTests(unittest.TestCase):
    def test_short_time_format(self):
        cases = {
            "%H:%M:%S": "%H:%M",
            "%T": "%H:%M",
            "%r": "%I:%M %p",
            "%I:%M:%S %p": "%I:%M %p",
            "%l:%M:%S %p": "%l:%M %p",
            "%H.%M.%S": "%H.%M",
            "%Hh%Mm%Ss": "%Hh%Mms",
            "": "%H:%M",
            None: "%H:%M",
            "%S": "%H:%M",
        }
        for t_fmt, expected in cases.items():
            with self.subTest(t_fmt=t_fmt):
                self.assertEqual(expected, timeformat.short_time_format(t_fmt))

    def test_time_of_day(self):
        moment = datetime.datetime(2026, 1, 2, 14, 5, 9)
        self.assertEqual("14:05", timeformat.time_of_day(moment, "%H:%M"))
        self.assertEqual("02:05 PM", timeformat.time_of_day(moment, "%I:%M %p"))

    def test_locale_time_format_has_no_seconds(self):
        self.assertNotIn("%S", timeformat.locale_time_format())

    def test_tray_text(self):
        moment = datetime.datetime(2026, 1, 2, 9, 30)
        self.assertEqual("Eye Care Reminder\nNext break at 09:30",
                         timeformat.tray_text(moment, translations.ENGLISH, "%H:%M"))
        self.assertEqual("Eye Care Reminder\nNächste Pause um 09:30",
                         timeformat.tray_text(moment, translations.GERMAN, "%H:%M"))


if __name__ == "__main__":
    unittest.main()
