using System;

namespace EyeCareReminder
{
    /// <summary>Progress of the notification popup's auto-hide countdown.</summary>
    internal static class Countdown
    {
        /// <summary>Remaining share of the countdown, from 1 (just shown) down to 0 (time is up).</summary>
        public static double RemainingFraction(long elapsedMs, int timeoutMs)
        {
            if (timeoutMs <= 0)
            {
                return 0.0;
            }
            return Math.Min(1.0, Math.Max(0.0, 1.0 - (double)elapsedMs / timeoutMs));
        }

        /// <summary>Width of the countdown bar for a track of <paramref name="trackWidth"/> pixels.</summary>
        public static int BarWidth(int trackWidth, long elapsedMs, int timeoutMs) =>
            (int)Math.Round(trackWidth * RemainingFraction(elapsedMs, timeoutMs));
    }
}
