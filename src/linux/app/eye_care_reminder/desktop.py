"""Which desktop the app runs on and which tray icon it needs there.

XDG_CURRENT_DESKTOP is a colon-separated list, e.g. "XFCE", "KDE",
"Unity:Unity7:ubuntu" (Ubuntu Unity), "ubuntu:GNOME" (Ubuntu's GNOME) or
"i3" (often unset under i3: then I3SOCK, which i3 sets for its children).
"""

import json
import os

STATUS_ICON = "status_icon"        # Gtk.StatusIcon (XEmbed notification area)
APP_INDICATOR = "app_indicator"    # AppIndicator / StatusNotifierItem

# Desktops that list "GNOME" but don't run GNOME Shell.
NOT_GNOME_SHELL = ("budgie", "gnome-flashback", "pantheon", "unity", "unity7")


def _env(environ):
    return os.environ if environ is None else environ


def current_desktops(environ=None):
    value = _env(environ).get("XDG_CURRENT_DESKTOP", "")
    return [name.lower() for name in value.split(":") if name]


def is_xfce(environ=None):
    return "xfce" in current_desktops(environ)


def is_unity(environ=None):
    return any(name.startswith("unity") for name in current_desktops(environ))


def is_gnome(environ=None):
    """GNOME Shell (Ubuntu, Fedora, ...)."""
    names = current_desktops(environ)
    return "gnome" in names and not any(name in NOT_GNOME_SHELL for name in names)


def is_kde(environ=None):
    return "kde" in current_desktops(environ)


def is_i3(environ=None):
    environ = _env(environ)
    if "i3" in current_desktops(environ):
        return True
    if current_desktops(environ):
        return False
    # sway sets I3SOCK too (compatibility), but also SWAYSOCK.
    return bool(environ.get("I3SOCK")) and not environ.get("SWAYSOCK") \
        or environ.get("XDG_SESSION_DESKTOP", "").lower() == "i3" \
        or environ.get("DESKTOP_SESSION", "").lower() == "i3"


def tray_kind(indicator_available, environ=None):
    """Xfce and i3 (i3bar): StatusIcon, their tray shows it best. Unity, GNOME, KDE and
    others: AppIndicator if installed (Unity and GNOME show nothing else), else StatusIcon."""
    if is_xfce(environ) or is_i3(environ):
        return STATUS_ICON
    return APP_INDICATOR if indicator_available else STATUS_ICON


def missing_tray_support(indicator_available, environ=None):
    """Whether the tray icon can't appear because the AppIndicator library is missing."""
    return (is_unity(environ) or is_gnome(environ)) and not indicator_available


def i3_work_area(workspaces_json, monitor):
    """The usable area (without i3bar) of the visible i3 workspace on the monitor
    (x, y, width, height), from `i3-msg -t get_workspaces`; None if unknown.
    i3 doesn't publish _NET_WORKAREA, so GTK would place popups over the bar."""
    try:
        workspaces = json.loads(workspaces_json)
    except ValueError:
        return None
    mx, my, mw, mh = monitor
    for workspace in workspaces if isinstance(workspaces, list) else ():
        rect = workspace.get("rect") if isinstance(workspace, dict) else None
        if not workspace.get("visible") or not isinstance(rect, dict):
            continue
        try:
            x, y, w, h = (int(rect[key]) for key in ("x", "y", "width", "height"))
        except (KeyError, TypeError, ValueError):
            continue
        if mx <= x and my <= y and x + w <= mx + mw and y + h <= my + mh and w > 0 and h > 0:
            return x, y, w, h
    return None
