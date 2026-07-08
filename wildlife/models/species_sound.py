import uuid

from django.db import models

from .species import Species


class SpeciesSound(models.Model):

    SOUND_TYPES = [
        ("Roar", "Roar"),
        ("Call", "Call"),
        ("Song", "Song"),
        ("Growl", "Growl"),
        ("Alarm", "Alarm"),
        ("Communication", "Communication"),
        ("Other", "Other"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    species = models.ForeignKey(
        Species,
        on_delete=models.CASCADE,
        related_name="sounds"
    )

    title = models.CharField(
        max_length=100
    )

    sound = models.FileField(
        upload_to="species/sounds/"
    )

    sound_type = models.CharField(
        max_length=30,
        choices=SOUND_TYPES,
        default="Other"
    )

    duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Duration in seconds"
    )

    recorded_by = models.CharField(
        max_length=150,
        blank=True
    )

    source = models.URLField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "Species Sound"
        verbose_name_plural = "Species Sounds"

    def __str__(self):
        return f"{self.species.common_name} - {self.title}"