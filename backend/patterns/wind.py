"""
Pure wind math. No Django imports on purpose.

If a function here needs the database, it belongs in summarize.py instead.
That split lets you test the actual kite logic with plain numbers.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import atan2, cos, degrees, radians, sin


@dataclass(frozen=True)
class WindWindow:
    min_kt: float
    max_kt: float
    start_deg: float
    end_deg: float


def direction_in_window(direction_deg, start_deg, end_deg) -> bool:
    """True if direction sits in the clockwise sector from start to end."""
    direction = direction_deg % 360
    start = start_deg % 360
    end = end_deg % 360
    if start <= end:
        return start <= direction <= end
    return direction >= start or direction <= end


def is_rideable(speed_kt, direction_deg, window: WindWindow) -> bool:
    if speed_kt is None or direction_deg is None:
        return False
    if not window.min_kt <= float(speed_kt) <= window.max_kt:
        return False
    return direction_in_window(float(direction_deg), window.start_deg, window.end_deg)


def circular_mean_deg(directions, weights=None) -> float | None:
    """Average of angles. Plain arithmetic mean is wrong across 0/360."""
    pairs = list(zip(directions, weights or [1] * len(directions)))
    pairs = [(float(d), float(w)) for d, w in pairs if d is not None]
    if not pairs:
        return None
    x = sum(cos(radians(d)) * w for d, w in pairs)
    y = sum(sin(radians(d)) * w for d, w in pairs)
    if abs(x) < 1e-12 and abs(y) < 1e-12:
        return None
    return (degrees(atan2(y, x)) + 360) % 360


def fill_in_hour(hourly_rows, window: WindWindow, hold_hours: int = 3) -> int | None:
    """
    First local hour where wind turns on and then holds.

    Overnight wind does not count. We wait for at least one non-rideable
    hour, then take the first stretch of `hold_hours` rideable hours.
    That is the thermal/gradient fill-in time, not "it was already blowing
    at midnight."
    """
    flags = [
        is_rideable(row.get("wind_speed_kt"), row.get("wind_direction_deg"), window)
        for row in hourly_rows
    ]
    seen_off = False
    for index in range(0, len(flags) - hold_hours + 1):
        if not flags[index]:
            seen_off = True
            continue
        if seen_off and all(flags[index : index + hold_hours]):
            return int(hourly_rows[index]["local_hour"])
    return None


def hourly_rideable_profile(daily_rows, window: WindWindow) -> dict[int, float]:
    """
    Probability that each local hour is rideable, across many days.

    This is the first 'deterministic pattern': not a neural net, just
    how often hour 14 is actually kitable in the history you stored.
    """
    totals = defaultdict(int)
    hits = defaultdict(int)
    for row in daily_rows:
        hour = int(row["local_hour"])
        totals[hour] += 1
        if is_rideable(row.get("wind_speed_kt"), row.get("wind_direction_deg"), window):
            hits[hour] += 1
    return {hour: hits[hour] / totals[hour] for hour in sorted(totals) if totals[hour]}


def typical_fill_in(fill_in_hours: list[int | None]) -> float | None:
    hours = [h for h in fill_in_hours if h is not None]
    if not hours:
        return None
    return sum(hours) / len(hours)
