from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/spots/", include("spots.urls")),
    path("api/weather/", include("weather.urls")),
    path("api/patterns/", include("patterns.urls")),
]
