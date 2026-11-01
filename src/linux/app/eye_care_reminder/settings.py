"""Per-user settings in $XDG_CONFIG_HOME/eye-care-reminder/settings.ini.

Same values and ranges as the Windows app (registry there). Invalid or missing
values fall back to the defaults.
"""

import configparser
import os

DEFAULT_INTERVAL_MINUTES = 20
MIN_INTERVAL_MINUTES = 1
MAX_INTERVAL_MINUTES = 24 * 60

DEFAULT_AUTO_HIDE = True
DEFAULT_AUTO_HIDE_SECONDS = 60
MIN_AUTO_HIDE_SECONDS = 1
MAX_AUTO_HIDE_SECONDS = 5 * 60

SECTION = "settings"


def default_path(environ=None):
    environ = os.environ if environ is None else environ
    config_home = environ.get("XDG_CONFIG_HOME") or os.path.join(environ.get("HOME", "~"), ".config")
    return os.path.join(os.path.expanduser(config_home), "eye-care-reminder", "settings.ini")


class Settings:
    def __init__(self, path=None):
        self.path = path or default_path()
        self.interval_minutes = DEFAULT_INTERVAL_MINUTES
        self.auto_hide = DEFAULT_AUTO_HIDE
        self.auto_hide_seconds = DEFAULT_AUTO_HIDE_SECONDS
        self.language = None  # language code, not validated (see languages.from_setting)
        self.exists = False  # False before the first save: first run

    @classmethod
    def load(cls, path=None):
        settings = cls(path)
        parser = configparser.ConfigParser(interpolation=None)
        try:
            with open(settings.path, encoding="utf-8") as f:
                parser.read_file(f)
        except (OSError, UnicodeDecodeError, configparser.Error):
            return settings
        if not parser.has_section(SECTION):
            return settings
        values = parser[SECTION]
        settings.exists = "interval_minutes" in values
        settings.interval_minutes = _int(values, "interval_minutes", MIN_INTERVAL_MINUTES,
                                         MAX_INTERVAL_MINUTES, DEFAULT_INTERVAL_MINUTES)
        settings.auto_hide_seconds = _int(values, "auto_hide_seconds", MIN_AUTO_HIDE_SECONDS,
                                          MAX_AUTO_HIDE_SECONDS, DEFAULT_AUTO_HIDE_SECONDS)
        try:
            settings.auto_hide = values.getboolean("auto_hide", DEFAULT_AUTO_HIDE)
        except ValueError:
            settings.auto_hide = DEFAULT_AUTO_HIDE
        settings.language = values.get("language") or None
        return settings

    def save(self):
        parser = configparser.ConfigParser(interpolation=None)
        parser[SECTION] = {
            "interval_minutes": str(self.interval_minutes),
            "auto_hide": "true" if self.auto_hide else "false",
            "auto_hide_seconds": str(self.auto_hide_seconds),
        }
        if self.language:
            parser[SECTION]["language"] = self.language
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        temporary = self.path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as f:
            parser.write(f)
        os.replace(temporary, self.path)  # never leaves a half-written file
        self.exists = True


def _int(values, key, minimum, maximum, default):
    try:
        value = int(values.get(key, ""))
    except ValueError:
        return default
    return value if minimum <= value <= maximum else default
