from django.contrib import admin

from .models import (
    Category,
    Habitat,
    ConservationStatus,
    Species,
    SpeciesImage,
    SpeciesSound,
    SpeciesDistribution,
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "display_order",
        "is_active",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "is_active",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

@admin.register(Habitat)
class HabitatAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "climate",
        "is_active",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "is_active",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

@admin.register(ConservationStatus)
class ConservationStatusAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
        "priority",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
    )

    list_filter = (
        "is_active",
    )

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):

    list_display = (
        "common_name",
        "scientific_name",
        "category",
        "conservation_status",
        "rarity",
        "xp_reward",
        "is_featured",
        "is_verified",
    )

    search_fields = (
        "common_name",
        "scientific_name",
    )

    list_filter = (
        "category",
        "conservation_status",
        "rarity",
        "is_featured",
        "is_verified",
    )

    prepopulated_fields = {
        "slug": ("common_name",)
    }

    filter_horizontal = (
        "habitats",
    )

@admin.register(SpeciesImage)
class SpeciesImageAdmin(admin.ModelAdmin):

    list_display = (
        "species",
        "caption",
        "photographer",
        "is_primary",
    )

    search_fields = (
        "species__common_name",
        "caption",
    )

    list_filter = (
        "is_primary",
    )

@admin.register(SpeciesSound)
class SpeciesSoundAdmin(admin.ModelAdmin):

    list_display = (
        "species",
        "title",
        "sound_type",
    )

    search_fields = (
        "species__common_name",
        "title",
    )

    list_filter = (
        "sound_type",
    )

@admin.register(SpeciesDistribution)
class SpeciesDistributionAdmin(admin.ModelAdmin):

    list_display = (
        "species",
        "state",
        "population_status",
        "is_native",
    )

    search_fields = (
        "species__common_name",
        "state__name",
    )

    list_filter = (
        "population_status",
        "is_native",
        "state",
    )