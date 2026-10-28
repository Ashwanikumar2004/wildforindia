"""Read locally cached, attributed catalogue material without network requests."""
import json
import re
from functools import lru_cache

from django.conf import settings


def media_manifest():
    path = settings.BASE_DIR / "datasets" / "catalogue_media.json"
    try:
        return _read_manifest(path.stat().st_mtime_ns)
    except OSError:
        return {"species": {}, "parks": {}}


@lru_cache(maxsize=1)
def _read_manifest(version):
    path = settings.BASE_DIR / "datasets" / "catalogue_media.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"species": {}, "parks": {}}


def catalogue_profile(obj):
    if obj._meta.model_name == "species":
        entry = media_manifest().get("species", {}).get(obj.scientific_name, {})
    else:
        entry = media_manifest().get("parks", {}).get(f"{obj.state.name}|{obj.name}", {})
    profile = dict(entry)
    if profile.get("summary"):
        sentences = re.findall(r".*?[.!?](?=\s|$)", " ".join(profile["summary"].split()))
        if sentences:
            profile["summary"] = " ".join(sentences).strip()
    return profile


@lru_cache(maxsize=1)
def species_sources():
    try:
        data = json.loads((settings.BASE_DIR / "datasets" / "species_catalogue.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {
        **{key: row["sources"] for key, row in data["enrichments"].items()},
        **{row["scientific_name"]: row["sources"] for row in data["records"]},
    }
