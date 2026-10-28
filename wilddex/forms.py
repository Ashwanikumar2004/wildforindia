from django import forms
from django.utils import timezone

from .models import WildDexEntry


class JournalForm(forms.ModelForm):
    class Meta:
        model = WildDexEntry
        fields = ["observed_on", "location", "notes"]
        widgets = {
            "observed_on": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }

    def clean_observed_on(self):
        value = self.cleaned_data["observed_on"]
        if value and value > timezone.localdate():
            raise forms.ValidationError("Choose today or an earlier date.")
        return value
