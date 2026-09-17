from .open_meteo import OpenMeteoArchiveClient, OpenMeteoForecastClient

# Register a client here when you finish writing it.
# ingest_weather looks up sources by this dictionary key.
FORECAST_CLIENTS = {
    "open-meteo": OpenMeteoForecastClient(
        slug="open-meteo-best-match",
        name="Open-Meteo Best Match",
    ),
    # Copy the line above and pass model="gfs_seamless" or model="ecmwf_ifs"
    # once you want a second forecast source.
}

HISTORY_CLIENTS = {
    "open-meteo-era5": OpenMeteoArchiveClient(),
}
