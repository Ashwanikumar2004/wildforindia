from django.contrib import admin

from .models import State, NationalPark, ParkImage, ParkFacility, ParkReview, ParkRoute


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
        "protected_area_type",
        "state",
        "area",
        "safari_available",
        "is_featured",
        "is_active",
    )

    list_filter = (
        "protected_area_type",
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
                "protected_area_type",
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
        "display_order",
        "is_popular",
        "is_active",
    )

    list_filter = (
        "is_popular",
        "is_active",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "display_order",
        "name",
    )

@admin.register(ParkReview)
class ParkReviewAdmin(admin.ModelAdmin):

    list_display = (
        "park",
        "reviewer_name",
        "rating",
        "visit_date",
        "is_verified",
    )

    list_filter = (
        "rating",
        "is_verified",
    )

    search_fields = (
        "park__name",
        "reviewer_name",
    )

@admin.register(ParkRoute)
class ParkRouteAdmin(admin.ModelAdmin):

    list_display = (
        "park",
        "starting_city",
        "transport_mode",
        "distance",
        "estimated_time",
        "is_best_route",
    )

    list_filter = (
        "transport_mode",
        "is_best_route",
    )

    search_fields = (
        "park__name",
        "starting_city",
    )

    ordering = (
        "display_order",
        "starting_city",
    )
