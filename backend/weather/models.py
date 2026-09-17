from django.db import models

from spots.models import Spot


class Station(models.Model):
    """
    A real sensor (airport, buoy, WMO site) or a virtual grid point.

    Observations happen at stations. Spots are launches. Link them with
    SpotStation so one buoy can serve two nearby beaches without duplicating hours.
    """

    class Kind(models.TextChoices):
        AIRPORT = "airport", "Airport / METAR"
        BUOY = "buoy", "Buoy"
        LAND = "land", "Land station"
        GRID = "grid", "Model grid point"

    network = models.SlugField(help_text="meteostat, ndbc, grid, ...")
    external_id = models.CharField(max_length=64)
    name = models.CharField(max_length=160)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    elevation_m = models.DecimalField(max_digits=7, decimal_places=1, null=True, blank=True)
    timezone = models.CharField(max_length=64, blank=True)
    country = models.CharField(max_length=8, blank=True)
    icao = models.CharField(max_length=8, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["network", "external_id"], name="unique_station")
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.network}:{self.external_id} {self.name}"


class SpotStation(models.Model):
    """Nearby sensor assigned to a launch, with distance for later weighting."""

    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name="station_links")
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="spot_links")
    distance_km = models.DecimalField(max_digits=7, decimal_places=2)
    is_preferred = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["spot", "station"], name="unique_spot_station")
        ]
        ordering = ["distance_km"]

    def __str__(self):
        return f"{self.spot.slug} ← {self.station.external_id} ({self.distance_km} km)"


class WeatherSource(models.Model):
    """
    One row per API (or per model inside an API).

    GFS and ECMWF both come from Open-Meteo, but they are different
    sources. Keeping them separate is how you later measure which model
    is honest at a given spot.
    """

    class Kind(models.TextChoices):
        FORECAST = "forecast", "Forecast"
        OBSERVATION = "observation", "Observation"
        REANALYSIS = "reanalysis", "Reanalysis"

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    homepage = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Observation(models.Model):
    """
    What the atmosphere actually did (or the best proxy we have).

    ERA5 reanalysis is not a beach anemometer, but it is the most
    practical "truth" layer until you add buoys or a personal weather
    station. Do not store forecasts in this table.
    """

    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name="observations")
    station = models.ForeignKey(
        Station,
        on_delete=models.PROTECT,
        related_name="observations",
        null=True,
        blank=True,
        help_text="Sensor that produced this hour. Grid ingest uses a virtual station at the spot.",
    )
    source = models.ForeignKey(WeatherSource, on_delete=models.PROTECT, related_name="observations")
    observed_at = models.DateTimeField(db_index=True)
    wind_speed_kt = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    wind_gust_kt = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    wind_direction_deg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    temperature_c = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pressure_hpa = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    precipitation_mm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    wave_height_m = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wave_period_s = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wave_direction_deg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    sea_level_m = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Sea surface height including tide, metres above global mean sea level.",
    )
    extras = models.JSONField(
        default=dict,
        blank=True,
        help_text="Vendor fields that are not in the canonical kite columns.",
    )
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["observed_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["spot", "station", "source", "observed_at"],
                name="unique_observation_per_station_source",
            )
        ]

    def __str__(self):
        return f"{self.spot.slug} @ {self.observed_at.isoformat()}"


class ForecastPoint(models.Model):
    """
    What a model claimed would happen.

    issued_at  = when the model run was published
    valid_at   = the hour being predicted
    lead_hours = how far ahead that prediction was

    You need all three to answer: "when GFS is 24 hours out, does it
    overstate afternoon wind at this beach?"
    """

    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name="forecasts")
    source = models.ForeignKey(WeatherSource, on_delete=models.PROTECT, related_name="forecasts")
    issued_at = models.DateTimeField(db_index=True)
    valid_at = models.DateTimeField(db_index=True)
    lead_hours = models.PositiveSmallIntegerField()
    wind_speed_kt = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    wind_gust_kt = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    wind_direction_deg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    temperature_c = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pressure_hpa = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    precipitation_mm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    wave_height_m = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wave_period_s = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wave_direction_deg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    sea_level_m = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Sea surface height including tide, metres above global mean sea level.",
    )
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["valid_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["spot", "source", "issued_at", "valid_at"],
                name="unique_forecast_point",
            )
        ]

    def __str__(self):
        return f"{self.source.slug} {self.spot.slug} valid {self.valid_at.isoformat()}"


class DailyWindSummary(models.Model):
    """
    One row per spot/source/local-date. This is the 'day by day' layer.

    Compute it from Observation rows. Do not fetch it from an API.
    """

    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name="summaries")
    source = models.ForeignKey(WeatherSource, on_delete=models.PROTECT, related_name="summaries")
    local_date = models.DateField(db_index=True)
    rideable_hours = models.PositiveSmallIntegerField(default=0)
    fill_in_hour = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Local hour (0-23) when wind first held in the rideable window.",
    )
    mean_wind_kt = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    max_gust_kt = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    dominant_direction_deg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["-local_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["spot", "source", "local_date"],
                name="unique_daily_summary",
            )
        ]

    def __str__(self):
        return f"{self.spot.slug} {self.local_date}"
