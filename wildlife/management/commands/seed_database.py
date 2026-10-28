from django.core.management.base import BaseCommand

from wildlife.models import (
    Category,
    Habitat,
    ConservationStatus,
    Species,
    SpeciesDistribution,
)
from parks.models import State


class Command(BaseCommand):

    help = "Seeds the Wildlife Database"

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.SUCCESS("Creating Categories..."))

        categories = [
            "Mammal",
            "Bird",
            "Reptile",
            "Amphibian",
            "Fish",
            "Insect",
            "Butterfly",
        ]

        for category in categories:
            Category.objects.get_or_create(
                name=category
            )

        self.stdout.write(self.style.SUCCESS("Categories Added"))

        self.stdout.write(self.style.SUCCESS("Creating Habitats..."))

        habitats = [
            "Forest",
            "Grassland",
            "Mangrove",
            "Wetland",
            "River",
            "Desert",
            "Mountain",
        ]

        for habitat in habitats:
            Habitat.objects.get_or_create(
                name=habitat
            )

        self.stdout.write(self.style.SUCCESS("Habitats Added"))

        self.stdout.write(self.style.SUCCESS("Creating Conservation Status..."))

        statuses = [
            ("Least Concern", "LC"),
            ("Near Threatened", "NT"),
            ("Vulnerable", "VU"),
            ("Endangered", "EN"),
            ("Critically Endangered", "CR"),
            ("Extinct in the Wild", "EW"),
            ("Extinct", "EX"),
        ]

        for name, code in statuses:
            ConservationStatus.objects.get_or_create(
                name=name,
                defaults={
                    "code": code
                }
            )

        self.stdout.write(self.style.SUCCESS("Conservation Status Added"))

        self.stdout.write(self.style.SUCCESS("Creating starter species..."))
        starter_species = [
            {
                "common_name": "Bengal Tiger",
                "scientific_name": "Panthera tigris",
                "category": "Mammal",
                "status": "EN",
                "habitats": ["Forest", "Grassland", "Mangrove"],
                "ai_label": "tiger (Panthera tigris)",
                "short_description": "A large striped cat found in several Indian landscapes.",
                "description": (
                    "Tigers are solitary predators that depend on connected habitat and "
                    "healthy prey populations. India supports important populations of "
                    "this globally endangered species."
                ),
                "fun_fact": "A tiger's stripe pattern is unique to the individual.",
                "diet": "Carnivore",
                "rarity": "Legendary",
                "xp_reward": 500,
                "featured_priority": 1,
            },
            {
                "common_name": "Asian Elephant",
                "scientific_name": "Elephas maximus",
                "category": "Mammal",
                "status": "EN",
                "habitats": ["Forest", "Grassland"],
                "ai_label": "Asian elephant (Elephas maximus)",
                "short_description": "A highly social, large herbivore of South and Southeast Asia.",
                "description": (
                    "Asian elephants live in herds and need large connected areas to "
                    "find food and water. Habitat fragmentation and conflict with people "
                    "are major conservation concerns."
                ),
                "fun_fact": "Elephants use their trunks for smelling, feeding, drinking, and touch.",
                "diet": "Herbivore",
                "rarity": "Epic",
                "xp_reward": 400,
                "featured_priority": 2,
            },
            {
                "common_name": "Gharial",
                "scientific_name": "Gavialis gangeticus",
                "category": "Reptile",
                "status": "CR",
                "habitats": ["River"],
                "ai_label": "gharial (Gavialis gangeticus)",
                "short_description": "A fish-eating crocodilian adapted to large rivers.",
                "description": (
                    "The gharial is known for its long, narrow snout and spends much of "
                    "its life in freshwater river systems. It is critically endangered, "
                    "with threats including river modification and loss of nesting banks."
                ),
                "fun_fact": "Adult male gharials develop a bulb at the end of the snout.",
                "diet": "Primarily fish",
                "rarity": "Legendary",
                "xp_reward": 500,
                "featured_priority": 3,
            },
            {
                "common_name": "Indian Peafowl",
                "scientific_name": "Pavo cristatus",
                "category": "Bird",
                "status": "LC",
                "habitats": ["Forest", "Grassland"],
                "ai_label": "Indian peafowl (Pavo cristatus)",
                "short_description": "India's national bird, recognized by the male's ornate train.",
                "description": (
                    "Indian peafowl use a range of open and wooded habitats and feed on "
                    "seeds, insects, and other small foods. The species is native to the "
                    "Indian subcontinent."
                ),
                "fun_fact": "The large iridescent train is made of elongated upper-tail coverts.",
                "diet": "Omnivore",
                "rarity": "Uncommon",
                "xp_reward": 150,
                "featured_priority": 4,
            },
            {
                "common_name": "Indian Leopard",
                "scientific_name": "Panthera pardus",
                "category": "Mammal",
                "status": "VU",
                "habitats": ["Forest", "Grassland", "Mountain"],
                "ai_label": "leopard (Panthera pardus)",
                "short_description": "A spotted, adaptable cat that lives across varied Indian habitats.",
                "description": (
                    "Leopards are solitary and adaptable predators. They can use forests, "
                    "scrub, and mountainous landscapes, but face pressure from habitat "
                    "loss, poaching, and conflict."
                ),
                "fun_fact": "The dark spots on a leopard's coat are called rosettes.",
                "diet": "Carnivore",
                "rarity": "Rare",
                "xp_reward": 300,
                "featured_priority": 5,
            },
            {
                "common_name": "Great Hornbill",
                "scientific_name": "Buceros bicornis",
                "category": "Bird",
                "status": "VU",
                "habitats": ["Forest", "Mountain"],
                "ai_label": "great hornbill (Buceros bicornis)",
                "short_description": "A large forest bird with a prominent casque on its bill.",
                "description": (
                    "Great hornbills live mainly in forests and feed on fruit and small "
                    "animals. They depend on large old trees for nesting, so forest loss "
                    "can reduce suitable nesting sites."
                ),
                "fun_fact": "The casque is a hollow structure above the bill.",
                "diet": "Omnivore",
                "rarity": "Rare",
                "xp_reward": 300,
                "featured_priority": 6,
            },
        ]

        for item in starter_species:
            category = Category.objects.get(name=item.pop("category"))
            status = ConservationStatus.objects.get(code=item.pop("status"))
            habitats = [Habitat.objects.get(name=name) for name in item.pop("habitats")]
            priority = item.pop("featured_priority")
            species, _ = Species.objects.update_or_create(
                scientific_name=item["scientific_name"],
                defaults={
                    **item,
                    "category": category,
                    "conservation_status": status,
                    "is_verified": True,
                    "is_featured": True,
                    "featured_priority": priority,
                },
            )
            species.habitats.set(habitats)

        self.stdout.write(self.style.SUCCESS("Starter species added or updated."))

        # These are a small set of sourced distribution records for the
        # starter catalogue, not exhaustive range maps. The search page makes
        # that limitation visible to users.
        distribution_sources = {
            "Bengal Tiger": {
                "states": [
                    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
                    "Chhattisgarh", "Jharkhand", "Karnataka", "Kerala",
                    "Madhya Pradesh", "Maharashtra", "Odisha", "Rajasthan",
                    "Tamil Nadu", "Telangana", "Uttar Pradesh", "Uttarakhand",
                    "West Bengal",
                ],
                "source": "https://wii.gov.in/images/images/documents/publications/Tiger%20Summary%20Report_07.08.2019.pdf",
            },
            "Asian Elephant": {
                "states": ["Karnataka", "Kerala", "Odisha", "Tamil Nadu", "West Bengal"],
                "source": "https://wii.gov.in/news/rap_for_comprehensive_understanding_management_human_elephant_conflict_in_south_india_technical_report_2026_release",
            },
            "Gharial": {
                "states": ["Madhya Pradesh", "Rajasthan", "Uttar Pradesh"],
                "source": "https://v1.wii.gov.in/node/2939",
            },
            "Indian Peafowl": {
                "states": [
                    "Andhra Pradesh", "Assam", "Chhattisgarh", "Gujarat",
                    "Madhya Pradesh", "Maharashtra", "Odisha", "Rajasthan",
                    "Tamil Nadu", "Uttar Pradesh", "Uttarakhand", "West Bengal",
                ],
                "source": "https://digitalrepository.wii.gov.in/bitstreams/16e3f302-80b2-4c60-8fd1-da1510f71c51/download",
            },
            "Indian Leopard": {
                "states": ["Karnataka", "Madhya Pradesh", "Maharashtra", "Tamil Nadu"],
                "source": "https://v1.wii.gov.in/images/images/documents/images_2024/leopard_status_2022a.pdf",
            },
            "Great Hornbill": {
                "states": [
                    "Arunachal Pradesh", "Assam", "Goa", "Karnataka", "Kerala",
                    "Maharashtra", "Meghalaya", "Mizoram", "Nagaland",
                    "Tamil Nadu", "Uttar Pradesh", "Uttarakhand", "West Bengal",
                ],
                "source": "https://doi.org/10.2305/IUCN.UK.2020-3.RLTS.T22682453A184603863.en",
            },
        }

        state_regions = {
            "Andhra Pradesh": ("IN-AP", "South"),
            "Arunachal Pradesh": ("IN-AR", "North-East"),
            "Assam": ("IN-AS", "North-East"),
            "Bihar": ("IN-BR", "East"),
            "Chhattisgarh": ("IN-CG", "Central"),
            "Goa": ("IN-GA", "West"),
            "Gujarat": ("IN-GJ", "West"),
            "Jharkhand": ("IN-JH", "East"),
            "Karnataka": ("IN-KA", "South"),
            "Kerala": ("IN-KL", "South"),
            "Madhya Pradesh": ("IN-MP", "Central"),
            "Maharashtra": ("IN-MH", "West"),
            "Meghalaya": ("IN-ML", "North-East"),
            "Mizoram": ("IN-MZ", "North-East"),
            "Nagaland": ("IN-NL", "North-East"),
            "Odisha": ("IN-OD", "East"),
            "Rajasthan": ("IN-RJ", "North"),
            "Tamil Nadu": ("IN-TN", "South"),
            "Telangana": ("IN-TS", "South"),
            "Uttar Pradesh": ("IN-UP", "North"),
            "Uttarakhand": ("IN-UT", "North"),
            "West Bengal": ("IN-WB", "East"),
        }

        distribution_count = 0
        for common_name, distribution in distribution_sources.items():
            species = Species.objects.get(common_name=common_name, is_verified=True)
            for state_name in distribution["states"]:
                code, region = state_regions[state_name]
                state, _ = State.objects.get_or_create(
                    name=state_name,
                    defaults={"code": code, "region": region},
                )
                _, created = SpeciesDistribution.objects.get_or_create(
                    species=species,
                    state=state,
                    defaults={
                        "is_native": True,
                        "population_status": "Unknown",
                        "notes": (
                            "Representative recorded range entry; this starter list is "
                            f"not an exhaustive state range. Source: {distribution['source']}"
                        ),
                    },
                )
                distribution_count += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Added {distribution_count} new sourced state-range records."
            )
        )
