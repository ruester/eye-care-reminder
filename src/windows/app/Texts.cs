namespace EyeCareReminder
{
    /// <summary>
    /// All user-facing texts of the app in one language (see <see cref="Translations"/>).
    /// Placeholders: {0} in <see cref="NextBreakAt"/> and <see cref="RunningMessage"/> is a
    /// time of day; {0}/{1} in the default hints are counts formatted with
    /// <see cref="FormatMinutes"/> / <see cref="FormatSeconds"/>. A leading "&amp;" marks the
    /// keyboard accelerator of menu items.
    /// </summary>
    internal sealed class Texts
    {
        public PluralRule PluralRule { get; set; }

        /// <summary>Counted forms "{0} minute(s)": [one, other] or [one, few, many] (see <see cref="Plural"/>).</summary>
        public string[] Minutes { get; set; }

        public string[] Seconds { get; set; }

        // Tray icon
        public string MenuSettings { get; set; }
        public string MenuBreakNow { get; set; }
        public string MenuExit { get; set; }
        public string NextBreakAt { get; set; }

        // Settings dialog
        public string SettingsTitle { get; set; }
        public string IntervalLabel { get; set; }
        public string MinutesUnit { get; set; }
        public string IntervalDefault { get; set; }
        public string AutoHideLabel { get; set; }
        public string SecondsUnit { get; set; }
        public string AutoHideDefault { get; set; }
        public string LanguageLabel { get; set; }
        public string TestNotification { get; set; }
        public string Save { get; set; }
        public string Cancel { get; set; }

        // Notifications
        public string BreakTitle { get; set; }
        public string BreakMessage { get; set; }
        public string RunningTitle { get; set; }
        public string RunningMessage { get; set; }

        public string FormatMinutes(int count) => Plural.Format(count, PluralRule, Minutes);

        public string FormatSeconds(int count) => Plural.Format(count, PluralRule, Seconds);
    }
}
