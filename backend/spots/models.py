from django.db import models


class Spot(models.Model):
    """
    A kite launch with a geographic wind window.

    A spot can exist in the catalog without being tracked. Weather is
    stored only while a SpotWatch row exists.
    """

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timezone = models.CharField(
        max_length=64,
        help_text="IANA timezone, e.g. America/New_York. Used to compute local fill-in hour.",
    )
    min_rideable_kt = models.PositiveSmallIntegerField(default=12)
    max_rideable_kt = models.PositiveSmallIntegerField(default=30)
    window_start_deg = models.PositiveSmallIntegerField(
        default=0,
        help_text="Clockwise start of the rideable wind sector, 0-359. 0-359 means all directions.",
    )
    window_end_deg = models.PositiveSmallIntegerField(
        default=359,
        help_text="Clockwise end of the rideable wind sector, 0-359.",
    )
    notes = models.TextField(blank=True)
    created_from_search = models.BooleanField(default=False)
    region_north = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    region_south = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    region_east = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    region_west = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    region_polygon = models.JSONField(
        null=True,
        blank=True,
        help_text="List of {lat, lng} vertices. Weather is still scored at the centroid.",
    )
    tide_preference = models.CharField(
        max_length=16,
        default="any",
        choices=[
            ("any", "Any tide"),
            ("incoming", "Incoming / flooding"),
            ("outgoing", "Outgoing / ebbing"),
            ("high", "High"),
            ("low", "Low"),
        ],
        help_text="Ocean spots often care about tide phase as much as wind.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class SpotWatch(models.Model):
    """
    Permission to store weather for this launch.

    Search can look at a place. Tracking is what writes rows. Untracking
    deletes stored weather. Favorite is only a pin on the home list.
    """

    spot = models.OneToOneField(Spot, on_delete=models.CASCADE, related_name="watch")
    is_favorite = models.BooleanField(default=False)
    tracked_at = models.DateTimeField(auto_now_add=True)
    last_ingested_at = models.DateTimeField(null=True, blank=True)
    is_paused = models.BooleanField(
        default=False,
        help_text="Stop polling without deleting the archive.",
    )

    class Meta:
        ordering = ["-is_favorite", "spot__name"]

    def __str__(self):
        return f"watch:{self.spot.slug}"
