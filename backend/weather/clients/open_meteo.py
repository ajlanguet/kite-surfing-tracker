from datetime import datetime, timezone

import httpx

from .base import WeatherClient

HOURLY_VARS = [
    "wind_speed_10m",
    "wind_gusts_10m",
    "wind_direction_10m",
    "temperature_2m",
    "pressure_msl",
    "precipitation",
]


def _zip_hourly(payload):
    """Open-Meteo returns parallel arrays. Pair them into row dicts."""
    hourly = payload.get("hourly") or {}
    times = hourly.get("time") or []
    rows = []
    for index, stamp in enumerate(times):
        rows.append(
            {
                "time": stamp,
                "wind_speed_kt": _at(hourly, "wind_speed_10m", index),
                "wind_gust_kt": _at(hourly, "wind_gusts_10m", index),
                "wind_direction_deg": _at(hourly, "wind_direction_10m", index),
                "temperature_c": _at(hourly, "temperature_2m", index),
                "pressure_hpa": _at(hourly, "pressure_msl", index),
                "precipitation_mm": _at(hourly, "precipitation", index),
            }
        )
    return rows


def _at(hourly, key, index):
    values = hourly.get(key) or []
    if index >= len(values):
        return None
    return values[index]


def _parse_utc(stamp):
    # Open-Meteo hourly stamps look like 2026-09-17T13:00
    return datetime.fromisoformat(stamp).replace(tzinfo=timezone.utc)


class OpenMeteoForecastClient(WeatherClient):
    """
    Live forecast. Free, no API key.

    `model` lets you pull GFS vs ECMWF from the same client class.
    See https://open-meteo.com/en/docs
    """

    homepage = "https://open-meteo.com/"
    source_kind = "forecast"
    endpoint = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, slug, name, model=None):
        self.source_slug = slug
        self.source_name = name
        self.model = model

    def fetch_forecast(self, latitude, longitude):
        params = {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "hourly": ",".join(HOURLY_VARS),
            "wind_speed_unit": "kn",
            "timezone": "UTC",
            "forecast_days": 7,
        }
        if self.model:
            params["models"] = self.model
        response = httpx.get(self.endpoint, params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()

    def parse_forecast(self, payload, issued_at):
        rows = []
        for raw in _zip_hourly(payload):
            valid_at = _parse_utc(raw["time"])
            lead = int((valid_at - issued_at).total_seconds() // 3600)
            if lead < 0:
                continue
            rows.append(
                {
                    "issued_at": issued_at,
                    "valid_at": valid_at,
                    "lead_hours": lead,
                    "wind_speed_kt": raw["wind_speed_kt"],
                    "wind_gust_kt": raw["wind_gust_kt"],
                    "wind_direction_deg": raw["wind_direction_deg"],
                    "temperature_c": raw["temperature_c"],
                    "pressure_hpa": raw["pressure_hpa"],
                    "precipitation_mm": raw["precipitation_mm"],
                    "raw_payload": raw,
                }
            )
        return rows


class OpenMeteoArchiveClient(WeatherClient):
    """
    ERA5 reanalysis — our first 'what actually happened' source.

    Next upgrade: Open-Meteo Historical Forecast API, which lets you
    compare what a model said yesterday against what ERA5 says happened.
    """

    source_slug = "open-meteo-era5"
    source_name = "Open-Meteo ERA5"
    source_kind = "reanalysis"
    homepage = "https://open-meteo.com/en/docs/historical-weather-api"
    endpoint = "https://archive-api.open-meteo.com/v1/archive"

    def fetch_forecast(self, latitude, longitude):
        raise NotImplementedError("ERA5 is historical only. Use fetch_history.")

    def parse_forecast(self, payload, issued_at):
        raise NotImplementedError("ERA5 is historical only.")

    def fetch_history(self, latitude, longitude, start_date, end_date):
        params = {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hourly": ",".join(HOURLY_VARS),
            "wind_speed_unit": "kn",
            "timezone": "UTC",
        }
        response = httpx.get(self.endpoint, params=params, timeout=60.0)
        response.raise_for_status()
        return response.json()

    def parse_history(self, payload):
        rows = []
        for raw in _zip_hourly(payload):
            rows.append(
                {
                    "observed_at": _parse_utc(raw["time"]),
                    "wind_speed_kt": raw["wind_speed_kt"],
                    "wind_gust_kt": raw["wind_gust_kt"],
                    "wind_direction_deg": raw["wind_direction_deg"],
                    "temperature_c": raw["temperature_c"],
                    "pressure_hpa": raw["pressure_hpa"],
                    "precipitation_mm": raw["precipitation_mm"],
                    "raw_payload": raw,
                }
            )
        return rows
