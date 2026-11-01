import unittest

from eye_care_reminder import fallback

ALL = (fallback.notify_send, fallback.kdialog, fallback.xmessage)


def build(builders=ALL, timeout_ms=60000, icon="/i.png", installed=("notify-send", "kdialog", "xmessage")):
    return fallback.commands(builders, "Title", "-message", timeout_ms, icon, "App",
                             which=lambda program: program in installed)


class FallbackTests(unittest.TestCase):
    def test_only_installed_commands_in_order(self):
        self.assertEqual([c[0] for c in build()], ["notify-send", "kdialog", "xmessage"])
        self.assertEqual([c[0] for c in build(installed=("xmessage",))], ["xmessage"])
        self.assertEqual(build(installed=()), [])

    def test_notify_send(self):
        command = build(installed=("notify-send",))[0]
        self.assertEqual(command, ["notify-send", "-a", "App", "-u", "normal", "-t", "60000",
                                   "-i", "/i.png", "--", "Title", "-message"])
        self.assertNotIn("-i", build(icon="", installed=("notify-send",))[0])
        self.assertIn("0", build(timeout_ms=0, installed=("notify-send",))[0])

    def test_seconds(self):
        self.assertEqual(build(timeout_ms=1500, installed=("kdialog",))[0][-1], "2")
        self.assertEqual(build(timeout_ms=0, installed=("kdialog",))[0][-1],
                         str(fallback.UNTIL_CLICKED_SECONDS))
        xmessage = build(timeout_ms=30000, installed=("xmessage",))[0]
        self.assertEqual(xmessage[xmessage.index("-timeout") + 1], "30")
        self.assertEqual(xmessage[-1], "Title\n\n-message")

    def test_notification_daemons(self):
        both = lambda program: program in ("mako", "dunst")  # noqa: E731
        self.assertEqual(fallback.notification_daemons({}, both), [["dunst"]])
        self.assertEqual(fallback.notification_daemons({"WAYLAND_DISPLAY": "wayland-0"}, both),
                         [["mako"], ["dunst"]])
        self.assertEqual(fallback.notification_daemons({"WAYLAND_DISPLAY": "w"}, lambda p: p == "dunst"),
                         [["dunst"]])
        self.assertEqual(fallback.notification_daemons({}, lambda p: p == "mako"), [])


if __name__ == "__main__":
    unittest.main()
