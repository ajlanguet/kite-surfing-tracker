"""
Station catalogs. These files only answer 'what sensors exist near this lat/lng'.
They do not ingest hourly observations.
"""

from __future__ import annotations

import gzip
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from functools import lru_cache

import httpx

from weather.geo import haversine_km

METEOSTAT_LITE = "https://bulk.meteostat.net/v2/stations/lite.json.gz"
NDBC_ACTIVE = "https://www.ndbc.noaa.gov/activestations.xml"
USER_AGENT = "KiteSurfingTracker/0.1 (local research)"


@dataclass(frozen=True)
class CatalogHit:
    network: str
    external_id: str
    name: str
    kind: str
    latitude: float
    longitude: float
    distance_km: float
    elevation_m: float | None = None
    timezone: str = ""
    country: str = ""
    icao: str = ""
    metadata: dict | None = None


def _client():
    return httpx.Client(timeout=60.0, headers={"User-Agent": USER_AGENT}, follow_redirects=True)


@lru_cache(maxsize=1)
def _meteostat_inventory():
    with _client() as client:
        response = client.get(METEOSTAT_LITE)
        response.raise_for_status()
    return json.loads(gzip.decompress(response.content))


@lru_cache(maxsize=1)
def _ndbc_xml():
    with _client() as client:
        response = client.get(NDBC_ACTIVE)
        response.raise_for_status()
    return response.content


def nearby_meteostat(latitude, longitude, radius_km=80, limit=8) -> list[CatalogHit]:
    """
    Global land/airport inventory (~16k stations). Free bulk file, no API key.
    Hourly values still come from ISD/IEM later; this is discovery only.
    """
    payload = _meteostat_inventory()
    hits = []
    for row in payload:
        location = row.get("location") or {}
        lat = location.get("latitude")
        lon = location.get("longitude")
        if lat is None or lon is None:
            continue
        distance = haversine_km(latitude, longitude, lat, lon)
        if distance > radius_km:
            continue
        identifiers = row.get("identifiers") or {}
        inventory = row.get("inventory") or {}
        hourly = inventory.get("hourly") or {}
        if not hourly.get("start"):
            continue
        name = (row.get("name") or {}).get("en") or row.get("id")
        icao = identifiers.get("icao") or ""
        kind = "airport" if icao else "land"
        hits.append(
            CatalogHit(
                network="meteostat",
                external_id=row["id"],
                name=name,
                kind=kind,
                latitude=float(lat),
                longitude=float(lon),
                distance_km=round(distance, 2),
                elevation_m=location.get("elevation"),
                timezone=row.get("timezone") or "",
                country=row.get("country") or "",
                icao=icao,
                metadata={"identifiers": identifiers, "hourly": hourly},
            )
        )
    hits.sort(key=lambda item: item.distance_km)
    return hits[:limit]


def nearby_ndbc(latitude, longitude, radius_km=120, limit=8) -> list[CatalogHit]:
    """Active NOAA buoys and C-MAN stations worldwide."""
    root = ET.fromstring(_ndbc_xml())
    hits = []
    for element in root.findall("station"):
        try:
            lat = float(element.attrib["lat"])
            lon = float(element.attrib["lon"])
        except (KeyError, ValueError):
            continue
        distance = haversine_km(latitude, longitude, lat, lon)
        if distance > radius_km:
            continue
        station_type = (element.attrib.get("type") or "buoy").lower()
        kind = "buoy" if "buoy" in station_type or station_type in {"dart", "tao"} else "land"
        hits.append(
            CatalogHit(
                network="ndbc",
                external_id=element.attrib["id"],
                name=element.attrib.get("name") or element.attrib["id"],
                kind=kind,
                latitude=lat,
                longitude=lon,
                distance_km=round(distance, 2),
                elevation_m=float(element.attrib["elev"]) if element.attrib.get("elev") else None,
                metadata={
                    "owner": element.attrib.get("owner"),
                    "type": element.attrib.get("type"),
                    "pgm": element.attrib.get("pgm"),
                },
            )
        )
    hits.sort(key=lambda item: item.distance_km)
    return hits[:limit]
