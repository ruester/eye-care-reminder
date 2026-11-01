using System;
using Microsoft.Win32;
using Xunit;

namespace EyeCareReminder.Tests
{
    /// <summary>
    /// Runs against a throwaway key below HKCU so the real settings of the
    /// developer running the tests stay untouched.
    /// </summary>
    public sealed class SettingsTests : IDisposable
    {
        private readonly string originalKeyPath = Settings.KeyPath;
        private readonly string testKeyPath = @"Software\EyeCareReminder.Tests\" + Guid.NewGuid().ToString("N");

        public SettingsTests()
        {
            Settings.KeyPath = testKeyPath;
        }

        public void Dispose()
        {
            Settings.KeyPath = originalKeyPath;
            Registry.CurrentUser.DeleteSubKeyTree(@"Software\EyeCareReminder.Tests", false);
        }

        [Fact]
        public void DefaultsWhenNothingIsStored()
        {
            Assert.False(Settings.Exists());
            Assert.Equal(60, Settings.LoadIntervalMinutes());
            Assert.True(Settings.LoadAutoHide());
            Assert.Equal(60, Settings.LoadAutoHideSeconds());
            Assert.Null(Settings.LoadLanguage());
        }

        [Fact]
        public void LanguageRoundTrip()
        {
            Settings.SaveLanguage("nl-BE");

            Assert.Equal("nl-BE", Settings.LoadLanguage());
            Assert.False(Settings.Exists()); // the installer writes the language before the first start
        }

        [Fact]
        public void LanguageOfTheWrongTypeIsIgnored()
        {
            SetValue("Language", 1, RegistryValueKind.DWord);

            Assert.Null(Settings.LoadLanguage());
        }

        [Fact]
        public void IntervalRoundTrip()
        {
            Settings.SaveIntervalMinutes(25);

            Assert.True(Settings.Exists());
            Assert.Equal(25, Settings.LoadIntervalMinutes());
        }

        [Theory]
        [InlineData(false, 1)]
        [InlineData(true, 300)]
        public void AutoHideRoundTrip(bool enabled, int seconds)
        {
            Settings.SaveAutoHide(enabled, seconds);

            Assert.Equal(enabled, Settings.LoadAutoHide());
            Assert.Equal(seconds, Settings.LoadAutoHideSeconds());
        }

        [Theory]
        [InlineData("IntervalMinutes", 0)]
        [InlineData("IntervalMinutes", 1441)]
        [InlineData("AutoHide", 2)]
        [InlineData("AutoHideSeconds", 0)]
        [InlineData("AutoHideSeconds", 301)]
        public void OutOfRangeValuesFallBackToDefaults(string name, int value)
        {
            SetValue(name, value, RegistryValueKind.DWord);

            AssertDefaults();
        }

        [Fact]
        public void ValuesOfTheWrongTypeFallBackToDefaults()
        {
            SetValue("IntervalMinutes", "30", RegistryValueKind.String);
            SetValue("AutoHide", "0", RegistryValueKind.String);
            SetValue("AutoHideSeconds", "10", RegistryValueKind.String);

            AssertDefaults();
        }

        private void SetValue(string name, object value, RegistryValueKind kind)
        {
            using (var key = Registry.CurrentUser.CreateSubKey(testKeyPath))
            {
                key.SetValue(name, value, kind);
            }
        }

        private static void AssertDefaults()
        {
            Assert.Equal(Settings.DefaultIntervalMinutes, Settings.LoadIntervalMinutes());
            Assert.Equal(Settings.DefaultAutoHide, Settings.LoadAutoHide());
            Assert.Equal(Settings.DefaultAutoHideSeconds, Settings.LoadAutoHideSeconds());
        }
    }
}
