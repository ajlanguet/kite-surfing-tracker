from datetime import datetime, timezone

from .clients import FORECAST_CLIENTS, HISTORY_CLIENTS
from .models import ForecastPoint, WeatherSource
from .persist import ensure_grid_station, get_or_create_source, persist_hours
from .schema import CanonicalHour


def ingest_forecast(spot, client_key="open-meteo"):
    client = FORECAST_CLIENTS[client_key]
    source = get_or_create_source(client)
    issued_at = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    payload = client.fetch_forecast(spot.latitude, spot.longitude)
    rows = client.parse_forecast(payload, issued_at)
    saved = 0
    for row in rows:
        _obj, created = ForecastPoint.objects.update_or_create(
            spot=spot,
            source=source,
            issued_at=row["issued_at"],
            valid_at=row["valid_at"],
            defaults={
                "lead_hours": row["lead_hours"],
                "wind_speed_kt": row["wind_speed_kt"],
                "wind_gust_kt": row["wind_gust_kt"],
                "wind_direction_deg": row["wind_direction_deg"],
                "temperature_c": row["temperature_c"],
                "pressure_hpa": row["pressure_hpa"],
                "precipitation_mm": row["precipitation_mm"],
                "raw_payload": row["raw_payload"],
            },
        )
        if created:
            saved += 1
    return saved


def ingest_history(spot, start_date, end_date, client_key="open-meteo-era5"):
    client = HISTORY_CLIENTS[client_key]
    source = get_or_create_source(client)
    station = ensure_grid_station(spot)
    payload = client.fetch_history(spot.latitude, spot.longitude, start_date, end_date)
    parsed = client.parse_history(payload)
    hours = [
        CanonicalHour(
            observed_at=row["observed_at"],
            wind_speed_kt=row["wind_speed_kt"],
            wind_gust_kt=row["wind_gust_kt"],
            wind_direction_deg=row["wind_direction_deg"],
            temperature_c=row["temperature_c"],
            pressure_hpa=row["pressure_hpa"],
            precipitation_mm=row["precipitation_mm"],
            raw=row["raw_payload"],
        )
        for row in parsed
    ]
    return persist_hours(spot, station, source, hours)


def marine_source():
    source, _created = WeatherSource.objects.get_or_create(
        slug="open-meteo-marine",
        defaults={
            "name": "Open-Meteo Marine",
            "kind": WeatherSource.Kind.FORECAST,
            "homepage": "https://open-meteo.com/en/docs/marine-weather-api",
        },
    )
    return source


def ingest_marine(spot, start_date=None, end_date=None) -> int:
    """
    Store waves + tide and stamp them onto the latest wind forecast hours.

    Daily polling creates a new forecast issued_at each run, so the archive
    of 'what Open-Meteo said that morning' grows instead of overwriting.
    """
    from .clients.open_meteo_marine import fetch_marine_forecast, fetch_marine_history, parse_marine
    import httpx

    try:
        if start_date and end_date:
            payload = fetch_marine_history(spot.latitude, spot.longitude, start_date, end_date)
        else:
            payload = fetch_marine_forecast(spot.latitude, spot.longitude)
    except httpx.HTTPError:
        return 0

    source = marine_source()
    hours = parse_marine(payload)
    station = ensure_grid_station(spot)
    saved = persist_hours(spot, station, source, hours)

    latest_issued = (
        ForecastPoint.objects.filter(spot=spot).order_by("-issued_at").values_list("issued_at", flat=True).first()
    )
    if latest_issued:
        for hour in hours:
            ForecastPoint.objects.filter(spot=spot, issued_at=latest_issued, valid_at=hour.observed_at).update(
                wave_height_m=hour.wave_height_m,
                wave_period_s=hour.wave_period_s,
                wave_direction_deg=hour.wave_direction_deg,
                sea_level_m=hour.sea_level_m,
            )
    return saved


def poll_tracked_spot(spot, history_days=1) -> dict:
    """
    One daily increment for a tracked launch: new forecast snapshot,
    marine/tide hours, and another day of delayed ERA5 history.
    """
    from datetime import date, timedelta

    forecast_rows = ingest_forecast(spot)
    marine_rows = ingest_marine(spot)
    history_rows = 0
    if history_days:
        end_date = date.today() - timedelta(days=6)
        start_date = end_date - timedelta(days=history_days - 1)
        history_rows = ingest_history(spot, start_date, end_date)
        ingest_marine(spot, start_date=start_date, end_date=end_date)
    return {
        "forecast_rows": forecast_rows,
        "marine_rows": marine_rows,
        "history_rows": history_rows,
    }
