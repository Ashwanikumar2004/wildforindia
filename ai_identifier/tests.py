from io import BytesIO
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from ai_identifier.models import Identification, IdentificationResult
from ai_identifier.predictor import identify_image
from wildlife.models import Category, ConservationStatus, Species


class IdentifierPageTests(TestCase):
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
        )

    def tearDown(self):
        # MEDIA_ROOT is the project's ignored media/ directory. Remove files
        # explicitly so the tests leave no local uploads behind.
        for identification in Identification.objects.all():
            if identification.image:
                identification.image.delete(save=False)
        super().tearDown()

    def test_identifier_page_loads_with_photo_upload_form(self):
        response = self.client.get(reverse("ai_identifier"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI Wildlife Identifier")
        self.assertContains(response, "Identify species")
        self.assertContains(response, "multipart/form-data")

    def make_png_upload(self):
        image_buffer = BytesIO()
        Image.new("RGB", (32, 32), color="orange").save(image_buffer, format="PNG")
        return SimpleUploadedFile(
            "tiger.png",
            image_buffer.getvalue(),
            content_type="image/png",
        )

    @patch("ai_identifier.views.identify_image")
    def test_valid_photo_shows_matched_species_details(self, identify_image):
        identify_image.return_value = [
            {"label": "Bengal Tiger", "score": 0.91, "species": self.species}
        ]

        response = self.client.post(
            reverse("ai_identifier"),
            {"image": self.make_png_upload()},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bengal Tiger")
        self.assertContains(response, "View species details")
        identify_image.assert_called_once()
        saved = Identification.objects.get(user=self.user)
        self.assertTrue(saved.image.name.startswith("identifications/"))
        self.assertEqual(saved.results.count(), 1)
        self.assertEqual(saved.results.get().species, self.species)
        self.assertEqual(saved.results.get().rank, 1)

    @patch("ai_identifier.views.identify_image")
    def test_unmatched_prediction_is_not_presented_as_a_species(self, identify_image):
        identify_image.return_value = [
            {"label": "not a wildlife species or no animal is visible", "score": 0.82, "species": None}
        ]

        response = self.client.post(
            reverse("ai_identifier"),
            {"image": self.make_png_upload()},
        )

        self.assertContains(response, "AI suggestion not in WildDex yet")
        self.assertNotContains(response, "View species details")
        self.assertEqual(Identification.objects.count(), 1)
        self.assertIsNone(IdentificationResult.objects.get().species)

    @patch("ai_identifier.predictor._get_speciesnet")
    def test_predictor_links_speciesnet_taxonomy_to_catalogue(self, get_speciesnet):
        image = Image.new("RGB", (32, 32))
        model = Mock()
        model.predict.return_value = {
            "predictions": [
                {
                    "detections": [
                        {
                            "raw_classifications": {
                                "classes": [
                                    "00000000-0000-0000-0000-000000000000;mammalia;carnivora;felidae;panthera;tigris;bengal tiger"
                                ],
                                "scores": [0.91],
                            }
                        }
                    ]
                }
            ]
        }
        get_speciesnet.return_value = model

        results = identify_image(image, [self.species])

        model.predict.assert_called_once()
        self.assertEqual(
            model.predict.call_args.kwargs["instances_dict"]["instances"][0]["country"],
            "IND",
        )
        self.assertEqual(results[0]["species"], self.species)

    def test_history_shows_only_the_signed_in_users_identifications(self):
        other_user = get_user_model().objects.create_user(
            username="another_user",
            password="Strong-Example-Password-42!",
        )
        own = Identification.objects.create(
            user=self.user,
            image=self.make_png_upload(),
        )
        IdentificationResult.objects.create(
            identification=own,
            species=self.species,
            label="Bengal Tiger",
            score=0.9,
            rank=1,
        )
        other = Identification.objects.create(
            user=other_user,
            image=self.make_png_upload(),
        )
        IdentificationResult.objects.create(
            identification=other,
            species=self.species,
            label="Bengal Tiger",
            score=0.9,
            rank=1,
        )

        response = self.client.get(reverse("identification_history"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["identifications"]), 1)
        self.assertEqual(response.context["identifications"][0].pk, own.pk)

    def test_identifier_requires_sign_in_to_save_a_photo(self):
        self.client.logout()

        response = self.client.get(reverse("ai_identifier"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_user_cannot_view_another_users_photo(self):
        other_user = get_user_model().objects.create_user(
            username="photo_owner",
            password="Strong-Example-Password-42!",
        )
        identification = Identification.objects.create(
            user=other_user,
            image=self.make_png_upload(),
        )

        response = self.client.get(
            reverse("identification_image", args=[identification.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_user_can_delete_their_identification_and_uploaded_file(self):
        identification = Identification.objects.create(
            user=self.user,
            image=self.make_png_upload(),
        )

        response = self.client.post(
            reverse("delete_identification", args=[identification.pk])
        )

        self.assertRedirects(response, reverse("identification_history"))
        self.assertFalse(Identification.objects.filter(pk=identification.pk).exists())
        self.assertFalse(identification.image.storage.exists(identification.image.name))
