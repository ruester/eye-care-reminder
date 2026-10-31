using Xunit;

namespace EyeCareReminder.Tests
{
    public class ProgramTests
    {
        [Fact]
        public void ManualLaunchOpensSettings()
        {
            Assert.True(Program.ShouldOpenSettings(new string[0]));
            Assert.True(Program.ShouldOpenSettings(new[] { "--something-else" }));
        }

        [Fact]
        public void AutostartLaunchStaysInTray()
        {
            Assert.False(Program.ShouldOpenSettings(new[] { "--autostart" }));
            Assert.False(Program.ShouldOpenSettings(new[] { "--other", "--autostart" }));
        }
    }
}
