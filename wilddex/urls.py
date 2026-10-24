from django.urls import path

from . import views


urlpatterns = [
    path("", views.wilddex_home, name="wilddex"),
]
