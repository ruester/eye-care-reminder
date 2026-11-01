import unittest

from eye_care_reminder import desktop


def env(value):
    return {"XDG_CURRENT_DESKTOP": value}


class DesktopTests(unittest.TestCase):
    def test_current_desktops(self):
        self.assertEqual(desktop.current_desktops(env("Unity:Unity7:ubuntu")), ["unity", "unity7", "ubuntu"])
        self.assertEqual(desktop.current_desktops({}), [])

    def test_xfce(self):
        self.assertTrue(desktop.is_xfce(env("XFCE")))
        self.assertFalse(desktop.is_xfce(env("ubuntu:GNOME")))

    def test_unity(self):
        for value in ("Unity", "Unity:Unity7:ubuntu", "ubuntu:Unity7"):
            self.assertTrue(desktop.is_unity(env(value)), value)
        for value in ("ubuntu:GNOME", "XFCE", ""):
            self.assertFalse(desktop.is_unity(env(value)), value)

    def test_tray_kind(self):
        self.assertEqual(desktop.tray_kind(True, env("XFCE")), desktop.STATUS_ICON)
        self.assertEqual(desktop.tray_kind(False, env("XFCE")), desktop.STATUS_ICON)
        self.assertEqual(desktop.tray_kind(True, env("Unity:Unity7:ubuntu")), desktop.APP_INDICATOR)
        self.assertEqual(desktop.tray_kind(True, env("KDE")), desktop.APP_INDICATOR)
        self.assertEqual(desktop.tray_kind(False, env("KDE")), desktop.STATUS_ICON)

    def test_missing_tray_support(self):
        self.assertTrue(desktop.missing_tray_support(False, env("Unity:Unity7:ubuntu")))
        self.assertFalse(desktop.missing_tray_support(True, env("Unity:Unity7:ubuntu")))
        self.assertFalse(desktop.missing_tray_support(False, env("XFCE")))


if __name__ == "__main__":
    unittest.main()
