import uuid

from django.db import models

from .species import Species
from parks.models import State


class SpeciesDistribution(models.Model):

    POPULATION_STATUS = [
        ("Common", "Common"),
        ("Uncommon", "Uncommon"),
        ("Rare", "Rare"),
        ("Declining", "Declining"),
        ("Increasing", "Increasing"),
        ("Unknown", "Unknown"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    species = models.ForeignKey(
        Species,
        on_delete=models.CASCADE,
        related_name="distributions"
    )

    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name="species_distributions"
    )

    is_native = models.BooleanField(
        default=True
    )

    population_status = models.CharField(
        max_length=20,
        choices=POPULATION_STATUS,
        default="Unknown"
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["species", "state"]

        constraints = [
            models.UniqueConstraint(
                fields=["species", "state"],
                name="unique_species_state"
            )
        ]

    def __str__(self):
        return f"{self.species.common_name} - {self.state.name}"