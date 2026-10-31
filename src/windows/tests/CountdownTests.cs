using Xunit;

namespace EyeCareReminder.Tests
{
    public class CountdownTests
    {
        [Theory]
        [InlineData(0, 60000, 1.0)]
        [InlineData(15000, 60000, 0.75)]
        [InlineData(30000, 60000, 0.5)]
        [InlineData(60000, 60000, 0.0)]
        [InlineData(90000, 60000, 0.0)]
        [InlineData(-100, 60000, 1.0)]
        [InlineData(500, 0, 0.0)]
        [InlineData(500, -1, 0.0)]
        public void RemainingFraction(long elapsedMs, int timeoutMs, double expected)
        {
            Assert.Equal(expected, Countdown.RemainingFraction(elapsedMs, timeoutMs), 6);
        }

        [Theory]
        [InlineData(300, 0, 60000, 300)]
        [InlineData(300, 20000, 60000, 200)]
        [InlineData(300, 30000, 60000, 150)]
        [InlineData(300, 59999, 60000, 0)]
        [InlineData(300, 60000, 60000, 0)]
        [InlineData(0, 30000, 60000, 0)]
        public void BarWidthShrinksWithElapsedTime(int trackWidth, long elapsedMs, int timeoutMs, int expected)
        {
            Assert.Equal(expected, Countdown.BarWidth(trackWidth, elapsedMs, timeoutMs));
        }
    }
}
