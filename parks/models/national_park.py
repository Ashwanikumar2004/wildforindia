import uuid

from django.db import models
from django.utils.text import slugify

from .state import State

from wildlife.models import Species
from .park_facility import ParkFacility


class NationalPark(models.Model):

    AREA_TYPE_CHOICES = [
        ("national_park", "National Park"),
        ("wildlife_sanctuary", "Wildlife Sanctuary"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # ==========================
    # Basic Information
    # ==========================

    name = models.CharField(
        max_length=200,
    )

    protected_area_type = models.CharField(
        max_length=24,
        choices=AREA_TYPE_CHOICES,
        default="national_park",
        db_index=True,
        help_text="Choose whether this protected area is a national park or wildlife sanctuary.",
    )

    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
    )

    state = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        related_name="national_parks",
    )

    description = models.TextField()

    established_year = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Area in square kilometres",
    )

    # ==========================
    # Location
    # ==========================

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )

    # ==========================
    # Tourism
    # ==========================

    opening_time = models.TimeField(
        blank=True,
        null=True,
    )

    closing_time = models.TimeField(
        blank=True,
        null=True,
    )

    entry_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
    )

    safari_available = models.BooleanField(
        blank=True,
        null=True,
        default=None,
    )

    official_website = models.URLField(
        blank=True,
    )

    # ==========================
    # Homepage
    # ==========================

    is_featured = models.BooleanField(
        default=False,
    )

    featured_priority = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

    # ==========================
    # SEO
    # ==========================

    seo_title = models.CharField(
        max_length=200,
        blank=True,
    )

    seo_description = models.TextField(
        blank=True,
    )

    # ==========================
    # Audit
    # ==========================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    # ==========================
    # Contact
    # ==========================

    nearest_city = models.CharField(
        max_length=100,
        blank=True,
    )

    nearest_airport = models.CharField(
        max_length=150,
        blank=True,
    )

    nearest_railway_station = models.CharField(
        max_length=150,
        blank=True,
    )

    contact_number = models.CharField(
        max_length=20,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )
    # ==========================
    # Hero
    # ==========================

    hero_image = models.ImageField(
        upload_to="parks/heroes/",
        blank=True,
        null=True,
        max_length=500,
    )

    species = models.ManyToManyField(
    Species,
    related_name="national_parks",
    blank=True,
    )

    facilities = models.ManyToManyField(
    ParkFacility,
    related_name="parks",
    blank=True,
)

    class Meta:

        ordering = ["name"]

        verbose_name = "Protected Area"

        verbose_name_plural = "Protected Areas"

        constraints = [
            models.UniqueConstraint(
                fields=["name", "state", "protected_area_type"],
                name="unique_protected_area_in_state",
            ),
        ]

    def save(self, *args, **kwargs):

        if not self.slug:
            state_code = self.state.code if self.state_id else "india"
            slug_base = slugify(
                f"{self.name}-{state_code}-{self.protected_area_type}"
            )
            self.slug = slug_base

        super().save(*args, **kwargs)

    def __str__(self):

        return self.name
