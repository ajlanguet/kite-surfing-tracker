import json

from django.utils import timezone
from django.utils.text import slugify

from patterns.outlook import forecast_outlook
from weather.services import discover_stations_for_spot, ingest_forecast, ingest_history, ingest_marine, purge_spot_weather

from .geocode import reverse_geocode, search_places
from .models import Spot, SpotWatch


def unique_slug(name, latitude, longitude):
    base = slugify(name) or "spot"
    if not Spot.objects.filter(slug=base).exists():
        return base
    geo = f"{base}-{abs(int(float(latitude) * 100))}-{abs(int(float(longitude) * 100))}"
    if not Spot.objects.filter(slug=geo).exists():
        return geo
    suffix = 2
    while Spot.objects.filter(slug=f"{base}-{suffix}").exists():
        suffix += 1
    return f"{base}-{suffix}"


def nearby_existing_spot(latitude, longitude, tolerance=0.08):
    """Reuse a catalog spot if the search landed on the same beach."""
    lat = float(latitude)
    lng = float(longitude)
    for spot in Spot.objects.all():
        if abs(float(spot.latitude) - lat) <= tolerance and abs(float(spot.longitude) - lng) <= tolerance:
            return spot
    return None


def search_spots_and_places(query):
    query = (query or "").strip()
    if len(query) < 2:
        return {"spots": [], "suggestions": []}

    spots = list(Spot.objects.filter(name__icontains=query)[:8])
    suggestions = []
    for place in search_places(query):
        existing = nearby_existing_spot(place["latitude"], place["longitude"])
        if existing and existing not in spots:
            spots.append(existing)
        elif not existing:
            suggestions.append(place)
    return {"spots": spots, "suggestions": suggestions}


def describe_map_point(latitude, longitude, bounds=None):
    place = reverse_geocode(latitude, longitude)
    if bounds:
        place.update(bounds)
    existing = nearby_existing_spot(latitude, longitude)
    return {"place": place, "existing_spot": existing}


def normalize_polygon(raw):
    if not raw:
        return None
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return None
    points = []
    for item in raw:
        if isinstance(item, dict):
            lat = item.get("lat", item.get("latitude"))
            lng = item.get("lng", item.get("longitude"))
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            lat, lng = item[0], item[1]
        else:
            continue
        try:
            points.append({"lat": round(float(lat), 6), "lng": round(float(lng), 6)})
        except (TypeError, ValueError):
            continue
    return points if len(points) >= 3 else None


def bbox_from_polygon(polygon):
    lats = [point["lat"] for point in polygon]
    lngs = [point["lng"] for point in polygon]
    return {
        "region_north": max(lats),
        "region_south": min(lats),
        "region_east": max(lngs),
        "region_west": min(lngs),
    }


def _has_region(place) -> bool:
    if normalize_polygon(place.get("region_polygon")):
        return True
    return any(place.get(key) not in (None, "") for key in ("region_north", "region_south", "region_east", "region_west"))


def get_or_create_spot_from_place(place) -> Spot:
    name = (place.get("name") or "").strip() or "Custom launch"
    existing = nearby_existing_spot(place["latitude"], place["longitude"])
    if existing and not _has_region(place) and existing.name.lower() == name.lower():
        return existing
    polygon = normalize_polygon(place.get("region_polygon"))
    bbox = bbox_from_polygon(polygon) if polygon else {}
    return Spot.objects.create(
        name=name,
        slug=unique_slug(name, place["latitude"], place["longitude"]),
        latitude=place["latitude"],
        longitude=place["longitude"],
        timezone=place.get("timezone") or "UTC",
        notes=place.get("label") or "",
        created_from_search=True,
        min_rideable_kt=12,
        max_rideable_kt=30,
        window_start_deg=0,
        window_end_deg=359,
        region_north=place.get("region_north", bbox.get("region_north")),
        region_south=place.get("region_south", bbox.get("region_south")),
        region_east=place.get("region_east", bbox.get("region_east")),
        region_west=place.get("region_west", bbox.get("region_west")),
        region_polygon=polygon,
    )


def track_spot(spot, ingest_history_days=0, favorite=False):
    """
    Start storing weather for this launch.

    Forecast is pulled immediately so the UI can score the next hours.
    History is optional: it is slower and only useful once you care
    about fill-in patterns.
    """
    watch, _created = SpotWatch.objects.get_or_create(spot=spot)
    if favorite:
        watch.is_favorite = True
        watch.save(update_fields=["is_favorite"])

    forecast_rows = ingest_forecast(spot)
    marine_rows = ingest_marine(spot)
    discover_stations_for_spot(spot)
    history_rows = 0
    if ingest_history_days:
        from datetime import date, timedelta

        end_date = date.today() - timedelta(days=6)
        start_date = end_date - timedelta(days=ingest_history_days - 1)
        history_rows = ingest_history(spot, start_date, end_date)
        ingest_marine(spot, start_date=start_date, end_date=end_date)

    watch.last_ingested_at = timezone.now()
    watch.save(update_fields=["last_ingested_at"])
    return {
        "spot": spot,
        "forecast_rows": forecast_rows,
        "marine_rows": marine_rows,
        "history_rows": history_rows,
        "outlook": forecast_outlook(spot),
    }


def untrack_spot(spot):
    """Stop following this place and delete stored weather for it."""
    created_from_search = spot.created_from_search
    purge_spot_weather(spot)
    SpotWatch.objects.filter(spot=spot).delete()
    deleted_spot = False
    if created_from_search:
        spot.delete()
        deleted_spot = True
    return {"deleted_spot": deleted_spot}


def set_favorite(spot, is_favorite: bool):
    watch = getattr(spot, "watch", None)
    if watch is None:
        raise ValueError("Favorite only applies to tracked spots.")
    watch.is_favorite = is_favorite
    watch.save(update_fields=["is_favorite"])
    return watch
