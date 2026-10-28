from django import forms
from django.contrib.auth import get_user_model


class ProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email"]
        widgets = {name: forms.TextInput(attrs={"class": "form-control"}) for name in ("first_name", "last_name")}
        widgets["email"] = forms.EmailInput(attrs={"class": "form-control"})
