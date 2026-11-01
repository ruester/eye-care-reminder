"""Commands that show a reminder when the app's own popup and the notification
daemon (org.freedesktop.Notifications over D-Bus) are not available, e.g. on a
minimal or broken desktop. Each one is tried only if the one before failed.
"""

import shutil

# A command still running after this many seconds counts as shown (kdialog and
# xmessage stay open while the reminder is visible).
STARTUP_SECONDS = 3

# Kept open "until clicked" (timeout 0) means one hour for commands that need a time.
UNTIL_CLICKED_SECONDS = 3600


def _seconds(timeout_ms):
    return max(1, (timeout_ms + 999) // 1000) if timeout_ms > 0 else UNTIL_CLICKED_SECONDS


def notify_send(title, message, timeout_ms, icon_path, app_name):
    """libnotify's notify-send (expire time 0 = until clicked)."""
    command = ["notify-send", "-a", app_name, "-u", "normal", "-t", str(max(0, timeout_ms))]
    if icon_path:
        command += ["-i", icon_path]
    return command + ["--", title, message]


def kdialog(title, message, timeout_ms, icon_path, app_name):
    """KDE's passive popup (works without a notification daemon on older Plasma)."""
    return ["kdialog", "--title", title, "--passivepopup", message, str(_seconds(timeout_ms))]


def xmessage(title, message, timeout_ms, icon_path, app_name):
    """X11's xmessage: needs nothing but an X server."""
    return ["xmessage", "-center", "-buttons", "OK:0", "-timeout", str(_seconds(timeout_ms)),
            "%s\n\n%s" % (title, message)]


def commands(builders, title, message, timeout_ms, icon_path, app_name, which=shutil.which):
    """Command lines of the builders whose program is installed, in order."""
    result = []
    for builder in builders:
        command = builder(title, message, timeout_ms, icon_path, app_name)
        if which(command[0]):
            result.append(command)
    return result


def notification_daemons(environ, which=shutil.which):
    """Installed notification daemons to start when none is running (e.g. i3 or sway
    without an autostarted one), best first: mako on Wayland (it only supports Wayland),
    dunst on X11 and Wayland."""
    names = ("mako", "dunst") if environ.get("WAYLAND_DISPLAY") else ("dunst",)
    return [[name] for name in names if which(name)]
