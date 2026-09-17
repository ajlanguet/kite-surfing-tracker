from .clients.catalogs import nearby_meteostat, nearby_ndbc
from .clients.iem_asos import fetch_asos_csv, icao_to_iem_id, parse_asos_csv
from .models import SpotStation, Station, WeatherSource
from .persist import ensure_grid_station, persist_hours, upsert_station_hit


def discover_stations_for_spot(spot, radius_km=80, limit=8) -> list[SpotStation]:
    ensure_grid_station(spot)
    hits = nearby_meteostat(spot.latitude, spot.longitude, radius_km=radius_km, limit=limit)
    hits += nearby_ndbc(spot.latitude, spot.longitude, radius_km=max(radius_km, 120), limit=limit)
    return [upsert_station_hit(spot, hit) for hit in hits]


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
