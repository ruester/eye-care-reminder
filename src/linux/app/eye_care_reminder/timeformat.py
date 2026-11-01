"""User-facing texts that contain times."""

import locale

from . import APP_NAME


def short_time_format(t_fmt):
    """strftime format for hours and minutes, from the locale's time format
    (nl_langinfo(T_FMT), e.g. "%H:%M:%S" or "%r"): the seconds are dropped."""
    fmt = t_fmt or "%H:%M"
    fmt = fmt.replace("%r", "%I:%M:%S %p").replace("%T", "%H:%M:%S").replace("%X", "%H:%M:%S")
    for seconds in (":%S", ".%S", "%S"):
        fmt = fmt.replace(seconds, "")
    return fmt.strip() or "%H:%M"


def locale_time_format():
    """Short time format of the user's regional settings (LC_TIME), e.g. "%H:%M" or "%I:%M %p"."""
    try:
        locale.setlocale(locale.LC_TIME, "")
        return short_time_format(locale.nl_langinfo(locale.T_FMT))
    except (locale.Error, AttributeError):
        return "%H:%M"


def time_of_day(moment, fmt=None):
    """Time of day in the user's regional format, e.g. "14:05" or "02:05 PM"."""
    return moment.strftime(fmt or locale_time_format())


def tray_text(next_break, texts, fmt=None):
    """Tray icon tooltip with the time of the next break."""
    return APP_NAME + "\n" + texts.next_break_at.format(time_of_day(next_break, fmt))
