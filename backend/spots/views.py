import json

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Spot
from .serializers import SpotSerializer
from .services import (
    describe_map_point,
    get_or_create_spot_from_place,
    search_spots_and_places,
    set_favorite,
    track_spot,
    untrack_spot,
)


class SpotListView(ListAPIView):
    """Home list is the watchlist. Pass ?all=1 to see catalog spots too."""

    serializer_class = SpotSerializer

    def get_queryset(self):
        qs = Spot.objects.select_related("watch")
        if self.request.query_params.get("all") == "1":
            return qs
        return qs.filter(watch__isnull=False).order_by("-watch__is_favorite", "name")


class SpotDetailView(RetrieveAPIView):
    queryset = Spot.objects.select_related("watch")
    serializer_class = SpotSerializer
    lookup_field = "slug"


class SpotFromPointView(APIView):
    def get(self, request):
        try:
            latitude = float(request.query_params["latitude"])
            longitude = float(request.query_params["longitude"])
        except (KeyError, TypeError, ValueError):
            return Response({"detail": "latitude and longitude are required."}, status=400)
        bounds = {}
        for key in ("region_north", "region_south", "region_east", "region_west"):
            raw = request.query_params.get(key)
            if raw not in (None, ""):
                bounds[key] = float(raw)
        raw_polygon = request.query_params.get("region_polygon")
        if raw_polygon:
            try:
                bounds["region_polygon"] = json.loads(raw_polygon)
            except json.JSONDecodeError:
                return Response({"detail": "region_polygon must be JSON."}, status=400)
        payload = describe_map_point(latitude, longitude, bounds or None)
        return Response(
            {
                "place": payload["place"],
                "existing_spot": SpotSerializer(payload["existing_spot"]).data
                if payload["existing_spot"]
                else None,
            }
        )


class SpotSearchView(APIView):
    def get(self, request):
        query = request.query_params.get("q", "")
        payload = search_spots_and_places(query)
        return Response(
            {
                "spots": SpotSerializer(payload["spots"], many=True).data,
                "suggestions": payload["suggestions"],
            }
        )


class SpotTrackView(APIView):
    def post(self, request):
        slug = request.data.get("slug")
        if slug:
            spot = get_object_or_404(Spot, slug=slug)
        else:
            required = ("name", "latitude", "longitude")
            if any(key not in request.data for key in required):
                return Response({"detail": "Pass slug or name/latitude/longitude."}, status=400)
            spot = get_or_create_spot_from_place(request.data)

        result = track_spot(
            spot,
            ingest_history_days=int(request.data.get("history_days") or 0),
            favorite=bool(request.data.get("favorite")),
        )
        return Response(
            {
                "spot": SpotSerializer(result["spot"]).data,
                "forecast_rows": result["forecast_rows"],
                "history_rows": result["history_rows"],
                "outlook": result["outlook"],
            }
        )


class SpotUntrackView(APIView):
    def post(self, request, slug):
        spot = get_object_or_404(Spot, slug=slug)
        result = untrack_spot(spot)
        return Response({"ok": True, **result})


class SpotFavoriteView(APIView):
    def post(self, request, slug):
        spot = get_object_or_404(Spot, slug=slug)
        is_favorite = request.data.get("is_favorite", True)
        try:
            watch = set_favorite(spot, bool(is_favorite))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response({"slug": spot.slug, "is_favorite": watch.is_favorite})
