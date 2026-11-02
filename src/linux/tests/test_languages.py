import unittest

from eye_care_reminder import languages


class LanguagesTests(unittest.TestCase):
    def test_codes_and_names_are_unique(self):
        codes = [language.code for language in languages.ALL]
        names = [language.native_name for language in languages.ALL]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(15, len(languages.ALL))

    def test_same_list_as_windows_app(self):
        import os
        import re
        path = os.path.join(os.path.dirname(__file__), "..", "..", "windows", "app", "Language.cs")
        with open(path, encoding="utf-8") as f:
            entries = re.findall(r'new Language\("([\w-]+)", "([^"]+)"', f.read())
        english = entries.pop(0)  # the English field, listed in All by name
        entries.insert([language.code for language in languages.ALL].index("en"), english)
        self.assertEqual(("en", "English"), english)
        self.assertEqual(entries, [(language.code, language.native_name) for language in languages.ALL])

    def test_same_codes_as_windows_installer(self):
        import os
        import re
        package = os.path.join(os.path.dirname(__file__), "..", "..", "windows", "installer", "Package.wxs")
        with open(package, encoding="utf-8") as f:
            codes = re.findall(r'<ListItem Value="([\w-]+)"', f.read())
        self.assertEqual(sorted(codes), sorted(language.code for language in languages.ALL))

    def test_switcher_shows_language_names_alphabetically(self):
        names = [language.native_name for language in languages.ALL]
        self.assertEqual(names[:3], ["Čeština", "Deutsch", "English"])
        self.assertIn("Français (Belgique)", names)
        self.assertIn("Nederlands (België)", names)
        # Alphabetical, letters with diacritics sorted with their base letter (Č with C).
        import unicodedata
        key = [unicodedata.normalize("NFD", name).casefold() for name in names]
        self.assertEqual(key, sorted(key))

    def test_find(self):
        self.assertEqual("de", languages.find("DE").code)
        self.assertEqual("nl-BE", languages.find("nl-be").code)
        self.assertIsNone(languages.find("xx"))
        self.assertIsNone(languages.find(None))
        self.assertIsNone(languages.find(""))

    def test_detect(self):
        cases = [
            ("de_DE.UTF-8", None, "de"),
            ("de_AT.UTF-8", "de_AT.UTF-8", "de"),
            ("en_US.UTF-8", None, "en"),
            ("en_GB", None, "en"),
            ("fr_FR.UTF-8", "fr_BE.UTF-8", "fr-BE"),
            ("fr_BE.UTF-8", None, "fr-BE"),
            ("nl_BE.UTF-8", None, "nl-BE"),
            ("nl_NL.UTF-8", "nl_BE.UTF-8", "nl-BE"),
            ("nl_NL.UTF-8", "de_DE.UTF-8", "nl"),
            ("de_BE.UTF-8", None, "de"),
            ("nb_NO.UTF-8", None, "nb"),
            ("nn_NO.UTF-8", None, "nb"),
            ("no_NO", None, "nb"),
            ("pt_BR.UTF-8", None, "pt"),
            ("cs_CZ.UTF-8", None, "cs"),
            ("sr_RS@latin", None, "en"),
            ("C.UTF-8", None, "en"),
            ("POSIX", None, "en"),
            ("", None, "en"),
            (None, None, "en"),
        ]
        for messages, region, expected in cases:
            with self.subTest(messages=messages, region=region):
                self.assertEqual(expected, languages.detect(messages, region).code)

    def test_locale_from_environment(self):
        env = {"LANG": "de_DE.UTF-8"}
        self.assertEqual(("de_DE.UTF-8", "de_DE.UTF-8"), languages.locale_from_environment(env))
        env = {"LANG": "en_US.UTF-8", "LC_MESSAGES": "fr_FR.UTF-8", "LC_TIME": "fr_BE.UTF-8"}
        self.assertEqual(("fr_FR.UTF-8", "fr_BE.UTF-8"), languages.locale_from_environment(env))
        env = {"LANG": "en_US.UTF-8", "LC_ALL": "it_IT.UTF-8", "LC_TIME": "fr_BE.UTF-8"}
        self.assertEqual(("it_IT.UTF-8", "it_IT.UTF-8"), languages.locale_from_environment(env))
        env = {"LANG": "en_US.UTF-8", "LANGUAGE": "sv:en"}
        self.assertEqual("sv", languages.locale_from_environment(env)[0])
        env = {"LANG": "C", "LANGUAGE": "sv:en"}
        self.assertEqual("C", languages.locale_from_environment(env)[0])
        self.assertEqual(("", ""), languages.locale_from_environment({}))

    def test_from_setting(self):
        env = {"LANG": "pl_PL.UTF-8"}
        self.assertEqual("hr", languages.from_setting("hr", env).code)
        self.assertEqual("pl", languages.from_setting(None, env).code)
        self.assertEqual("pl", languages.from_setting("invalid", env).code)
        self.assertEqual("nl-BE", languages.from_setting(None, {"LANG": "nl_BE.UTF-8"}).code)


if __name__ == "__main__":
    unittest.main()
