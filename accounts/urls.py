from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView

from . import views


urlpatterns = [
    path("profile/", views.profile_view, name="profile"),
    path("password/", PasswordChangeView.as_view(template_name="accounts/password_change.html", success_url=reverse_lazy("password_change_done")), name="password_change"),
    path("password/done/", PasswordChangeDoneView.as_view(template_name="accounts/password_changed.html"), name="password_change_done"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
]
