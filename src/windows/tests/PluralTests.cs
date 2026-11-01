using Xunit;

namespace EyeCareReminder.Tests
{
    public class PluralTests
    {
        [Theory]
        [InlineData(1, "1 minute")]
        [InlineData(2, "2 minutes")]
        [InlineData(60, "60 minutes")]
        public void English(int n, string expected) => Assert.Equal(expected, Translations.English.FormatMinutes(n));

        [Theory]
        [InlineData(0, "0 minute")]
        [InlineData(1, "1 minute")]
        [InlineData(2, "2 minutes")]
        public void French(int n, string expected) => Assert.Equal(expected, Translations.French.FormatMinutes(n));

        [Theory]
        [InlineData(1, "1 minuta")]
        [InlineData(3, "3 minuty")]
        [InlineData(5, "5 minut")]
        [InlineData(22, "22 minut")]
        public void Czech(int n, string expected) => Assert.Equal(expected, Translations.Czech.FormatMinutes(n));

        [Theory]
        [InlineData(1, "1 minuta")]
        [InlineData(4, "4 minuty")]
        [InlineData(12, "12 minut")]
        [InlineData(22, "22 minuty")]
        [InlineData(60, "60 minut")]
        public void Polish(int n, string expected) => Assert.Equal(expected, Translations.Polish.FormatMinutes(n));

        [Theory]
        [InlineData(1, "1 sekunda")]
        [InlineData(2, "2 sekunde")]
        [InlineData(11, "11 sekundi")]
        [InlineData(21, "21 sekunda")]
        [InlineData(24, "24 sekunde")]
        [InlineData(60, "60 sekundi")]
        public void Croatian(int n, string expected) => Assert.Equal(expected, Translations.Croatian.FormatSeconds(n));
    }
}
