import contextlib
import io
import os
import shutil
import tempfile
import unittest

import eye_care_reminder
from eye_care_reminder import main


class MainTests(unittest.TestCase):
    def test_should_open_settings(self):
        self.assertTrue(eye_care_reminder.should_open_settings([]))
        self.assertTrue(eye_care_reminder.should_open_settings(["--other"]))
        self.assertFalse(eye_care_reminder.should_open_settings(["--autostart"]))

    def test_version(self):
        directory = tempfile.mkdtemp()
        try:
            self.assertEqual("0.0.0", main.read_version(directory))
            with open(os.path.join(directory, "VERSION"), "w") as f:
                f.write("1.2.3\n")
            self.assertEqual("1.2.3", main.read_version(directory))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(0, main.main(["eye-care-reminder", "--version"], directory))
            self.assertEqual("Eye Care Reminder 1.2.3\n", out.getvalue())
            self.assertEqual("v1.2.3", main.display_version(main.read_version(directory)))
        finally:
            shutil.rmtree(directory)


if __name__ == "__main__":
    unittest.main()
