from django.db import models


class ConservationStatus(models.Model):

    STATUS_CODES = [
        ("LC", "Least Concern"),
        ("NT", "Near Threatened"),
        ("VU", "Vulnerable"),
        ("EN", "Endangered"),
        ("CR", "Critically Endangered"),
        ("EW", "Extinct in the Wild"),
        ("EX", "Extinct"),
    ]

    name = models.CharField(
        max_length=100,
        unique=True
    )

    code = models.CharField(
        max_length=2,
        choices=STATUS_CODES,
        unique=True
    )

    badge_color = models.CharField(
        max_length=20,
        default="#28a745"
    )

    priority = models.PositiveIntegerField(
        default=1
    )

    icon = models.ImageField(
        upload_to="status/",
        blank=True,
        null=True,
        max_length=500,
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["priority"]

    def __str__(self):
        return self.name
