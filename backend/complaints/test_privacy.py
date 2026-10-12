"""
backend/complaints/test_privacy.py
Automated tests for object-level privacy and permission enforcement on ComplaintDetailView,
plus D4 field-level privacy tests (submitted_by_username / room_no masking for public complaints).
"""
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from complaints.models import Complaint, StudentProfile


class ComplaintPrivacyPermissionsTests(APITestCase):
    """Verifies that private complaints are visible only to owners and staff."""

    def setUp(self):
        # 1. Create Student A (owner of private complaint)
        self.student_a = User.objects.create_user(
            username="student_a", password="password123", first_name="Student A"
        )
        StudentProfile.objects.create(
            user=self.student_a, roll_no="SA101", block="A", floor="First", room_no="101", profile_complete=True
        )

        # 2. Create Student B (other student)
        self.student_b = User.objects.create_user(
            username="student_b", password="password123", first_name="Student B"
        )
        StudentProfile.objects.create(
            user=self.student_b, roll_no="SB102", block="B", floor="Second", room_no="102", profile_complete=True
        )

        # 3. Create Admin / Staff user
        self.admin = User.objects.create_superuser(
            username="admin_staff", password="password123", email="admin@example.com"
        )

        # 4. Create Private Complaint owned by Student A
        self.private_complaint = Complaint.objects.create(
            submitted_by=self.student_a,
            complaint_text="Private issue in room 101",
            complaint_type="Private",
            category="Security",
            block="A",
            floor="First",
            room_no="101",
            predicted_priority="High",
            status="Pending"
        )

        # 5. Create Public Complaint owned by Student A
        self.public_complaint = Complaint.objects.create(
            submitted_by=self.student_a,
            complaint_text="Water cooler leaking near room 101",
            complaint_type="Public",
            category="Water Cooler",
            block="A",
            floor="First",
            room_no="101",
            predicted_priority="Medium",
            status="Pending"
        )

    def test_owner_can_access_own_private_complaint(self):
        """Student A (owner) should get HTTP 200 OK for their own private complaint."""
        self.client.force_authenticate(user=self.student_a)
        url = reverse("complaint-detail", kwargs={"pk": self.private_complaint.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.private_complaint.pk)

    def test_other_student_cannot_access_private_complaint(self):
        """Student B (non-owner) should get HTTP 404 Not Found for Student A's private complaint."""
        self.client.force_authenticate(user=self.student_b)
        url = reverse("complaint-detail", kwargs={"pk": self.private_complaint.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_student_can_access_public_complaint(self):
        """Student B should get HTTP 200 OK when requesting Student A's public complaint."""
        self.client.force_authenticate(user=self.student_b)
        url = reverse("complaint-detail", kwargs={"pk": self.public_complaint.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_can_access_any_private_complaint(self):
        """Admin staff should get HTTP 200 OK when requesting Student A's private complaint."""
        self.client.force_authenticate(user=self.admin)
        url = reverse("complaint-detail", kwargs={"pk": self.private_complaint.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admin_student_cannot_delete_complaint(self):
        """Student B should get HTTP 403 Forbidden when attempting DELETE on a complaint."""
        self.client.force_authenticate(user=self.student_b)
        url = reverse("complaint-detail", kwargs={"pk": self.public_complaint.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PublicComplaintD4PrivacyTests(APITestCase):
    """
    D4: For public complaints viewed by non-owner / non-staff:
      - submitted_by_username must be "Anonymous"
      - room_no must be "" (blank)
    For the owner and staff, real values are shown.
    block and floor remain visible to everyone.
    """

    def setUp(self):
        # Owner (Student A)
        self.owner = User.objects.create_user(
            username="owner_user", password="pass123", first_name="Alice"
        )
        StudentProfile.objects.create(
            user=self.owner, roll_no="OW001", block="A", floor="First", room_no="A101",
            profile_complete=True,
        )

        # Other student
        self.other = User.objects.create_user(
            username="other_user", password="pass123", first_name="Bob"
        )
        StudentProfile.objects.create(
            user=self.other, roll_no="OT002", block="B", floor="Second", room_no="B201",
            profile_complete=True,
        )

        # Staff / admin
        self.staff = User.objects.create_superuser(
            username="staff_user", password="pass123", email="staff@test.com"
        )

        # A public complaint submitted by owner
        self.public_c = Complaint.objects.create(
            submitted_by=self.owner,
            complaint_text="The water supply is disrupted in the entire block.",
            complaint_type="Public",
            category="Water Cooler",
            block="A",
            floor="First",
            room_no="A101",
            predicted_priority="Medium",
            status="Pending",
        )
        self.url = reverse("complaint-detail", kwargs={"pk": self.public_c.pk})

    # ── Anonymous (unauthenticated) viewer ────────────────────────────────────
    def test_anonymous_sees_anonymous_username(self):
        """Unauthenticated request should get submitted_by_username='Anonymous'."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["submitted_by_username"], "Anonymous")

    def test_anonymous_sees_blank_room_no(self):
        """Unauthenticated request should get room_no=''."""
        response = self.client.get(self.url)
        self.assertEqual(response.data["room_no"], "")

    def test_anonymous_still_sees_block_and_floor(self):
        """block and floor should always be visible."""
        response = self.client.get(self.url)
        self.assertEqual(response.data["block"], "A")
        self.assertEqual(response.data["floor"], "First")

    # ── Other student (authenticated non-owner) ───────────────────────────────
    def test_other_student_sees_anonymous_username(self):
        """Non-owner student should see submitted_by_username='Anonymous'."""
        self.client.force_authenticate(user=self.other)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["submitted_by_username"], "Anonymous")

    def test_other_student_sees_blank_room_no(self):
        """Non-owner student should see room_no=''."""
        self.client.force_authenticate(user=self.other)
        response = self.client.get(self.url)
        self.assertEqual(response.data["room_no"], "")

    # ── Owner ─────────────────────────────────────────────────────────────────
    def test_owner_sees_own_real_username(self):
        """Owner should see their real first_name as submitted_by_username."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["submitted_by_username"], "Alice")

    def test_owner_sees_own_real_room_no(self):
        """Owner should see the actual room_no."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.data["room_no"], "A101")

    # ── Admin / staff ─────────────────────────────────────────────────────────
    def test_staff_sees_real_username(self):
        """Staff should see the real submitted_by_username."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["submitted_by_username"], "Alice")

    def test_staff_sees_real_room_no(self):
        """Staff should see the actual room_no."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(self.url)
        self.assertEqual(response.data["room_no"], "A101")
