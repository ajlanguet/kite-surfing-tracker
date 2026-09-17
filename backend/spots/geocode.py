import httpx

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HEADERS = {"User-Agent": "KiteSurfingTracker/0.1 (local research)"}


def search_places(query, count=8):
    """
    Place names → lat/lng/timezone. This is not weather and not GIS;
    it is only how a typed beach name becomes a point we can track.
    """
    response = httpx.get(
        GEOCODE_URL,
        params={"name": query, "count": count, "language": "en", "format": "json"},
        timeout=20.0,
        headers=HEADERS,
    )
    response.raise_for_status()
    payload = response.json()
    suggestions = []
    for row in payload.get("results") or []:
        suggestions.append(
            {
                "name": row.get("name"),
                "latitude": row.get("latitude"),
                "longitude": row.get("longitude"),
                "timezone": row.get("timezone") or "UTC",
                "country": row.get("country") or "",
                "region": row.get("admin1") or "",
                "label": ", ".join(
                    part
                    for part in [row.get("name"), row.get("admin1"), row.get("country")]
                    if part
                ),
            }
        )
    return suggestions


def lookup_timezone(latitude, longitude) -> str:
    response = httpx.get(
        FORECAST_URL,
        params={
            "latitude": float(latitude),
            "longitude": float(longitude),
            "current": "temperature_2m",
            "timezone": "auto",
        },
        timeout=20.0,
        headers=HEADERS,
    )
    response.raise_for_status()
    return response.json().get("timezone") or "UTC"


def reverse_geocode(latitude, longitude) -> dict:
    """Map click → a human name. Nominatim reverse, timezone from Open-Meteo."""
    response = httpx.get(
        REVERSE_URL,
        params={
            "lat": float(latitude),
            "lon": float(longitude),
            "format": "jsonv2",
            "zoom": 14,
        },
        timeout=20.0,
        headers=HEADERS,
    )
    response.raise_for_status()
    payload = response.json()
    address = payload.get("address") or {}
    name = (
        address.get("village")
        or address.get("hamlet")
        or address.get("town")
        or address.get("city")
        or address.get("suburb")
        or address.get("county")
        or payload.get("name")
        or f"Map {float(latitude):.3f}, {float(longitude):.3f}"
    )
    label_parts = [
        name,
        address.get("state"),
        address.get("country"),
    ]
    return {
        "name": name,
        "latitude": round(float(latitude), 6),
        "longitude": round(float(longitude), 6),
        "timezone": lookup_timezone(latitude, longitude),
        "country": address.get("country") or "",
        "region": address.get("state") or "",
        "label": ", ".join(part for part in label_parts if part),
    }
