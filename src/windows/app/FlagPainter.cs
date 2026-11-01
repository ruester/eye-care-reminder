using System;
using System.Drawing;
using System.Drawing.Drawing2D;

namespace EyeCareReminder
{
    /// <summary>Draws a <see cref="Flag"/> into a rectangle (with a thin gray outline).</summary>
    internal static class FlagPainter
    {
        private static readonly Color OutlineColor = Color.FromArgb(160, 160, 160);

        public static void Paint(Graphics g, Rectangle bounds, Flag flag)
        {
            var state = g.Save();
            try
            {
                g.SetClip(bounds);
                g.SmoothingMode = SmoothingMode.AntiAlias;
                g.PixelOffsetMode = PixelOffsetMode.Half;
                RectangleF r = bounds;
                switch (flag.Pattern)
                {
                    case FlagPattern.HorizontalStripes:
                        PaintStripes(g, r, flag, horizontal: true);
                        break;
                    case FlagPattern.VerticalStripes:
                        PaintStripes(g, r, flag, horizontal: false);
                        break;
                    case FlagPattern.NordicCross:
                        PaintNordicCross(g, r, flag);
                        break;
                    case FlagPattern.UnionJack:
                        PaintUnionJack(g, r, flag.Colors);
                        break;
                    case FlagPattern.Czechia:
                        PaintCzechia(g, r, flag.Colors);
                        break;
                }
                PaintEmblem(g, r, flag);
            }
            finally
            {
                g.Restore(state);
            }

            using (var pen = new Pen(OutlineColor))
            {
                g.DrawRectangle(pen, bounds.X, bounds.Y, bounds.Width - 1, bounds.Height - 1);
            }
        }

        private static void PaintStripes(Graphics g, RectangleF r, Flag flag, bool horizontal)
        {
            float[] edges = Edges(horizontal ? r.Top : r.Left, horizontal ? r.Height : r.Width, flag.Weights);
            for (int i = 0; i < flag.Colors.Length; i++)
            {
                using (var brush = new SolidBrush(flag.Colors[i]))
                {
                    var stripe = horizontal
                        ? RectangleF.FromLTRB(r.Left, edges[i], r.Right, edges[i + 1])
                        : RectangleF.FromLTRB(edges[i], r.Top, edges[i + 1], r.Bottom);
                    g.FillRectangle(brush, stripe);
                }
            }
        }

        private static void PaintNordicCross(Graphics g, RectangleF r, Flag flag)
        {
            float[] x = Edges(r.Left, r.Width, flag.Weights);
            float[] y = Edges(r.Top, r.Height, flag.CrossWeightsY);
            Fill(g, flag.Colors[0], r);
            // Outer cross: everything between the first and the last field.
            int last = x.Length - 2;
            FillCross(g, flag.Colors[1], r, x[1], x[last], y[1], y[last]);
            if (flag.Colors.Length > 2)
            {
                FillCross(g, flag.Colors[2], r, x[2], x[3], y[2], y[3]);
            }
        }

        private static void FillCross(Graphics g, Color color, RectangleF r, float left, float right, float top, float bottom)
        {
            Fill(g, color, RectangleF.FromLTRB(left, r.Top, right, r.Bottom));
            Fill(g, color, RectangleF.FromLTRB(r.Left, top, r.Right, bottom));
        }

        private static void PaintUnionJack(Graphics g, RectangleF r, Color[] colors)
        {
            Fill(g, colors[0], r);
            float unit = r.Height / 30f; // the real flag is 30 units high
            using (var white = new Pen(colors[1], 6 * unit))
            using (var red = new Pen(colors[2], 2 * unit))
            {
                g.DrawLine(white, r.Left, r.Top, r.Right, r.Bottom);
                g.DrawLine(white, r.Left, r.Bottom, r.Right, r.Top);
                g.DrawLine(red, r.Left, r.Top, r.Right, r.Bottom);
                g.DrawLine(red, r.Left, r.Bottom, r.Right, r.Top);
            }
            float cx = r.Left + r.Width / 2;
            float cy = r.Top + r.Height / 2;
            FillCross(g, colors[1], r, cx - 5 * unit, cx + 5 * unit, cy - 5 * unit, cy + 5 * unit);
            FillCross(g, colors[2], r, cx - 3 * unit, cx + 3 * unit, cy - 3 * unit, cy + 3 * unit);
        }

        private static void PaintCzechia(Graphics g, RectangleF r, Color[] colors)
        {
            float cy = r.Top + r.Height / 2;
            Fill(g, colors[0], RectangleF.FromLTRB(r.Left, r.Top, r.Right, cy));
            Fill(g, colors[1], RectangleF.FromLTRB(r.Left, cy, r.Right, r.Bottom));
            using (var blue = new SolidBrush(colors[2]))
            {
                g.FillPolygon(blue, new[]
                {
                    new PointF(r.Left, r.Top), new PointF(r.Left + r.Width / 2, cy), new PointF(r.Left, r.Bottom),
                });
            }
        }

        private static void PaintEmblem(Graphics g, RectangleF r, Flag flag)
        {
            switch (flag.Emblem)
            {
                case FlagEmblem.Portugal:
                {
                    float cx = r.Left + r.Width * 2 / 5;
                    float cy = r.Top + r.Height / 2;
                    float radius = r.Height * 0.3f;
                    Fill(g, Color.FromArgb(255, 255, 0), cx - radius, cy - radius, 2 * radius, 2 * radius, ellipse: true);
                    float w = radius * 1.1f;
                    float h = radius * 1.3f;
                    Fill(g, Color.FromArgb(255, 0, 0), cx - w / 2, cy - h / 2, w, h);
                    Fill(g, Color.White, cx - w / 4, cy - h / 4, w / 2, h / 2);
                    break;
                }
                case FlagEmblem.Croatia:
                {
                    // Checkerboard shield, 3 x 3 squares, starting with red.
                    float cell = r.Height * 0.55f / 3;
                    float left = r.Left + r.Width / 2 - 1.5f * cell;
                    float top = r.Top + r.Height / 2 - 1.5f * cell;
                    for (int row = 0; row < 3; row++)
                    {
                        for (int column = 0; column < 3; column++)
                        {
                            var color = (row + column) % 2 == 0 ? flag.Colors[0] : Color.White;
                            Fill(g, color, left + column * cell, top + row * cell, cell, cell);
                        }
                    }
                    break;
                }
            }
        }

        /// <summary>Positions of the borders between parts with the given relative sizes.</summary>
        private static float[] Edges(float start, float length, float[] weights)
        {
            float total = 0;
            foreach (float weight in weights)
            {
                total += weight;
            }
            var edges = new float[weights.Length + 1];
            edges[0] = start;
            for (int i = 0; i < weights.Length; i++)
            {
                edges[i + 1] = edges[i] + length * weights[i] / total;
            }
            return edges;
        }

        private static void Fill(Graphics g, Color color, RectangleF r) => Fill(g, color, r.X, r.Y, r.Width, r.Height);

        private static void Fill(Graphics g, Color color, float x, float y, float width, float height, bool ellipse = false)
        {
            using (var brush = new SolidBrush(color))
            {
                if (ellipse)
                {
                    g.FillEllipse(brush, x, y, width, height);
                }
                else
                {
                    g.FillRectangle(brush, x, y, width, height);
                }
            }
        }
    }
}
