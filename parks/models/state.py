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
        ("Union Territory", "Union Territory"),
    ]

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    capital = models.CharField(
        max_length=100,
        blank=True
    )

    region = models.CharField(
        max_length=20,
        choices=REGION_CHOICES
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    state_map = models.ImageField(
        upload_to="states/maps/",
        blank=True,
        null=True
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
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name