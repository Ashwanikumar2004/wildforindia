from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class AccountPageTests(TestCase):
    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back")

    def test_register_page_loads(self):
        response = self.client.get(reverse("register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Join WildFIndia")

    def test_register_creates_user_and_logs_them_in(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "wildlife_learner",
                "password1": "Strong-Example-Password-42!",
                "password2": "Strong-Example-Password-42!",
            },
        )

        self.assertRedirects(response, reverse("wilddex"))
        self.assertTrue(User.objects.filter(username="wildlife_learner").exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_accepts_valid_credentials(self):
        User.objects.create_user(username="ranger", password="Strong-Example-Password-42!")

        response = self.client.post(
            reverse("login"),
            {"username": "ranger", "password": "Strong-Example-Password-42!"},
        )

        self.assertRedirects(response, reverse("wilddex"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_rejects_external_next_url(self):
        User.objects.create_user(username="ranger", password="Strong-Example-Password-42!")

        response = self.client.post(
            f"{reverse('login')}?next=https://example.com/",
            {
                "username": "ranger",
                "password": "Strong-Example-Password-42!",
                "next": "https://example.com/",
            },
        )

        self.assertRedirects(response, reverse("wilddex"))

    def test_logout_requires_post_and_returns_home(self):
        User.objects.create_user(username="ranger", password="Strong-Example-Password-42!")
        self.client.login(username="ranger", password="Strong-Example-Password-42!")

        get_response = self.client.get(reverse("logout"))
        post_response = self.client.post(reverse("logout"))

        self.assertEqual(get_response.status_code, 405)
        self.assertRedirects(post_response, reverse("home"))
