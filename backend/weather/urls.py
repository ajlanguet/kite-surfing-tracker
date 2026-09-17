from django.urls import path

from .views import ForecastListView, ObservationListView, SummaryListView

urlpatterns = [
    path("<slug:slug>/observations/", ObservationListView.as_view(), name="spot-observations"),
    path("<slug:slug>/forecasts/", ForecastListView.as_view(), name="spot-forecasts"),
    path("<slug:slug>/summaries/", SummaryListView.as_view(), name="spot-summaries"),
]
