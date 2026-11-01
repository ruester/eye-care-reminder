import dataclasses
import re
import string
import unittest

import windows_translations
from eye_care_reminder import translations
from eye_care_reminder.plural import PluralRule
from eye_care_reminder.translations import Texts, mnemonic

ALL = {name: value for name, value in vars(translations).items() if isinstance(value, Texts)}
FIELDS = [f.name for f in dataclasses.fields(Texts)]
STRING_FIELDS = [name for name in FIELDS if name not in ("plural_rule", "minutes", "seconds")]


def placeholders(text):
    return sorted(field for _, field, _, _ in string.Formatter().parse(text) if field is not None)


class TranslationsTests(unittest.TestCase):
    def test_same_texts_as_the_windows_app(self):
        windows = windows_translations.load()
        self.assertEqual(sorted(name.upper() for name in windows), sorted(ALL))
        for name, fields in windows.items():
            texts = ALL[name.upper()]
            for field in FIELDS:
                with self.subTest(language=name, field=field):
                    value = getattr(texts, field)
                    if isinstance(value, PluralRule):
                        value = value.value
                    elif isinstance(value, tuple):
                        value = list(value)
                    self.assertEqual(fields[field], value)

    def test_texts_are_not_empty(self):
        for name, texts in ALL.items():
            for field in STRING_FIELDS:
                with self.subTest(language=name, field=field):
                    self.assertTrue(getattr(texts, field).strip())

    def test_placeholders_match_english(self):
        for name, texts in ALL.items():
            for field in STRING_FIELDS:
                with self.subTest(language=name, field=field):
                    self.assertEqual(placeholders(getattr(translations.ENGLISH, field)),
                                     placeholders(getattr(texts, field)))
                    getattr(texts, field).format("x", "y")  # no format errors

    def test_counted_forms(self):
        for name, texts in ALL.items():
            three = texts.plural_rule in (PluralRule.CZECH, PluralRule.POLISH, PluralRule.CROATIAN)
            for forms in (texts.minutes, texts.seconds):
                with self.subTest(language=name, forms=forms):
                    self.assertEqual(3 if three else 2, len(forms))
                    for form in forms:
                        self.assertEqual(["0"], placeholders(form))

    def test_menu_accelerators(self):
        for name, texts in ALL.items():
            keys = []
            for field in ("menu_settings", "menu_break_now", "menu_exit"):
                text = getattr(texts, field)
                with self.subTest(language=name, field=field):
                    self.assertEqual(1, text.count("&"))
                    keys.append(text[text.index("&") + 1].lower())
            self.assertEqual(len(keys), len(set(keys)), name)

    def test_mnemonic(self):
        self.assertEqual("E_xit", mnemonic("E&xit"))
        self.assertEqual("a__b _c", mnemonic("a_b &c"))

    def test_format_counts(self):
        self.assertEqual("1 minute", translations.ENGLISH.format_minutes(1))
        self.assertEqual("60 seconds", translations.ENGLISH.format_seconds(60))
        self.assertEqual("5 minut", translations.POLISH.format_minutes(5))
        self.assertEqual("22 sekundy", translations.POLISH.format_seconds(22))

    def test_no_windows_only_characters(self):
        for name, texts in ALL.items():
            for field in STRING_FIELDS:
                self.assertIsNone(re.search(r"[\r\t]", getattr(texts, field)), (name, field))


if __name__ == "__main__":
    unittest.main()
