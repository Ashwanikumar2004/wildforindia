import uuid

from django.db import models
from django.conf import settings

from .national_park import NationalPark


class ParkReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="park_reviews")

    RATING_CHOICES = [
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    park = models.ForeignKey(
        NationalPark,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    reviewer_name = models.CharField(
        max_length=100,
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
    )

    review = models.TextField()

    visit_date = models.DateField(
        blank=True,
        null=True,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [models.UniqueConstraint(fields=["park", "user"], name="unique_park_review_per_user")]

        ordering = ["-created_at"]

        verbose_name = "Park Review"

        verbose_name_plural = "Park Reviews"

    def __str__(self):

        return f"{self.park.name} ({self.rating}★)"
