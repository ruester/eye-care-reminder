"""Which desktop the app runs on and which tray icon it needs there.

XDG_CURRENT_DESKTOP is a colon-separated list, e.g. "XFCE",
"Unity:Unity7:ubuntu" (Ubuntu Unity) or "ubuntu:GNOME".
"""

import os

STATUS_ICON = "status_icon"        # Gtk.StatusIcon (XEmbed notification area)
APP_INDICATOR = "app_indicator"    # AppIndicator / StatusNotifierItem


def current_desktops(environ=None):
    environ = os.environ if environ is None else environ
    value = environ.get("XDG_CURRENT_DESKTOP", "")
    return [name.lower() for name in value.split(":") if name]


def is_xfce(environ=None):
    return "xfce" in current_desktops(environ)


def is_unity(environ=None):
    return any(name.startswith("unity") for name in current_desktops(environ))


def tray_kind(indicator_available, environ=None):
    """Xfce: StatusIcon (its panel shows it best). Unity: AppIndicator, its panel shows
    nothing else. Other desktops: AppIndicator if installed, else StatusIcon."""
    if is_xfce(environ):
        return STATUS_ICON
    return APP_INDICATOR if indicator_available else STATUS_ICON


def missing_tray_support(indicator_available, environ=None):
    """Whether the tray icon can't appear: Unity without the AppIndicator library."""
    return is_unity(environ) and not indicator_available
