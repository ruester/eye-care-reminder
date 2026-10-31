using System;

namespace EyeCareReminder
{
    /// <summary>User-facing texts that contain times and intervals.</summary>
    internal static class TimeFormat
    {
        /// <summary>NotifyIcon.Text throws on .NET Framework if longer than this.</summary>
        public const int MaxTrayTextLength = 63;

        /// <summary>"hour", "2 hours", "minute", "90 minutes" (as in "every ...").</summary>
        public static string Interval(int minutes)
        {
            if (minutes % 60 == 0)
            {
                int hours = minutes / 60;
                return hours == 1 ? "hour" : $"{hours} hours";
            }
            return minutes == 1 ? "minute" : $"{minutes} minutes";
        }

        /// <summary>Tray icon tooltip with the time of the next break.</summary>
        public static string TrayText(DateTime nextBreak)
        {
            string text = $"Eye Care Reminder\nNext break at {nextBreak:t}";
            return text.Length <= MaxTrayTextLength ? text : text.Substring(0, MaxTrayTextLength);
        }
    }
}
