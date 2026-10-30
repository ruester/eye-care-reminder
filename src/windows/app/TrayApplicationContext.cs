using System;
using System.Threading;
using System.Windows.Forms;
using Microsoft.Win32;

namespace EyeCareReminder
{
    /// <summary>
    /// Runs the application from the notification area (system tray) and shows
    /// an eye break notification every configured interval.
    /// </summary>
    internal sealed class TrayApplicationContext : ApplicationContext
    {
        private const int NotificationTimeoutMs = 60000;

        private readonly NotifyIcon trayIcon;
        private readonly System.Windows.Forms.Timer reminderTimer;
        private readonly RegisteredWaitHandle showSettingsRegistration;
        private int intervalMinutes;
        private SettingsForm settingsForm;
        private NotificationPopup popup;

        public TrayApplicationContext(WaitHandle showSettingsSignal, bool openSettings)
        {
            bool isFirstRun = !Settings.Exists();
            intervalMinutes = Settings.LoadIntervalMinutes();
            if (isFirstRun)
            {
                Settings.SaveIntervalMinutes(intervalMinutes);
            }

            var menu = new ContextMenuStrip();
            var settingsItem = new ToolStripMenuItem("&Settings...", null, (s, e) => ShowSettings());
            settingsItem.Font = new System.Drawing.Font(settingsItem.Font, System.Drawing.FontStyle.Bold);
            menu.Items.Add(settingsItem);
            menu.Items.Add("&Take a break now", null, (s, e) => ShowReminder());
            menu.Items.Add(new ToolStripSeparator());
            menu.Items.Add("E&xit", null, (s, e) => ExitThread());

            trayIcon = new NotifyIcon
            {
                Icon = AppIcon.Load(SystemInformation.SmallIconSize),
                ContextMenuStrip = menu,
                Visible = true,
            };
            trayIcon.MouseClick += (s, e) =>
            {
                if (e.Button == MouseButtons.Left)
                {
                    ShowSettings();
                }
            };

            reminderTimer = new System.Windows.Forms.Timer();
            reminderTimer.Tick += (s, e) => ShowReminder();
            RestartTimer();

            // A second instance (e.g. started from the Start menu) asks us to open the settings.
            var uiContext = new WindowsFormsSynchronizationContext();
            showSettingsRegistration = ThreadPool.RegisterWaitForSingleObject(
                showSettingsSignal, (state, timedOut) => uiContext.Post(_ => ShowSettings(), null),
                null, Timeout.Infinite, false);

            // Locking the screen counts as a break: restart the interval on unlock.
            SystemEvents.SessionSwitch += OnSessionSwitch;

            if (isFirstRun)
            {
                ShowPopup("Eye Care Reminder is running",
                    $"You will be reminded to rest your eyes every {FormatInterval(intervalMinutes)}. "
                    + "Click the eye icon in the notification area to change the interval.");
            }

            if (openSettings)
            {
                uiContext.Post(_ => ShowSettings(), null);
            }
        }

        private void ShowReminder()
        {
            ShowBreakNotification();
            RestartTimer();
        }

        private void ShowBreakNotification()
        {
            ShowPopup("Time for an eye break",
                "Look at something at least 6 metres (20 feet) away for 20 seconds and blink a few times.");
        }

        private void ShowPopup(string title, string message)
        {
            popup?.Close();
            popup = new NotificationPopup(title, message, NotificationTimeoutMs);
            popup.FormClosed += (s, e) =>
            {
                if (s == popup)
                {
                    popup = null;
                }
                ((Form)s).Dispose();
            };
            popup.Show();
        }

        private void ShowSettings()
        {
            if (settingsForm != null)
            {
                settingsForm.Activate();
                return;
            }

            using (settingsForm = new SettingsForm(intervalMinutes, ShowBreakNotification))
            {
                if (settingsForm.ShowDialog() == DialogResult.OK)
                {
                    intervalMinutes = settingsForm.IntervalMinutes;
                    Settings.SaveIntervalMinutes(intervalMinutes);
                    RestartTimer();
                }
            }
            settingsForm = null;
        }

        private void RestartTimer()
        {
            reminderTimer.Stop();
            reminderTimer.Interval = intervalMinutes * 60 * 1000;
            reminderTimer.Start();

            // NotifyIcon.Text is limited to 63 characters.
            trayIcon.Text = $"Eye Care Reminder\nNext break at {DateTime.Now.AddMinutes(intervalMinutes):t}";
        }

        private void OnSessionSwitch(object sender, SessionSwitchEventArgs e)
        {
            if (e.Reason == SessionSwitchReason.SessionUnlock)
            {
                RestartTimer();
            }
        }

        private static string FormatInterval(int minutes)
        {
            if (minutes % 60 == 0)
            {
                int hours = minutes / 60;
                return hours == 1 ? "hour" : $"{hours} hours";
            }
            return minutes == 1 ? "minute" : $"{minutes} minutes";
        }

        protected override void ExitThreadCore()
        {
            settingsForm?.Close();
            popup?.Close();
            SystemEvents.SessionSwitch -= OnSessionSwitch;
            showSettingsRegistration.Unregister(null);
            reminderTimer.Dispose();
            trayIcon.Visible = false;
            trayIcon.Dispose();
            base.ExitThreadCore();
        }
    }
}
