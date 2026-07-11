import uuid

from django.db import models
from django.utils.text import slugify


class State(models.Model):

    REGION_CHOICES = [
        ("North", "North"),
        ("South", "South"),
        ("East", "East"),
        ("West", "West"),
        ("Central", "Central"),
        ("North-East", "North-East"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
    )

    code = models.CharField(
        max_length=5,
        unique=True,
    )

    capital = models.CharField(
        max_length=100,
        blank=True,
    )

    region = models.CharField(
        max_length=20,
        choices=REGION_CHOICES,
    )

    area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Area in square kilometres",
    )

    population = models.BigIntegerField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = ["name"]

        verbose_name = "State"

        verbose_name_plural = "States"

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):

        return self.name