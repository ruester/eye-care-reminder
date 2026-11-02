"""Selectable app languages and detection from the locale (as in the Windows app's Language.cs)."""

import os
from dataclasses import dataclass

from . import flags, translations
from .flags import Flag
from .translations import Texts


@dataclass(frozen=True)
class Language:
    code: str  # stored in the settings file
    native_name: str  # name of the language in itself, shown in the switcher
    flag: Flag
    texts: Texts


ENGLISH = Language("en", "English", flags.UNITED_KINGDOM, translations.ENGLISH)

# Order of the language switcher (alphabetical by native language name), same codes as on Windows.
ALL = (
    Language("cs", "Čeština", flags.CZECHIA, translations.CZECH),
    Language("de", "Deutsch", flags.GERMANY, translations.GERMAN),
    ENGLISH,
    Language("es", "Español", flags.SPAIN, translations.SPANISH),
    Language("fr", "Français", flags.FRANCE, translations.FRENCH),
    Language("hr", "Hrvatski", flags.CROATIA, translations.CROATIAN),
    Language("it", "Italiano", flags.ITALY, translations.ITALIAN),
    Language("nl", "Nederlands", flags.NETHERLANDS, translations.DUTCH),
    Language("nb", "Norsk", flags.NORWAY, translations.NORWEGIAN),
    Language("pl", "Polski", flags.POLAND, translations.POLISH),
    Language("pt", "Português", flags.PORTUGAL, translations.PORTUGUESE),
    Language("fi", "Suomi", flags.FINLAND, translations.FINNISH),
    Language("sv", "Svenska", flags.SWEDEN, translations.SWEDISH),
)


def find(code):
    """The language with this code (case-insensitive), or None."""
    if not code:
        return None
    for language in ALL:
        if language.code.lower() == code.lower():
            return language
    return None


def _parse(locale_name):
    """"de_AT.UTF-8@euro" -> ("de", "AT"); "C" / "" -> ("", "")."""
    name = (locale_name or "").split(".")[0].split("@")[0]
    language, _, region = name.replace("-", "_").partition("_")
    return language.lower(), region.upper()


def detect(messages_locale):
    """The language of the messages locale (e.g. "de_DE.UTF-8"), whatever its region
    (fr_BE is French). Unsupported languages: English."""
    language, _region = _parse(messages_locale)
    if language in ("nn", "no"):
        language = "nb"
    return find(language) or ENGLISH


def locale_from_environment(environ=None):
    """The user's messages locale, as gettext picks it."""
    environ = os.environ if environ is None else environ

    def first(*names):
        for name in names:
            value = environ.get(name, "")
            if value:
                return value
        return ""

    # LANGUAGE is a priority list ("de_DE:en"); like gettext, it is ignored for the C locale.
    messages = first("LC_ALL", "LC_MESSAGES", "LANG")
    language_list = environ.get("LANGUAGE", "")
    if language_list and messages not in ("", "C", "POSIX") and not messages.startswith("C."):
        messages = language_list.split(":")[0]
    return messages


def from_setting(code, environ=None):
    """The stored language if valid, otherwise the one of the user's locale. A stored code
    with a region that no longer exists (the Belgian nl-BE / fr-BE up to version 1.3) is
    its language."""
    language = find(code)
    if language is None and code and "-" in code:
        language = find(code.split("-")[0])
    return language or detect(locale_from_environment(environ))
