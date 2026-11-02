using System;
using System.Collections.Generic;
using System.Globalization;

namespace EyeCareReminder
{
    /// <summary>
    /// A selectable app language, shown with its flag and its name in the language itself
    /// ("Deutsch", "Français", ...).
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
            new Language("hr", "Hrvatski", Flags.Croatia, Translations.Croatian),
            new Language("it", "Italiano", Flags.Italy, Translations.Italian),
            new Language("nl", "Nederlands", Flags.Netherlands, Translations.Dutch),
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
        /// The language matching the Windows display language (<paramref name="uiCulture"/>),
        /// whatever its region (fr-BE is French). Unsupported languages: English.
        /// </summary>
        public static Language Detect(CultureInfo uiCulture)
        {
            string language = uiCulture.TwoLetterISOLanguageName;
            if (language == "nn" || language == "no")
            {
                language = "nb";
            }
            return Find(language) ?? English;
        }

        /// <summary>
        /// The stored language if valid, otherwise the detected one. A stored code with a region
        /// that no longer exists (the Belgian nl-BE / fr-BE up to version 1.3) is its language.
        /// </summary>
        public static Language FromSetting(string code, CultureInfo uiCulture)
        {
            var language = Find(code);
            if (language == null && code != null && code.Contains("-"))
            {
                language = Find(code.Substring(0, code.IndexOf('-')));
            }
            return language ?? Detect(uiCulture);
        }

        /// <summary>The stored language if valid, otherwise the one of the current Windows user.</summary>
        public static Language FromSetting(string code) => FromSetting(code, CultureInfo.CurrentUICulture);
    }
}
