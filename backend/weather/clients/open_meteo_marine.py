"""
Open-Meteo Marine: waves + sea level (tides).

sea_level_height_msl includes ocean tide. It is relative to global mean
sea level, not a local tide gauge datum, so we use the shape of the
curve (rising/falling, high/low in the day's range) rather than the
absolute metre value.
"""

from datetime import datetime, timezone

import httpx

from weather.schema import CanonicalHour

MARINE_HOURLY = [
    "wave_height",
    "wave_direction",
    "wave_period",
    "sea_level_height_msl",
    "sea_surface_temperature",
]
FORECAST_URL = "https://marine-api.open-meteo.com/v1/marine"


def _at(hourly, key, index):
    values = hourly.get(key) or []
    if index >= len(values):
        return None
    return values[index]


def _parse_utc(stamp):
    return datetime.fromisoformat(stamp).replace(tzinfo=timezone.utc)


def _rows_from_payload(payload) -> list[CanonicalHour]:
    hourly = payload.get("hourly") or {}
    times = hourly.get("time") or []
    rows = []
    for index, stamp in enumerate(times):
        raw = {
            "time": stamp,
            "wave_height": _at(hourly, "wave_height", index),
            "wave_direction": _at(hourly, "wave_direction", index),
            "wave_period": _at(hourly, "wave_period", index),
            "sea_level_height_msl": _at(hourly, "sea_level_height_msl", index),
            "sea_surface_temperature": _at(hourly, "sea_surface_temperature", index),
        }
        rows.append(
            CanonicalHour(
                observed_at=_parse_utc(stamp),
                wave_height_m=raw["wave_height"],
                wave_period_s=raw["wave_period"],
                wave_direction_deg=raw["wave_direction"],
                sea_level_m=raw["sea_level_height_msl"],
                extras={"sea_surface_temperature_c": raw["sea_surface_temperature"]},
                raw=raw,
            )
        )
    return rows


def _get(params):
    response = httpx.get(FORECAST_URL, params=params, timeout=45.0)
    response.raise_for_status()
    return response.json()


def fetch_marine_forecast(latitude, longitude, forecast_days=7):
    return _get(
        {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "hourly": ",".join(MARINE_HOURLY),
            "timezone": "UTC",
            "forecast_days": forecast_days,
        }
    )


def fetch_marine_history(latitude, longitude, start_date, end_date):
    return _get(
        {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "hourly": ",".join(MARINE_HOURLY),
            "timezone": "UTC",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
    )


def parse_marine(payload) -> list[CanonicalHour]:
    return _rows_from_payload(payload)
