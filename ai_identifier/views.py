import logging
import mimetypes
from io import BytesIO
from pathlib import PurePath

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from PIL import Image

from wildlife.models import Species

from .forms import WildlifeImageForm
from .models import Identification, IdentificationResult
from .predictor import SpeciesNetUnavailable, identify_image


logger = logging.getLogger(__name__)


@login_required
def identifier_home(request):
    form = WildlifeImageForm(request.POST or None, request.FILES or None)
    results = []
    uploaded_name = None

    if request.method == "POST" and form.is_valid():
        uploaded = form.cleaned_data["image"]
        uploaded_name = uploaded.name
        species_records = list(Species.objects.filter(is_verified=True))

        if not species_records:
            form.add_error(None, "There are no verified species available for identification yet.")
        else:
            try:
                with Image.open(uploaded) as source:
                    image = source.convert("RGB")
                results = identify_image(image, species_records)
                if not results:
                    form.add_error(
                        None,
                        "SpeciesNet could not clearly identify an animal in this photo. Try a closer, brighter photo with one animal clearly visible.",
                    )
                else:
                    # Re-encode as JPEG so camera GPS and other EXIF metadata
                    # from a user's original upload are not retained.
                    clean_image = BytesIO()
                    image.save(clean_image, format="JPEG", quality=90, optimize=True)
                    image_file = ContentFile(
                        clean_image.getvalue(),
                        name=f"{PurePath(uploaded.name).stem or 'wildlife-photo'}.jpg",
                    )
                    identification = None
                    try:
                        with transaction.atomic():
                            identification = Identification(
                                user=request.user,
                                model_name="SpeciesNet 4.0.3a",
                            )
                            identification.image.save(
                                image_file.name,
                                image_file,
                                save=True,
                            )
                            IdentificationResult.objects.bulk_create(
                                [
                                    IdentificationResult(
                                        identification=identification,
                                        species=result["species"],
                                        label=result["label"],
                                        score=result["score"],
                                        rank=rank,
                                    )
                                    for rank, result in enumerate(results, start=1)
                                ]
                            )
                    except Exception:
                        # The database transaction rolls back its rows. Remove
                        # the separately stored file too if it was written.
                        if identification and identification.image:
                            identification.image.delete(save=False)
                        raise
                    uploaded_name = uploaded.name
                    for result in results:
                        result["identification_id"] = identification.pk
            except SpeciesNetUnavailable:
                form.add_error(
                    None,
                    "SpeciesNet is not installed on this server. Follow the local AI setup in the project README.",
                )
            except Exception:
                logger.exception("Wildlife image identification failed")
                form.add_error(
                    None,
                    "We could not process this photo. Please try another clear JPG or PNG image.",
                )

    prediction = results[0] if results else None
    if prediction:
        for result in results:
            result["score_percent"] = round(result["score"] * 100, 1)
            species = result["species"]
            result["threshold_percent"] = (
                round(float(species.confidence_threshold) * 100, 1)
                if species
                else None
            )
            result["accepted"] = bool(
                species
                and result["score"] >= float(species.confidence_threshold)
            )

    return render(
        request,
        "ai_identifier/home.html",
        {
            "form": form,
            "prediction": prediction,
            "other_predictions": results[1:],
            "uploaded_name": uploaded_name,
        },
    )


@login_required
def identification_history(request):
    identifications = (
        Identification.objects.filter(user=request.user)
        .prefetch_related("results__species")
        .order_by("-created_at")
    )
    return render(
        request,
        "ai_identifier/history.html",
        {"identifications": identifications},
    )


@login_required
def identification_image(request, identification_id):
    identification = get_object_or_404(
        Identification,
        pk=identification_id,
        user=request.user,
    )
    image_file = identification.image.open("rb")
    return FileResponse(
        image_file,
        content_type=mimetypes.guess_type(identification.image.name)[0] or "application/octet-stream",
        filename="wildlife-photo",
        as_attachment=False,
    )


@require_POST
@login_required
def delete_identification(request, identification_id):
    identification = get_object_or_404(
        Identification,
        pk=identification_id,
        user=request.user,
    )
    identification.image.delete(save=False)
    identification.delete()
    return redirect("identification_history")
