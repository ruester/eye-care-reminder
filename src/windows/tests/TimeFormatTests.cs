using System;
using Xunit;

namespace EyeCareReminder.Tests
{
    public class TimeFormatTests
    {
        [Fact]
        public void TrayTextContainsTheNextBreak()
        {
            var nextBreak = new DateTime(2026, 10, 31, 14, 5, 0);

            string text = TimeFormat.TrayText(nextBreak, Translations.English);

            Assert.Equal("Eye Care Reminder\nNext break at " + nextBreak.ToString("t"), text);
        }

        [Fact]
        public void TrayTextFitsIntoNotifyIconWithoutCuttingTheTimeInEveryLanguage()
        {
            foreach (var language in Languages.All)
            {
                // Long times of day in the current culture's format, e.g. "12:59 PM".
                foreach (int hour in new[] { 0, 10, 12, 23 })
                {
                    var nextBreak = new DateTime(2026, 12, 31, hour, 59, 59);

                    string text = TimeFormat.TrayText(nextBreak, language.Texts);

                    Assert.True(text.Length <= TimeFormat.MaxTrayTextLength, $"Too long: {text}");
                    Assert.EndsWith(TimeFormat.Time(nextBreak), text);
                }
            }
        }
    }
}
