using System;
using Xunit;

namespace EyeCareReminder.Tests
{
    public class TimeFormatTests
    {
        [Theory]
        [InlineData(1, "minute")]
        [InlineData(2, "2 minutes")]
        [InlineData(45, "45 minutes")]
        [InlineData(60, "hour")]
        [InlineData(90, "90 minutes")]
        [InlineData(120, "2 hours")]
        [InlineData(1440, "24 hours")]
        public void Interval(int minutes, string expected)
        {
            Assert.Equal(expected, TimeFormat.Interval(minutes));
        }

        [Fact]
        public void TrayTextContainsTheNextBreak()
        {
            var nextBreak = new DateTime(2026, 10, 31, 14, 5, 0);

            string text = TimeFormat.TrayText(nextBreak);

            Assert.StartsWith("Eye Care Reminder\nNext break at ", text);
            Assert.EndsWith(nextBreak.ToString("t"), text);
        }

        [Fact]
        public void TrayTextFitsIntoNotifyIconWithoutCuttingTheTime()
        {
            // Long times of day in the current culture's format, e.g. "12:59 PM".
            foreach (int hour in new[] { 0, 10, 12, 23 })
            {
                var nextBreak = new DateTime(2026, 12, 31, hour, 59, 59);

                string text = TimeFormat.TrayText(nextBreak);

                Assert.True(text.Length <= TimeFormat.MaxTrayTextLength, $"Too long: {text}");
                Assert.EndsWith(nextBreak.ToString("t"), text);
            }
        }
    }
}
