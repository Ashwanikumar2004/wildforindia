import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from parks.models import NationalPark, State


def build_directory_description(name, state_name, area_type, source):
    label = dict(NationalPark.AREA_TYPE_CHOICES)[area_type].lower()
    return (
        f"{name} is listed as a {label} in {state_name}, India. The Wild Life "
        f"(Protection) Act, 1972 provides the legal framework for protected "
        f"areas in India. The directory source identifies this site's name, "
        f"category, and state, but does not include a verified site profile, "
        f"species list, or visitor guide. Confirm local boundaries and rules "
        f"with the responsible Forest Department before planning a visit. "
        f"Source: {source}"
    )


class Command(BaseCommand):
    help = "Import the sourced national park and wildlife sanctuary name catalogue."

    def handle(self, *args, **options):
        data_path = Path(settings.BASE_DIR) / "datasets" / "protected_areas.json"
        try:
            dataset = json.loads(data_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise CommandError(f"Could not read {data_path}: {error}") from error

        records = dataset.get("records", [])
        counts = {
            "national_park": sum(row.get("type") == "national_park" for row in records),
            "wildlife_sanctuary": sum(
                row.get("type") == "wildlife_sanctuary" for row in records
            ),
        }
        if counts != {"national_park": 106, "wildlife_sanctuary": 574}:
            raise CommandError(
                "The protected-area file did not contain the expected 106 national parks "
                "and 574 wildlife sanctuaries; no records were imported."
            )

        states = dataset.get("states", {})
        state_objects = {}
        for state_name, metadata in states.items():
            state, _ = State.objects.get_or_create(
                name=state_name,
                defaults={
                    "code": metadata["code"],
                    "region": metadata["region"],
                },
            )
            state_objects[state_name] = state

        created_count = 0
        existing_count = 0
        source = dataset["source"]

        for row in records:
            area_type = row["type"]
            state = state_objects[row["state"]]
            name = row["name"].strip()

            park = NationalPark.objects.filter(
                name=name,
                state=state,
                protected_area_type=area_type,
            ).first()

            # Preserve the original seed record and its detail-page URL while
            # bringing its display name into line with the sourced list.
            if park is None and name == "Jim Corbett National Park":
                park = NationalPark.objects.filter(
                    name="Corbett National Park",
                    state=state,
                    protected_area_type=area_type,
                ).first()
                if park:
                    park.name = name
                    park.save(update_fields=["name"])

            if park:
                if "appears in the Wildlife Institute of India's protected-area list." in park.description:
                    park.description = build_directory_description(
                        name,
                        state.name,
                        area_type,
                        source,
                    )
                    park.save(update_fields=["description"])
                existing_count += 1
                continue

            NationalPark.objects.create(
                name=name,
                protected_area_type=area_type,
                state=state,
                description=build_directory_description(
                    name,
                    state.name,
                    area_type,
                    source,
                ),
                area=None,
                established_year=None,
                safari_available=None,
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished: {created_count} protected areas added, "
                f"{existing_count} already existed. Source lists contain "
                f"{counts['national_park']} national parks and "
                f"{counts['wildlife_sanctuary']} wildlife sanctuaries."
            )
        )
