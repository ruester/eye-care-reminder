"""Reminder popups.

On X11 the app draws its own popup in the bottom-right corner of the primary
monitor's work area (as on Windows): borderless, always on top, never takes
the focus, shown regardless of the desktop's Do Not Disturb setting, with a
countdown bar that shrinks from right to left until it closes; a click closes
it. Without X11 (pure Wayland, where windows can't position themselves) a
standard desktop notification (org.freedesktop.Notifications) is sent instead.
"""

import time

from gi.repository import Gdk, Gio, GLib, Gtk, Pango

from . import APP_NAME, countdown, painting

SCREEN_MARGIN = 12
COUNTDOWN_TICK_MS = 30

CSS = b"""
.eye-care-reminder-popup { background-color: @theme_base_color; }
.eye-care-reminder-popup .title { font-weight: bold; font-size: 115%; }
"""


def own_popups_supported():
    return "X11" in type(Gdk.Display.get_default()).__name__


def show(title, message, timeout_ms, icon_path, on_closed=None):
    """Shows a reminder; timeout_ms 0 keeps it until it is clicked. Returns an object with close()."""
    if own_popups_supported():
        popup = NotificationPopup(title, message, timeout_ms, on_closed)
        popup.present_without_focus()
        return popup
    return DesktopNotification(title, message, timeout_ms, icon_path)


def _rgb(cr, color):
    cr.set_source_rgb(((color >> 16) & 0xFF) / 255, ((color >> 8) & 0xFF) / 255, (color & 0xFF) / 255)


class NotificationPopup(Gtk.Window):
    _css_installed = False

    def __init__(self, title, message, timeout_ms, on_closed=None):
        super().__init__(type=Gtk.WindowType.POPUP)
        self._install_css()
        self.timeout_ms = timeout_ms
        self.on_closed = on_closed
        self.started = None
        self.timer_id = None
        self.closed = False
        self.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION)
        self.set_keep_above(True)
        self.set_accept_focus(False)
        self.set_focus_on_map(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.get_style_context().add_class("eye-care-reminder-popup")

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        content.set_border_width(12)
        icon = Gtk.Image.new_from_pixbuf(Gdk.pixbuf_get_from_surface(painting.icon_surface(48), 0, 0, 48, 48))
        icon.set_valign(Gtk.Align.START)
        content.pack_start(icon, False, False, 0)

        text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        title_label = Gtk.Label(label=title, xalign=0)
        title_label.get_style_context().add_class("title")
        title_label.set_line_wrap(True)
        title_label.set_max_width_chars(40)
        text.pack_start(title_label, False, False, 0)
        message_label = Gtk.Label(label=message, xalign=0)
        message_label.set_line_wrap(True)
        message_label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        # Equal minimum and natural width, otherwise the window takes the height of the
        # text wrapped at its minimum width.
        message_label.set_width_chars(40)
        message_label.set_max_width_chars(40)
        text.pack_start(message_label, False, False, 0)
        content.pack_start(text, True, True, 0)

        close = Gtk.Label(label="✕")
        close.get_style_context().add_class("dim-label")
        close.set_valign(Gtk.Align.START)
        content.pack_start(close, False, False, 0)

        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        layout.set_border_width(1)  # room for the accent border
        layout.pack_start(content, True, True, 0)
        if timeout_ms > 0:
            self.bar = Gtk.DrawingArea()
            self.bar.set_size_request(-1, max(3, self._font_height() // 4))
            self.bar.connect("draw", self._draw_bar)
            layout.pack_end(self.bar, False, False, 0)
        self.add(layout)

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", lambda *_: self.close())
        self.connect("realize", self._on_realize)
        # Wrapped labels get their final height only on allocation: place the popup then.
        self.connect("size-allocate", lambda _, allocation: self._place(allocation.width, allocation.height))
        self.connect_after("draw", self._draw_border)

    @classmethod
    def _install_css(cls):
        if not cls._css_installed:
            provider = Gtk.CssProvider()
            provider.load_from_data(CSS)
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            cls._css_installed = True

    def _font_height(self):
        metrics = self.get_pango_context().get_metrics(None, None)
        return (metrics.get_ascent() + metrics.get_descent()) // Pango.SCALE

    def _on_realize(self, _widget):
        self.get_window().set_cursor(Gdk.Cursor.new_from_name(self.get_display(), "pointer"))

    def present_without_focus(self):
        self.get_child().show_all()
        _, natural = self.get_preferred_size()
        self._place(natural.width, natural.height)
        self.show()
        if self.timeout_ms > 0:
            self.started = time.monotonic()
            self.timer_id = GLib.timeout_add(COUNTDOWN_TICK_MS, self._tick)

    def _place(self, width, height):
        """Bottom-right corner of the primary monitor's work area (without panels)."""
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        area = monitor.get_workarea()
        position = (area.x + area.width - width - SCREEN_MARGIN, area.y + area.height - height - SCREEN_MARGIN)
        if self.get_position() != position:
            self.move(*position)

    def _elapsed_ms(self):
        return 0 if self.started is None else (time.monotonic() - self.started) * 1000

    def _tick(self):
        if self._elapsed_ms() >= self.timeout_ms:
            self.timer_id = None
            self.close()
            return False
        self.bar.queue_draw()
        return True

    def _draw_bar(self, widget, cr):
        width, height = widget.get_allocated_width(), widget.get_allocated_height()
        _rgb(cr, painting.COUNTDOWN_TRACK)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        _rgb(cr, painting.ACCENT)
        cr.rectangle(0, 0, countdown.bar_width(width, self._elapsed_ms(), self.timeout_ms), height)
        cr.fill()

    def _draw_border(self, widget, cr):
        _rgb(cr, painting.ACCENT)
        cr.set_line_width(1)
        cr.rectangle(0.5, 0.5, widget.get_allocated_width() - 1, widget.get_allocated_height() - 1)
        cr.stroke()

    def close(self):
        if self.closed:
            return
        self.closed = True
        if self.timer_id is not None:
            GLib.source_remove(self.timer_id)
            self.timer_id = None
        self.destroy()
        if self.on_closed:
            self.on_closed(self)


class DesktopNotification:
    """Fallback without X11: a notification of the desktop's notification daemon."""

    def __init__(self, title, message, timeout_ms, icon_path):
        self.id = 0
        try:
            self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            result = self.bus.call_sync(
                "org.freedesktop.Notifications", "/org/freedesktop/Notifications",
                "org.freedesktop.Notifications", "Notify",
                GLib.Variant("(susssasa{sv}i)", (APP_NAME, 0, icon_path or "", title, message, [],
                                                {"urgency": GLib.Variant("y", 1)}, timeout_ms)),
                GLib.VariantType("(u)"), Gio.DBusCallFlags.NONE, -1, None)
            self.id = result.unpack()[0]
        except GLib.Error as error:
            print("eye-care-reminder: cannot show a notification: %s" % error.message)

    def close(self):
        if not self.id:
            return
        try:
            self.bus.call_sync(
                "org.freedesktop.Notifications", "/org/freedesktop/Notifications",
                "org.freedesktop.Notifications", "CloseNotification", GLib.Variant("(u)", (self.id,)),
                None, Gio.DBusCallFlags.NONE, -1, None)
        except GLib.Error:
            pass
        self.id = 0
