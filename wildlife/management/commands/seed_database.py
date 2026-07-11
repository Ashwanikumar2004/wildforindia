from django.core.management.base import BaseCommand

from wildlife.models import (
    Category,
    Habitat,
    ConservationStatus,
)


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