from django.urls import path

from .views import (
    SpotDetailView,
    SpotFavoriteView,
    SpotFromPointView,
    SpotListView,
    SpotSearchView,
    SpotTrackView,
    SpotUntrackView,
)

urlpatterns = [
    path("", SpotListView.as_view(), name="spot-list"),
    path("search/", SpotSearchView.as_view(), name="spot-search"),
    path("from-point/", SpotFromPointView.as_view(), name="spot-from-point"),
    path("track/", SpotTrackView.as_view(), name="spot-track"),
    path("<slug:slug>/", SpotDetailView.as_view(), name="spot-detail"),
    path("<slug:slug>/untrack/", SpotUntrackView.as_view(), name="spot-untrack"),
    path("<slug:slug>/favorite/", SpotFavoriteView.as_view(), name="spot-favorite"),
]
