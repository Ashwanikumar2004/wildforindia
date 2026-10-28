from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from ai_identifier.models import Identification, IdentificationResult
from wildlife.models import Category, ConservationStatus, Species

from .models import WildDexEntry


class WildDexPageTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="wildlife_learner",
            password="Strong-Example-Password-42!",
        )
        self.client.force_login(self.user)
        category = Category.objects.create(name="Mammal")
        status = ConservationStatus.objects.create(name="Endangered", code="EN")
        self.species = Species.objects.create(
            common_name="Bengal Tiger",
            scientific_name="Panthera tigris tigris",
            category=category,
            conservation_status=status,
            short_description="A large wild cat found in India.",
            description="Species details for the test.",
            is_verified=True,
            xp_reward=150,
        )

    def make_png_upload(self):
        buffer = BytesIO()
        Image.new("RGB", (16, 16), color="green").save(buffer, format="PNG")
        return SimpleUploadedFile("wildlife.png", buffer.getvalue(), content_type="image/png")

    def tearDown(self):
        for identification in Identification.objects.all():
            if identification.image:
                identification.image.delete(save=False)
        super().tearDown()

    def make_identification(self, user=None, species=None):
        identification = Identification.objects.create(
            user=user or self.user,
            image=self.make_png_upload(),
        )
        IdentificationResult.objects.create(
            identification=identification,
            species=species or self.species,
            label="Bengal Tiger (Panthera tigris tigris)",
            score=0.91,
            rank=1,
        )
        return identification

    def test_wilddex_uses_verified_catalogue_and_starts_empty(self):
        response = self.client.get(reverse("wilddex"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your WildDex")
        self.assertContains(response, "Undiscovered species")
        self.assertNotContains(response, "Demo data")
        self.assertEqual(response.context["discovery_count"], 0)
        self.assertEqual(response.context["experience_points"], 0)

    def test_user_can_confirm_a_species_from_their_own_prediction(self):
        identification = self.make_identification()

        response = self.client.post(
            reverse("wilddex_add_discovery", args=[identification.pk]),
            {"species_id": self.species.pk},
        )

        self.assertRedirects(response, reverse("wilddex"))
        entry = WildDexEntry.objects.get(user=self.user, species=self.species)
        self.assertEqual(entry.source_identification, identification)

        collection_response = self.client.get(reverse("wilddex"))
        self.assertEqual(collection_response.context["discovery_count"], 1)
        self.assertEqual(collection_response.context["experience_points"], 150)
        self.assertContains(collection_response, "Discovered")

    def test_duplicate_confirmations_do_not_duplicate_discovery_or_xp(self):
        identification = self.make_identification()
        url = reverse("wilddex_add_discovery", args=[identification.pk])
        payload = {"species_id": self.species.pk}

        self.client.post(url, payload)
        self.client.post(url, payload)

        self.assertEqual(WildDexEntry.objects.filter(user=self.user).count(), 1)
        response = self.client.get(reverse("wilddex"))
        self.assertEqual(response.context["experience_points"], 150)

    def test_user_cannot_add_species_from_another_users_photo(self):
        other_user = get_user_model().objects.create_user(
            username="other_user",
            password="Strong-Example-Password-42!",
        )
        identification = self.make_identification(user=other_user)

        response = self.client.post(
            reverse("wilddex_add_discovery", args=[identification.pk]),
            {"species_id": self.species.pk},
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(WildDexEntry.objects.exists())

    def test_species_not_in_prediction_cannot_be_added(self):
        identification = Identification.objects.create(
            user=self.user,
            image=self.make_png_upload(),
        )

        response = self.client.post(
            reverse("wilddex_add_discovery", args=[identification.pk]),
            {"species_id": self.species.pk},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(WildDexEntry.objects.exists())

    def test_invalid_species_id_returns_bad_request_instead_of_server_error(self):
        identification = Identification.objects.create(
            user=self.user,
            image=self.make_png_upload(),
        )

        response = self.client.post(
            reverse("wilddex_add_discovery", args=[identification.pk]),
            {"species_id": "not-a-uuid"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(WildDexEntry.objects.exists())
