from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.parks_list,
        name="parks_list",
    ),

    path(
        "<slug:slug>/",
        views.park_detail,
        name="park_detail",
    ),

]