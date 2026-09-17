"""
NOAA National Data Buoy Center — real anemometers on the water.

Discovery already lives in weather/clients/catalogs.py (nearby_ndbc).
Hourly ingest is the remaining adapter:

1. Realtime: https://www.ndbc.noaa.gov/data/realtime2/{station}.txt
2. Historical: https://www.ndbc.noaa.gov/data/historical/stdmet/{station}h{year}.txt.gz
3. Parse into CanonicalHour (weather/schema.py). Convert WSPD from m/s with mps_to_kt.
4. Keep extra columns (WVHT, DPD, APD, MWD, WTMP) in extras or wave_* fields.
5. Call persist_hours() from weather/services.py.

Do not fetch NOAA from a view. This file should only fetch + parse.
"""

from weather.schema import CanonicalHour, mps_to_kt


def fetch_realtime(station_id: str) -> str:
    raise NotImplementedError("Fetch realtime2/{station}.txt and return the text.")


def parse_realtime(payload: str) -> list[CanonicalHour]:
    raise NotImplementedError("Map WDIR/WSPD/GST/WVHT onto CanonicalHour; extras keep the rest.")
