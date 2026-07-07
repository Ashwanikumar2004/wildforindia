from django.contrib import admin
from .models.category import Category
from .models.habitat import Habitat
from .models.conservation import ConservationStatus

# Register your models here.
admin.site.register(Category)
admin.site.register(Habitat)
admin.site.register(ConservationStatus)