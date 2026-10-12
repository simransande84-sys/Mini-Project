"""
complaints/test_water_level.py
==============================
Unit tests for Blynk IoT water-level monitoring and automated email alert integration.
"""
import os
from unittest.mock import patch, MagicMock
import requests
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from complaints.water_level import (
    compute_water_status,
    WaterAlertTracker,
    fetch_blynk_water_data,
    CRITICAL_THRESHOLD,
    LOW_THRESHOLD,
    HIGH_THRESHOLD,
)


class WaterLevelThresholdTests(TestCase):
    """Test strict threshold categorization."""

    def test_critical_threshold(self):
        self.assertEqual(compute_water_status(14.9), "Critical")
        self.assertEqual(compute_water_status(0.0), "Critical")

    def test_low_threshold(self):
        self.assertEqual(compute_water_status(15.0), "Low")
        self.assertEqual(compute_water_status(29.9), "Low")

    def test_normal_threshold(self):
        self.assertEqual(compute_water_status(30.0), "Normal")
        self.assertEqual(compute_water_status(72.5), "Normal")
        self.assertEqual(compute_water_status(90.0), "Normal")

    def test_high_threshold(self):
        self.assertEqual(compute_water_status(90.1), "High")
        self.assertEqual(compute_water_status(100.0), "High")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    ADMIN_EMAIL="admin@hostelsense.edu",
    DEFAULT_FROM_EMAIL="noreply@hostelsense.local",
)
class WaterAlertTrackerEmailTests(TestCase):
    """Test automated low-water email alert logic, anti-spam guard, and recovery."""

    def setUp(self):
        mail.outbox.clear()
        self.tracker = WaterAlertTracker()

    def test_alert_sent_on_first_drop_below_threshold(self):
        # Level drops to 12% (< 15%)
        alert_sent = self.tracker.process_reading(12.0, 12.0, "2026-10-12T10:00:00Z")
        self.assertTrue(alert_sent)
        self.assertTrue(self.tracker.alert_active)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertIn("Critical Low Water Level", email.subject)
        self.assertIn("12.0%", email.body)
        self.assertIn("12.0 cm", email.body)
        self.assertIn("admin@hostelsense.edu", email.to)

    def test_anti_spam_prevents_duplicate_emails_while_level_stays_low(self):
        # First poll below 15%
        self.tracker.process_reading(10.0, 10.0, "2026-10-12T10:00:00Z")
        self.assertEqual(len(mail.outbox), 1)

        # Subsequent polls while still < 15%
        for i in range(5):
            alert_sent = self.tracker.process_reading(9.5, 9.5, f"2026-10-12T10:00:0{i+1}Z")
            self.assertFalse(alert_sent)

        # Still only 1 email sent!
        self.assertEqual(len(mail.outbox), 1)

    def test_alert_rearms_after_recovery(self):
        # 1. Level drops below 15% -> Alert 1 sent
        self.tracker.process_reading(10.0, 10.0, "2026-10-12T10:00:00Z")
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(self.tracker.alert_active)

        # 2. Water tank refilled to 60% -> Recovers, tracker re-arms
        self.tracker.process_reading(60.0, 60.0, "2026-10-12T10:10:00Z")
        self.assertFalse(self.tracker.alert_active)
        self.assertEqual(len(mail.outbox), 1)

        # 3. Water tank drops again to 14% -> Alert 2 sent
        alert_sent = self.tracker.process_reading(14.0, 14.0, "2026-10-12T11:00:00Z")
        self.assertTrue(alert_sent)
        self.assertTrue(self.tracker.alert_active)
        self.assertEqual(len(mail.outbox), 2)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    ADMIN_EMAIL="admin@hostelsense.edu",
    DEFAULT_FROM_EMAIL="noreply@hostelsense.local",
)
class WaterLevelApiEndpointTests(TestCase):
    """Test REST API endpoint GET /api/water-level/."""

    def setUp(self):
        mail.outbox.clear()
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="admin_test",
            password="password123",
            email="admin_test@hostel.edu"
        )
        self.student = User.objects.create_user(
            username="student_test",
            password="password123",
            email="student_test@hostel.edu"
        )

    def test_unauthenticated_request_denied(self):
        resp = self.client.get("/api/water-level/", HTTP_HOST="localhost")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_staff_student_request_denied(self):
        self.client.force_authenticate(user=self.student)
        resp = self.client.get("/api/water-level/", HTTP_HOST="localhost")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(BLYNK_DEVICE_TOKEN="")
    @patch.dict(os.environ, {"BLYNK_DEVICE_TOKEN": ""})
    def test_missing_token_returns_503(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get("/api/water-level/", HTTP_HOST="localhost")
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("error", resp.data)
        self.assertEqual(resp.data["configured"], False)

    @override_settings(BLYNK_DEVICE_TOKEN="test_token_abc")
    @patch("requests.get")
    def test_online_device_with_valid_readings(self, mock_get):
        """1. Online device: isHardwareConnected is true, V0 and V1 are retrieved."""
        def side_effect(url, *args, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            if "isHardwareConnected" in url:
                mock_resp.text = "true"
            else:
                mock_resp.json.return_value = {"v0": 72.0, "v1": 72.0}
            return mock_resp

        mock_get.side_effect = side_effect

        self.client.force_authenticate(user=self.admin)
        resp = self.client.get("/api/water-level/", HTTP_HOST="localhost")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["percentage"], 72.0)
        self.assertEqual(resp.data["water_level_cm"], 72.0)
        self.assertEqual(resp.data["status"], "Normal")
        self.assertEqual(resp.data["device_status"], "Online")
        self.assertEqual(resp.data["source"], "Blynk")
        self.assertIn("timestamp", resp.data)

    @override_settings(BLYNK_DEVICE_TOKEN="test_token_abc")
    @patch("requests.get")
    def test_confirmed_offline_device_does_not_expose_stale_readings(self, mock_get):
        """2. Offline device: isHardwareConnected is false, do not return old readings."""
        mock_hw = MagicMock()
        mock_hw.status_code = 200
        mock_hw.text = "false"
        mock_get.return_value = mock_hw

        self.client.force_authenticate(user=self.admin)
        resp = self.client.get("/api/water-level/", HTTP_HOST="localhost")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["status"], "Offline")
        self.assertEqual(resp.data["device_status"], "Offline")
        self.assertIsNone(resp.data["percentage"])
        self.assertIsNone(resp.data["water_level_cm"])
        self.assertIn("disconnected", resp.data["detail"])
        # Ensure only isHardwareConnected was called, datastream pins were not fetched as live
        self.assertEqual(mock_get.call_count, 1)
        self.assertIn("isHardwareConnected", mock_get.call_args[0][0])
        # Ensure no alert email is triggered for offline state
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(BLYNK_DEVICE_TOKEN="test_token_abc")
    @patch("requests.get")
    def test_connection_status_timeout_or_network_failure(self, mock_get):
        """3. Network timeout: return 503 with Telemetry Unavailable and unknown device status."""
        mock_get.side_effect = requests.RequestException("Connection timed out")

        self.client.force_authenticate(user=self.admin)
        resp = self.client.get("/api/water-level/", HTTP_HOST="localhost")

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(resp.data["status"], "Unavailable")
        self.assertEqual(resp.data["device_status"], "Unknown")
        self.assertIsNone(resp.data["percentage"])
        self.assertIsNone(resp.data["water_level_cm"])
        # Ensure timeout does not trigger an email alert
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(BLYNK_DEVICE_TOKEN="test_token_abc")
    @patch("requests.get")
    def test_timeout_and_offline_do_not_count_as_recovery(self, mock_get):
        """Timeout or offline disconnect must not reset low-water alert state."""
        from complaints.water_level import water_alert_tracker
        water_alert_tracker.reset()

        # Step 1: Online reading below 15% -> Alert sent
        def online_low(url, *args, **kwargs):
            m = MagicMock()
            m.status_code = 200
            if "isHardwareConnected" in url:
                m.text = "true"
            else:
                m.json.return_value = {"v0": 10.0, "v1": 10.0}
            return m

        mock_get.side_effect = online_low
        self.client.force_authenticate(user=self.admin)
        resp1 = self.client.get("/api/water-level/", HTTP_HOST="localhost")
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(water_alert_tracker.alert_active)

        # Step 2: Connection times out (offline/unreachable)
        mock_get.side_effect = requests.RequestException("Timeout")
        resp2 = self.client.get("/api/water-level/", HTTP_HOST="localhost")
        self.assertEqual(resp2.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        # Alert state must NOT have recovered
        self.assertTrue(water_alert_tracker.alert_active)
        self.assertEqual(len(mail.outbox), 1)

        # Step 3: Online reading still at 10% -> Anti-spam prevents duplicate email
        mock_get.side_effect = online_low
        resp3 = self.client.get("/api/water-level/", HTTP_HOST="localhost")
        self.assertEqual(resp3.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)  # Still only 1 email sent!
