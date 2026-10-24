from django.urls import path

from . import views


urlpatterns = [
    path("", views.identifier_home, name="ai_identifier"),
]
