from django.utils import timezone

from patterns.outlook import forecast_outlook
from weather.ingest import ingest_forecast, ingest_history, ingest_marine
from weather.persist import purge_spot_weather
from weather.stations import discover_stations_for_spot

from .geometry import bbox_from_polygon, has_region, normalize_polygon
from .models import Spot, SpotWatch
from .search import nearby_existing_spot, unique_slug


def get_or_create_spot_from_place(place) -> Spot:
    name = (place.get("name") or "").strip() or "Custom launch"
    existing = nearby_existing_spot(place["latitude"], place["longitude"])
    if existing and not has_region(place) and existing.name.lower() == name.lower():
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
