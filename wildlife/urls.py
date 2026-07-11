from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("species/",views.species_list,name="species_list"),
    path("species/<slug:slug>/",views.species_detail,name="species_detail",),
    path("search/",views.search_species,name="search_species",),
]