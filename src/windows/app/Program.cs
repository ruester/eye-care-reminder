using System;
using System.Threading;
using System.Windows.Forms;

namespace EyeCareReminder
{
    internal static class Program
    {
        private const string MutexName = @"Local\EyeCareReminder";
        private const string ShowSettingsEventName = @"Local\EyeCareReminder.ShowSettings";

        [STAThread]
        private static void Main()
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
                    Application.Run(new TrayApplicationContext(showSettings));
                }
            }
        }
    }
}
