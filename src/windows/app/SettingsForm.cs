using System;
using System.Drawing;
using System.Windows.Forms;

namespace EyeCareReminder
{
    /// <summary>Simple dialog to configure the reminder interval and how long notifications stay.</summary>
    internal sealed class SettingsForm : Form
    {
        private readonly NumericUpDown intervalInput;
        private readonly CheckBox autoHideCheckBox;
        private readonly NumericUpDown autoHideInput;

        /// <param name="showTestNotification">Shows a sample notification; receives the
        /// auto-hide time currently entered in the dialog in seconds (0 = never hide).</param>
        public SettingsForm(int intervalMinutes, bool autoHide, int autoHideSeconds, Action<int> showTestNotification)
        {
            Text = "Eye Care Reminder - Settings";
            Icon = AppIcon.Load(SystemInformation.IconSize);
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            MinimizeBox = false;
            StartPosition = FormStartPosition.CenterScreen;
            AutoScaleMode = AutoScaleMode.Font;
            Font = SystemFonts.MessageBoxFont;
            AutoSize = true;
            AutoSizeMode = AutoSizeMode.GrowAndShrink;

            var layout = new FlowLayoutPanel
            {
                FlowDirection = FlowDirection.TopDown,
                WrapContents = false,
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
                Padding = new Padding(12),
            };

            layout.Controls.Add(new Label
            {
                Text = "Remind me to take an eye break every:",
                AutoSize = true,
                Margin = new Padding(3, 3, 3, 9),
            });

            intervalInput = new NumericUpDown
            {
                Minimum = Settings.MinIntervalMinutes,
                Maximum = Settings.MaxIntervalMinutes,
                Value = intervalMinutes,
                Width = 80,
            };
            var intervalRow = new FlowLayoutPanel { AutoSize = true, WrapContents = false, Margin = Padding.Empty };
            intervalRow.Controls.Add(intervalInput);
            intervalRow.Controls.Add(new Label
            {
                Text = "minutes",
                AutoSize = true,
                Anchor = AnchorStyles.Left,
            });
            layout.Controls.Add(intervalRow);

            layout.Controls.Add(new Label
            {
                Text = $"Default: {Settings.DefaultIntervalMinutes} minutes",
                AutoSize = true,
                ForeColor = SystemColors.GrayText,
                Margin = new Padding(3, 6, 3, 3),
            });

            autoHideCheckBox = new CheckBox
            {
                Text = "Hide notifications automatically after:",
                Checked = autoHide,
                AutoSize = true,
                Margin = new Padding(3, 15, 3, 9),
            };
            layout.Controls.Add(autoHideCheckBox);

            autoHideInput = new NumericUpDown
            {
                Minimum = Settings.MinAutoHideSeconds,
                Maximum = Settings.MaxAutoHideSeconds,
                Value = autoHideSeconds,
                Width = 80,
                Enabled = autoHide,
            };
            autoHideCheckBox.CheckedChanged += (s, e) => autoHideInput.Enabled = autoHideCheckBox.Checked;
            var autoHideRow = new FlowLayoutPanel { AutoSize = true, WrapContents = false, Margin = Padding.Empty };
            autoHideRow.Controls.Add(autoHideInput);
            autoHideRow.Controls.Add(new Label
            {
                Text = "seconds",
                AutoSize = true,
                Anchor = AnchorStyles.Left,
            });
            layout.Controls.Add(autoHideRow);

            layout.Controls.Add(new Label
            {
                Text = $"Default: {Settings.DefaultAutoHideSeconds} seconds (max. {Settings.MaxAutoHideSeconds / 60} minutes)",
                AutoSize = true,
                ForeColor = SystemColors.GrayText,
                Margin = new Padding(3, 6, 3, 3),
            });

            // Shows a sample reminder with the entered auto-hide time without affecting the timer.
            var testButton = new Button { Text = "Test notification", AutoSize = true };
            testButton.Click += (s, e) => showTestNotification(AutoHide ? AutoHideSeconds : 0);
            var saveButton = new Button { Text = "Save", DialogResult = DialogResult.OK, AutoSize = true };
            var cancelButton = new Button { Text = "Cancel", DialogResult = DialogResult.Cancel, AutoSize = true };
            var buttons = new FlowLayoutPanel
            {
                AutoSize = true,
                WrapContents = false,
                Anchor = AnchorStyles.Right,
                Margin = new Padding(0, 12, 0, 0),
            };
            buttons.Controls.Add(testButton);
            buttons.Controls.Add(saveButton);
            buttons.Controls.Add(cancelButton);
            layout.Controls.Add(buttons);

            Controls.Add(layout);
            AcceptButton = saveButton;
            CancelButton = cancelButton;
        }

        public int IntervalMinutes => (int)intervalInput.Value;

        public bool AutoHide => autoHideCheckBox.Checked;

        public int AutoHideSeconds => (int)autoHideInput.Value;
    }
}
