"""Progress of the notification popup's auto-hide countdown (as in the Windows app)."""


def remaining_fraction(elapsed_ms, timeout_ms):
    """Remaining share of the countdown, from 1 (just shown) down to 0 (time is up)."""
    if timeout_ms <= 0:
        return 0.0
    return min(1.0, max(0.0, 1.0 - elapsed_ms / timeout_ms))


def bar_width(track_width, elapsed_ms, timeout_ms):
    """Width of the countdown bar for a track of track_width pixels."""
    return int(round(track_width * remaining_fraction(elapsed_ms, timeout_ms)))
