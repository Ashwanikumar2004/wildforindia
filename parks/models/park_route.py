import uuid

from django.db import models

from .national_park import NationalPark


class ParkRoute(models.Model):

    TRANSPORT_CHOICES = [
        ("Car", "Car"),
        ("Bus", "Bus"),
        ("Train", "Train"),
        ("Flight", "Flight"),
        ("Mixed", "Mixed"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    park = models.ForeignKey(
        NationalPark,
        on_delete=models.CASCADE,
        related_name="routes",
    )

    starting_city = models.CharField(
        max_length=150,
    )

    transport_mode = models.CharField(
        max_length=20,
        choices=TRANSPORT_CHOICES,
        default="Car",
    )

    distance = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        help_text="Distance in kilometres",
    )

    estimated_time = models.CharField(
        max_length=50,
        help_text="Example: 5 Hours 30 Minutes",
    )

    google_maps_link = models.URLField(
        blank=True,
    )

    route_description = models.TextField(
        blank=True,
    )

    is_best_route = models.BooleanField(
        default=False,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "display_order",
            "starting_city",
        ]

        verbose_name = "Park Route"

        verbose_name_plural = "Park Routes"

    def __str__(self):

        return f"{self.starting_city} → {self.park.name}"