import unittest

from eye_care_reminder.plural import FEW, ONE, OTHER, PluralRule, category, format_count


class PluralTests(unittest.TestCase):
    def test_categories(self):
        cases = {
            PluralRule.ONE_OTHER: {0: OTHER, 1: ONE, 2: OTHER, 5: OTHER, 21: OTHER},
            PluralRule.FRENCH: {0: ONE, 1: ONE, 2: OTHER, 60: OTHER},
            PluralRule.CZECH: {1: ONE, 2: FEW, 4: FEW, 5: OTHER, 22: OTHER, 60: OTHER},
            PluralRule.POLISH: {1: ONE, 2: FEW, 4: FEW, 5: OTHER, 12: OTHER, 14: OTHER, 21: OTHER,
                                22: FEW, 24: FEW, 25: OTHER, 112: OTHER},
            PluralRule.CROATIAN: {1: ONE, 2: FEW, 5: OTHER, 11: OTHER, 12: OTHER, 21: ONE, 22: FEW,
                                  60: OTHER, 101: ONE, 111: OTHER},
        }
        for rule, expected in cases.items():
            for n, cat in expected.items():
                with self.subTest(rule=rule, n=n):
                    self.assertEqual(cat, category(rule, n))

    def test_format_two_forms_uses_other_for_few(self):
        self.assertEqual("3 minutes", format_count(3, PluralRule.CZECH, ("{0} minute", "{0} minutes")))

    def test_format_three_forms(self):
        forms = ("{0} minuta", "{0} minuty", "{0} minut")
        self.assertEqual("1 minuta", format_count(1, PluralRule.CZECH, forms))
        self.assertEqual("3 minuty", format_count(3, PluralRule.CZECH, forms))
        self.assertEqual("60 minut", format_count(60, PluralRule.CZECH, forms))


if __name__ == "__main__":
    unittest.main()
