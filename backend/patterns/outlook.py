from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from weather.models import ForecastPoint

from .summarize import window_for
from .tide import daily_range, tide_matches, tide_phase
from .wind import is_rideable


def forecast_outlook(spot, hours=72):
    """
    Instant 'is it worth going' view from stored forecast rows.

    Wind window first, then tide preference if the spot cares.
    Historical fill-in still lives on the pattern endpoint.
    """
    window = window_for(spot)
    points = list(ForecastPoint.objects.filter(spot=spot).order_by("valid_at")[:hours])
    levels = [point.sea_level_m for point in points]
    day_min, day_max = daily_range(levels)

    scored = []
    next_go = None
    previous_level = None
    for point in points:
        wind_ok = is_rideable(point.wind_speed_kt, point.wind_direction_deg, window)
        phase = tide_phase(previous_level, point.sea_level_m, day_min, day_max)
        previous_level = point.sea_level_m
        tide_ok = tide_matches(phase, getattr(spot, "tide_preference", "any"))
        go = wind_ok and tide_ok
        local = point.valid_at
        if spot.timezone:
            local = point.valid_at.astimezone(ZoneInfo(spot.timezone))
        row = {
            "valid_at": point.valid_at.isoformat(),
            "local_hour": local.hour,
            "wind_speed_kt": None if point.wind_speed_kt is None else float(point.wind_speed_kt),
            "wind_gust_kt": None if point.wind_gust_kt is None else float(point.wind_gust_kt),
            "wind_direction_deg": None
            if point.wind_direction_deg is None
            else float(point.wind_direction_deg),
            "sea_level_m": None if point.sea_level_m is None else float(point.sea_level_m),
            "wave_height_m": None if point.wave_height_m is None else float(point.wave_height_m),
            "tide_phase": phase,
            "wind_ok": wind_ok,
            "tide_ok": tide_ok,
            "rideable": go,
        }
        scored.append(row)
        if go and next_go is None:
            next_go = row["valid_at"]

    now = datetime.now(timezone.utc)
    upcoming = [row for row in scored if datetime.fromisoformat(row["valid_at"]) >= now]
    return {
        "hours_scored": len(scored),
        "rideable_hours": sum(1 for row in upcoming if row["rideable"]),
        "next_rideable_at": next_go,
        "tide_preference": getattr(spot, "tide_preference", "any"),
        "hours": upcoming[:48],
    }
