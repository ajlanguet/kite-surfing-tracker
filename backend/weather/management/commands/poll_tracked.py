from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from spots.models import Spot
from weather.services import poll_tracked_spot


class Command(BaseCommand):
    help = (
        "Grow the Open-Meteo archive for tracked spots: a new forecast snapshot, "
        "marine/tide hours, and the next delayed ERA5 day."
    )

    def add_arguments(self, parser):
        parser.add_argument("--spot", help="Spot slug. Omit to poll every active watch.")
        parser.add_argument("--history-days", type=int, default=1)

    def handle(self, *args, **options):
        spots = Spot.objects.filter(watch__isnull=False, watch__is_paused=False)
        if options["spot"]:
            spots = Spot.objects.filter(slug=options["spot"])
        if not spots.exists():
            raise CommandError("No active tracked spots to poll.")

        for spot in spots:
            counts = poll_tracked_spot(spot, history_days=options["history_days"])
            watch = spot.watch
            watch.last_ingested_at = timezone.now()
            watch.save(update_fields=["last_ingested_at"])
            self.stdout.write(
                f"{spot.slug}: forecast +{counts['forecast_rows']} "
                f"marine +{counts['marine_rows']} history +{counts['history_rows']}"
            )
