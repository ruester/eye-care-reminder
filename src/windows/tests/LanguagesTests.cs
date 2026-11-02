using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;
using Xunit;

namespace EyeCareReminder.Tests
{
    public class LanguagesTests
    {
        public static IEnumerable<object[]> AllLanguages => Languages.All.Select(l => new object[] { l.Code });

        [Fact]
        public void CodesAndNamesAreUnique()
        {
            Assert.Equal(Languages.All.Count, Languages.All.Select(l => l.Code.ToLowerInvariant()).Distinct().Count());
            Assert.Equal(Languages.All.Count, Languages.All.Select(l => l.NativeName).Distinct().Count());
        }

        [Theory]
        [MemberData(nameof(AllLanguages))]
        public void TextsAreCompleteAndHaveTheSamePlaceholdersAsEnglish(string code)
        {
            var texts = Languages.Find(code).Texts;
            foreach (var property in typeof(Texts).GetProperties().Where(p => p.PropertyType == typeof(string)))
            {
                string text = (string)property.GetValue(texts);
                string english = (string)property.GetValue(Translations.English);
                Assert.False(string.IsNullOrWhiteSpace(text), $"{code}: {property.Name} is missing");
                Assert.Equal(Placeholders(english), Placeholders(text));
                Assert.Equal(english.Count(c => c == '&'), text.Count(c => c == '&'));
            }
        }

        [Theory]
        [MemberData(nameof(AllLanguages))]
        public void CountedFormsMatchThePluralRule(string code)
        {
            var texts = Languages.Find(code).Texts;
            bool hasFewForm = texts.PluralRule == PluralRule.Czech || texts.PluralRule == PluralRule.Polish
                || texts.PluralRule == PluralRule.Croatian;
            foreach (var forms in new[] { texts.Minutes, texts.Seconds })
            {
                Assert.Equal(hasFewForm ? 3 : 2, forms.Length);
                Assert.All(forms, form => Assert.Contains("{0}", form));
            }
        }

        [Theory]
        [MemberData(nameof(AllLanguages))]
        public void MenuAcceleratorsAreDistinct(string code)
        {
            var texts = Languages.Find(code).Texts;
            var keys = new[] { texts.MenuSettings, texts.MenuBreakNow, texts.MenuExit }
                .Select(t => char.ToLowerInvariant(t[t.IndexOf('&') + 1]));
            Assert.Equal(3, keys.Distinct().Count());
        }

        [Theory]
        [MemberData(nameof(AllLanguages))]
        public void EveryLanguageHasAFlag(string code)
        {
            var flag = Languages.Find(code).Flag;
            Assert.NotNull(flag);
            Assert.NotEmpty(flag.Colors);
            if (flag.Pattern == FlagPattern.HorizontalStripes || flag.Pattern == FlagPattern.VerticalStripes)
            {
                Assert.Equal(flag.Colors.Length, flag.Weights.Length);
            }
            if (flag.Pattern == FlagPattern.NordicCross)
            {
                Assert.Equal(flag.Weights.Length, flag.CrossWeightsY.Length);
                Assert.Equal(flag.Weights.Length == 5 ? 3 : 2, flag.Colors.Length);
            }
        }

        [Theory]
        [InlineData("de", "de")]
        [InlineData("DE", "de")]
        [InlineData("nl", "nl")]
        [InlineData("nl-BE", null)]
        [InlineData("xx", null)]
        [InlineData("", null)]
        [InlineData(null, null)]
        public void Find(string code, string expected) => Assert.Equal(expected, Languages.Find(code)?.Code);

        [Theory]
        [InlineData("en-US", "en")]
        [InlineData("en-GB", "en")]
        [InlineData("de-DE", "de")]
        [InlineData("de-AT", "de")]
        [InlineData("fr-FR", "fr")]
        [InlineData("fr-BE", "fr")]
        [InlineData("nl-NL", "nl")]
        [InlineData("nl-BE", "nl")]
        [InlineData("it-IT", "it")]
        [InlineData("es-ES", "es")]
        [InlineData("es-MX", "es")]
        [InlineData("pt-PT", "pt")]
        [InlineData("nb-NO", "nb")]
        [InlineData("nn-NO", "nb")]
        [InlineData("sv-SE", "sv")]
        [InlineData("fi-FI", "fi")]
        [InlineData("cs-CZ", "cs")]
        [InlineData("pl-PL", "pl")]
        [InlineData("hr-HR", "hr")]
        [InlineData("ja-JP", "en")]
        public void DetectUsesTheDisplayLanguage(string ui, string expected)
        {
            var language = Languages.Detect(new CultureInfo(ui));

            Assert.Equal(expected, language.Code);
        }

        [Theory]
        [InlineData("pl", "pl")]
        [InlineData("nl-BE", "nl")] // former Belgian variants
        [InlineData("fr-BE", "fr")]
        [InlineData("unknown", "de")]
        [InlineData(null, "de")]
        public void FromSettingFallsBackToDetection(string stored, string expected)
        {
            var german = new CultureInfo("de-DE");

            Assert.Equal(expected, Languages.FromSetting(stored, german).Code);
        }

        private static string[] Placeholders(string text) =>
            Regex.Matches(text, @"\{\d+\}").Cast<Match>().Select(m => m.Value).OrderBy(v => v).ToArray();
    }
}
