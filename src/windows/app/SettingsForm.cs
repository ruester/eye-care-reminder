using System;
using System.Drawing;
using System.Windows.Forms;

namespace EyeCareReminder
{
    /// <summary>
    /// Dialog to configure the reminder interval, how long notifications stay and the
    /// language. Choosing a language translates the dialog right away.
    /// </summary>
    internal sealed class SettingsForm : Form
    {
        private readonly Label intervalLabel;
        private readonly NumericUpDown intervalInput;
        private readonly Label minutesLabel;
        private readonly Label intervalDefaultLabel;
        private readonly CheckBox autoHideCheckBox;
        private readonly NumericUpDown autoHideInput;
        private readonly Label secondsLabel;
        private readonly Label autoHideDefaultLabel;
        private readonly Label languageLabel;
        private readonly LanguageComboBox languageInput;
        private readonly Button testButton;
        private readonly Button saveButton;
        private readonly Button cancelButton;

        /// <param name="showTestNotification">Shows a sample notification; receives the
        /// auto-hide time currently entered in the dialog in seconds (0 = never hide)
        /// and the texts of the selected language.</param>
        public SettingsForm(int intervalMinutes, bool autoHide, int autoHideSeconds, Language language,
            Action<int, Texts> showTestNotification)
        {
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

            intervalLabel = new Label { AutoSize = true, Margin = new Padding(3, 3, 3, 9) };
            layout.Controls.Add(intervalLabel);

            intervalInput = new NumericUpDown
            {
                Minimum = Settings.MinIntervalMinutes,
                Maximum = Settings.MaxIntervalMinutes,
                Value = intervalMinutes,
                Width = 80,
            };
            minutesLabel = new Label { AutoSize = true, Anchor = AnchorStyles.Left };
            layout.Controls.Add(Row(intervalInput, minutesLabel));

            intervalDefaultLabel = HintLabel();
            layout.Controls.Add(intervalDefaultLabel);

            autoHideCheckBox = new CheckBox
            {
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
            secondsLabel = new Label { AutoSize = true, Anchor = AnchorStyles.Left };
            layout.Controls.Add(Row(autoHideInput, secondsLabel));

            autoHideDefaultLabel = HintLabel();
            layout.Controls.Add(autoHideDefaultLabel);

            languageLabel = new Label { AutoSize = true, Margin = new Padding(3, 15, 3, 9) };
            layout.Controls.Add(languageLabel);
            languageInput = new LanguageComboBox { SelectedLanguage = language };
            languageInput.SelectedIndexChanged += (s, e) => ApplyTexts(SelectedLanguage.Texts);
            layout.Controls.Add(languageInput);

            // Shows a sample reminder with the entered values without affecting the timer.
            testButton = new Button { AutoSize = true };
            testButton.Click += (s, e) => showTestNotification(AutoHide ? AutoHideSeconds : 0, SelectedLanguage.Texts);
            saveButton = new Button { DialogResult = DialogResult.OK, AutoSize = true };
            cancelButton = new Button { DialogResult = DialogResult.Cancel, AutoSize = true };
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

            ApplyTexts(language.Texts);
        }

        public int IntervalMinutes => (int)intervalInput.Value;

        public bool AutoHide => autoHideCheckBox.Checked;

        public int AutoHideSeconds => (int)autoHideInput.Value;

        public Language SelectedLanguage => languageInput.SelectedLanguage;

        private void ApplyTexts(Texts texts)
        {
            Text = texts.SettingsTitle;
            intervalLabel.Text = texts.IntervalLabel;
            minutesLabel.Text = texts.MinutesUnit;
            intervalDefaultLabel.Text = string.Format(texts.IntervalDefault, texts.FormatMinutes(Settings.DefaultIntervalMinutes));
            autoHideCheckBox.Text = texts.AutoHideLabel;
            secondsLabel.Text = texts.SecondsUnit;
            autoHideDefaultLabel.Text = string.Format(texts.AutoHideDefault,
                texts.FormatSeconds(Settings.DefaultAutoHideSeconds), texts.FormatMinutes(Settings.MaxAutoHideSeconds / 60));
            languageLabel.Text = texts.LanguageLabel;
            testButton.Text = texts.TestNotification;
            saveButton.Text = texts.Save;
            cancelButton.Text = texts.Cancel;
        }

        private static FlowLayoutPanel Row(Control input, Label unit)
        {
            var row = new FlowLayoutPanel { AutoSize = true, WrapContents = false, Margin = Padding.Empty };
            row.Controls.Add(input);
            row.Controls.Add(unit);
            return row;
        }

        private static Label HintLabel() => new Label
        {
            AutoSize = true,
            ForeColor = SystemColors.GrayText,
            Margin = new Padding(3, 6, 3, 3),
        };
    }
}
