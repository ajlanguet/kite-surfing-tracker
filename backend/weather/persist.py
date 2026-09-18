from decimal import Decimal

from .clients.catalogs import CatalogHit
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


def purge_spot_weather(spot):
    """Delete stored weather for a spot. Catalog stations (ASOS/NDBC) stay."""
    Observation.objects.filter(spot=spot).delete()
    ForecastPoint.objects.filter(spot=spot).delete()
    DailyWindSummary.objects.filter(spot=spot).delete()
    SpotStation.objects.filter(spot=spot).delete()
    Station.objects.filter(network="grid", external_id=spot.slug).delete()


def upsert_station_hit(spot, hit: CatalogHit) -> SpotStation:
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
