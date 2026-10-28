import json
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from wildlife.models import Category, ConservationStatus, Habitat, Species


class Command(BaseCommand):
    help = "Add researched wildlife profiles and fill missing facts without overwriting curated or AI settings."

    @transaction.atomic
    def handle(self, *args, **options):
        data = json.loads((settings.BASE_DIR / "datasets" / "species_catalogue.json").read_text(encoding="utf-8"))
        created_count = 0
        for record in data["records"]:
            category, _ = Category.objects.get_or_create(name=record["category"])
            status = ConservationStatus.objects.get(code=record["status"])
            fields = {k: v for k, v in record.items() if k not in {"category", "status", "habitats", "sources"}}
            species, created = Species.objects.get_or_create(
                scientific_name=record["scientific_name"],
                defaults={**fields, "category": category, "conservation_status": status, "is_verified": True},
            )
            if created:
                for name in record["habitats"]:
                    habitat, _ = Habitat.objects.get_or_create(name=name)
                    species.habitats.add(habitat)
                created_count += 1
        for scientific_name, fields in data["enrichments"].items():
            species = Species.objects.filter(scientific_name=scientific_name).first()
            if not species:
                continue
            changed = []
            for field, value in fields.items():
                if field != "sources" and not getattr(species, field):
                    setattr(species, field, value)
                    changed.append(field)
            if changed:
                species.save(update_fields=changed)
        self.stdout.write(self.style.SUCCESS(f"Added {created_count} species and filled missing profile facts."))
