using System.Drawing;

namespace EyeCareReminder
{
    internal enum FlagPattern
    {
        /// <summary>Stripes from top to bottom (<see cref="Flag.Weights"/> = relative heights).</summary>
        HorizontalStripes,

        /// <summary>Stripes from left to right (<see cref="Flag.Weights"/> = relative widths).</summary>
        VerticalStripes,

        /// <summary>
        /// Colors[0] background with a cross. <see cref="Flag.Weights"/> / <see cref="Flag.CrossWeightsY"/>
        /// split the width / height: [field, cross, field] or [field, border, cross, border, field];
        /// Colors[1] is the cross (or its border), Colors[2] the inner cross.
        /// </summary>
        NordicCross,

        /// <summary>Colors: [blue field, white, red].</summary>
        UnionJack,

        /// <summary>Colors: [white, red, blue triangle at the hoist].</summary>
        Czechia,
    }

    internal enum FlagEmblem
    {
        None,

        /// <summary>Simplified armillary sphere and shield on the green/red border.</summary>
        Portugal,

        /// <summary>Red and white checkerboard shield in the centre.</summary>
        Croatia,
    }

    /// <summary>Simplified national flag, drawn by <see cref="FlagPainter"/> (Windows has no flag emoji).</summary>
    internal sealed class Flag
    {
        public Flag(FlagPattern pattern, Color[] colors, float[] weights = null, float[] crossWeightsY = null,
            FlagEmblem emblem = FlagEmblem.None)
        {
            Pattern = pattern;
            Colors = colors;
            Weights = weights ?? Equal(colors.Length);
            CrossWeightsY = crossWeightsY;
            Emblem = emblem;
        }

        public FlagPattern Pattern { get; }
        public Color[] Colors { get; }
        public float[] Weights { get; }
        public float[] CrossWeightsY { get; }
        public FlagEmblem Emblem { get; }

        private static float[] Equal(int count)
        {
            var weights = new float[count];
            for (int i = 0; i < count; i++)
            {
                weights[i] = 1;
            }
            return weights;
        }
    }

    internal static class Flags
    {
        private static Color Rgb(int rgb) => Color.FromArgb((rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF);

        public static readonly Flag Belgium = new Flag(FlagPattern.VerticalStripes,
            new[] { Rgb(0x000000), Rgb(0xFDDA24), Rgb(0xEF3340) });

        public static readonly Flag Croatia = new Flag(FlagPattern.HorizontalStripes,
            new[] { Rgb(0xFF0000), Rgb(0xFFFFFF), Rgb(0x171796) }, emblem: FlagEmblem.Croatia);

        public static readonly Flag Czechia = new Flag(FlagPattern.Czechia,
            new[] { Rgb(0xFFFFFF), Rgb(0xD7141A), Rgb(0x11457E) });

        public static readonly Flag Finland = new Flag(FlagPattern.NordicCross,
            new[] { Rgb(0xFFFFFF), Rgb(0x002F6C) }, new float[] { 5, 3, 10 }, new float[] { 4, 3, 4 });

        public static readonly Flag France = new Flag(FlagPattern.VerticalStripes,
            new[] { Rgb(0x0055A4), Rgb(0xFFFFFF), Rgb(0xEF4135) });

        public static readonly Flag Germany = new Flag(FlagPattern.HorizontalStripes,
            new[] { Rgb(0x000000), Rgb(0xDD0000), Rgb(0xFFCE00) });

        public static readonly Flag Italy = new Flag(FlagPattern.VerticalStripes,
            new[] { Rgb(0x009246), Rgb(0xFFFFFF), Rgb(0xCE2B37) });

        public static readonly Flag Netherlands = new Flag(FlagPattern.HorizontalStripes,
            new[] { Rgb(0xAE1C28), Rgb(0xFFFFFF), Rgb(0x21468B) });

        public static readonly Flag Norway = new Flag(FlagPattern.NordicCross,
            new[] { Rgb(0xBA0C2F), Rgb(0xFFFFFF), Rgb(0x00205B) },
            new float[] { 6, 1, 2, 1, 12 }, new float[] { 6, 1, 2, 1, 6 });

        public static readonly Flag Poland = new Flag(FlagPattern.HorizontalStripes,
            new[] { Rgb(0xFFFFFF), Rgb(0xDC143C) });

        public static readonly Flag Portugal = new Flag(FlagPattern.VerticalStripes,
            new[] { Rgb(0x006600), Rgb(0xFF0000) }, new float[] { 2, 3 }, emblem: FlagEmblem.Portugal);

        public static readonly Flag Spain = new Flag(FlagPattern.HorizontalStripes,
            new[] { Rgb(0xAA151B), Rgb(0xF1BF00), Rgb(0xAA151B) }, new float[] { 1, 2, 1 });

        public static readonly Flag Sweden = new Flag(FlagPattern.NordicCross,
            new[] { Rgb(0x006AA7), Rgb(0xFECC00) }, new float[] { 5, 2, 9 }, new float[] { 4, 2, 4 });

        public static readonly Flag UnitedKingdom = new Flag(FlagPattern.UnionJack,
            new[] { Rgb(0x012169), Rgb(0xFFFFFF), Rgb(0xC8102E) });
    }
}
