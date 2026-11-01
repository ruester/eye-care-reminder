"""Reads the texts of the Windows app (src/windows/app/Translations.cs).

The Linux app has the same texts as the Windows app; test_translations.py
compares both so they can't drift apart.
"""

import os
import re

TRANSLATIONS_CS = os.path.join(
    os.path.dirname(__file__), "..", "..", "windows", "app", "Translations.cs")

_BLOCK = re.compile(r"public static readonly Texts (\w+) = new Texts\s*\{(.*?)\n\s*\};", re.S)
_ARRAY = re.compile(r"(\w+) = new\[\] \{(.*?)\},")
_STRING = re.compile(r'(\w+) = ("(?:[^"\\]|\\.)*"),')
_RULE = re.compile(r"PluralRule = PluralRule\.(\w+),")
_LITERAL = re.compile(r'"((?:[^"\\]|\\.)*)"')


def snake_case(name):
    """MenuBreakNow -> menu_break_now"""
    return re.sub(r"(?<!^)([A-Z])", r"_\1", name).lower()


def _unescape(literal):
    return literal.encode("ascii", "backslashreplace").decode("unicode_escape") \
        if "\\" in literal else literal


def load(path=TRANSLATIONS_CS):
    """{language name (e.g. "German"): {snake_case field: value}}; counted forms are lists."""
    with open(path, encoding="utf-8") as f:
        source = f.read()
    languages = {}
    for name, body in _BLOCK.findall(source):
        fields = {"plural_rule": snake_case(_RULE.search(body).group(1))}
        for key, items in _ARRAY.findall(body):
            fields[snake_case(key)] = [_unescape(s) for s in _LITERAL.findall(items)]
        for key, literal in _STRING.findall(body):
            fields[snake_case(key)] = _unescape(literal[1:-1])
        languages[name] = fields
    return languages
