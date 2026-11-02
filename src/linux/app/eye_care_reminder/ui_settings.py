"""Settings dialog: interval, auto-hide time and language (with flags).
Choosing a language translates the dialog right away; "Test notification"
uses the values entered so far, even unsaved ones (as on Windows)."""

from gi.repository import Gdk, GdkPixbuf, GLib, Gtk, Pango

from . import languages, painting, settings


class LanguageComboBox(Gtk.ComboBox):
    """Drop-down list of languages.ALL, each with its flag and its name in the language itself."""

    def __init__(self, selected):
        store = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        super().__init__(model=store)
        metrics = self.get_pango_context().get_metrics(None, None)
        height = max(8, (metrics.get_ascent() + metrics.get_descent()) // Pango.SCALE - 2)
        width = height * 3 // 2
        for language in languages.ALL:
            surface = painting.flag_surface(language.flag, width, height)
            store.append([Gdk.pixbuf_get_from_surface(surface, 0, 0, width, height), language.native_name])
        flag = Gtk.CellRendererPixbuf()
        self.pack_start(flag, False)
        self.add_attribute(flag, "pixbuf", 0)
        name = Gtk.CellRendererText()
        self.pack_start(name, True)
        self.add_attribute(name, "text", 1)
        self.selected_language = selected

    @property
    def selected_language(self):
        index = self.get_active()
        return languages.ALL[index] if index >= 0 else languages.ENGLISH

    @selected_language.setter
    def selected_language(self, language):
        self.set_active(languages.ALL.index(language) if language in languages.ALL else -1)


class SettingsDialog(Gtk.Window):
    def __init__(self, current, language, icon, on_test, on_save, version=""):
        """current: Settings; on_test(auto_hide_seconds or 0, texts); on_save(interval_minutes,
        auto_hide, auto_hide_seconds, language); the dialog closes itself. version: shown
        small at the bottom left ("v1.3.3")."""
        super().__init__(title="")
        self.on_test = on_test
        self.on_save = on_save
        self.set_icon(icon)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(12)
        self.connect("key-press-event", self._on_key)

        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.interval_label = self._label(layout)
        self.interval_input = self._spin(settings.MIN_INTERVAL_MINUTES, settings.MAX_INTERVAL_MINUTES,
                                         current.interval_minutes)
        self.minutes_label = self._row(layout, self.interval_input)
        self.interval_default_label = self._hint(layout)

        self.auto_hide_check = Gtk.CheckButton(active=current.auto_hide)
        self.auto_hide_check.set_margin_top(12)
        layout.pack_start(self.auto_hide_check, False, False, 0)
        self.auto_hide_input = self._spin(settings.MIN_AUTO_HIDE_SECONDS, settings.MAX_AUTO_HIDE_SECONDS,
                                          current.auto_hide_seconds)
        self.auto_hide_input.set_sensitive(current.auto_hide)
        self.auto_hide_check.connect(
            "toggled", lambda check: self.auto_hide_input.set_sensitive(check.get_active()))
        self.seconds_label = self._row(layout, self.auto_hide_input)
        self.auto_hide_default_label = self._hint(layout)

        self.language_label = self._label(layout)
        self.language_label.set_margin_top(12)
        self.language_input = LanguageComboBox(language)
        self.language_input.set_halign(Gtk.Align.START)
        self.language_input.connect("changed", lambda _: self.apply_texts(self.selected_language.texts))
        layout.pack_start(self.language_input, False, False, 0)

        # Bottom row: the installed version, small and gray, at the left; the buttons at the right.
        bottom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        bottom.set_margin_top(18)
        self.version_label = Gtk.Label(xalign=0)
        self.version_label.set_markup("<small>%s</small>" % GLib.markup_escape_text(version))
        self.version_label.get_style_context().add_class("dim-label")
        self.version_label.set_valign(Gtk.Align.CENTER)
        bottom.pack_start(self.version_label, True, True, 0)
        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        buttons.set_halign(Gtk.Align.END)
        self.test_button = Gtk.Button()
        self.test_button.connect(
            "clicked", lambda _: self.on_test(self.auto_hide_seconds if self.auto_hide else 0,
                                              self.selected_language.texts))
        self.save_button = Gtk.Button(can_default=True)
        self.save_button.get_style_context().add_class("suggested-action")
        self.save_button.connect("clicked", lambda _: self._save())
        self.cancel_button = Gtk.Button()
        self.cancel_button.connect("clicked", lambda _: self.destroy())
        for button in (self.test_button, self.save_button, self.cancel_button):
            buttons.pack_start(button, False, False, 0)
        bottom.pack_end(buttons, False, False, 0)
        layout.pack_start(bottom, False, False, 0)

        self.add(layout)
        self.set_default(self.save_button)
        self.apply_texts(language.texts)
        layout.show_all()

    @property
    def interval_minutes(self):
        self.interval_input.update()
        return self.interval_input.get_value_as_int()

    @property
    def auto_hide(self):
        return self.auto_hide_check.get_active()

    @property
    def auto_hide_seconds(self):
        self.auto_hide_input.update()
        return self.auto_hide_input.get_value_as_int()

    @property
    def selected_language(self):
        return self.language_input.selected_language

    def apply_texts(self, texts):
        self.set_title(texts.settings_title)
        self.interval_label.set_text(texts.interval_label)
        self.minutes_label.set_text(texts.minutes_unit)
        self.interval_default_label.set_text(
            texts.interval_default.format(texts.format_minutes(settings.DEFAULT_INTERVAL_MINUTES)))
        self.auto_hide_check.set_label(texts.auto_hide_label)
        self.seconds_label.set_text(texts.seconds_unit)
        self.auto_hide_default_label.set_text(texts.auto_hide_default.format(
            texts.format_seconds(settings.DEFAULT_AUTO_HIDE_SECONDS),
            texts.format_minutes(settings.MAX_AUTO_HIDE_SECONDS // 60)))
        self.language_label.set_text(texts.language_label)
        self.test_button.set_label(texts.test_notification)
        self.save_button.set_label(texts.save)
        self.cancel_button.set_label(texts.cancel)

    def _save(self):
        self.on_save(self.interval_minutes, self.auto_hide, self.auto_hide_seconds, self.selected_language)
        self.destroy()

    def _on_key(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
            return True
        return False

    @staticmethod
    def _label(layout):
        label = Gtk.Label(xalign=0)
        layout.pack_start(label, False, False, 0)
        return label

    @staticmethod
    def _spin(minimum, maximum, value):
        spin = Gtk.SpinButton.new_with_range(minimum, maximum, 1)
        spin.set_value(value)
        spin.set_activates_default(True)
        spin.set_width_chars(5)
        return spin

    @staticmethod
    def _row(layout, spin):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row.pack_start(spin, False, False, 0)
        unit = Gtk.Label(xalign=0)
        row.pack_start(unit, False, False, 0)
        layout.pack_start(row, False, False, 0)
        return unit

    @staticmethod
    def _hint(layout):
        label = Gtk.Label(xalign=0)
        label.get_style_context().add_class("dim-label")
        layout.pack_start(label, False, False, 0)
        return label
