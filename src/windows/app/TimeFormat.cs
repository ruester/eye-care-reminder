using System;

namespace EyeCareReminder
{
    /// <summary>User-facing texts that contain times.</summary>
    internal static class TimeFormat
    {
        public const string AppName = "Eye Care Reminder";

        /// <summary>NotifyIcon.Text throws on .NET Framework if longer than this.</summary>
        public const int MaxTrayTextLength = 63;

        /// <summary>Tray icon tooltip with the time of the next break.</summary>
        public static string TrayText(DateTime nextBreak, Texts texts)
        {
            string text = AppName + "\n" + string.Format(texts.NextBreakAt, Time(nextBreak));
            return text.Length <= MaxTrayTextLength ? text : text.Substring(0, MaxTrayTextLength);
        }

        /// <summary>Time of day in the user's regional format, e.g. "14:05" or "2:05 PM".</summary>
        public static string Time(DateTime time) => time.ToString("t");
    }
}
