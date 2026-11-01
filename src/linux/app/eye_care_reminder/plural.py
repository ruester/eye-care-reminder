"""Plural rules of the supported languages (CLDR, integers only), as in the Windows app."""

import enum

ONE = 0
FEW = 1
OTHER = 2


class PluralRule(enum.Enum):
    ONE_OTHER = "one_other"  # 1 = one, everything else = other (English, German, ...)
    FRENCH = "french"  # 0 and 1 = one
    CZECH = "czech"  # 1 = one, 2-4 = few, else other
    POLISH = "polish"  # 1 = one, 2-4, 22-24, ... (not 12-14) = few, else other
    CROATIAN = "croatian"  # 1, 21, 31, ... (not 11) = one, 2-4, 22-24, ... (not 12-14) = few, else other


def category(rule, n):
    mod10 = n % 10
    mod100 = n % 100
    few_ending = 2 <= mod10 <= 4 and not 12 <= mod100 <= 14
    if rule is PluralRule.FRENCH:
        return ONE if n <= 1 else OTHER
    if rule is PluralRule.CZECH:
        return ONE if n == 1 else FEW if 2 <= n <= 4 else OTHER
    if rule is PluralRule.POLISH:
        return ONE if n == 1 else FEW if few_ending else OTHER
    if rule is PluralRule.CROATIAN:
        return ONE if mod10 == 1 and mod100 != 11 else FEW if few_ending else OTHER
    return ONE if n == 1 else OTHER


def format_count(n, rule, forms):
    """n with the matching form of forms: (one, other) or (one, few, other)."""
    return forms[min(category(rule, n), len(forms) - 1)].format(n)
