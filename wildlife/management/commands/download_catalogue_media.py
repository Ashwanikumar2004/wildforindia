"""Cache attributed, freely licensed catalogue photos. Never runs in a web request."""
import hashlib
import html
import json
import time
from io import BytesIO
from urllib.parse import urlencode, quote, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.html import strip_tags
from PIL import Image, ImageOps

from parks.models import NationalPark
from wildlife.models import Species


API = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "WildFIndiaUniversityProject/1.0 (educational catalogue; Wikimedia attribution retained)"}
PARK_ARTICLE_TITLES = {
    "Bhagwan Mahaveer (Mollem) National Park": "Mollem National Park",
    "Bison (Rajbari) National Park": "Rajbari National Park",
    "Blackbuck (Velavadar) National Park": "Blackbuck National Park, Velavadar",
    "Govind National Park": "Govind Pashu Vihar National Park and Sanctuary",
    "Guru Ghasidas (Sanjay) National Park": "Guru Ghasidas National Park",
    "Intanki (Ntangki) National Park": "Ntangki National Park",
    "Kishtwar High Altitude National Park": "Kishtwar National Park",
    "Mahatma Gandhi Marine (Wandoor) National Park": "Mahatma Gandhi Marine National Park",
    "Marine National Park, Gulf of Kachchh": "Marine National Park, Gulf of Kutch",
    "Mount Manipur National Park (formerly Mount Harriet)": "Mount Manipur National Park",
    "Nawegaon National Park": "Navegaon National Park",
    "Phawngpui (Blue Mountain) National Park": "Phawngpui National Park",
    "Rajiv Gandhi (Rameswaram) National Park": "Rajiv Gandhi National Park",
}


def fetch(url):
    for attempt in range(4):
        try:
            with urlopen(Request(url, headers=HEADERS), timeout=30) as response:
                data = response.read(10_000_001)
            if len(data) > 10_000_000:
                raise ValueError("Remote file exceeded size limit")
            return data
        except Exception as error:
            if attempt == 3:
                raise
            delay = 3 + attempt
            if isinstance(error, HTTPError) and error.code in {429, 503}:
                delay = min(60, max(15 * (attempt + 1), int(error.headers.get("Retry-After", "0") or 0)))
            time.sleep(delay)


def query(endpoint, **params):
    time.sleep(2)
    payload = json.loads(fetch(endpoint + "?" + urlencode({"action": "query", "format": "json", **params})))
    if "error" in payload:
        raise ValueError(f"Wikimedia API error: {payload['error'].get('code', 'unknown')}")
    return payload


def plain(value):
    return html.unescape(strip_tags(value or "")).strip()


