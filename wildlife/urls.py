from django.urls import path
from . import views

urlpatterns = [
    path("about/", views.about, name="about"),
    path("", views.home, name="home"),
    path("map/", views.wildlife_map, name="parks_map"),
    path("species/",views.species_list,name="species_list"),
    path("species/<slug:slug>/",views.species_detail,name="species_detail",),
    path("search/",views.search_species,name="search_species",),
]
