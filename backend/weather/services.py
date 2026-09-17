from datetime import datetime, timezone
from decimal import Decimal

from .clients import FORECAST_CLIENTS, HISTORY_CLIENTS
from .clients.catalogs import CatalogHit, nearby_meteostat, nearby_ndbc
from .clients.iem_asos import fetch_asos_csv, icao_to_iem_id, parse_asos_csv
from .models import DailyWindSummary, ForecastPoint, Observation, SpotStation, Station, WeatherSource
from .schema import CanonicalHour


def get_or_create_source(client):
    source, _created = WeatherSource.objects.get_or_create(
        slug=client.source_slug,
        defaults={
            "name": client.source_name,
            "kind": client.source_kind,
            "homepage": client.homepage,
        },
    )
    return source


def ensure_grid_station(spot) -> Station:
    station, _created = Station.objects.get_or_create(
        network="grid",
        external_id=spot.slug,
        defaults={
            "name": f"Model grid at {spot.name}",
            "kind": Station.Kind.GRID,
            "latitude": spot.latitude,
            "longitude": spot.longitude,
            "timezone": spot.timezone,
        },
    )
    SpotStation.objects.get_or_create(
        spot=spot,
        station=station,
        defaults={"distance_km": 0, "is_preferred": False},
    )
    return station


def persist_hours(spot, station, source, hours: list[CanonicalHour]) -> int:
    saved = 0
    for hour in hours:
        _obj, created = Observation.objects.update_or_create(
            spot=spot,
            station=station,
            source=source,
            observed_at=hour.observed_at,
            defaults={
                "wind_speed_kt": hour.wind_speed_kt,
                "wind_gust_kt": hour.wind_gust_kt,
                "wind_direction_deg": hour.wind_direction_deg,
                "temperature_c": hour.temperature_c,
                "pressure_hpa": hour.pressure_hpa,
                "precipitation_mm": hour.precipitation_mm,
                "wave_height_m": hour.wave_height_m,
                "wave_period_s": hour.wave_period_s,
                "wave_direction_deg": hour.wave_direction_deg,
                "sea_level_m": hour.sea_level_m,
                "extras": hour.extras,
                "raw_payload": hour.raw,
            },
        )
        if created:
            saved += 1
    return saved


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


def _upsert_hit(spot, hit: CatalogHit) -> SpotStation:
    station, _created = Station.objects.update_or_create(
        network=hit.network,
        external_id=hit.external_id,
        defaults={
            "name": hit.name,
            "kind": hit.kind,
            "latitude": Decimal(str(hit.latitude)),
            "longitude": Decimal(str(hit.longitude)),
            "elevation_m": None if hit.elevation_m is None else Decimal(str(hit.elevation_m)),
            "timezone": hit.timezone,
            "country": hit.country,
            "icao": hit.icao,
            "metadata": hit.metadata or {},
        },
    )
    link, _created = SpotStation.objects.update_or_create(
        spot=spot,
        station=station,
        defaults={"distance_km": Decimal(str(hit.distance_km))},
    )
    return link


def discover_stations_for_spot(spot, radius_km=80, limit=8) -> list[SpotStation]:
    ensure_grid_station(spot)
    hits = nearby_meteostat(spot.latitude, spot.longitude, radius_km=radius_km, limit=limit)
    hits += nearby_ndbc(spot.latitude, spot.longitude, radius_km=max(radius_km, 120), limit=limit)
    return [_upsert_hit(spot, hit) for hit in hits]


def ingest_linked_stations(spot, start_date, end_date) -> dict[str, int]:
    """
    Pull hourly data for discovered sensors linked to this spot.

    ASOS/METAR goes through IEM. NDBC buoy hours are the next adapter to write.
    """
    source, _created = WeatherSource.objects.get_or_create(
        slug="iem-asos",
        defaults={
            "name": "IEM ASOS/METAR",
            "kind": WeatherSource.Kind.OBSERVATION,
            "homepage": "https://mesonet.agron.iastate.edu/request/download.phtml",
        },
    )
    counts = {}
    links = SpotStation.objects.filter(spot=spot).select_related("station")
    for link in links:
        station = link.station
        if station.kind == Station.Kind.GRID:
            continue
        if not station.icao:
            counts[station.external_id] = 0
            continue
        csv_text = fetch_asos_csv(icao_to_iem_id(station.icao), start_date, end_date)
        hours = parse_asos_csv(csv_text)
        counts[station.external_id] = persist_hours(spot, station, source, hours)
    return counts


def purge_spot_weather(spot):
    """Delete stored weather for a spot. Catalog stations (ASOS/NDBC) stay."""
    Observation.objects.filter(spot=spot).delete()
    ForecastPoint.objects.filter(spot=spot).delete()
    DailyWindSummary.objects.filter(spot=spot).delete()
    SpotStation.objects.filter(spot=spot).delete()
    Station.objects.filter(network="grid", external_id=spot.slug).delete()
