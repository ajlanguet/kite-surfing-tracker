"""
Every weather API you add should look like this from the rest of the app.

fetch_* returns the vendor JSON.
parse_* turns that JSON into a list of dicts with OUR field names.
The ingest service never cares which vendor produced the dicts.
"""

from abc import ABC, abstractmethod


class WeatherClient(ABC):
    source_slug = ""
    source_name = ""
    source_kind = ""
    homepage = ""

    @abstractmethod
    def fetch_forecast(self, latitude, longitude):
        raise NotImplementedError

    @abstractmethod
    def parse_forecast(self, payload, issued_at):
        raise NotImplementedError

    def fetch_history(self, latitude, longitude, start_date, end_date):
        raise NotImplementedError("This client does not support history yet.")

    def parse_history(self, payload):
        raise NotImplementedError("This client does not support history yet.")
