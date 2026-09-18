from django.utils.text import slugify

from .geocode import reverse_geocode, search_places
from .models import Spot


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
