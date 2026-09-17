from django.test import SimpleTestCase

from patterns.wind import (
    WindWindow,
    circular_mean_deg,
    direction_in_window,
    fill_in_hour,
    hourly_rideable_profile,
    is_rideable,
)


WINDOW = WindWindow(min_kt=14, max_kt=30, start_deg=180, end_deg=270)


class DirectionWindowTests(SimpleTestCase):
    def test_plain_sector(self):
        self.assertTrue(direction_in_window(200, 180, 270))
        self.assertFalse(direction_in_window(90, 180, 270))

    def test_wraps_across_north(self):
        self.assertTrue(direction_in_window(350, 330, 20))
        self.assertTrue(direction_in_window(10, 330, 20))
        self.assertFalse(direction_in_window(180, 330, 20))


class RideableTests(SimpleTestCase):
    def test_needs_both_speed_and_direction(self):
        self.assertTrue(is_rideable(18, 220, WINDOW))
        self.assertFalse(is_rideable(8, 220, WINDOW))
        self.assertFalse(is_rideable(18, 40, WINDOW))
        self.assertFalse(is_rideable(None, 220, WINDOW))


class FillInTests(SimpleTestCase):
    def test_first_held_window(self):
        rows = [
            {"local_hour": 9, "wind_speed_kt": 8, "wind_direction_deg": 220},
            {"local_hour": 10, "wind_speed_kt": 12, "wind_direction_deg": 220},
            {"local_hour": 11, "wind_speed_kt": 16, "wind_direction_deg": 220},
            {"local_hour": 12, "wind_speed_kt": 18, "wind_direction_deg": 230},
            {"local_hour": 13, "wind_speed_kt": 20, "wind_direction_deg": 240},
        ]
        self.assertEqual(fill_in_hour(rows, WINDOW, hold_hours=3), 11)

    def test_overnight_wind_is_not_fill_in(self):
        rows = [
            {"local_hour": hour, "wind_speed_kt": 18, "wind_direction_deg": 220}
            for hour in range(0, 24)
        ]
        self.assertIsNone(fill_in_hour(rows, WINDOW))

    def test_never_holds(self):
        rows = [
            {"local_hour": hour, "wind_speed_kt": 10, "wind_direction_deg": 220}
            for hour in range(8, 18)
        ]
        self.assertIsNone(fill_in_hour(rows, WINDOW))


class CircularMeanTests(SimpleTestCase):
    def test_around_north(self):
        mean = circular_mean_deg([350, 10])
        self.assertTrue(mean < 10 or mean > 350)


class ProfileTests(SimpleTestCase):
    def test_probability_by_hour(self):
        rows = [
            {"local_hour": 10, "wind_speed_kt": 8, "wind_direction_deg": 220},
            {"local_hour": 10, "wind_speed_kt": 18, "wind_direction_deg": 220},
            {"local_hour": 14, "wind_speed_kt": 20, "wind_direction_deg": 220},
            {"local_hour": 14, "wind_speed_kt": 22, "wind_direction_deg": 230},
        ]
        profile = hourly_rideable_profile(rows, WINDOW)
        self.assertEqual(profile[10], 0.5)
        self.assertEqual(profile[14], 1.0)


class TideTests(SimpleTestCase):
    def test_rising_is_incoming(self):
        from patterns.tide import tide_matches, tide_phase

        self.assertEqual(tide_phase(0.4, 0.7, 0.2, 1.0), "incoming")
        self.assertEqual(tide_phase(0.2, 0.95, 0.2, 1.0), "high")
        self.assertTrue(tide_matches("incoming", "incoming"))
        self.assertTrue(tide_matches("incoming", "any"))
        self.assertFalse(tide_matches("outgoing", "incoming"))
