from django.urls import path

from .views import SpotOutlookView, SpotPatternView

urlpatterns = [
    path("<slug:slug>/outlook/", SpotOutlookView.as_view(), name="spot-outlook"),
    path("<slug:slug>/", SpotPatternView.as_view(), name="spot-pattern"),
]
