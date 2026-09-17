import json


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


def has_region(place) -> bool:
    if normalize_polygon(place.get("region_polygon")):
        return True
    return any(place.get(key) not in (None, "") for key in ("region_north", "region_south", "region_east", "region_west"))
