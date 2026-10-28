from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import ProfileForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("wilddex")

    form = AuthenticationForm(request, data=request.POST or None)
    for field in form.fields.values():
        field.widget.attrs.update({"class": "form-control"})

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        next_url = request.POST.get("next") or request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect("wilddex")

    return render(request, "accounts/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("wilddex")

    form = UserCreationForm(request.POST or None)
    for field in form.fields.values():
        field.widget.attrs.update({"class": "form-control"})

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("wilddex")

    return render(request, "accounts/register.html", {"form": form})


@require_POST
@login_required
def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def profile_view(request):
    form = ProfileForm(request.POST if request.method == "POST" else None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("profile")
    return render(request, "accounts/profile.html", {"form": form})
