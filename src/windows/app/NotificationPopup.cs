using System;
using System.Drawing;
using System.Windows.Forms;

namespace EyeCareReminder
{
    /// <summary>
    /// Small notification window in the bottom-right corner of the primary screen.
    /// Drawn by the app itself, so it shows regardless of the Windows notification
    /// settings (Do Not Disturb / Focus Assist suppress tray balloon notifications).
    /// Closes on click or after a timeout and never takes the keyboard focus.
    /// </summary>
    internal sealed class NotificationPopup : Form
    {
        private const int ScreenMargin = 12;
        private const int WS_EX_TOOLWINDOW = 0x00000080;
        private const int WS_EX_TOPMOST = 0x00000008;
        private const int WS_EX_NOACTIVATE = 0x08000000;

        private static readonly Color AccentColor = Color.FromArgb(0, 137, 123);

        private readonly Timer closeTimer;

        public NotificationPopup(string title, string message, int timeoutMs)
        {
            FormBorderStyle = FormBorderStyle.None;
            ShowInTaskbar = false;
            TopMost = true;
            StartPosition = FormStartPosition.Manual;
            AutoScaleMode = AutoScaleMode.Font;
            Font = SystemFonts.MessageBoxFont;
            BackColor = SystemColors.Window;
            ForeColor = SystemColors.WindowText;
            AutoSize = true;
            AutoSizeMode = AutoSizeMode.GrowAndShrink;
            // 1px border on every side: content starts at (1, 1), plus right/bottom padding.
            Padding = new Padding(0, 0, 1, 1);
            Cursor = Cursors.Hand;

            var layout = new TableLayoutPanel
            {
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
                ColumnCount = 3,
                RowCount = 1,
                Location = new Point(1, 1),
                Padding = new Padding(12),
            };

            var icon = new PictureBox
            {
                Image = AppIcon.Load(new Size(48, 48)).ToBitmap(),
                SizeMode = PictureBoxSizeMode.Zoom,
                Size = new Size(48, 48),
                Margin = new Padding(0, 0, 12, 0),
            };
            layout.Controls.Add(icon, 0, 0);

            var text = new FlowLayoutPanel
            {
                FlowDirection = FlowDirection.TopDown,
                WrapContents = false,
                AutoSize = true,
                Margin = Padding.Empty,
            };
            text.Controls.Add(new Label
            {
                Text = title,
                AutoSize = true,
                Font = new Font(Font.FontFamily, Font.Size * 1.15f, FontStyle.Bold),
                Margin = new Padding(0, 0, 0, 4),
            });
            text.Controls.Add(new Label
            {
                Text = message,
                AutoSize = true,
                MaximumSize = new Size(280, 0),
                Margin = Padding.Empty,
            });
            layout.Controls.Add(text, 1, 0);

            var close = new Label
            {
                Text = "✕",
                AutoSize = true,
                ForeColor = SystemColors.GrayText,
                Margin = new Padding(12, 0, 0, 0),
            };
            layout.Controls.Add(close, 2, 0);

            Controls.Add(layout);
            CloseOnClick(this);

            closeTimer = new Timer { Interval = timeoutMs };
            closeTimer.Tick += (s, e) => Close();
        }

        // Show on top without stealing the focus from the window the user is working in.
        protected override bool ShowWithoutActivation => true;

        protected override CreateParams CreateParams
        {
            get
            {
                var cp = base.CreateParams;
                cp.ExStyle |= WS_EX_TOOLWINDOW | WS_EX_TOPMOST | WS_EX_NOACTIVATE;
                return cp;
            }
        }

        protected override void OnShown(EventArgs e)
        {
            base.OnShown(e);
            var area = Screen.PrimaryScreen.WorkingArea;
            Location = new Point(area.Right - Width - ScreenMargin, area.Bottom - Height - ScreenMargin);
            closeTimer.Start();
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            using (var pen = new Pen(AccentColor))
            {
                e.Graphics.DrawRectangle(pen, 0, 0, Width - 1, Height - 1);
            }
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                closeTimer.Dispose();
            }
            base.Dispose(disposing);
        }

        private void CloseOnClick(Control control)
        {
            control.Click += (s, e) => Close();
            foreach (Control child in control.Controls)
            {
                CloseOnClick(child);
            }
        }
    }
}
