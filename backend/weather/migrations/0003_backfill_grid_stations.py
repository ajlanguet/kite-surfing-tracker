from django.db import migrations


def backfill_grid_stations(apps, schema_editor):
    Spot = apps.get_model("spots", "Spot")
    Station = apps.get_model("weather", "Station")
    SpotStation = apps.get_model("weather", "SpotStation")
    Observation = apps.get_model("weather", "Observation")

    for spot in Spot.objects.all():
        station, _created = Station.objects.get_or_create(
            network="grid",
            external_id=spot.slug,
            defaults={
                "name": f"Model grid at {spot.name}",
                "kind": "grid",
                "latitude": spot.latitude,
                "longitude": spot.longitude,
                "timezone": spot.timezone,
            },
        )
        SpotStation.objects.get_or_create(
            spot=spot,
            station=station,
            defaults={"distance_km": 0, "is_preferred": False},
        )
        Observation.objects.filter(spot=spot, station__isnull=True).update(station=station)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("weather", "0002_spotstation_station_and_more"),
    ]

    operations = [
        migrations.RunPython(backfill_grid_stations, noop),
    ]
