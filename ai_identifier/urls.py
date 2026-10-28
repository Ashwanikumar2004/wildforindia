from django.urls import path

from . import views


urlpatterns = [
    path("", views.identifier_home, name="ai_identifier"),
    path("history/", views.identification_history, name="identification_history"),
    path("history/<int:identification_id>/image/", views.identification_image, name="identification_image"),
    path("history/<int:identification_id>/delete/", views.delete_identification, name="delete_identification"),
]
