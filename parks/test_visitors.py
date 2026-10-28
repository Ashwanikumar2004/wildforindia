from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import NationalPark, ParkReview, State


class VisitorReviewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="visitor", password="Example-Secret-2026!")
        self.state = State.objects.create(name="Assam", code="IN-AS", region="North-East")
        self.park = NationalPark.objects.create(name="Example", state=self.state, description="A forest park")
        self.url = reverse("park_detail", args=[self.park.slug])
        self.payload = {"rating": "5", "review": "We followed the marked trails and enjoyed the forest.", "visit_date": "2025-01-10"}

    def test_login_required_and_review_moderation(self):
        self.assertEqual(self.client.post(self.url, self.payload).status_code, 302)
        self.assertFalse(ParkReview.objects.exists())
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(self.url, self.payload).status_code, 302)
        review = ParkReview.objects.get()
        self.assertFalse(review.is_verified)
        self.assertEqual(review.user, self.user)
        self.client.logout()
        self.assertNotContains(self.client.get(self.url), self.payload["review"])
        review.is_verified = True
        review.save()
        self.assertContains(self.client.get(self.url), self.payload["review"])

    def test_updates_do_not_duplicate_reviews_and_need_reapproval(self):
        self.client.force_login(self.user)
        self.client.post(self.url, self.payload)
        ParkReview.objects.update(is_verified=True)
        self.client.post(self.url, {**self.payload, "rating": "4"})
        self.assertEqual(ParkReview.objects.count(), 1)
        self.assertFalse(ParkReview.objects.get().is_verified)
        self.assertEqual(ParkReview.objects.get().rating, 4)

    def test_invalid_rating_future_date_and_inactive_park(self):
        self.client.force_login(self.user)
        for extra in [{"rating": "9"}, {"visit_date": (timezone.localdate() + timedelta(days=1)).isoformat()}]:
            self.assertEqual(self.client.post(self.url, {**self.payload, **extra}).status_code, 200)
            self.assertFalse(ParkReview.objects.exists())
        self.park.is_active = False
        self.park.save()
        self.assertEqual(self.client.get(self.url).status_code, 404)
