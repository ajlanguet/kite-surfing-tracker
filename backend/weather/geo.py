from math import asin, cos, radians, sin, sqrt


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Great-circle distance. This is enough; we do not need a GIS stack yet."""
    phi1, phi2 = radians(float(lat1)), radians(float(lat2))
    dphi = radians(float(lat2) - float(lat1))
    dlambda = radians(float(lon2) - float(lon1))
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 6371.0 * 2 * asin(sqrt(a))
