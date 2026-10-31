using Microsoft.Win32;

namespace EyeCareReminder
{
    /// <summary>Per-user settings stored in HKCU\Software\EyeCareReminder.</summary>
    internal static class Settings
    {
        public const int DefaultIntervalMinutes = 60;
        public const int MinIntervalMinutes = 1;
        public const int MaxIntervalMinutes = 24 * 60;

        public const bool DefaultAutoHide = true;
        public const int DefaultAutoHideSeconds = 60;
        public const int MinAutoHideSeconds = 1;
        public const int MaxAutoHideSeconds = 5 * 60;

        /// <summary>Registry key below HKCU; tests point it to a separate key.</summary>
        internal static string KeyPath { get; set; } = @"Software\EyeCareReminder";
        private const string IntervalValueName = "IntervalMinutes";
        private const string AutoHideValueName = "AutoHide";
        private const string AutoHideSecondsValueName = "AutoHideSeconds";

        public static bool Exists()
        {
            using (var key = Registry.CurrentUser.OpenSubKey(KeyPath))
            {
                return key?.GetValue(IntervalValueName) != null;
            }
        }

        public static int LoadIntervalMinutes() =>
            LoadDword(IntervalValueName, MinIntervalMinutes, MaxIntervalMinutes, DefaultIntervalMinutes);

        public static void SaveIntervalMinutes(int minutes) => SaveDword(IntervalValueName, minutes);

        public static bool LoadAutoHide() => LoadDword(AutoHideValueName, 0, 1, DefaultAutoHide ? 1 : 0) == 1;

        public static int LoadAutoHideSeconds() =>
            LoadDword(AutoHideSecondsValueName, MinAutoHideSeconds, MaxAutoHideSeconds, DefaultAutoHideSeconds);

        public static void SaveAutoHide(bool enabled, int seconds)
        {
            SaveDword(AutoHideValueName, enabled ? 1 : 0);
            SaveDword(AutoHideSecondsValueName, seconds);
        }

        private static int LoadDword(string name, int min, int max, int defaultValue)
        {
            using (var key = Registry.CurrentUser.OpenSubKey(KeyPath))
            {
                if (key?.GetValue(name) is int value && value >= min && value <= max)
                {
                    return value;
                }
            }
            return defaultValue;
        }

        private static void SaveDword(string name, int value)
        {
            using (var key = Registry.CurrentUser.CreateSubKey(KeyPath))
            {
                key.SetValue(name, value, RegistryValueKind.DWord);
            }
        }
    }
}
