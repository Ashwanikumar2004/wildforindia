from django.contrib import admin

from .models import Identification, IdentificationResult

# Register your models here.
@admin.register(Identification)
class IdentificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "model_name", "created_at")
    list_filter = ("model_name", "created_at")
    search_fields = ("user__username",)
    readonly_fields = ("user", "image", "model_name", "created_at")


@admin.register(IdentificationResult)
class IdentificationResultAdmin(admin.ModelAdmin):
    list_display = ("identification", "rank", "label", "score", "species")
    list_filter = ("rank",)
    search_fields = ("label", "species__common_name", "identification__user__username")
