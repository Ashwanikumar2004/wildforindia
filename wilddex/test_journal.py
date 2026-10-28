from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from wildlife.models import Category, ConservationStatus, Species
from .models import WildDexEntry


class PrivateJournalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_user(username="owner")
        cls.other = get_user_model().objects.create_user(username="other")
        species = Species.objects.create(common_name="Tiger", scientific_name="Panthera tigris", category=Category.objects.create(name="Mammal"), conservation_status=ConservationStatus.objects.create(name="Endangered", code="EN"), short_description="Forest cat", description="A forest predator", is_verified=True, xp_reward=200)
        cls.entry = WildDexEntry.objects.create(user=cls.owner, species=species, notes="A private note.")

    def test_entry_is_private_for_reads_writes_removal_and_export(self):
        self.client.force_login(self.other)
        url = reverse("wilddex_entry", args=[self.entry.pk])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(url, {"notes": "changed"}).status_code, 404)
        self.assertEqual(self.client.post(reverse("wilddex_remove", args=[self.entry.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("wilddex_export")), "private note")

    def test_edit_export_and_remove_keeps_xp_consistent(self):
        self.client.force_login(self.owner)
        url = reverse("wilddex_entry", args=[self.entry.pk])
        self.assertEqual(self.client.post(url, {"notes": "=unsafe_formula()", "observed_on": "2025-01-10", "location": "Forest"}).status_code, 302)
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.location, "Forest")
        self.assertContains(self.client.get(reverse("wilddex_export")), "'=unsafe_formula()")
        self.assertEqual(self.client.get(reverse("wilddex")).context["experience_points"], 200)
        remove_url = reverse("wilddex_remove", args=[self.entry.pk])
        self.assertEqual(self.client.get(remove_url).status_code, 405)
        self.assertEqual(self.client.post(remove_url).status_code, 302)
        self.assertEqual(self.client.get(reverse("wilddex")).context["experience_points"], 0)

    def test_future_observation_date_does_not_save(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("wilddex_entry", args=[self.entry.pk]), {"notes": "updated", "observed_on": (timezone.localdate() + timedelta(days=1)).isoformat()})
        self.assertEqual(response.status_code, 200)
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.notes, "A private note.")

    def test_collection_filters_do_not_change_total_progress(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("wilddex"), {"status": "undiscovered"})
        self.assertEqual(response.context["page_obj"].paginator.count, 0)
        self.assertEqual(response.context["discovery_count"], 1)
