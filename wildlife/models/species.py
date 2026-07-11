import uuid

from django.db import models
from django.utils.text import slugify

from .category import Category
from .habitat import Habitat
from .conservation import ConservationStatus


class Species(models.Model):

    # ==========================
    # Choices
    # ==========================

    WEIGHT_UNITS = [
        ("g", "Grams"),
        ("kg", "Kilograms"),
    ]

    LENGTH_UNITS = [
        ("cm", "Centimeters"),
        ("m", "Meters"),
    ]

    SPEED_UNITS = [
        ("km/h", "Kilometers per Hour"),
        ("m/s", "Meters per Second"),
    ]

    ACTIVITY_CHOICES = [
        ("Diurnal", "Diurnal"),
        ("Nocturnal", "Nocturnal"),
        ("Crepuscular", "Crepuscular"),
    ]

    RARITY_CHOICES = [
        ("Common", "Common"),
        ("Uncommon", "Uncommon"),
        ("Rare", "Rare"),
        ("Epic", "Epic"),
        ("Legendary", "Legendary"),
    ]

    # ==========================
    # Identity
    # ==========================

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    common_name = models.CharField(
        max_length=200,
        unique=True
    )

    scientific_name = models.CharField(
        max_length=250,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    # ==========================
    # Relationships
    # ==========================

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="species"
    )

    habitats = models.ManyToManyField(
        Habitat,
        related_name="species",
        blank=True
    )

    conservation_status = models.ForeignKey(
        ConservationStatus,
        on_delete=models.PROTECT,
        related_name="species"
    )

    # ==========================
    # Description
    # ==========================

    short_description = models.CharField(
        max_length=300
    )

    description = models.TextField()

    fun_fact = models.TextField(
        blank=True
    )

    # ==========================
    # Physical Characteristics
    # ==========================

    average_weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True
    )

    weight_unit = models.CharField(
        max_length=5,
        choices=WEIGHT_UNITS,
        default="kg"
    )

    average_height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )

    height_unit = models.CharField(
        max_length=5,
        choices=LENGTH_UNITS,
        default="m"
    )

    average_length = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )

    length_unit = models.CharField(
        max_length=5,
        choices=LENGTH_UNITS,
        default="m"
    )

    top_speed = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )

    speed_unit = models.CharField(
        max_length=5,
        choices=SPEED_UNITS,
        default="km/h"
    )

    lifespan = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Average lifespan in years"
    )

    # ==========================
    # Biology
    # ==========================

    diet = models.CharField(
        max_length=100,
        blank=True
    )

    behaviour = models.TextField(
        blank=True
    )

    activity_pattern = models.CharField(
        max_length=20,
        choices=ACTIVITY_CHOICES,
        blank=True
    )

    reproduction = models.TextField(
        blank=True
    )

    predators = models.TextField(
        blank=True
    )

    endemic_to_india = models.BooleanField(
        default=False
    )

    # ==========================
    # AI
    # ==========================

    ai_label = models.CharField(
        max_length=100,
        blank=True
    )

    confidence_threshold = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.90
    )

    # ==========================
    # WildDex
    # ==========================

    rarity = models.CharField(
        max_length=20,
        choices=RARITY_CHOICES,
        default="Common"
    )

    xp_reward = models.PositiveIntegerField(
        default=100
    )

    unlock_level = models.PositiveIntegerField(
        default=1
    )

    # ==========================
    # Homepage
    # ==========================

    is_featured = models.BooleanField(
        default=False
    )

    featured_priority = models.PositiveIntegerField(
        default=0
    )

    is_verified = models.BooleanField(
        default=False
    )

    # ==========================
    # SEO
    # ==========================

    seo_title = models.CharField(
        max_length=200,
        blank=True
    )

    seo_description = models.TextField(
        blank=True
    )

    # ==========================
    # Audit
    # ==========================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["common_name"]
        verbose_name = "Species"
        verbose_name_plural = "Species"

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.common_name)

        super().save(*args, **kwargs)
    
    @property
    def primary_image(self):
        """
        Returns the primary image of the species.
        If no image is marked as primary, returns the first image.
        """

        primary = self.images.filter(is_primary=True).first()

        if primary:
            return primary

        return self.images.first()

    def __str__(self):
        return self.common_name