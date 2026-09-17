"""
Canonical weather row.

Every vendor client must parse into this shape. Known kite fields are
promoted onto columns. Everything else stays in `extras` so we do not
throw away data while still having a stable schema for analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


def mps_to_kt(value) -> float | None:
    if value is None:
        return None
    return float(value) * 1.94384


def f_to_c(value) -> float | None:
    if value is None:
        return None
    return (float(value) - 32.0) * 5.0 / 9.0


def inch_to_mm(value) -> float | None:
    if value is None:
        return None
    return float(value) * 25.4


def num(value):
    if value in (None, "", "null", "M", "T"):
        return None
    return float(value)


@dataclass
class CanonicalHour:
    observed_at: datetime
    wind_speed_kt: float | None = None
    wind_gust_kt: float | None = None
    wind_direction_deg: float | None = None
    temperature_c: float | None = None
    pressure_hpa: float | None = None
    precipitation_mm: float | None = None
    wave_height_m: float | None = None
    wave_period_s: float | None = None
    wave_direction_deg: float | None = None
    sea_level_m: float | None = None
    extras: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)
