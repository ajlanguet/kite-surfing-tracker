from rest_framework import serializers

from .models import DailyWindSummary, ForecastPoint, Observation


class ObservationSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(read_only=True, slug_field="slug")
    station = serializers.SerializerMethodField()

    class Meta:
        model = Observation
        fields = [
            "id",
            "source",
            "station",
            "observed_at",
            "wind_speed_kt",
            "wind_gust_kt",
            "wind_direction_deg",
            "temperature_c",
            "precipitation_mm",
            "wave_height_m",
            "wave_period_s",
            "wave_direction_deg",
        ]

    def get_station(self, obj):
        if not obj.station_id:
            return None
        return f"{obj.station.network}:{obj.station.external_id}"


class ForecastPointSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(read_only=True, slug_field="slug")

    class Meta:
        model = ForecastPoint
        fields = [
            "id",
            "source",
            "issued_at",
            "valid_at",
            "lead_hours",
            "wind_speed_kt",
            "wind_gust_kt",
            "wind_direction_deg",
            "temperature_c",
            "precipitation_mm",
            "wave_height_m",
            "wave_period_s",
            "wave_direction_deg",
        ]


class DailyWindSummarySerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(read_only=True, slug_field="slug")

    class Meta:
        model = DailyWindSummary
        fields = [
            "id",
            "source",
            "local_date",
            "rideable_hours",
            "fill_in_hour",
            "mean_wind_kt",
            "max_gust_kt",
            "dominant_direction_deg",
        ]