class Command(BaseCommand):
    help = "Download attributed Wikimedia photos and short sourced park introductions. Resumable; preserves existing assets."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=0)
        parser.add_argument("--retry-missing", action="store_true")
        parser.add_argument("--batch-size", type=int, default=5, choices=range(1, 21))
        parser.add_argument("--only-national-parks", action="store_true")

    def handle(self, *args, **options):
        manifest_path = settings.BASE_DIR / "datasets" / "catalogue_media.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {"parks": {}, "species": {}}
        output = settings.BASE_DIR / "static" / "images" / "catalogue"
        output.mkdir(parents=True, exist_ok=True)
        parks = NationalPark.objects.select_related("state").filter(is_active=True).order_by("protected_area_type", "name")
        if options["only_national_parks"]:
            parks = parks.filter(protected_area_type="national_park")
        rows = [
            ("species", s.scientific_name, s.common_name.capitalize(), "")
            for s in (Species.objects.none() if options["only_national_parks"] else Species.objects.filter(is_verified=True))
        ] + [
            ("parks", f"{p.state.name}|{p.name}", PARK_ARTICLE_TITLES.get(p.name, p.name), p.state.name)
            for p in parks
        ]
        rows = [r for r in rows if r[1] not in manifest[r[0]] or (options["retry_missing"] and not manifest[r[0]][r[1]].get("path"))]
        if options["limit"]:
            rows = rows[:options["limit"]]
        downloaded = 0
        batch_size = options["batch_size"]
        for start in range(0, len(rows), batch_size):
            batch = rows[start:start + batch_size]
            try:
                result = query(API, titles="|".join(r[2] for r in batch), redirects=1,
                    prop="pageimages|extracts|coordinates", piprop="thumbnail|name", pithumbsize=800,
                    pilicense="free", pilimit=50, exintro=1, explaintext=1, exchars=950, exlimit=batch_size)
                data = result.get("query", {})
                aliases = {r["from"]: r["to"] for k in ("normalized", "redirects") for r in data.get(k, [])}
                pages = {p["title"]: p for p in data.get("pages", {}).values()}
                image_names = ["File:" + p["pageimage"] for p in pages.values() if p.get("pageimage")]
                image_meta = {}
                if image_names:
                    commons = query(API, titles="|".join(image_names), prop="imageinfo", iiprop="url|extmetadata", iiurlwidth=640)
                    for p in commons.get("query", {}).get("pages", {}).values():
                        if p.get("imageinfo"):
                            image_meta[p["title"].replace("_", " ")] = p["imageinfo"][0]
                for kind, key, title, state in batch:
                    visited = set()
                    while title in aliases and title not in visited:
                        visited.add(title)
                        title = aliases[title]
                    page = pages.get(title, {})
                    summary = page.get("extract", "")
                    # Exact article/redirect names and state context avoid matching a different place.
                    state_names = {"Odisha": ["odisha", "orissa"], "Uttarakhand": ["uttarakhand", "uttaranchal"], "Jammu and Kashmir": ["kashmir"], "Andaman and Nicobar Islands": ["andaman", "nicobar"]}.get(state, [state.casefold()])
                    if not page or "missing" in page or (state and not any(n in summary.casefold() for n in state_names)):
                        manifest[kind][key] = {}
                        continue
                    entry = {
                        "article": "https://en.wikipedia.org/wiki/" + quote(title.replace(" ", "_")),
                        "summary": summary[:950], "text_license": "CC BY-SA 4.0",
                        "retrieved": time.strftime("%Y-%m-%d"),
                    }
                    coords = page.get("coordinates", [])
                    if coords and kind == "parks":
                        entry["latitude"], entry["longitude"] = coords[0]["lat"], coords[0]["lon"]
                    info = image_meta.get(("File:" + page.get("pageimage", "")).replace("_", " "), {})
                    meta = info.get("extmetadata", {})
                    license_name = plain(meta.get("LicenseShortName", {}).get("value"))
                    thumb = info.get("thumburl") or page.get("thumbnail", {}).get("source", "")
                    thumb = thumb.split("?")[0]
                    normalized_license = license_name.lower().replace("-", " ")
                    if thumb and (normalized_license.startswith(("cc by", "cc0")) or normalized_license == "public domain"):
                        if urlparse(thumb).hostname not in {"upload.wikimedia.org", "thumb.wikimedia.org"}:
                            raise ValueError("Unexpected image host")
                        filename = hashlib.sha256((kind + key).encode()).hexdigest()[:20] + ".webp"
                        try:
                            time.sleep(1)
                            with Image.open(BytesIO(fetch(thumb))) as photo:
                                photo = ImageOps.exif_transpose(photo).convert("RGB")
                                photo.thumbnail((960, 800))
                                photo.save(output / filename, "WEBP", quality=82)
                            entry.update(path="images/catalogue/" + filename,
                                artist=plain(meta.get("Artist", {}).get("value"))[:1000],
                                license=license_name, license_url=meta.get("LicenseUrl", {}).get("value", ""),
                                source=info.get("descriptionurl", ""), title=page.get("pageimage", ""))
                            downloaded += 1
                        except Exception as error:
                            self.stderr.write(f"Photo unavailable for {title}: {type(error).__name__}")
                    manifest[kind][key] = entry
                temporary = manifest_path.with_suffix(".json.tmp")
                temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                temporary.replace(manifest_path)
                self.stdout.write(f"Processed {min(start + batch_size, len(rows))}/{len(rows)}; downloaded {downloaded} photos", ending="\n")
                self.stdout.flush()
            except Exception as error:
                self.stderr.write(f"Batch starting {start} failed: {type(error).__name__}: {error}; URL: {getattr(error, 'url', '')[:150]}")
        self.stdout.write(self.style.SUCCESS(f"Finished. {downloaded} photos downloaded with attribution."))
