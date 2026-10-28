import uuid

from django.db import models

from .species import Species


class SpeciesImage(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    species = models.ForeignKey(
        Species,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="species/images/",
        max_length=500,
    )

    caption = models.CharField(
        max_length=255,
        blank=True
    )

    photographer = models.CharField(
        max_length=150,
        blank=True
    )

    source = models.URLField(
        blank=True
    )

    is_primary = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-is_primary", "caption"]
        verbose_name = "Species Image"
        verbose_name_plural = "Species Images"

    def __str__(self):
        return f"{self.species.common_name} Image"
