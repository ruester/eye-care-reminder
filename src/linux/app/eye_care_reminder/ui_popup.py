"""Reminder popups.

On X11 the app draws its own popup in the bottom-right corner of the primary
monitor's work area (as on Windows): borderless, always on top, never takes
the focus, shown regardless of the desktop's Do Not Disturb setting, with a
countdown bar that shrinks from right to left until it closes; a click closes
it. The override-redirect popup needs no window manager, so it also shows when
the window manager is missing or broken.

If that is not possible (pure Wayland, where windows can't position themselves)
or fails, the reminder falls back step by step until one works:
1. the desktop's notification daemon (org.freedesktop.Notifications, if running
   or D-Bus activatable),
2. if none runs: start an installed one (mako on Wayland, dunst; e.g. i3 or sway
   without an autostarted daemon) and use it,
3. notify-send, 4. kdialog --passivepopup (if installed, see fallback.py),
5. an ordinary window of the app (any window manager, Wayland too),
6. xmessage.
"""

import os
import sys
import time

from gi.repository import Gdk, Gio, GLib, Gtk, Pango

from . import APP_NAME, countdown, fallback, painting

SCREEN_MARGIN = 12
COUNTDOWN_TICK_MS = 30

CSS = b"""
.eye-care-reminder-popup { background-color: @theme_base_color; }
.eye-care-reminder-popup .title { font-weight: bold; font-size: 115%; }
"""


def own_popups_supported():
    return "X11" in type(Gdk.Display.get_default()).__name__


def _log(text):
    print("eye-care-reminder: %s" % text, file=sys.stderr)


def show(title, message, timeout_ms, icon_path, on_closed=None):
    """Shows a reminder; timeout_ms 0 keeps it until it is clicked. Returns an object with close()."""
    if own_popups_supported():
        try:
            popup = NotificationPopup(title, message, timeout_ms, on_closed)
            popup.present_without_focus()
            return popup
        except Exception as error:  # noqa: BLE001 - any failure: use the fallbacks
            _log("cannot show the popup (%s), using a fallback" % error)
    return FallbackReminder(title, message, timeout_ms, icon_path)


def _rgb(cr, color):
    cr.set_source_rgb(((color >> 16) & 0xFF) / 255, ((color >> 8) & 0xFF) / 255, (color & 0xFF) / 255)


class NotificationPopup(Gtk.Window):
    _css_installed = False

    def __init__(self, title, message, timeout_ms, on_closed=None, managed=False):
        """managed: an ordinary window handled by the window manager (fallback)."""
        super().__init__(type=Gtk.WindowType.TOPLEVEL if managed else Gtk.WindowType.POPUP)
        self._install_css()
        self.timeout_ms = timeout_ms
        self.on_closed = on_closed
        self.started = None
        self.timer_id = None
        self.closed = False
        if managed:
            self.set_title(APP_NAME)
            self.set_resizable(False)
            self.set_urgency_hint(True)
            self.set_icon(Gdk.pixbuf_get_from_surface(painting.icon_surface(64), 0, 0, 64, 64))
            self.connect("delete-event", lambda *_: self.close() or True)
        else:
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


NOTIFICATIONS = "org.freedesktop.Notifications"


def _notification_daemon_available(bus):
    """Whether a notification daemon runs or can be started by D-Bus activation."""
    for method in ("NameHasOwner", "ListActivatableNames"):
        try:
            result = bus.call_sync(
                "org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus", method,
                GLib.Variant("(s)", (NOTIFICATIONS,)) if method == "NameHasOwner" else None,
                None, Gio.DBusCallFlags.NONE, 2000, None).unpack()[0]
        except GLib.Error:
            continue
        if result is True or (isinstance(result, list) and NOTIFICATIONS in result):
            return True
    return False


class DesktopNotification:
    """A notification of the desktop's notification daemon; ok is False if it failed."""

    def __init__(self, title, message, timeout_ms, icon_path):
        self.id = 0
        self.ok = False
        try:
            self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            if not _notification_daemon_available(self.bus):
                _log("no notification daemon")
                return
            result = self.bus.call_sync(
                "org.freedesktop.Notifications", "/org/freedesktop/Notifications",
                "org.freedesktop.Notifications", "Notify",
                GLib.Variant("(susssasa{sv}i)", (APP_NAME, 0, icon_path or "", title, message, [],
                                                {"urgency": GLib.Variant("y", 1)}, timeout_ms)),
                GLib.VariantType("(u)"), Gio.DBusCallFlags.NONE, 10000, None)
            self.id = result.unpack()[0]
            self.ok = True
        except GLib.Error as error:
            _log("cannot show a desktop notification: %s" % error.message)

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


