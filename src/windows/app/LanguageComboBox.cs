using System.Drawing;
using System.Windows.Forms;

namespace EyeCareReminder
{
    /// <summary>Drop-down list of <see cref="Languages.All"/>, each with its flag and native name.</summary>
    internal sealed class LanguageComboBox : ComboBox
    {
        public LanguageComboBox()
        {
            DropDownStyle = ComboBoxStyle.DropDownList;
            DrawMode = DrawMode.OwnerDrawFixed;
            MaxDropDownItems = Languages.All.Count;
            foreach (var language in Languages.All)
            {
                Items.Add(language);
            }
            UpdateSize();
        }

        public Language SelectedLanguage
        {
            get => SelectedItem as Language ?? Languages.English;
            set => SelectedItem = value;
        }

        protected override void OnFontChanged(System.EventArgs e)
        {
            base.OnFontChanged(e);
            UpdateSize();
        }

        private void UpdateSize()
        {
            ItemHeight = Font.Height + 4;
            int widest = 0;
            foreach (var language in Languages.All)
            {
                widest = System.Math.Max(widest, TextRenderer.MeasureText(language.NativeName, Font).Width);
            }
            Width = FlagSize.Width + 12 + widest + SystemInformation.VerticalScrollBarWidth + 8;
        }

        /// <summary>3:2 flags fitting into an item.</summary>
        private Size FlagSize
        {
            get
            {
                int height = System.Math.Max(8, Font.Height - 2);
                return new Size(height * 3 / 2, height);
            }
        }

        protected override void OnDrawItem(DrawItemEventArgs e)
        {
            e.DrawBackground();
            if (e.Index >= 0 && Items[e.Index] is Language language)
            {
                var flag = FlagSize;
                var flagBounds = new Rectangle(
                    e.Bounds.Left + 4, e.Bounds.Top + (e.Bounds.Height - flag.Height) / 2, flag.Width, flag.Height);
                FlagPainter.Paint(e.Graphics, flagBounds, language.Flag);

                var textBounds = Rectangle.FromLTRB(flagBounds.Right + 8, e.Bounds.Top, e.Bounds.Right, e.Bounds.Bottom);
                TextRenderer.DrawText(e.Graphics, language.NativeName, e.Font, textBounds, e.ForeColor,
                    TextFormatFlags.Left | TextFormatFlags.VerticalCenter | TextFormatFlags.NoPrefix);
            }
            e.DrawFocusRectangle();
        }
    }
}
