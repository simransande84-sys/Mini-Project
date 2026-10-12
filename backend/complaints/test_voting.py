"""
backend/complaints/test_voting.py
==================================
Automated unit tests for Phase 4A:
- Derived support count calculations
- Vote creation and deletion
- User deletion impact on support count
- Duplicate voting (HTTP 409 Conflict)
"""
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from complaints.models import Complaint, ComplaintVote


class DerivedSupportCountTests(APITestCase):

    def setUp(self):
        # Create student users
        self.student_a = User.objects.create_user(
            username="student_a",
            password="password123",
            first_name="Alice"
        )
        self.student_b = User.objects.create_user(
            username="student_b",
            password="password123",
            first_name="Bob"
        )

        # Create a public complaint (simulating imported or newly created complaint with 0 votes)
        self.complaint = Complaint.objects.create(
            complaint_text="Water leakage in 2nd floor corridor",
            complaint_type="Public",
            category="Leakage",
            block="A",
            floor="Second",
            predicted_priority="Low",
            submitted_by=self.student_a,
        )

    def test_first_vote_on_imported_complaint_gives_count_1(self):
        """First vote on a complaint with 0 votes returns support_count = 1 without crash."""
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(f"/api/complaints/{self.complaint.id}/vote/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["support_count"], 1)

    def test_vote_then_unvote_returns_count_0(self):
        """Voting then unvoting returns support_count = 0."""
        self.client.force_authenticate(user=self.student_a)
        post_resp = self.client.post(f"/api/complaints/{self.complaint.id}/vote/")
        self.assertEqual(post_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(post_resp.data["support_count"], 1)

        del_resp = self.client.delete(f"/api/complaints/{self.complaint.id}/vote/")
        self.assertEqual(del_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(del_resp.data["support_count"], 0)

    def test_deleting_user_who_voted_reduces_count(self):
        """Deleting a user who voted automatically reduces the derived support count via CASCADE."""
        self.client.force_authenticate(user=self.student_a)
        self.client.post(f"/api/complaints/{self.complaint.id}/vote/")

        self.client.force_authenticate(user=self.student_b)
        self.client.post(f"/api/complaints/{self.complaint.id}/vote/")

        # Verify count is 2 before deletion
        detail_resp = self.client.get(f"/api/complaints/{self.complaint.id}/")
        self.assertEqual(detail_resp.data["support_count"], 2)

        # Delete student_a
        self.student_a.delete()

        # Verify count drops to 1
        detail_resp_after = self.client.get(f"/api/complaints/{self.complaint.id}/")
        self.assertEqual(detail_resp_after.data["support_count"], 1)

    def test_two_different_users_voting_gives_count_2(self):
        """Two different users voting on the same complaint gives support_count = 2."""
        self.client.force_authenticate(user=self.student_a)
        resp1 = self.client.post(f"/api/complaints/{self.complaint.id}/vote/")
        self.assertEqual(resp1.data["support_count"], 1)

        self.client.force_authenticate(user=self.student_b)
        resp2 = self.client.post(f"/api/complaints/{self.complaint.id}/vote/")
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp2.data["support_count"], 2)

    def test_same_user_voting_twice_returns_409(self):
        """The same user attempting to vote twice on the same complaint receives HTTP 409 Conflict."""
        self.client.force_authenticate(user=self.student_a)
        resp1 = self.client.post(f"/api/complaints/{self.complaint.id}/vote/")
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        resp2 = self.client.post(f"/api/complaints/{self.complaint.id}/vote/")
        self.assertEqual(resp2.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(resp2.data["error"], "You have already supported this complaint.")
