from django.conf import settings
from django.db import models

from wildlife.models import Species


class WildDexEntry(models.Model):
    """A species a user confirmed and added to their wildlife journal."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wilddex_entries",
    )
    species = models.ForeignKey(
        Species,
        on_delete=models.PROTECT,
        related_name="wilddex_entries",
    )
    source_identification = models.ForeignKey(
        "ai_identifier.Identification",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wilddex_entries",
    )
    discovered_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, max_length=3000)
    observed_on = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=150, blank=True, help_text="A park or general area; avoid precise wildlife locations.")

    class Meta:
        ordering = ["-discovered_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "species"],
                name="unique_wilddex_species_per_user",
            )
        ]

    def __str__(self):
        return f"{self.user}: {self.species.common_name}"
