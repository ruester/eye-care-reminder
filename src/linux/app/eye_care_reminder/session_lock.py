"""Calls back when the screen is unlocked (locking the screen counts as a break).

Listens on D-Bus to the screen savers / lockers of the common desktops
(xfce4-screensaver, light-locker and others implementing
org.freedesktop.ScreenSaver, GNOME, Cinnamon, MATE), to Unity's lock screen
(com.canonical.Unity.Session Unlocked) and to systemd-logind (Unlock signal and
LockedHint of this session).
"""

import os

from gi.repository import Gio, GLib

SCREEN_SAVER_INTERFACES = (
    "org.freedesktop.ScreenSaver",
    "org.xfce.ScreenSaver",
    "org.gnome.ScreenSaver",
    "org.cinnamon.ScreenSaver",
    "org.mate.ScreenSaver",
)

UNITY_SESSION = "com.canonical.Unity.Session"

LOGIN1 = "org.freedesktop.login1"


class UnlockWatcher:
    def __init__(self, on_unlock):
        self.on_unlock = on_unlock
        self.locked_hint = False
        # GLib only keeps a weak reference to the shared bus connections: hold them here,
        # otherwise they are closed together with the subscriptions.
        self.session_bus = self.system_bus = None
        try:
            self.session_bus = session_bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            for interface in SCREEN_SAVER_INTERFACES:
                session_bus.signal_subscribe(None, interface, "ActiveChanged", None, None,
                                             Gio.DBusSignalFlags.NONE, self._on_active_changed)
            session_bus.signal_subscribe(None, UNITY_SESSION, "Unlocked", None, None,
                                         Gio.DBusSignalFlags.NONE, lambda *_: self.on_unlock())
        except GLib.Error:
            pass
        try:
            self.system_bus = system_bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
            session_path = self._session_path(system_bus)
            if session_path:
                system_bus.signal_subscribe(LOGIN1, LOGIN1 + ".Session", "Unlock", session_path, None,
                                            Gio.DBusSignalFlags.NONE, lambda *_: self.on_unlock())
                system_bus.signal_subscribe(LOGIN1, "org.freedesktop.DBus.Properties", "PropertiesChanged",
                                            session_path, None, Gio.DBusSignalFlags.NONE,
                                            self._on_properties_changed)
        except GLib.Error:
            pass

    @staticmethod
    def _session_path(system_bus):
        session_id = os.environ.get("XDG_SESSION_ID")
        method, args = ("GetSession", ("s", session_id)) if session_id else ("GetSessionByPID", ("u", os.getpid()))
        try:
            result = system_bus.call_sync(
                LOGIN1, "/org/freedesktop/login1", LOGIN1 + ".Manager", method,
                GLib.Variant("(%s)" % args[0], (args[1],)), GLib.VariantType("(o)"),
                Gio.DBusCallFlags.NONE, 5000, None)
            return result.unpack()[0]
        except GLib.Error:
            return None

    def _on_active_changed(self, _connection, _sender, _path, _interface, _signal, parameters):
        if parameters.get_type_string() == "(b)" and not parameters.unpack()[0]:
            self.on_unlock()

    def _on_properties_changed(self, _connection, _sender, _path, _interface, _signal, parameters):
        interface, changed, _invalidated = parameters.unpack()
        if interface == LOGIN1 + ".Session" and "LockedHint" in changed:
            locked = bool(changed["LockedHint"])
            if self.locked_hint and not locked:
                self.on_unlock()
            self.locked_hint = locked
