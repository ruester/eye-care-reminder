"""Entry point (eye-care-reminder.py)."""

import os
import sys

from . import APP_NAME


def read_version(app_dir):
    try:
        with open(os.path.join(app_dir, "VERSION"), encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "0.0.0"


def main(argv, app_dir):
    if "--version" in argv[1:]:
        print("%s %s" % (APP_NAME, read_version(app_dir)))
        return 0

    # Under Wayland, run through XWayland when available: only X11 lets the
    # reminder popup place itself in the bottom-right corner and has a tray.
    if os.environ.get("WAYLAND_DISPLAY") and os.environ.get("DISPLAY") and "GDK_BACKEND" not in os.environ:
        os.environ["GDK_BACKEND"] = "x11"

    try:
        import gi

        gi.require_version("Gtk", "3.0")
        gi.require_version("Gdk", "3.0")
        gi.require_foreign("cairo")
        from gi.repository import GLib, Gtk  # noqa: F401
    except (ImportError, ValueError) as error:
        print("eye-care-reminder: GTK 3 for Python is missing (%s).\n"
              "Install python3-gi, python3-gi-cairo and gir1.2-gtk-3.0 (Debian/Ubuntu) "
              "or python3-gobject and gtk3 (Fedora/openSUSE/Arch)." % error, file=sys.stderr)
        return 1

    from .app import EyeCareReminderApp

    GLib.set_application_name(APP_NAME)
    GLib.set_prgname("eye-care-reminder")
    return EyeCareReminderApp(app_dir).run(argv)
