using Microsoft.Win32;

namespace EyeCareReminder
{
    /// <summary>Per-user settings stored in HKCU\Software\EyeCareReminder.</summary>
    internal static class Settings
    {
        public const int DefaultIntervalMinutes = 60;
        public const int MinIntervalMinutes = 1;
        public const int MaxIntervalMinutes = 24 * 60;

        private const string KeyPath = @"Software\EyeCareReminder";
        private const string IntervalValueName = "IntervalMinutes";

        public static bool Exists()
        {
            using (var key = Registry.CurrentUser.OpenSubKey(KeyPath))
            {
                return key?.GetValue(IntervalValueName) != null;
            }
        }

        public static int LoadIntervalMinutes()
        {
            using (var key = Registry.CurrentUser.OpenSubKey(KeyPath))
            {
                if (key?.GetValue(IntervalValueName) is int minutes
                    && minutes >= MinIntervalMinutes && minutes <= MaxIntervalMinutes)
                {
                    return minutes;
                }
            }
            return DefaultIntervalMinutes;
        }

        public static void SaveIntervalMinutes(int minutes)
        {
            using (var key = Registry.CurrentUser.CreateSubKey(KeyPath))
            {
                key.SetValue(IntervalValueName, minutes, RegistryValueKind.DWord);
            }
        }
    }
}
