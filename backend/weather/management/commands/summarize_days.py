from django.core.management.base import BaseCommand

from spots.models import Spot
from weather.models import Observation, WeatherSource
from patterns.summarize import summarize_spot_source


class Command(BaseCommand):
    help = "Rebuild daily wind summaries from stored observations."

    def add_arguments(self, parser):
        parser.add_argument("--spot", help="Spot slug. Omit to run every spot.")

    def handle(self, *args, **options):
        spots = Spot.objects.filter(watch__isnull=False)
        if options["spot"]:
            spots = Spot.objects.filter(slug=options["spot"])

        for spot in spots:
            source_ids = (
                Observation.objects.filter(spot=spot).values_list("source_id", flat=True).distinct()
            )
            for source in WeatherSource.objects.filter(id__in=source_ids):
                count = summarize_spot_source(spot, source)
                self.stdout.write(f"{spot.slug}/{source.slug}: {count} day summaries")
