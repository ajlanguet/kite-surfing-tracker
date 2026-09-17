from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView

from spots.models import Spot

from .models import DailyWindSummary, ForecastPoint, Observation
from .serializers import DailyWindSummarySerializer, ForecastPointSerializer, ObservationSerializer


class SpotScopedMixin:
    slug_kwarg = "slug"

    def get_spot(self):
        return get_object_or_404(Spot, slug=self.kwargs[self.slug_kwarg])


class ObservationListView(SpotScopedMixin, ListAPIView):
    serializer_class = ObservationSerializer

    def get_queryset(self):
        return Observation.objects.filter(spot=self.get_spot()).select_related("source", "station")


class ForecastListView(SpotScopedMixin, ListAPIView):
    serializer_class = ForecastPointSerializer

    def get_queryset(self):
        return ForecastPoint.objects.filter(spot=self.get_spot()).select_related("source")


class SummaryListView(SpotScopedMixin, ListAPIView):
    serializer_class = DailyWindSummarySerializer

    def get_queryset(self):
        return DailyWindSummary.objects.filter(spot=self.get_spot()).select_related("source")
