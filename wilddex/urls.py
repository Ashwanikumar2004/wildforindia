from django.urls import path

from . import views


urlpatterns = [
    path("", views.wilddex_home, name="wilddex"),
    path("export/", views.export_journal, name="wilddex_export"),
    path("entry/<int:entry_id>/", views.entry_detail, name="wilddex_entry"),
    path("entry/<int:entry_id>/remove/", views.remove_entry, name="wilddex_remove"),
    path("add/<int:identification_id>/", views.add_discovery, name="wilddex_add_discovery"),
]
