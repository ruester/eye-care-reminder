"""The tray application: shows an eye break reminder every configured interval.

GtkApplication keeps one instance per session: starting the app again (menu
entry, installer) makes the running instance open its settings instead.
"""

import datetime
import os
import time

from gi.repository import Gdk, Gio, GLib, Gtk

from . import APP_ID, languages, painting, should_open_settings, timeformat, ui_popup
from .session_lock import UnlockWatcher
from .settings import Settings
from .ui_settings import SettingsDialog
from .ui_tray import Tray

CHECK_SECONDS = 5  # wall-clock check, so the reminder also follows after suspend


class EyeCareReminderApp(Gtk.Application):
    def __init__(self, app_dir):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.app_dir = app_dir
        self.started = False
        self.settings = None
        self.language = None
        self.tray = None
        self.popup = None
        self.settings_dialog = None
        self.next_break = 0.0
        self.time_format = None

    @property
    def icon_path(self):
        return os.path.join(self.app_dir, "icons", "eye-care-reminder-256.png")

    def do_command_line(self, command_line):
        args = command_line.get_arguments()[1:]
        if not self.started:
            self.start()
        if should_open_settings(args):
            self.show_settings()
        return 0

    def start(self):
        self.started = True
        self.hold()  # keep running without windows
        self.time_format = timeformat.locale_time_format()
        self.settings = Settings.load()
        self.language = languages.from_setting(self.settings.language)
        first_run = not self.settings.exists
        if first_run:
            self.settings.save()

        self.tray = Tray(self.icon_path, self.show_settings, self.show_reminder, self.exit)
        self.tray.set_texts(self.language.texts)
        self.restart_timer()
        GLib.timeout_add_seconds(CHECK_SECONDS, self._check)
        self.unlock_watcher = UnlockWatcher(self.restart_timer)

        if first_run:
            texts = self.language.texts
            next_break = datetime.datetime.fromtimestamp(self.next_break)
            self.show_popup(texts.running_title,
                            texts.running_message.format(timeformat.time_of_day(next_break, self.time_format)),
                            self._hide_after_seconds())

    def _hide_after_seconds(self):
        return self.settings.auto_hide_seconds if self.settings.auto_hide else 0

    def _check(self):
        if time.time() >= self.next_break:
            self.show_reminder()
        return True

    def restart_timer(self):
        self.next_break = time.time() + self.settings.interval_minutes * 60
        texts = self.language.texts
        next_break = datetime.datetime.fromtimestamp(self.next_break)
        self.tray.set_next_break(timeformat.tray_text(next_break, texts, self.time_format),
                                 texts.next_break_at.format(timeformat.time_of_day(next_break, self.time_format)))

    def show_reminder(self):
        self.show_break_notification(self._hide_after_seconds(), self.language.texts)
        self.restart_timer()

    def show_break_notification(self, hide_after_seconds, texts):
        self.show_popup(texts.break_title, texts.break_message, hide_after_seconds)

    def show_popup(self, title, message, hide_after_seconds):
        """hide_after_seconds 0 keeps the popup open until it is clicked."""
        if self.popup:
            self.popup.close()
        self.popup = ui_popup.show(title, message, hide_after_seconds * 1000, self.icon_path, self._popup_closed)

    def _popup_closed(self, popup):
        if self.popup is popup:
            self.popup = None

    def show_settings(self):
        if self.settings_dialog:
            self.settings_dialog.present_with_time(Gtk.get_current_event_time() or Gdk.CURRENT_TIME)
            return
        icon = Gdk.pixbuf_get_from_surface(painting.icon_surface(64), 0, 0, 64, 64)
        self.settings_dialog = SettingsDialog(self.settings, self.language, icon,
                                              self.show_break_notification, self._save_settings)
        self.settings_dialog.connect("destroy", self._settings_closed)
        self.add_window(self.settings_dialog)
        self.settings_dialog.present()

    def _settings_closed(self, _dialog):
        self.settings_dialog = None

    def _save_settings(self, interval_minutes, auto_hide, auto_hide_seconds, language):
        self.settings.interval_minutes = interval_minutes
        self.settings.auto_hide = auto_hide
        self.settings.auto_hide_seconds = auto_hide_seconds
        self.settings.language = language.code
        self.language = language
        try:
            self.settings.save()
        except OSError as error:
            print("eye-care-reminder: cannot save the settings: %s" % error)
        self.tray.set_texts(language.texts)
        self.restart_timer()

    def exit(self):
        if self.settings_dialog:
            self.settings_dialog.destroy()
        if self.popup:
            self.popup.close()
        self.tray.destroy()
        self.release()
        self.quit()
