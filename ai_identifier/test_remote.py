from concurrent.futures import TimeoutError
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings
from PIL import Image

from .predictor import RemoteInferenceUnavailable, identify_image


@override_settings(
    HF_SPACE_ID="Ashwanikumar21/wildforindia-ai-test",
    HF_TOKEN="",
    HF_INFERENCE_TIMEOUT=90,
)
class RemotePredictionTests(SimpleTestCase):
    def setUp(self):
        self.species = SimpleNamespace(
            common_name="Bengal Tiger",
            scientific_name="Panthera tigris tigris",
            ai_label="bengal tiger",
        )
        self.payload = {"predictions": [{"detections": [{
            "raw_classifications": {
                "classes": ["id;mammalia;carnivora;felidae;panthera;tigris;tiger"],
                "scores": [0.9989],
            }
        }]}]}
        self.image = Image.new("RGB", (32, 32), "orange")

    @patch("ai_identifier.predictor._get_speciesnet")
    @patch("gradio_client.Client")
    def test_remote_result_matches_catalogue_without_loading_local_model(self, client_class, local):
        client = client_class.return_value
        client.submit.return_value.result.return_value = self.payload
        uploaded_paths = []

        def upload(path):
            uploaded_paths.append(path)
            with Image.open(path) as photo:
                self.assertEqual(photo.format, "JPEG")
                self.assertFalse(photo.getexif())
            return {"path": path}

        with patch("gradio_client.handle_file", side_effect=upload):
            result = identify_image(self.image, [self.species])

        local.assert_not_called()
        self.assertIs(result[0]["species"], self.species)
        self.assertEqual(result[0]["score"], 0.9989)
        self.assertEqual(client.submit.call_args.kwargs["api_name"], "/identify")
        client.submit.return_value.result.assert_called_once_with(timeout=90)
        client.close.assert_called_once()
        self.assertFalse(Path(uploaded_paths[0]).exists())

    @patch("gradio_client.Client")
    def test_timeout_cancels_job_and_closes_client(self, client_class):
        client = client_class.return_value
        client.submit.return_value.result.side_effect = TimeoutError()
        with self.assertRaises(RemoteInferenceUnavailable):
            identify_image(self.image, [self.species])
        client.submit.return_value.cancel.assert_called_once()
        client.close.assert_called_once()

    @patch("gradio_client.Client")
    def test_quota_failure_is_not_returned_as_no_animal(self, client_class):
        client_class.return_value.submit.return_value.result.side_effect = RuntimeError("GPU quota exceeded")
        with self.assertRaises(RemoteInferenceUnavailable):
            identify_image(self.image, [self.species])

    @patch("gradio_client.Client")
    def test_invalid_and_failed_responses_are_rejected(self, client_class):
        for payload in (None, {}, {"predictions": []}, {"predictions": [{"errors": ["failed"]}]}):
            with self.subTest(payload=payload):
                client_class.return_value.submit.return_value.result.return_value = payload
                with self.assertRaises(RemoteInferenceUnavailable):
                    identify_image(self.image, [self.species])

    @patch("gradio_client.Client")
    def test_valid_no_detection_result_is_empty(self, client_class):
        client_class.return_value.submit.return_value.result.return_value = {
            "predictions": [{"detections": []}]
        }
        self.assertEqual(identify_image(self.image, [self.species]), [])

    @override_settings(HF_TOKEN="test-secret")
    @patch("gradio_client.Client")
    def test_token_is_only_passed_to_server_side_client(self, client_class):
        client_class.return_value.submit.return_value.result.return_value = self.payload
        identify_image(self.image, [self.species])
        self.assertEqual(client_class.call_args.kwargs["token"], "test-secret")
