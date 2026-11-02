using System;
using Xunit;

namespace EyeCareReminder.Tests
{
    public class AppVersionTests
    {
        [Theory]
        [InlineData("1.3.3.0", "v1.3.3")]
        [InlineData("0.0.75.0", "v0.0.75")]
        [InlineData("2.0", "v2.0.0")]
        public void Display(string version, string expected) =>
            Assert.Equal(expected, AppVersion.Display(new Version(version)));

        [Fact]
        public void CurrentIsTheAssemblyVersion() =>
            Assert.Equal(typeof(AppVersion).Assembly.GetName().Version, AppVersion.Current);
    }
}
