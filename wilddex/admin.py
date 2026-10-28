from django.contrib import admin

from .models import WildDexEntry


@admin.register(WildDexEntry)
class WildDexEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "species", "discovered_at", "source_identification")
    search_fields = ("user__username", "species__common_name", "species__scientific_name")
    list_filter = ("discovered_at",)
