from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccountSettingsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="explorer", password="Original-Password-42!")

    def test_profile_requires_login_and_updates_only_current_user(self):
        self.assertEqual(self.client.get(reverse("profile")).status_code, 302)
        self.client.force_login(self.user)
        response = self.client.post(reverse("profile"), {"first_name": "River", "last_name": "Explorer", "email": "river@example.org", "is_staff": "true"})
        self.assertRedirects(response, reverse("profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "River")
        self.assertFalse(self.user.is_staff)

    def test_password_change_checks_old_password_and_keeps_session(self):
        self.client.force_login(self.user)
        url = reverse("password_change")
        payload = {"old_password": "wrong", "new_password1": "New-Unique-Password-77!", "new_password2": "New-Unique-Password-77!"}
        self.assertEqual(self.client.post(url, payload).status_code, 200)
        payload["old_password"] = "Original-Password-42!"
        self.assertRedirects(self.client.post(url, payload), reverse("password_change_done"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("New-Unique-Password-77!"))
        self.assertEqual(self.client.get(reverse("profile")).status_code, 200)