class FallbackReminder:
    """Tries the fallbacks in order until one shows the reminder (see the module docstring)."""

    def __init__(self, title, message, timeout_ms, icon_path):
        self.title, self.message, self.timeout_ms, self.icon_path = title, message, timeout_ms, icon_path
        self.current = None      # object with close() of the step that worked
        self.process = None      # running command
        self.closed = False
        commands = fallback.commands((fallback.notify_send, fallback.kdialog), title, message,
                                     timeout_ms, icon_path, APP_NAME)
        last = fallback.commands((fallback.xmessage,), title, message, timeout_ms, icon_path, APP_NAME)
        daemons = fallback.notification_daemons(os.environ)
        self.steps = [self._desktop_notification] \
            + [lambda command=command: self._start_daemon(command) for command in daemons] \
            + [lambda command=command: self._command(command) for command in commands] \
            + [self._window] \
            + [lambda command=command: self._command(command) for command in last]
        self._next()

    def _next(self):
        """Runs the next step; a step returns True (shown), False (failed) or None (pending)."""
        while self.steps and not self.closed:
            result = self.steps.pop(0)()
            if result is None or result:
                return
        if not self.steps and not self.closed and self.current is None and self.process is None:
            _log("no way to show the reminder: %s - %s" % (self.title, self.message))

    def _desktop_notification(self):
        notification = DesktopNotification(self.title, self.message, self.timeout_ms, self.icon_path)
        if notification.ok:
            self.current = notification
        return notification.ok

    def _start_daemon(self, command):
        """Starts a notification daemon (it keeps running) and notifies through it."""
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        if _notification_daemon_available(bus):  # e.g. started meanwhile
            return self._desktop_notification()
        try:
            process = Gio.Subprocess.new(command, Gio.SubprocessFlags.NONE)
        except GLib.Error as error:
            _log("cannot start %s: %s" % (command[0], error.message))
            return False
        _log("no notification daemon running: started %s" % command[0])
        deadline = time.monotonic() + fallback.STARTUP_SECONDS

        def poll():
            if self.closed:
                return False
            if _notification_daemon_available(bus):
                if not self._desktop_notification():
                    self._next()
                return False
            if process.get_identifier() is None or time.monotonic() > deadline:
                _log("%s did not start" % command[0])
                if process.get_identifier() is not None:
                    process.force_exit()
                self._next()
                return False
            return True

        GLib.timeout_add(100, poll)
        return None

    def _window(self):
        try:
            window = NotificationPopup(self.title, self.message, self.timeout_ms, managed=True)
            window.present_without_focus()
        except Exception as error:  # noqa: BLE001 - any failure: next fallback
            _log("cannot open a window: %s" % error)
            return False
        self.current = window
        return True

    def _command(self, command):
        """Runs a command: shown if it exits with 0 or still runs after STARTUP_SECONDS."""
        try:
            process = Gio.Subprocess.new(command, Gio.SubprocessFlags.STDOUT_SILENCE)
        except GLib.Error as error:
            _log("cannot run %s: %s" % (command[0], error.message))
            return False
        self.process = process
        state = {"done": False}

        def finished(proc, result):
            try:
                proc.wait_finish(result)
                success = proc.get_if_exited() and proc.get_exit_status() == 0
            except GLib.Error:
                success = False
            if self.process is proc:
                self.process = None
            if state["done"]:
                return
            state["done"] = True
            if not success:
                _log("%s failed" % command[0])
                self._next()

        def still_running():
            state["done"] = True
            return False

        process.wait_async(None, finished)
        GLib.timeout_add_seconds(fallback.STARTUP_SECONDS, still_running)
        return None

    def close(self):
        self.closed = True
        if self.current is not None:
            self.current.close()
            self.current = None
        if self.process is not None:
            self.process.force_exit()
            self.process = None
