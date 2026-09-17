"""
Iowa Environmental Mesonet ASOS/METAR archive.

This is the first *station* hourly ingest: real anemometers at airports,
not a model grid. Wind is already in knots (`sknt`).
"""

from csv import DictReader
from datetime import datetime, timezone
from io import StringIO

import httpx

from weather.schema import CanonicalHour, f_to_c, inch_to_mm, num

IEM_ASOS = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
CANONICAL_KEYS = {
    "sknt",
    "gust",
    "drct",
    "tmpf",
    "mslp",
    "p01i",
    "station",
    "valid",
}


def icao_to_iem_id(icao: str) -> str:
    """CONUS ICAO codes are Kxxx; IEM uses the three-letter FAA id."""
    code = (icao or "").strip().upper()
    if len(code) == 4 and code.startswith("K"):
        return code[1:]
    return code


def fetch_asos_csv(station_id, start_date, end_date) -> str:
    params = {
        "station": station_id,
        "data": "all",
        "year1": start_date.year,
        "month1": start_date.month,
        "day1": start_date.day,
        "year2": end_date.year,
        "month2": end_date.month,
        "day2": end_date.day,
        "tz": "UTC",
        "format": "onlycomma",
        "latlon": "no",
        "missing": "null",
        "trace": "T",
        "direct": "no",
        "report_type": "3",
    }
    response = httpx.get(
        IEM_ASOS,
        params=params,
        timeout=60.0,
        headers={"User-Agent": "KiteSurfingTracker/0.1 (local research)"},
        follow_redirects=True,
    )
    response.raise_for_status()
    return response.text


def parse_asos_csv(payload: str) -> list[CanonicalHour]:
    reader = DictReader(StringIO(payload))
    rows = []
    for raw in reader:
        valid = raw.get("valid")
        if not valid:
            continue
        observed_at = datetime.fromisoformat(valid.replace(" ", "T")).replace(tzinfo=timezone.utc)
        extras = {key: value for key, value in raw.items() if key not in CANONICAL_KEYS}
        rows.append(
            CanonicalHour(
                observed_at=observed_at,
                wind_speed_kt=num(raw.get("sknt")),
                wind_gust_kt=num(raw.get("gust")),
                wind_direction_deg=num(raw.get("drct")),
                temperature_c=f_to_c(num(raw.get("tmpf"))),
                pressure_hpa=num(raw.get("mslp")),
                precipitation_mm=inch_to_mm(num(raw.get("p01i"))),
                extras=extras,
                raw=raw,
            )
        )
    return rows
