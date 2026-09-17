from collections import defaultdict
from decimal import Decimal
from zoneinfo import ZoneInfo

from weather.models import DailyWindSummary, Observation

from .wind import WindWindow, circular_mean_deg, fill_in_hour, is_rideable


def window_for(spot) -> WindWindow:
    return WindWindow(
        min_kt=spot.min_rideable_kt,
        max_kt=spot.max_rideable_kt,
        start_deg=spot.window_start_deg,
        end_deg=spot.window_end_deg,
    )


def observation_to_local_row(observation, timezone_name):
    local = observation.observed_at.astimezone(ZoneInfo(timezone_name))
    return {
        "local_date": local.date(),
        "local_hour": local.hour,
        "wind_speed_kt": observation.wind_speed_kt,
        "wind_gust_kt": observation.wind_gust_kt,
        "wind_direction_deg": observation.wind_direction_deg,
    }


def summarize_spot_source(spot, source) -> int:
    window = window_for(spot)
    observations = Observation.objects.filter(spot=spot, source=source).order_by("observed_at")
    by_date = defaultdict(list)
    for observation in observations:
        row = observation_to_local_row(observation, spot.timezone)
        by_date[row["local_date"]].append(row)

    saved = 0
    for local_date, rows in by_date.items():
        speeds = [r["wind_speed_kt"] for r in rows if r["wind_speed_kt"] is not None]
        gusts = [r["wind_gust_kt"] for r in rows if r["wind_gust_kt"] is not None]
        rideable_hours = sum(
            1
            for row in rows
            if is_rideable(row["wind_speed_kt"], row["wind_direction_deg"], window)
        )
        mean_wind = (sum(float(s) for s in speeds) / len(speeds)) if speeds else None
        max_gust = max((float(g) for g in gusts), default=None)
        dominant = circular_mean_deg(
            [r["wind_direction_deg"] for r in rows],
            [r["wind_speed_kt"] or 0 for r in rows],
        )
        DailyWindSummary.objects.update_or_create(
            spot=spot,
            source=source,
            local_date=local_date,
            defaults={
                "rideable_hours": rideable_hours,
                "fill_in_hour": fill_in_hour(rows, window),
                "mean_wind_kt": None if mean_wind is None else Decimal(str(round(mean_wind, 2))),
                "max_gust_kt": None if max_gust is None else Decimal(str(round(max_gust, 2))),
                "dominant_direction_deg": None
                if dominant is None
                else Decimal(str(round(dominant, 2))),
            },
        )
        saved += 1
    return saved
