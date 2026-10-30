using System;
using System.Threading;
using System.Windows.Forms;

namespace EyeCareReminder
{
    internal static class Program
    {
        private const string MutexName = @"Local\EyeCareReminder";
        private const string ShowSettingsEventName = @"Local\EyeCareReminder.ShowSettings";

        /// <summary>Passed by the logon autostart entry: start silently in the tray.</summary>
        private const string AutostartArgument = "--autostart";

        [STAThread]
        private static void Main(string[] args)
        {
            using (var mutex = new Mutex(true, MutexName, out bool isFirstInstance))
            {
                if (!isFirstInstance)
                {
                    // Already running in the tray: ask that instance to open its settings.
                    try
                    {
                        using (var showSettings = EventWaitHandle.OpenExisting(ShowSettingsEventName))
                        {
                            showSettings.Set();
                        }
                    }
                    catch (WaitHandleCannotBeOpenedException)
                    {
                    }
                    return;
                }

                Application.EnableVisualStyles();
                Application.SetCompatibleTextRenderingDefault(false);

                using (var showSettings = new EventWaitHandle(false, EventResetMode.AutoReset, ShowSettingsEventName))
                {
                    // Started by the user (Start menu, installer): open the settings so the app is visible.
                    bool openSettings = Array.IndexOf(args, AutostartArgument) < 0;
                    Application.Run(new TrayApplicationContext(showSettings, openSettings));
                }
            }
        }
    }
}
