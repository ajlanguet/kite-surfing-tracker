"""
Stormglass aggregates several marine models in one response.

Useful later for waves + multi-model wind. Requires an API key.
Docs: https://stormglass.io/

YOUR TURN after Open-Meteo + NOAA are saving rows:
1. Put STORMGLASS_API_KEY in a .env file.
2. GET https://api.stormglass.io/v2/weather/point with params:
   lat, lng, params=windSpeed,windDirection,gust,waveHeight,wavePeriod,waveDirection
3. Parse hours[].windSpeed.noaa vs hours[].windSpeed.sg (their blended value).
4. Store each vendor as its own WeatherSource so you can compare them.
"""

from .base import WeatherClient


class StormglassClient(WeatherClient):
    source_slug = "stormglass"
    source_name = "Stormglass"
    source_kind = "forecast"
    homepage = "https://stormglass.io/"

    def fetch_forecast(self, latitude, longitude):
        raise NotImplementedError("Add the API key and GET /v2/weather/point.")

    def parse_forecast(self, payload, issued_at):
        raise NotImplementedError("Split vendor keys into separate source slugs.")
