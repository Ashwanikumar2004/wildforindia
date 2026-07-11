from django.contrib import admin

from .models import State, NationalPark, ParkImage, ParkFacility


@admin.register(State)
class StateAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
        "capital",
        "region",
        "is_active",
    )

    list_filter = (
        "region",
        "is_active",
    )

    search_fields = (
        "name",
        "capital",
        "code",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(NationalPark)
class NationalParkAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "state",
        "area",
        "safari_available",
        "is_featured",
        "is_active",
    )

    list_filter = (
        "state",
        "is_featured",
        "is_active",
    )

    search_fields = (
        "name",
        "state__name",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    # 👇 Add the fieldsets here
    fieldsets = (

        ("Basic Information", {
            "fields": (
                "name",
                "slug",
                "state",
                "description",
            )
        }),

        ("Location", {
            "fields": (
                "latitude",
                "longitude",
                "area",
                "established_year",
            )
        }),

        ("Tourism", {
        "fields": (
            "opening_time",
            "closing_time",
            "entry_fee",
            "safari_available",
            "facilities",
            "nearest_city",
            "nearest_airport",
            "nearest_railway_station",
            "contact_number",
            "email",
            "official_website",
            )
        }),

        ("Species", {
            "fields": (
                "species",
            )
        }),

        ("Homepage", {
            "fields": (
                "hero_image",
                "is_featured",
                "featured_priority",
                "is_active",
            )
        }),

        ("SEO", {
            "fields": (
                "seo_title",
                "seo_description",
            )
        }),

    )

@admin.register(ParkImage)
class ParkImageAdmin(admin.ModelAdmin):

    list_display = (
        "park",
        "caption",
        "photographer",
        "is_primary",
        "display_order",
    )

    list_filter = (
        "is_primary",
        "park",
    )

    search_fields = (
        "park__name",
        "caption",
        "photographer",
    )

@admin.register(ParkFacility)
class ParkFacilityAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
    )