using System;

namespace EyeCareReminder
{
    /// <summary>The installed version, shown small in the settings dialog ("v1.3.3").</summary>
    internal static class AppVersion
    {
        /// <summary>The app's version (set by the build: -p:Version=X.Y.Z).</summary>
        public static Version Current => typeof(AppVersion).Assembly.GetName().Version;

        /// <summary>"v1.3.3" (major.minor.patch; the fourth part is always 0).</summary>
        public static string Display(Version version) =>
            string.Format("v{0}.{1}.{2}", version.Major, version.Minor, Math.Max(0, version.Build));
    }
}
