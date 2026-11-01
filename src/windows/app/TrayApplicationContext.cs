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
        private readonly NotifyIcon trayIcon;
        private readonly System.Windows.Forms.Timer reminderTimer;
        private readonly RegisteredWaitHandle showSettingsRegistration;
        private int intervalMinutes;
        private bool autoHide;
        private int autoHideSeconds;
        private Language language;
        private readonly ToolStripMenuItem settingsItem;
        private readonly ToolStripMenuItem breakNowItem;
        private readonly ToolStripMenuItem exitItem;
        private SettingsForm settingsForm;
        private NotificationPopup popup;

        public TrayApplicationContext(WaitHandle showSettingsSignal, bool openSettings)
        {
            bool isFirstRun = !Settings.Exists();
            intervalMinutes = Settings.LoadIntervalMinutes();
            autoHide = Settings.LoadAutoHide();
            autoHideSeconds = Settings.LoadAutoHideSeconds();
            language = Languages.FromSetting(Settings.LoadLanguage());
            if (isFirstRun)
            {
                Settings.SaveIntervalMinutes(intervalMinutes);
                Settings.SaveAutoHide(autoHide, autoHideSeconds);
            }

            var menu = new ContextMenuStrip();
            settingsItem = new ToolStripMenuItem(null, null, (s, e) => ShowSettings());
            settingsItem.Font = new System.Drawing.Font(settingsItem.Font, System.Drawing.FontStyle.Bold);
            breakNowItem = new ToolStripMenuItem(null, null, (s, e) => ShowReminder());
            exitItem = new ToolStripMenuItem(null, null, (s, e) => ExitThread());
            menu.Items.Add(settingsItem);
            menu.Items.Add(breakNowItem);
            menu.Items.Add(new ToolStripSeparator());
            menu.Items.Add(exitItem);
            ApplyMenuTexts();

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
                var texts = language.Texts;
                ShowPopup(texts.RunningTitle,
                    string.Format(texts.RunningMessage, TimeFormat.Time(DateTime.Now.AddMinutes(intervalMinutes))),
                    autoHide ? autoHideSeconds : 0);
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

        private void ShowBreakNotification() => ShowBreakNotification(autoHide ? autoHideSeconds : 0, language.Texts);

        private void ShowBreakNotification(int hideAfterSeconds, Texts texts)
        {
            ShowPopup(texts.BreakTitle, texts.BreakMessage, hideAfterSeconds);
        }

        /// <param name="hideAfterSeconds">0 keeps the popup open until it is clicked.</param>
        private void ShowPopup(string title, string message, int hideAfterSeconds)
        {
            popup?.Close();
            popup = new NotificationPopup(title, message, hideAfterSeconds * 1000);
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

            using (settingsForm = new SettingsForm(intervalMinutes, autoHide, autoHideSeconds, language, ShowBreakNotification))
            {
                if (settingsForm.ShowDialog() == DialogResult.OK)
                {
                    intervalMinutes = settingsForm.IntervalMinutes;
                    autoHide = settingsForm.AutoHide;
                    autoHideSeconds = settingsForm.AutoHideSeconds;
                    language = settingsForm.SelectedLanguage;
                    Settings.SaveIntervalMinutes(intervalMinutes);
                    Settings.SaveAutoHide(autoHide, autoHideSeconds);
                    Settings.SaveLanguage(language.Code);
                    ApplyMenuTexts();
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

            trayIcon.Text = TimeFormat.TrayText(DateTime.Now.AddMinutes(intervalMinutes), language.Texts);
        }

        private void ApplyMenuTexts()
        {
            var texts = language.Texts;
            settingsItem.Text = texts.MenuSettings;
            breakNowItem.Text = texts.MenuBreakNow;
            exitItem.Text = texts.MenuExit;
        }

        private void OnSessionSwitch(object sender, SessionSwitchEventArgs e)
        {
            if (e.Reason == SessionSwitchReason.SessionUnlock)
            {
                RestartTimer();
            }
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
