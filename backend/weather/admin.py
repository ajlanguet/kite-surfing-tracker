from django.contrib import admin

from .models import DailyWindSummary, ForecastPoint, Observation, SpotStation, Station, WeatherSource


@admin.register(WeatherSource)
class WeatherSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "kind")


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name", "network", "external_id", "kind", "icao", "country")
    list_filter = ("network", "kind")
    search_fields = ("name", "external_id", "icao")


@admin.register(SpotStation)
class SpotStationAdmin(admin.ModelAdmin):
    list_display = ("spot", "station", "distance_km", "is_preferred")
    list_filter = ("spot",)


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ("spot", "station", "source", "observed_at", "wind_speed_kt", "wind_direction_deg")
    list_filter = ("source", "spot", "station__network")


@admin.register(ForecastPoint)
class ForecastPointAdmin(admin.ModelAdmin):
    list_display = ("spot", "source", "issued_at", "valid_at", "lead_hours", "wind_speed_kt")
    list_filter = ("source", "spot")


@admin.register(DailyWindSummary)
class DailyWindSummaryAdmin(admin.ModelAdmin):
    list_display = ("spot", "source", "local_date", "rideable_hours", "fill_in_hour", "mean_wind_kt")
    list_filter = ("source", "spot")
