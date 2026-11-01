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

    def test_gnome(self):
        for value in ("GNOME", "ubuntu:GNOME", "GNOME-Classic:GNOME", "pop:GNOME"):
            self.assertTrue(desktop.is_gnome(env(value)), value)
        for value in ("Budgie:GNOME", "GNOME-Flashback:GNOME", "Pantheon", "Unity", "KDE", ""):
            self.assertFalse(desktop.is_gnome(env(value)), value)

    def test_kde(self):
        self.assertTrue(desktop.is_kde(env("KDE")))
        self.assertFalse(desktop.is_kde(env("GNOME")))

    def test_i3(self):
        self.assertTrue(desktop.is_i3(env("i3")))
        self.assertTrue(desktop.is_i3({"I3SOCK": "/run/user/1000/i3/ipc"}))
        self.assertTrue(desktop.is_i3({"DESKTOP_SESSION": "i3"}))
        self.assertFalse(desktop.is_i3({"I3SOCK": "/run/i3", "SWAYSOCK": "/run/sway"}))
        self.assertFalse(desktop.is_i3({"I3SOCK": "/run/i3", "XDG_CURRENT_DESKTOP": "sway"}))
        self.assertFalse(desktop.is_i3({}))

    def test_i3_work_area(self):
        workspaces = ('[{"visible": false, "rect": {"x": 0, "y": 0, "width": 1920, "height": 1060}},'
                      ' {"visible": true, "rect": {"x": 1920, "y": 0, "width": 1280, "height": 1004}},'
                      ' {"visible": true, "rect": {"x": 0, "y": 20, "width": 1920, "height": 1040}}]')
        self.assertEqual(desktop.i3_work_area(workspaces, (0, 0, 1920, 1080)), (0, 20, 1920, 1040))
        self.assertEqual(desktop.i3_work_area(workspaces, (1920, 0, 1280, 1024)), (1920, 0, 1280, 1004))
        self.assertIsNone(desktop.i3_work_area(workspaces, (5000, 0, 100, 100)))
        self.assertIsNone(desktop.i3_work_area("not json", (0, 0, 1, 1)))
        self.assertIsNone(desktop.i3_work_area('{"error": 1}', (0, 0, 1, 1)))
        self.assertIsNone(desktop.i3_work_area('[{"visible": true, "rect": {"x": "?"}}]', (0, 0, 9, 9)))

    def test_tray_kind(self):
        self.assertEqual(desktop.tray_kind(True, env("XFCE")), desktop.STATUS_ICON)
        self.assertEqual(desktop.tray_kind(False, env("XFCE")), desktop.STATUS_ICON)
        self.assertEqual(desktop.tray_kind(True, env("Unity:Unity7:ubuntu")), desktop.APP_INDICATOR)
        self.assertEqual(desktop.tray_kind(True, env("KDE")), desktop.APP_INDICATOR)
        self.assertEqual(desktop.tray_kind(False, env("KDE")), desktop.STATUS_ICON)
        self.assertEqual(desktop.tray_kind(True, env("ubuntu:GNOME")), desktop.APP_INDICATOR)
        self.assertEqual(desktop.tray_kind(True, {"I3SOCK": "/run/i3"}), desktop.STATUS_ICON)

    def test_missing_tray_support(self):
        self.assertTrue(desktop.missing_tray_support(False, env("Unity:Unity7:ubuntu")))
        self.assertFalse(desktop.missing_tray_support(True, env("Unity:Unity7:ubuntu")))
        self.assertFalse(desktop.missing_tray_support(False, env("XFCE")))
        self.assertTrue(desktop.missing_tray_support(False, env("ubuntu:GNOME")))
        self.assertFalse(desktop.missing_tray_support(False, env("KDE")))  # xembedsniproxy shows StatusIcons


if __name__ == "__main__":
    unittest.main()
