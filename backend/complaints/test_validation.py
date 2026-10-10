"""
backend/complaints/test_validation.py
======================================
Automated tests for complaint text validation and priority assignment across API endpoints:
  1. POST /api/predict/
  2. POST /api/complaints/
  3. PUT / PATCH /api/complaints/<id>/
"""
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from complaints.models import Complaint, StudentProfile


class ComplaintTextValidationAndPriorityTests(APITestCase):
    """Verifies text quality validation, length bounds, and LinearSVC priority assignment."""

    def setUp(self):
        # 1. Create a student with a complete hostel profile
        self.student = User.objects.create_user(
            username="student_val", password="password123", first_name="Val Student"
        )
        StudentProfile.objects.create(
            user=self.student,
            roll_no="VAL101",
            block="A",
            floor="First",
            room_no="101",
            profile_complete=True,
        )

        # 2. Create an admin user for update tests
        self.admin = User.objects.create_superuser(
            username="admin_val", password="password123", email="adminval@example.com"
        )

        # 3. Create an existing complaint for update testing
        self.existing_complaint = Complaint.objects.create(
            submitted_by=self.student,
            complaint_text="Valid existing complaint text here.",
            complaint_type="Public",
            category="Cleanliness",
            block="A",
            floor="First",
            room_no="101",
            predicted_priority="Medium",
            status="Pending",
        )

    # ── 1. Meaningless & Gibberish Description Rejections ─────────────────────

    def test_meaningless_gibberish_m_h_gh_g_rejected(self):
        """'m h gh g' should be rejected with HTTP 400 Bad Request."""
        self.client.force_authenticate(user=self.student)
        url = reverse("complaint-list-create")
        payload = {
            "complaint_text": "m h gh g",
            "category": "Cleanliness",
            "complaint_type": "Public",
            "duration": "1 day",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_meaningless_gibberish_gdggf_trf_rejected(self):
        """'gdggf trf' should be rejected with HTTP 400 Bad Request."""
        self.client.force_authenticate(user=self.student)
        url = reverse("complaint-list-create")
        payload = {
            "complaint_text": "gdggf trf",
            "category": "Cleanliness",
            "complaint_type": "Public",
            "duration": "1 day",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_meaningless_gibberish_simran_htfht_rejected(self):
        """'simran htfht' should be rejected with HTTP 400 Bad Request."""
        self.client.force_authenticate(user=self.student)
        url = reverse("complaint-list-create")
        payload = {
            "complaint_text": "simran htfht",
            "category": "Cleanliness",
            "complaint_type": "Public",
            "duration": "1 day",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── 2. Regression Check for Legitimate Descriptions & Abbreviations ────────

    def test_regression_legitimate_descriptions_accepted(self):
        """Verifies legitimate descriptions including technical terms, words like rhythm, and abbreviations are accepted."""
        self.client.force_authenticate(user=self.student)
        url = reverse("complaint-list-create")

        legitimate_inputs = [
            ("The rhythm of the exhaust fan is irregular", "Electricity"),
            ("The washroom tap is leaking", "Washroom"),
            ("TV in room is not working", "Furniture"),
            ("Water supply problem in hostel", "Water Cooler"),
            ("The MCB trips whenever we switch on the lights", "Electricity"),
        ]

        for text, category in legitimate_inputs:
            payload = {
                "complaint_text": text,
                "category": category,
                "complaint_type": "Public",
                "duration": "1 hour",
            }
            response = self.client.post(url, payload, format="json")
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                f"Legitimate description '{text}' was incorrectly rejected.",
            )

    # ── 3. Empty, Short, and Long Description Rejections ───────────────────────

    def test_empty_and_whitespace_text_rejected(self):
        """Empty or whitespace-only text should return HTTP 400 Bad Request."""
        self.client.force_authenticate(user=self.student)
        url = reverse("complaint-list-create")
        payload = {
            "complaint_text": "         ",
            "category": "Mess",
            "complaint_type": "Public",
            "duration": "1 hour",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_text_too_short_rejected(self):
        """Text < 10 characters should return HTTP 400 Bad Request."""
        self.client.force_authenticate(user=self.student)
        url = reverse("complaint-list-create")
        payload = {
            "complaint_text": "Too short",
            "category": "Mess",
            "complaint_type": "Public",
            "duration": "1 hour",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_text_too_long_rejected(self):
        """Text > 1000 characters should return HTTP 400 Bad Request."""
        self.client.force_authenticate(user=self.student)
        url = reverse("complaint-list-create")
        payload = {
            "complaint_text": "B" * 1001,
            "category": "Mess",
            "complaint_type": "Public",
            "duration": "1 hour",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── 4. Priority Predictions for Valid Complaints ──────────────────────────

    def test_valid_low_urgency_complaint_prediction(self):
        """Low-urgency complaint should be accepted and assigned Low priority by LinearSVC."""
        self.client.force_authenticate(user=self.student)
        url = reverse("complaint-list-create")
        payload = {
            "complaint_text": "The study table chair leg is wobbling.",
            "category": "Furniture",
            "complaint_type": "Public",
            "duration": "2 hours",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["predicted_priority"], "Low")

    def test_valid_medium_urgency_complaint_prediction(self):
        """Medium-urgency complaint should be accepted and assigned Medium priority by LinearSVC."""
        self.client.force_authenticate(user=self.student)
        url = reverse("complaint-list-create")
        payload = {
            "complaint_text": "Light bulb in room needs replacement",
            "category": "Electricity",
            "complaint_type": "Public",
            "duration": "1 day",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["predicted_priority"], "Medium")

    def test_valid_high_urgency_complaint_prediction(self):
        """High-urgency complaint should be accepted and assigned High priority by LinearSVC."""
        self.client.force_authenticate(user=self.student)
        url = reverse("complaint-list-create")
        payload = {
            "complaint_text": "The water tap in my bathroom is leaking",
            "category": "Washroom",
            "complaint_type": "Public",
            "duration": "1 hour",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["predicted_priority"], "High")

    def test_complaint_without_urgency_keywords_not_unconditionally_medium(self):
        """A valid complaint without explicit urgency keywords receives Low from LinearSVC (not Medium fallback)."""
        self.client.force_authenticate(user=self.student)
        url = reverse("complaint-list-create")
        payload = {
            "complaint_text": "The dustbin near the entrance is full and smells bad.",
            "category": "Cleanliness",
            "complaint_type": "Public",
            "duration": "4 days",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["predicted_priority"], "Low")

    # ── 5. Endpoint Consistency (Predict, Create, Update) ─────────────────────

    def test_predict_endpoint_validation_consistency(self):
        """POST /api/predict/ enforces gibberish check consistently."""
        self.client.force_authenticate(user=self.student)
        url = reverse("predict")

        # Invalid gibberish
        gib_response = self.client.post(url, {"complaint_text": "simran htfht", "category": "Other"}, format="json")
        self.assertEqual(gib_response.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid description
        val_response = self.client.post(
            url,
            {"complaint_text": "The water tap in my bathroom is leaking", "category": "Washroom"},
            format="json",
        )
        self.assertEqual(val_response.status_code, status.HTTP_200_OK)
        self.assertIn("predicted_priority", val_response.data)

    def test_update_endpoint_validation_consistency(self):
        """PATCH /api/complaints/<id>/ enforces gibberish check consistently."""
        self.client.force_authenticate(user=self.admin)
        url = reverse("complaint-detail", kwargs={"pk": self.existing_complaint.pk})

        # Invalid gibberish update
        gib_response = self.client.patch(url, {"complaint_text": "gdggf trf ddd"}, format="json")
        self.assertEqual(gib_response.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid update
        val_response = self.client.patch(
            url,
            {"complaint_text": "Updated valid text for bathroom tap leakage issue."},
            format="json",
        )
        self.assertEqual(val_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            val_response.data["complaint_text"],
            "Updated valid text for bathroom tap leakage issue.",
        )
