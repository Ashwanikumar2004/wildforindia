from django.contrib import admin

from .models import State


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