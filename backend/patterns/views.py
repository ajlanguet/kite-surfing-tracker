from collections import defaultdict

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from spots.models import Spot
from weather.models import DailyWindSummary, Observation

from .outlook import forecast_outlook
from .summarize import observation_to_local_row, window_for
from .wind import hourly_rideable_profile, typical_fill_in


class SpotPatternView(APIView):
    """
    Read-only view of the pattern we can already prove from stored hours.

    This is meant to stay boring: probabilities by local hour, and the
    average fill-in time. Fancy scoring comes after this looks right.
    """

    def get(self, request, slug):
        spot = get_object_or_404(Spot, slug=slug)
        window = window_for(spot)
        observations = Observation.objects.filter(spot=spot).order_by("observed_at")
        rows = [observation_to_local_row(obs, spot.timezone) for obs in observations]
        summaries = DailyWindSummary.objects.filter(spot=spot)

        fill_by_month = defaultdict(list)
        for summary in summaries:
            fill_by_month[summary.local_date.month].append(summary.fill_in_hour)

        return Response(
            {
                "spot": spot.slug,
                "sample_hours": len(rows),
                "hourly_rideable_probability": {
                    str(hour): round(prob, 3)
                    for hour, prob in hourly_rideable_profile(rows, window).items()
                },
                "typical_fill_in_hour": typical_fill_in(
                    [summary.fill_in_hour for summary in summaries]
                ),
                "typical_fill_in_by_month": {
                    str(month): typical_fill_in(hours)
                    for month, hours in sorted(fill_by_month.items())
                },
            }
        )


class SpotOutlookView(APIView):
    def get(self, request, slug):
        spot = get_object_or_404(Spot, slug=slug)
        return Response(forecast_outlook(spot))
