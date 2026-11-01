"""Eye Care Reminder for Linux: reminds you to rest your eyes at an interval you choose.

The modules without GTK (plural, translations, languages, flags, settings,
timeformat, countdown) hold the logic and are unit tested; the ui_* modules
need GTK 3 (PyGObject).
"""

APP_NAME = "Eye Care Reminder"

# D-Bus name: GtkApplication uses it to keep a single instance per session.
APP_ID = "io.github.ruester.EyeCareReminder"

# Passed by the login autostart entry: start silently in the tray.
AUTOSTART_ARGUMENT = "--autostart"


def should_open_settings(args):
    """Started by the user (menu, installer) rather than at login: open the settings
    so the user sees that the app is running (as on Windows)."""
    return AUTOSTART_ARGUMENT not in args
