from django.core.management.base import BaseCommand

from spots.models import Spot, SpotWatch

STARTER_SPOTS = [
    {
        "name": "Cape Hatteras",
        "slug": "cape-hatteras",
        "latitude": "35.222600",
        "longitude": "-75.529000",
        "timezone": "America/New_York",
        "min_rideable_kt": 14,
        "max_rideable_kt": 30,
        "window_start_deg": 180,
        "window_end_deg": 270,
        "tide_preference": "incoming",
        "notes": "SW through W is the classic sideshore/onshore window on the sound and ocean sides.",
    },
    {
        "name": "Hood River",
        "slug": "hood-river",
        "latitude": "45.714000",
        "longitude": "-121.515000",
        "timezone": "America/Los_Angeles",
        "min_rideable_kt": 15,
        "max_rideable_kt": 35,
        "window_start_deg": 240,
        "window_end_deg": 300,
        "notes": "Gorge westerly thermal. Fill-in is often late morning in summer.",
    },
    {
        "name": "Cabarete",
        "slug": "cabarete",
        "latitude": "19.762000",
        "longitude": "-70.414000",
        "timezone": "America/Santo_Domingo",
        "min_rideable_kt": 14,
        "max_rideable_kt": 28,
        "window_start_deg": 50,
        "window_end_deg": 120,
        "notes": "Typical easterly trade. Afternoon thermal often adds a few knots.",
    },
]


class Command(BaseCommand):
    help = "Create a few real kite spots so you have something to ingest against."

    def handle(self, *args, **options):
        created = 0
        for payload in STARTER_SPOTS:
            spot, was_created = Spot.objects.get_or_create(slug=payload["slug"], defaults=payload)
            if was_created:
                created += 1
                self.stdout.write(f"created {payload['slug']}")
            else:
                self.stdout.write(f"already exists {payload['slug']}")
            SpotWatch.objects.get_or_create(spot=spot)
        self.stdout.write(self.style.SUCCESS(f"done. {created} new spots."))
