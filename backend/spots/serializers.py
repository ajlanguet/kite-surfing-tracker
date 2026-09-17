from rest_framework import serializers

from .models import Spot


class SpotSerializer(serializers.ModelSerializer):
    is_tracked = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    last_ingested_at = serializers.SerializerMethodField()

    class Meta:
        model = Spot
        fields = [
            "id",
            "name",
            "slug",
            "latitude",
            "longitude",
            "timezone",
            "min_rideable_kt",
            "max_rideable_kt",
            "window_start_deg",
            "window_end_deg",
            "tide_preference",
            "notes",
            "created_from_search",
            "is_tracked",
            "is_favorite",
            "last_ingested_at",
            "region_north",
            "region_south",
            "region_east",
            "region_west",
            "region_polygon",
        ]

    def get_is_tracked(self, obj):
        return hasattr(obj, "watch")

    def get_is_favorite(self, obj):
        watch = getattr(obj, "watch", None)
        return bool(watch and watch.is_favorite)

    def get_last_ingested_at(self, obj):
        watch = getattr(obj, "watch", None)
        if not watch or not watch.last_ingested_at:
            return None
        return watch.last_ingested_at.isoformat()
