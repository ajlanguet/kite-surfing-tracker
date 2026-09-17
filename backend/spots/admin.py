from django.contrib import admin

from .models import Spot, SpotWatch


@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "created_from_search",
        "min_rideable_kt",
        "max_rideable_kt",
        "window_start_deg",
        "window_end_deg",
    )
    prepopulated_fields = {"slug": ("name",)}


@admin.register(SpotWatch)
class SpotWatchAdmin(admin.ModelAdmin):
    list_display = ("spot", "is_favorite", "tracked_at", "last_ingested_at")
