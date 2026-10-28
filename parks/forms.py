from django import forms
from django.utils import timezone
from .models import ParkReview


class ParkReviewForm(forms.ModelForm):
    review = forms.CharField(min_length=20, max_length=3000, widget=forms.Textarea(attrs={"rows": 4, "class": "form-control"}))

    class Meta:
        model = ParkReview
        fields = ["rating", "visit_date", "review"]
        widgets = {"rating": forms.Select(attrs={"class": "form-select"}), "visit_date": forms.DateInput(attrs={"type": "date", "class": "form-control"})}

    def clean_visit_date(self):
        date = self.cleaned_data["visit_date"]
        if date and date > timezone.localdate():
            raise forms.ValidationError("Your visit date cannot be in the future.")
        return date
