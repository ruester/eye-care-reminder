using System;
using System.Collections.Generic;
using System.Globalization;

namespace EyeCareReminder
{
    /// <summary>
    /// A selectable app language, shown with its flag and its name in the language itself
    /// ("Deutsch", "Français", ...); the Belgian variants name the country in brackets.
    /// </summary>
    internal sealed class Language
    {
        public Language(string code, string nativeName, Flag flag, Texts texts)
        {
            Code = code;
            NativeName = nativeName;
            Flag = flag;
            Texts = texts;
        }

        /// <summary>Stored in the registry value "Language" (also written by the installer).</summary>
        public string Code { get; }

        public string NativeName { get; }

        public Flag Flag { get; }

        public Texts Texts { get; }

        public override string ToString() => NativeName;
    }

    internal static class Languages
    {
        public static readonly Language English = new Language("en", "English", Flags.UnitedKingdom, Translations.English);

        /// <summary>All languages in the order of the language switcher (alphabetical by native language name).
        /// Keep in sync with the language list in src/windows/installer/Package.wxs.</summary>
        public static readonly IReadOnlyList<Language> All = new[]
        {
            new Language("cs", "Čeština", Flags.Czechia, Translations.Czech),
            new Language("de", "Deutsch", Flags.Germany, Translations.German),
            English,
            new Language("es", "Español", Flags.Spain, Translations.Spanish),
            new Language("fr", "Français", Flags.France, Translations.French),
            new Language("fr-BE", "Français (Belgique)", Flags.Belgium, Translations.French),
            new Language("hr", "Hrvatski", Flags.Croatia, Translations.Croatian),
            new Language("it", "Italiano", Flags.Italy, Translations.Italian),
            new Language("nl", "Nederlands", Flags.Netherlands, Translations.Dutch),
            new Language("nl-BE", "Nederlands (België)", Flags.Belgium, Translations.Dutch),
            new Language("nb", "Norsk", Flags.Norway, Translations.Norwegian),
            new Language("pl", "Polski", Flags.Poland, Translations.Polish),
            new Language("pt", "Português", Flags.Portugal, Translations.Portuguese),
            new Language("fi", "Suomi", Flags.Finland, Translations.Finnish),
            new Language("sv", "Svenska", Flags.Sweden, Translations.Swedish),
        };

        /// <summary>The language with this code (case-insensitive), or null.</summary>
        public static Language Find(string code)
        {
            foreach (var language in All)
            {
                if (string.Equals(language.Code, code, StringComparison.OrdinalIgnoreCase))
                {
                    return language;
                }
            }
            return null;
        }

        /// <summary>
        /// The language matching the Windows display language (<paramref name="uiCulture"/>);
        /// Dutch and French become Belgian if either culture is Belgian (the regional format
        /// usually is, Windows has no Belgian display language). Unsupported languages: English.
        /// </summary>
        public static Language Detect(CultureInfo uiCulture, CultureInfo regionCulture)
        {
            string language = uiCulture.TwoLetterISOLanguageName;
            if (language == "nn" || language == "no")
            {
                language = "nb";
            }
            if ((language == "nl" || language == "fr") && (IsBelgian(uiCulture) || IsBelgian(regionCulture)))
            {
                language += "-BE";
            }
            return Find(language) ?? English;
        }

        /// <summary>The stored language if valid, otherwise the detected one.</summary>
        public static Language FromSetting(string code, CultureInfo uiCulture, CultureInfo regionCulture) =>
            Find(code) ?? Detect(uiCulture, regionCulture);

        /// <summary>The stored language if valid, otherwise the one of the current Windows user.</summary>
        public static Language FromSetting(string code) =>
            FromSetting(code, CultureInfo.CurrentUICulture, CultureInfo.CurrentCulture);

        private static bool IsBelgian(CultureInfo culture) =>
            culture.Name.EndsWith("-BE", StringComparison.OrdinalIgnoreCase);
    }
}
