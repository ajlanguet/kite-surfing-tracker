from django.test import TestCase

from spots.models import Spot
from spots.services import get_or_create_spot_from_place, unique_slug, untrack_spot
from weather.models import ForecastPoint, WeatherSource


class SlugTests(TestCase):
    def test_slugify_name(self):
        self.assertEqual(unique_slug("Tarifa", 36.01, -5.6), "tarifa")


class UntrackTests(TestCase):
    def test_untrack_deletes_weather_and_search_spot(self):
        spot = Spot.objects.create(
            name="Test Beach",
            slug="test-beach",
            latitude="10.000000",
            longitude="20.000000",
            timezone="UTC",
            created_from_search=True,
        )
        source = WeatherSource.objects.create(slug="test-src", name="Test", kind="forecast")
        ForecastPoint.objects.create(
            spot=spot,
            source=source,
            issued_at="2026-09-17T00:00:00Z",
            valid_at="2026-09-17T06:00:00Z",
            lead_hours=6,
            wind_speed_kt=18,
            wind_direction_deg=240,
        )
        from spots.models import SpotWatch

        SpotWatch.objects.create(spot=spot)
        result = untrack_spot(spot)
        self.assertTrue(result["deleted_spot"])
        self.assertFalse(Spot.objects.filter(slug="test-beach").exists())
        self.assertEqual(ForecastPoint.objects.count(), 0)


class CreateSpotTests(TestCase):
    def setUp(self):
        self.hatteras = Spot.objects.create(
            name="Cape Hatteras",
            slug="cape-hatteras",
            latitude="35.222600",
            longitude="-75.529000",
            timezone="America/New_York",
        )

    def test_same_name_reuses_nearby_catalog_spot(self):
        spot = get_or_create_spot_from_place(
            {
                "name": "Cape Hatteras",
                "latitude": 35.22,
                "longitude": -75.53,
                "timezone": "America/New_York",
            }
        )
        self.assertEqual(spot.slug, "cape-hatteras")

    def test_custom_name_creates_a_new_spot(self):
        spot = get_or_create_spot_from_place(
            {
                "name": "Secret launch",
                "latitude": 35.22,
                "longitude": -75.53,
                "timezone": "America/New_York",
            }
        )
        self.assertEqual(spot.name, "Secret launch")
        self.assertNotEqual(spot.slug, "cape-hatteras")

    def test_region_box_creates_its_own_spot(self):
        spot = get_or_create_spot_from_place(
            {
                "name": "Cape Hatteras",
                "latitude": 35.22,
                "longitude": -75.53,
                "timezone": "America/New_York",
                "region_north": 35.3,
                "region_south": 35.1,
                "region_east": -75.4,
                "region_west": -75.6,
            }
        )
        self.assertNotEqual(spot.slug, "cape-hatteras")
        self.assertEqual(float(spot.region_north), 35.3)

    def test_polygon_is_stored_and_does_not_reuse_nearby(self):
        polygon = [
            {"lat": 35.3, "lng": -75.6},
            {"lat": 35.28, "lng": -75.4},
            {"lat": 35.1, "lng": -75.45},
            {"lat": 35.12, "lng": -75.62},
        ]
        spot = get_or_create_spot_from_place(
            {
                "name": "Cape Hatteras",
                "latitude": 35.22,
                "longitude": -75.53,
                "timezone": "America/New_York",
                "region_polygon": polygon,
            }
        )
        self.assertNotEqual(spot.slug, "cape-hatteras")
        self.assertEqual(len(spot.region_polygon), 4)
        self.assertEqual(float(spot.region_north), 35.3)
        self.assertEqual(float(spot.region_west), -75.62)
