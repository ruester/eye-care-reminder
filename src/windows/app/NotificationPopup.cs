using System;
using System.Diagnostics;
using System.Drawing;
using System.Windows.Forms;

namespace EyeCareReminder
{
    /// <summary>
    /// Small notification window in the bottom-right corner of the primary screen.
    /// Drawn by the app itself, so it shows regardless of the Windows notification
    /// settings (Do Not Disturb / Focus Assist suppress tray balloon notifications).
    /// A bar at the bottom counts down the remaining time (full at first, shrinking
    /// from right to left); the popup closes when it is empty or when clicked.
    /// Never takes the keyboard focus.
    /// </summary>
    internal sealed class NotificationPopup : Form
    {
        private const int ScreenMargin = 12;
        private const int WS_EX_TOOLWINDOW = 0x00000080;
        private const int WS_EX_TOPMOST = 0x00000008;
        private const int WS_EX_NOACTIVATE = 0x08000000;

        private const int CountdownTickMs = 30;

        private static readonly Color AccentColor = Color.FromArgb(0, 137, 123);
        private static readonly Color CountdownTrackColor = Color.FromArgb(214, 236, 233);

        private readonly int timeoutMs;
        private readonly int countdownHeight;
        private readonly Stopwatch elapsed = new Stopwatch();
        private readonly Timer countdownTimer;

        /// <param name="timeoutMs">Closes the popup after this time and shows a countdown bar;
        /// 0 keeps it open until it is clicked.</param>
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
            DoubleBuffered = true;
            this.timeoutMs = timeoutMs;
            countdownHeight = timeoutMs > 0 ? Math.Max(3, Font.Height / 4) : 0;
            // 1px border on every side: content starts at (1, 1), plus right/bottom padding;
            // the countdown bar sits in the extra bottom padding.
            Padding = new Padding(0, 0, 1, 1 + countdownHeight);
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

            countdownTimer = new Timer { Interval = CountdownTickMs };
            countdownTimer.Tick += OnCountdownTick;
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
            if (timeoutMs > 0)
            {
                elapsed.Start();
                countdownTimer.Start();
            }
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            using (var pen = new Pen(AccentColor))
            {
                e.Graphics.DrawRectangle(pen, 0, 0, Width - 1, Height - 1);
            }

            if (timeoutMs <= 0)
            {
                return;
            }

            var track = CountdownBounds;
            int filledWidth = Countdown.BarWidth(track.Width, elapsed.ElapsedMilliseconds, timeoutMs);
            using (var trackBrush = new SolidBrush(CountdownTrackColor))
            using (var barBrush = new SolidBrush(AccentColor))
            {
                e.Graphics.FillRectangle(trackBrush, track);
                e.Graphics.FillRectangle(barBrush, track.X, track.Y, filledWidth, track.Height);
            }
        }

        private Rectangle CountdownBounds => new Rectangle(1, Height - 1 - countdownHeight, Width - 2, countdownHeight);

        private void OnCountdownTick(object sender, EventArgs e)
        {
            if (elapsed.ElapsedMilliseconds >= timeoutMs)
            {
                countdownTimer.Stop();
                Close();
                return;
            }
            Invalidate(CountdownBounds);
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                countdownTimer.Dispose();
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
