from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from parks.models import NationalPark, State
from wildlife.models import Category, ConservationStatus, Habitat, Species, SpeciesDistribution


class CatalogueFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Mammal")
        cls.status = ConservationStatus.objects.create(name="Endangered", code="EN")
        cls.habitat = Habitat.objects.create(name="Forest")
        cls.state = State.objects.create(name="Assam", code="IN-AS", region="North-East")
        cls.tiger = Species.objects.create(common_name="Bengal Tiger", scientific_name="Panthera tigris", category=cls.category, conservation_status=cls.status, short_description="A striped forest cat", description="A solitary predator", is_verified=True)
        cls.tiger.habitats.add(cls.habitat)
        SpeciesDistribution.objects.create(species=cls.tiger, state=cls.state)
        cls.park = NationalPark.objects.create(name="Example park", state=cls.state, description="Forest habitat", latitude="26.5", longitude="93.1")

    def test_combined_filters_and_scientific_search(self):
        response = self.client.get(reverse("search_species"), {"q": "Panthera", "category": self.category.slug, "habitat": self.habitat.slug, "state": self.state.slug})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["result_count"], 1)
        self.assertContains(response, "Bengal Tiger")
        self.assertContains(response, "selected")
        self.assertEqual(self.client.get(reverse("search_species"), {"category": "not-a-category"}).context["result_count"], 0)

    def test_public_pages_render_with_incomplete_records(self):
        for url in [reverse("home"), reverse("species_list"), reverse("about"), reverse("parks_map"), reverse("species_detail", args=[self.tiger.slug]), reverse("parks_list"), reverse("park_detail", args=[self.park.slug])]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.get(reverse("species_detail", args=[self.tiger.slug]))
        self.assertNotContains(response, "None Years")
        self.tiger.is_verified = False
        self.tiger.save()
        self.assertEqual(self.client.get(reverse("species_detail", args=[self.tiger.slug])).status_code, 404)

    @patch("wildlife.views.catalogue_profile", return_value={})
    def test_map_does_not_turn_state_ranges_into_park_sightings(self, profile):
        response = self.client.get(reverse("parks_map"))
        marker = response.context["map_locations"][0]
        self.assertEqual(marker["species"], [])
        self.park.species.add(self.tiger)
        response = self.client.get(reverse("parks_map"))
        self.assertEqual(response.context["map_locations"][0]["species"][0]["name"], "Bengal Tiger")

    def test_first_run_park_seed_is_repeatable_and_preserves_edits(self):
        from io import StringIO
        call_command("seed_park_locations", stdout=StringIO())
        count = NationalPark.objects.count()
        park = NationalPark.objects.get(name="Kaziranga National Park")
        park.description = "A manually researched description."
        park.save()
        call_command("seed_park_locations", stdout=StringIO())
        park.refresh_from_db()
        self.assertEqual(NationalPark.objects.count(), count)
        self.assertEqual(park.description, "A manually researched description.")

    def test_long_directory_names_fit_postgresql_field_limits(self):
        park = NationalPark(name="A very long descriptive wildlife sanctuary name " * 2, state=self.state, description="Profile")
        park.save()
        park.full_clean()
