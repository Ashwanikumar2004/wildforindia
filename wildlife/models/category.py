from django.db import models
from django.utils.text import slugify


class Category(models.Model):

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

    icon = models.ImageField(
        upload_to="categories/icons/",
        blank=True,
        null=True,
        max_length=500,
    )

    cover_image = models.ImageField(
        upload_to="categories/covers/",
        blank=True,
        null=True,
        max_length=500,
    )

    color = models.CharField(
        max_length=20,
        default="#2E8B57"
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    seo_title = models.CharField(
        max_length=200,
        blank=True
    )

    seo_description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
