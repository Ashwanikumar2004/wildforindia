from django import forms
from PIL import Image, UnidentifiedImageError


MAX_IMAGE_SIZE = 4 * 1024 * 1024  # Keep uploads below Vercel's function body limit.
MAX_IMAGE_PIXELS = 25_000_000
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG"}


class WildlifeImageForm(forms.Form):
    image = forms.ImageField(
        label="Choose a wildlife photo",
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": "image/jpeg,image/png"}
        ),
    )

    def clean_image(self):
        image = self.cleaned_data["image"]

        if image.size > MAX_IMAGE_SIZE:
            raise forms.ValidationError("Please choose an image smaller than 4 MB.")

        try:
            image.seek(0)
            with Image.open(image) as decoded:
                if decoded.format not in ALLOWED_IMAGE_FORMATS:
                    raise forms.ValidationError("Please upload a JPG or PNG image.")
                if decoded.width * decoded.height > MAX_IMAGE_PIXELS:
                    raise forms.ValidationError("This image has too many pixels to process.")
                decoded.verify()
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
            raise forms.ValidationError("The uploaded file is not a valid image.")
        finally:
            image.seek(0)

        return image
