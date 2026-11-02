import os
import shutil
import tempfile
import unittest

from eye_care_reminder import settings
from eye_care_reminder.settings import Settings


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.path = os.path.join(self.directory, "eye-care-reminder", "settings.ini")

    def tearDown(self):
        shutil.rmtree(self.directory)

    def write(self, text):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(text)

    def test_defaults_without_file(self):
        s = Settings.load(self.path)
        self.assertFalse(s.exists)
        self.assertEqual(20, s.interval_minutes)
        self.assertTrue(s.auto_hide)
        self.assertEqual(60, s.auto_hide_seconds)
        self.assertIsNone(s.language)

    def test_round_trip(self):
        s = Settings(self.path)
        s.interval_minutes = 25
        s.auto_hide = False
        s.auto_hide_seconds = 300
        s.language = "nl"
        s.save()
        self.assertTrue(s.exists)
        loaded = Settings.load(self.path)
        self.assertTrue(loaded.exists)
        self.assertEqual((25, False, 300, "nl"),
                         (loaded.interval_minutes, loaded.auto_hide, loaded.auto_hide_seconds, loaded.language))
        self.assertFalse(os.path.exists(self.path + ".tmp"))

    def test_without_language(self):
        Settings(self.path).save()
        self.assertIsNone(Settings.load(self.path).language)

    def test_out_of_range_and_invalid_values_use_defaults(self):
        cases = [
            ("interval_minutes = 0", "interval_minutes", 20),
            ("interval_minutes = 1441", "interval_minutes", 20),
            ("interval_minutes = 1440", "interval_minutes", 1440),
            ("interval_minutes = abc", "interval_minutes", 20),
            ("auto_hide_seconds = 0", "auto_hide_seconds", 60),
            ("auto_hide_seconds = 301", "auto_hide_seconds", 60),
            ("auto_hide_seconds = 1", "auto_hide_seconds", 1),
            ("auto_hide = maybe", "auto_hide", True),
            ("auto_hide = no", "auto_hide", False),
            ("auto_hide = 0", "auto_hide", False),
        ]
        for line, attribute, expected in cases:
            with self.subTest(line=line):
                self.write("[settings]\n%s\n" % line)
                self.assertEqual(expected, getattr(Settings.load(self.path), attribute))

    def test_exists_needs_interval(self):
        self.write("[settings]\nlanguage = de\n")
        s = Settings.load(self.path)
        self.assertFalse(s.exists)
        self.assertEqual("de", s.language)

    def test_broken_files_use_defaults(self):
        for text in ("not an ini file", "[other]\ninterval_minutes = 5\n", "[settings]\n[settings]\n"):
            with self.subTest(text=text):
                self.write(text)
                s = Settings.load(self.path)
                self.assertFalse(s.exists)
                self.assertEqual(20, s.interval_minutes)

    def test_default_path(self):
        self.assertEqual("/cfg/eye-care-reminder/settings.ini",
                         settings.default_path({"XDG_CONFIG_HOME": "/cfg", "HOME": "/home/u"}))
        self.assertEqual("/home/u/.config/eye-care-reminder/settings.ini",
                         settings.default_path({"HOME": "/home/u"}))
        self.assertEqual("/home/u/.config/eye-care-reminder/settings.ini",
                         settings.default_path({"XDG_CONFIG_HOME": "", "HOME": "/home/u"}))


if __name__ == "__main__":
    unittest.main()
