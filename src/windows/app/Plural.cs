using System;
using System.Globalization;

namespace EyeCareReminder
{
    /// <summary>Plural rules of the supported languages (CLDR, integers only).</summary>
    internal enum PluralRule
    {
        /// <summary>1 = one, everything else = other (English, German, ...).</summary>
        OneOther,

        /// <summary>0 and 1 = one (French).</summary>
        French,

        /// <summary>1 = one, 2-4 = few, else many (Czech).</summary>
        Czech,

        /// <summary>1 = one, 2-4, 22-24, ... (not 12-14) = few, else many (Polish).</summary>
        Polish,

        /// <summary>1, 21, 31, ... (not 11) = one, 2-4, 22-24, ... (not 12-14) = few, else other (Croatian).</summary>
        Croatian,
    }

    internal static class Plural
    {
        public const int One = 0;
        public const int Few = 1;
        public const int Other = 2;

        public static int Category(PluralRule rule, int n)
        {
            int mod10 = n % 10;
            int mod100 = n % 100;
            bool fewEnding = mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14);
            switch (rule)
            {
                case PluralRule.French:
                    return n <= 1 ? One : Other;
                case PluralRule.Czech:
                    return n == 1 ? One : n >= 2 && n <= 4 ? Few : Other;
                case PluralRule.Polish:
                    return n == 1 ? One : fewEnding ? Few : Other;
                case PluralRule.Croatian:
                    return mod10 == 1 && mod100 != 11 ? One : fewEnding ? Few : Other;
                default:
                    return n == 1 ? One : Other;
            }
        }

        /// <summary>
        /// Formats <paramref name="n"/> with the matching form of <paramref name="forms"/>:
        /// [one, other] for languages without a "few" form, [one, few, other] otherwise.
        /// </summary>
        public static string Format(int n, PluralRule rule, string[] forms)
        {
            int index = Math.Min(Category(rule, n), forms.Length - 1);
            return string.Format(CultureInfo.CurrentCulture, forms[index], n);
        }
    }
}
