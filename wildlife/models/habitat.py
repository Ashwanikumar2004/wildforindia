from django.db import models
from django.utils.text import slugify


class Habitat(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    hero_image = models.ImageField(
        upload_to="habitats/",
        blank=True,
        null=True
    )

    climate = models.CharField(
        max_length=150,
        blank=True
    )

    vegetation = models.TextField(
        blank=True
    )

    average_temperature = models.FloatField(
        null=True,
        blank=True
    )

    rainfall = models.FloatField(
        null=True,
        blank=True
    )

    icon = models.ImageField(
        upload_to="habitats/icons/",
        blank=True,
        null=True
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