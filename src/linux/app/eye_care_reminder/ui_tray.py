"""Tray icon with the menu "Settings..." / "Take a break now" / "Exit".

Xfce (and other X11 panels with a notification area / status tray) get a
Gtk.StatusIcon: left click opens the settings, right click the menu, the
tooltip shows the next break. Elsewhere an AppIndicator (StatusNotifierItem:
KDE Plasma, Unity, GNOME with the AppIndicator extension, ...) is used if its
library is installed; it only has a menu, so the next break is a menu entry.
"""

import os
import warnings

import gi
from gi.repository import Gdk, GLib, Gtk

from . import APP_ID, APP_NAME, painting
from .translations import mnemonic

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        gi.require_version("AyatanaAppIndicator3", "0.1")
        from gi.repository import AyatanaAppIndicator3 as AppIndicator
    except (ImportError, ValueError):
        try:
            gi.require_version("AppIndicator3", "0.1")
            from gi.repository import AppIndicator3 as AppIndicator
        except (ImportError, ValueError):
            AppIndicator = None


def use_app_indicator(environ=None):
    """StatusIcon on Xfce and whenever no AppIndicator library is installed."""
    environ = os.environ if environ is None else environ
    if AppIndicator is None:
        return False
    return "xfce" not in environ.get("XDG_CURRENT_DESKTOP", "").lower()


class Tray:
    def __init__(self, icon_path, on_settings, on_break_now, on_exit):
        self.menu = Gtk.Menu()
        self.next_break_item = Gtk.MenuItem(sensitive=False)
        self.settings_item = Gtk.MenuItem(use_underline=True)
        self.settings_item.connect("activate", lambda _: on_settings())
        self.break_now_item = Gtk.MenuItem(use_underline=True)
        self.break_now_item.connect("activate", lambda _: on_break_now())
        self.exit_item = Gtk.MenuItem(use_underline=True)
        self.exit_item.connect("activate", lambda _: on_exit())
        self.indicator = None
        self.status_icon = None

        if use_app_indicator():
            self.menu.append(self.next_break_item)
            self.menu.append(Gtk.SeparatorMenuItem())
        for item in (self.settings_item, self.break_now_item, Gtk.SeparatorMenuItem(), self.exit_item):
            self.menu.append(item)
        self.menu.show_all()

        if use_app_indicator():
            self.indicator = AppIndicator.Indicator.new(
                APP_ID, icon_path, AppIndicator.IndicatorCategory.APPLICATION_STATUS)
            self.indicator.set_title(APP_NAME)
            self.indicator.set_menu(self.menu)
            self.indicator.set_secondary_activate_target(self.settings_item)
            self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # Gtk.StatusIcon is deprecated, but what Xfce supports best
                self.status_icon = Gtk.StatusIcon()
                self.status_icon.set_title(APP_NAME)
                self.status_icon.connect("activate", lambda _: on_settings())
                self.status_icon.connect("popup-menu", self._popup_menu)
                self.status_icon.connect("size-changed", self._size_changed)
                self._size_changed(self.status_icon, 22)
                self.status_icon.set_visible(True)

    def _size_changed(self, icon, size):
        size = max(16, size)
        surface = painting.icon_surface(size)
        icon.set_from_pixbuf(Gdk.pixbuf_get_from_surface(surface, 0, 0, size, size))
        return True

    def _popup_menu(self, icon, button, activate_time):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, activate_time)

    def set_texts(self, texts):
        self.settings_item.set_label(mnemonic(texts.menu_settings))
        label = self.settings_item.get_child()
        label.set_markup_with_mnemonic("<b>%s</b>" % GLib.markup_escape_text(mnemonic(texts.menu_settings)))
        self.break_now_item.set_label(mnemonic(texts.menu_break_now))
        self.exit_item.set_label(mnemonic(texts.menu_exit))

    def set_next_break(self, tooltip, next_break_text):
        """tooltip: app name and next break (StatusIcon); next_break_text: menu entry (AppIndicator)."""
        self.next_break_item.set_label(next_break_text)
        if self.status_icon:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.status_icon.set_tooltip_text(tooltip)

    def destroy(self):
        if self.status_icon:
            self.status_icon.set_visible(False)
        if self.indicator:
            self.indicator.set_status(AppIndicator.IndicatorStatus.PASSIVE)
