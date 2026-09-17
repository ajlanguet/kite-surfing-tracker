from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError

from spots.models import Spot
from weather.clients import FORECAST_CLIENTS, HISTORY_CLIENTS
from weather.services import ingest_forecast, ingest_history, ingest_linked_stations


class Command(BaseCommand):
    help = "Pull forecast or historical wind into the database for one or all spots."

    def add_arguments(self, parser):
        parser.add_argument("--mode", choices=["forecast", "history", "stations"], required=True)
        parser.add_argument("--spot", help="Spot slug. Omit to run every spot.")
        parser.add_argument("--source", help="Client key from weather/clients/__init__.py")
        parser.add_argument("--days", type=int, default=30, help="History window ending yesterday.")

    def handle(self, *args, **options):
        spots = Spot.objects.filter(watch__isnull=False)
        if options["spot"]:
            spots = Spot.objects.filter(slug=options["spot"])
        if not spots.exists():
            raise CommandError(
                "No tracked spots. Search and track a place in the app, or pass --spot <slug>."
            )

        # ERA5 is published with a multi-day delay. Asking for yesterday 404s or returns nulls.
        end_date = date.today() - timedelta(days=6)
        start_date = end_date - timedelta(days=options["days"] - 1)
        mode = options["mode"]

        if mode == "stations":
            for spot in spots:
                counts = ingest_linked_stations(spot, start_date, end_date)
                self.stdout.write(f"{spot.slug} stations: {counts}")
            return

        source = options["source"] or ("open-meteo" if mode == "forecast" else "open-meteo-era5")
        registry = FORECAST_CLIENTS if mode == "forecast" else HISTORY_CLIENTS
        if source not in registry:
            raise CommandError(f"Unknown source '{source}'. Known: {', '.join(registry)}")

        for spot in spots:
            if mode == "forecast":
                saved = ingest_forecast(spot, client_key=source)
            else:
                saved = ingest_history(spot, start_date, end_date, client_key=source)
            self.stdout.write(f"{spot.slug} {mode}/{source}: {saved} new rows")
