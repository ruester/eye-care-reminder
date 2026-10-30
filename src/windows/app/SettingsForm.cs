using System.Drawing;
using System.Windows.Forms;

namespace EyeCareReminder
{
    /// <summary>Simple dialog to configure the reminder interval.</summary>
    internal sealed class SettingsForm : Form
    {
        private readonly NumericUpDown intervalInput;

        public SettingsForm(int intervalMinutes)
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

            var saveButton = new Button { Text = "Save", DialogResult = DialogResult.OK, AutoSize = true };
            var cancelButton = new Button { Text = "Cancel", DialogResult = DialogResult.Cancel, AutoSize = true };
            var buttons = new FlowLayoutPanel
            {
                AutoSize = true,
                WrapContents = false,
                Anchor = AnchorStyles.Right,
                Margin = new Padding(0, 12, 0, 0),
            };
            buttons.Controls.Add(saveButton);
            buttons.Controls.Add(cancelButton);
            layout.Controls.Add(buttons);

            Controls.Add(layout);
            AcceptButton = saveButton;
            CancelButton = cancelButton;
        }

        public int IntervalMinutes => (int)intervalInput.Value;
    }
}
