from django.core.management.base import BaseCommand

from parks.models import NationalPark, State
from wildlife.models import Species


class Command(BaseCommand):
    help = "Add a small set of sourced park records with approximate map coordinates."

    states = {
        "Uttarakhand": {"code": "IN-UT", "capital": "Dehradun", "region": "North"},
        "Assam": {"code": "IN-AS", "capital": "Dispur", "region": "North-East"},
        "Rajasthan": {"code": "IN-RJ", "capital": "Jaipur", "region": "North"},
        "Kerala": {"code": "IN-KL", "capital": "Thiruvananthapuram", "region": "South"},
    }

    parks = [
        {
            "name": "Jim Corbett National Park",
            "state": "Uttarakhand",
            "area": "520.82",
            "established_year": 1936,
            "latitude": "29.530000",
            "longitude": "78.774700",
            "description": (
                "A protected landscape of Himalayan foothills, rivers, grasslands, "
                "and forest. Corbett was established as Hailey National Park in 1936. "
                "The map pin is an approximate display point, not a survey coordinate."
            ),
            "official_website": "https://corbettgov.org/about",
            # https://uttarakhandtourism.gov.in/destination/corbett-national-park
            "safari_available": True,
            "species": ["Bengal Tiger", "Asian Elephant", "Indian Leopard"],
        },
        {
            "name": "Kaziranga National Park",
            "state": "Assam",
            "area": "889.51",
            "established_year": 1974,
            "latitude": "26.577500",
            "longitude": "93.171100",
            "description": (
                "A Brahmaputra floodplain landscape of grasslands and wetlands. "
                "The Assam Forest Department lists the park and its notified "
                "additions; the map pin is an approximate display point."
            ),
            "official_website": "https://forest.assam.gov.in/portlets/national-park",
            "safari_available": True,
            "species": ["Bengal Tiger", "Asian Elephant", "Indian Leopard", "Indian Rhinoceros"],
        },
        {
            "name": "Ranthambore National Park",
            "state": "Rajasthan",
            "area": "282.03",
            "established_year": 1980,
            "latitude": "26.017300",
            "longitude": "76.502600",
            "description": (
                "A dry forest and rocky landscape in Sawai Madhopur district. "
                "The Rajasthan Forest Department lists the park area and "
                "notification; the map pin is an approximate display point."
            ),
            "official_website": "https://forest.rajasthan.gov.in/content/raj/forest/en/aboutus/departmental-wings/wildlife/details-of-protected-area-.html",
            # https://www.tourism.rajasthan.gov.in/ranthambore.html
            "safari_available": True,
            "species": ["Bengal Tiger"],
        },
        {
            "name": "Periyar National Park",
            "state": "Kerala",
            "area": "350.00",
            "established_year": 1982,
            "latitude": "9.462000",
            "longitude": "77.236000",
            "description": (
                "A Western Ghats forest and lake landscape. The Kerala Forest "
                "Department lists Periyar National Park at 350 square kilometres; "
                "the larger tiger reserve is a separate area. The map pin is approximate."
            ),
            "official_website": "https://forest.kerala.gov.in/en/preserving-natures-heritage/",
            "safari_available": None,
            "species": ["Bengal Tiger", "Asian Elephant", "Indian Leopard"],
        },
    ]

    def handle(self, *args, **kwargs):
        created_count = 0
        existing_count = 0

        for state_name, state_fields in self.states.items():
            State.objects.get_or_create(name=state_name, defaults=state_fields)

        for item in self.parks:
            park_state = State.objects.get(name=item["state"])
            park_data = {
                key: value
                for key, value in item.items()
                if key not in {"name", "state", "species"}
            }
            legacy_names = {
                "Jim Corbett National Park": ["Corbett National Park"],
            }.get(item["name"], [])
            park = NationalPark.objects.filter(
                state=park_state,
                protected_area_type="national_park",
                name__in=[item["name"], *legacy_names],
            ).first()

            if park:
                created = False
                if park.name != item["name"]:
                    park.name = item["name"]
                    park.save(update_fields=["name"])
                changed = []
                for field, value in park_data.items():
                    current = getattr(park, field)
                    legacy_safari_default = field == "safari_available" and current is False and "map pin" in park.description
                    if current in (None, "") or legacy_safari_default or (field == "description" and "The directory source identifies" in current):
                        setattr(park, field, value)
                        changed.append(field)
                if changed:
                    park.save(update_fields=changed)
            else:
                park = NationalPark.objects.create(
                    name=item["name"],
                    state=park_state,
                    **park_data,
                )
                created = True
            if not park.is_featured:
                park.is_featured = True
                park.save(update_fields=["is_featured"])

            # Do not overwrite park details or species associations that an
            # administrator may already have curated.
            verified_species = Species.objects.filter(
                is_verified=True,
                common_name__in=item["species"],
            )
            park.species.add(*verified_species)

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Added {park.name}"))
            else:
                existing_count += 1
                self.stdout.write(f"Kept existing record: {park.name}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished: {created_count} parks added, {existing_count} already existed."
            )
        )
