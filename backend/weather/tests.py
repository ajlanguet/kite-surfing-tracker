from datetime import datetime, timezone

from django.test import SimpleTestCase

from weather.clients.iem_asos import icao_to_iem_id, parse_asos_csv
from weather.clients.open_meteo import OpenMeteoForecastClient
from weather.clients.open_meteo_marine import parse_marine
from weather.geo import haversine_km
from weather.schema import f_to_c, mps_to_kt


class OpenMeteoParseTests(SimpleTestCase):
    def test_hourly_arrays_become_rows(self):
        payload = {
            "hourly": {
                "time": ["2026-09-17T12:00", "2026-09-17T13:00"],
                "wind_speed_10m": [16.0, 18.5],
                "wind_gusts_10m": [22.0, 24.0],
                "wind_direction_10m": [240, 250],
                "temperature_2m": [21.0, 21.5],
                "pressure_msl": [1014.0, 1013.0],
                "precipitation": [0, 0],
            }
        }
        issued_at = datetime(2026, 9, 17, 12, 0, tzinfo=timezone.utc)
        client = OpenMeteoForecastClient(slug="test", name="Test")
        rows = client.parse_forecast(payload, issued_at)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["lead_hours"], 0)
        self.assertEqual(rows[1]["lead_hours"], 1)
        self.assertEqual(rows[1]["wind_speed_kt"], 18.5)


class UnitTests(SimpleTestCase):
    def test_conversions(self):
        self.assertAlmostEqual(mps_to_kt(1), 1.94384)
        self.assertAlmostEqual(f_to_c(32), 0)
        self.assertAlmostEqual(haversine_km(35.22, -75.53, 35.23, -75.62), 8.2, delta=1)


class IemParseTests(SimpleTestCase):
    def test_icao_strip(self):
        self.assertEqual(icao_to_iem_id("KHSE"), "HSE")
        self.assertEqual(icao_to_iem_id("MDPP"), "MDPP")

    def test_promotes_wind_and_keeps_extras(self):
        csv = (
            "station,valid,tmpf,drct,sknt,gust,mslp,p01i,metar\n"
            "HSE,2026-09-10 00:51,80.00,170.00,9.00,null,1022.30,0.00,KHSE AUTO\n"
        )
        rows = parse_asos_csv(csv)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].wind_speed_kt, 9.0)
        self.assertAlmostEqual(rows[0].temperature_c, 26.666, places=2)
        self.assertIn("metar", rows[0].extras)


class MarineParseTests(SimpleTestCase):
    def test_sea_level_and_waves(self):
        payload = {
            "hourly": {
                "time": ["2026-09-17T12:00"],
                "wave_height": [1.2],
                "wave_direction": [180],
                "wave_period": [8.0],
                "sea_level_height_msl": [0.45],
                "sea_surface_temperature": [24.0],
            }
        }
        rows = parse_marine(payload)
        self.assertEqual(rows[0].sea_level_m, 0.45)
        self.assertEqual(rows[0].wave_height_m, 1.2)
