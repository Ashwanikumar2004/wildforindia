import uuid

from django.db import models

from .national_park import NationalPark


class ParkImage(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    park = models.ForeignKey(
        NationalPark,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="parks/images/",
        max_length=500,
    )

    caption = models.CharField(
        max_length=255,
        blank=True,
    )

    photographer = models.CharField(
        max_length=150,
        blank=True,
    )

    source = models.URLField(
        blank=True,
    )

    is_primary = models.BooleanField(
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
            "-is_primary",
        ]

        verbose_name = "Park Image"

        verbose_name_plural = "Park Images"

    def __str__(self):

        return f"{self.park.name} Image"
