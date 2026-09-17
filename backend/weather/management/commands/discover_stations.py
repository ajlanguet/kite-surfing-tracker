from django.core.management.base import BaseCommand, CommandError

from spots.models import Spot
from weather.services import discover_stations_for_spot


class Command(BaseCommand):
    help = "Find nearby METAR/WMO stations and NDBC buoys for each kite spot."

    def add_arguments(self, parser):
        parser.add_argument("--spot", help="Spot slug. Omit to run every spot.")
        parser.add_argument("--radius-km", type=float, default=80)
        parser.add_argument("--limit", type=int, default=8)

    def handle(self, *args, **options):
        spots = Spot.objects.all()
        if options["spot"]:
            spots = spots.filter(slug=options["spot"])
        if not spots.exists():
            raise CommandError("No spots found. Run: python manage.py seed_spots")

        for spot in spots:
            links = discover_stations_for_spot(
                spot,
                radius_km=options["radius_km"],
                limit=options["limit"],
            )
            self.stdout.write(self.style.SUCCESS(f"{spot.slug}: {len(links)} nearby stations"))
            for link in links:
                station = link.station
                self.stdout.write(
                    f"  {link.distance_km} km  {station.network}:{station.external_id}  "
                    f"{station.kind}  {station.name}  {station.icao or ''}"
                )
