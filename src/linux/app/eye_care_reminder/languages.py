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
    Language("fr-BE", "Français (Belgique)", flags.BELGIUM, translations.FRENCH),
    Language("hr", "Hrvatski", flags.CROATIA, translations.CROATIAN),
    Language("it", "Italiano", flags.ITALY, translations.ITALIAN),
    Language("nl", "Nederlands", flags.NETHERLANDS, translations.DUTCH),
    Language("nl-BE", "Nederlands (België)", flags.BELGIUM, translations.DUTCH),
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


def detect(messages_locale, region_locale=None):
    """The language of the messages locale (e.g. "de_DE.UTF-8"); Dutch and French become
    Belgian if either locale is Belgian. Unsupported languages: English."""
    language, region = _parse(messages_locale)
    if language in ("nn", "no"):
        language = "nb"
    if language in ("nl", "fr") and "BE" in (region, _parse(region_locale)[1]):
        language += "-BE"
    return find(language) or ENGLISH


def locale_from_environment(environ=None):
    """(messages locale, regional format locale) of the user, as the C library picks them."""
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
    return messages, first("LC_ALL", "LC_TIME", "LANG")


def from_setting(code, environ=None):
    """The stored language if valid, otherwise the one of the user's locale."""
    return find(code) or detect(*locale_from_environment(environ))
