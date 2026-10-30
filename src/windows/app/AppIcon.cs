using System.Drawing;

namespace EyeCareReminder
{
    internal static class AppIcon
    {
        /// <summary>Loads the embedded application icon at the given size.</summary>
        public static Icon Load(Size size)
        {
            using (var stream = typeof(AppIcon).Assembly.GetManifestResourceStream("EyeCareReminder.ico"))
            {
                return new Icon(stream, size);
            }
        }
    }
}
