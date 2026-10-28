from django.conf import settings
from django.db import models
from config.storage import VercelBlobStorage

from wildlife.models import Species


class Identification(models.Model):
    """A signed-in user's submitted wildlife photo and model version."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wildlife_identifications",
    )
    image = models.ImageField(
        upload_to="identifications/%Y/%m/",
        storage=VercelBlobStorage(access="private"),
        max_length=500,
    )
    model_name = models.CharField(max_length=100, default="SpeciesNet 4.0.3a")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Identification {self.pk} by {self.user}"


class IdentificationResult(models.Model):
    """One ranked candidate returned for an uploaded photo."""

    identification = models.ForeignKey(
        Identification,
        on_delete=models.CASCADE,
        related_name="results",
    )
    species = models.ForeignKey(
        Species,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="identification_results",
    )
    label = models.CharField(max_length=200)
    score = models.FloatField()
    rank = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["rank"]
        constraints = [
            models.UniqueConstraint(
                fields=["identification", "rank"],
                name="unique_identification_result_rank",
            )
        ]

    def __str__(self):
        return f"{self.rank}. {self.label} ({self.score:.3f})"
