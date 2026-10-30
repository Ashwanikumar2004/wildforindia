"""SpeciesNet inference and matching to the verified WildDex catalogue."""

import os
import tempfile
import threading
from concurrent.futures import TimeoutError as FutureTimeoutError
from functools import lru_cache
from pathlib import Path

from django.conf import settings


class SpeciesNetUnavailable(Exception):
    """Raised when the optional SpeciesNet package is not installed."""


class RemoteInferenceUnavailable(Exception):
    """The hosted model could not complete this identification."""


def _remote_prediction(image_path):
    from gradio_client import Client, handle_file

    client = None
    job = None
    try:
        # A separate client per request avoids sharing Gradio sessions between
        # users. Never obtain credentials from a user's browser or uploaded file.
        client = Client(
            settings.HF_SPACE_ID,
            token=settings.HF_TOKEN or None,
            verbose=False,
            analytics_enabled=False,
            download_files=False,
            httpx_kwargs={"timeout": 20.0},
        )
        job = client.submit(handle_file(str(image_path)), api_name="/identify")
        response = job.result(timeout=settings.HF_INFERENCE_TIMEOUT)
        if (
            not isinstance(response, dict)
            or not isinstance(response.get("predictions"), list)
            or not response["predictions"]
            or any(
                not isinstance(row, dict) or row.get("errors") or row.get("failures")
                for row in response["predictions"]
            )
        ):
            raise RemoteInferenceUnavailable("Invalid prediction response")
        return response
    except FutureTimeoutError as exc:
        if job is not None:
            job.cancel()
        raise RemoteInferenceUnavailable("Prediction timed out") from exc
    except RemoteInferenceUnavailable:
        raise
    except Exception as exc:
        # Keep provider messages, URLs and credentials out of the page.
        raise RemoteInferenceUnavailable("Hosted prediction unavailable") from exc
    finally:
        if client is not None:
            client.close()


def _normalise_name(value):
    return " ".join((value or "").casefold().replace("_", " ").split())


def _parse_model_label(model_label):
    """Return the model's binomial and common label from its taxonomy string.

    Current SpeciesNet labels look like
    ``id;class;order;family;genus;species;common name``. The last item is a
    common label, not a scientific epithet. Keeping it separate is important:
    otherwise an ordinary label such as "plains zebra" gets treated as the
    scientific name and every valid prediction is silently discarded.
    """
    parts = [part.strip() for part in (model_label or "").split(";")]
    if len(parts) < 2:
        return "", ""

    common_name = parts[-1]
    taxonomy = parts[1:-1]
    scientific_name = ""
    if len(taxonomy) >= 2:
        genus, epithet = taxonomy[-2:]
        if genus and epithet:
            scientific_name = f"{genus.capitalize()} {epithet.casefold()}"
    return scientific_name, common_name


def _species_index(species_records):
    by_name = {}
    by_binomial = {}
    for species in species_records:
        for name in (species.common_name, species.scientific_name, species.ai_label):
            normalized = _normalise_name(name)
            if normalized:
                by_name.setdefault(normalized, species)
        scientific = _normalise_name(species.scientific_name)
        words = scientific.split()
        if len(words) >= 2:
            by_binomial.setdefault(" ".join(words[:2]), []).append(species)

    # A model may return the binomial while the catalogue stores a subspecies.
    # Use that match only when it identifies exactly one verified catalogue row.
    for binomial, matches in by_binomial.items():
        if len(matches) == 1:
            by_name.setdefault(binomial, matches[0])
    return by_name


@lru_cache(maxsize=1)
def _get_speciesnet():
    """Load one model per application process; weights are cached by SpeciesNet."""
    try:
        from speciesnet.multiprocessing import SpeciesNet
    except ImportError as exc:
        raise SpeciesNetUnavailable from exc

    model_name = os.environ.get(
        "SPECIESNET_MODEL", "kaggle:google/speciesnet/pyTorch/v4.0.3a/1"
    ).strip()
    return SpeciesNet(model_name=model_name, multiprocessing=False)


_inference_lock = threading.Lock()


def identify_image(image, species_records):
    """Run SpeciesNet on one image and link candidates to verified catalogue rows.

    SpeciesNet is designed for camera-trap images. This call supplies India as the
    geographic context because WildFIndia is an India-focused guide; its result is
    still a suggestion and must not be treated as a field-verified identification.
    """
    model = None if settings.HF_SPACE_ID else _get_speciesnet()
    species_by_name = _species_index(species_records)

    # SpeciesNet accepts a filesystem path. A private temporary file avoids keeping
    # a second copy of the uploaded image in the project's working/media directory.
    with tempfile.TemporaryDirectory(prefix="wildfindia-speciesnet-") as workdir:
        image_path = Path(workdir) / "upload.jpg"
        image.convert("RGB").save(image_path, format="JPEG", quality=90)
        instances = {"instances": [{"filepath": str(image_path), "country": "IND"}]}

        # Model objects are cached, but model inference itself is serialized to avoid
        # concurrent Django requests using the same CPU/GPU instance at once.
        if settings.HF_SPACE_ID:
            response = _remote_prediction(image_path)
        else:
            with _inference_lock:
                response = model.predict(
                    instances_dict=instances,
                    run_mode="single_thread",
                    progress_bars=False,
                    max_classifications_per_detection=5,
                )

    predictions = response.get("predictions", []) if isinstance(response, dict) else []
    if not predictions:
        return []

    image_prediction = predictions[0]
    candidates = {}
    for detection in image_prediction.get("detections", []):
        raw = detection.get("raw_classifications") or {}
        labels = raw.get("classes", [])
        scores = raw.get("scores", [])
        for model_label, raw_score in zip(labels, scores):
            scientific_name, common_name = _parse_model_label(model_label)
            normalised_common = _normalise_name(common_name)
            if normalised_common in {
                "", "animal", "blank", "human", "vehicle", "unknown",
                "no cv result",
            }:
                continue
            species = (
                species_by_name.get(_normalise_name(scientific_name))
                or species_by_name.get(normalised_common)
            )
            label = species.common_name if species else common_name.title()
            score = float(raw_score)
            key = _normalise_name(scientific_name or common_name)
            if key not in candidates or score > candidates[key]["score"]:
                candidates[key] = {
                    "label": label,
                    "scientific_name": scientific_name,
                    "score": score,
                    "species": species,
                }

    return sorted(candidates.values(), key=lambda item: item["score"], reverse=True)[:5]
