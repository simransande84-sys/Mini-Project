"""
complaints/water_level.py
=========================
Dedicated service for Blynk Cloud IoT water-level integration.

Features:
- Verifies real hardware connection status via Blynk `isHardwareConnected` before treating telemetry as live.
- Avoids exposing stale/retained cloud values when ESP32 is offline.
- Fetches real-time datastreams V0 (percentage) and V1 (height in cm) from Blynk Cloud API.
- Evaluates status based on strict thresholds:
    * Below 15%: Critical
    * 15% to below 30%: Low
    * 30% to 90%: Normal
    * Above 90%: High
- Automatic low-water email alert to ADMIN_EMAIL when level < 15%.
- Anti-spam guard: fires alert once when dropping below 15%, resets only after recovery >= 15%.
- Safe error handling: timeouts or offline states do NOT trigger recovery or leak credentials.
"""
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)

# Constants
CRITICAL_THRESHOLD = 15.0
LOW_THRESHOLD = 30.0
HIGH_THRESHOLD = 90.0
TANK_HEIGHT_CM = 100.0


def compute_water_status(percentage: float) -> str:
    """
    Evaluates status label based on water level percentage.
    - Below 15%: Critical
    - 15% to below 30%: Low
    - 30% to 90%: Normal
    - Above 90%: High
    """
    if percentage < CRITICAL_THRESHOLD:
        return "Critical"
    elif percentage < LOW_THRESHOLD:
        return "Low"
    elif percentage <= HIGH_THRESHOLD:
        return "Normal"
    else:
        return "High"


class WaterAlertTracker:
    """
    Manages low-water alert email dispatching and state.
    Ensures email is sent when level drops below 15%, but avoids
    spamming on every 3-second poll. Only re-arms after recovery >= 15%.
    """

    def __init__(self) -> None:
        self.alert_active: bool = False
        self.last_alert_sent_at: Optional[datetime] = None
        self.last_valid_reading: Optional[Dict[str, Any]] = None

    def reset(self) -> None:
        """Resets alert tracker state (used for testing and system resets)."""
        self.alert_active = False
        self.last_alert_sent_at = None
        self.last_valid_reading = None

    def process_reading(self, percentage: float, water_level_cm: float, timestamp_iso: str) -> bool:
        """
        Processes a valid, verified reading.
        Returns True if a new email alert was sent, False otherwise.
        """
        self.last_valid_reading = {
            "percentage": percentage,
            "water_level_cm": water_level_cm,
            "timestamp": timestamp_iso,
        }

        # Check for recovery
        if percentage >= CRITICAL_THRESHOLD:
            if self.alert_active:
                logger.info(
                    "Water level recovered to %.1f%% (>= %.1f%%). Re-arming low water alert.",
                    percentage,
                    CRITICAL_THRESHOLD,
                )
                self.alert_active = False
            return False

        # Water level is critical (< 15%)
        if not self.alert_active:
            email_sent = self._send_alert_email(percentage, water_level_cm, timestamp_iso)
            self.alert_active = True
            self.last_alert_sent_at = timezone.now()
            return email_sent

        return False

    def _send_alert_email(self, percentage: float, water_level_cm: float, timestamp_iso: str) -> bool:
        admin_email = getattr(settings, "ADMIN_EMAIL", "") or os.getenv("ADMIN_EMAIL", "")
        if not admin_email:
            logger.warning(
                "HostelSense water-level is CRITICAL (%.1f%% < %.1f%%), but ADMIN_EMAIL is not set in backend/.env. Email not sent.",
                percentage,
                CRITICAL_THRESHOLD,
            )
            return False

        subject = f"[HostelSense Alert] Critical Low Water Level Detected ({percentage:.1f}%)"
        message = (
            f"HostelSense Campus Water-Level Monitoring Alert\n"
            f"=================================================\n\n"
            f"ATTENTION ADMINISTRATOR:\n"
            f"The hostel water storage tank has fallen below the critical threshold!\n\n"
            f"  • Current Water Level:  {percentage:.1f}%\n"
            f"  • Current Water Height: {water_level_cm:.1f} cm\n"
            f"  • Safety Threshold:     {CRITICAL_THRESHOLD:.1f}%\n"
            f"  • Status:               Critical\n"
            f"  • Timestamp:            {timestamp_iso}\n\n"
            f"ACTION REQUIRED:\n"
            f"Please arrange for an immediate water tanker refill or activate auxiliary supply\n"
            f"to prevent water shortage for hostel residents.\n\n"
            f"--\n"
            f"HostelSense AI Automated Alert Service\n"
        )

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or os.getenv(
            "DEFAULT_FROM_EMAIL", "noreply@hostelsense.local"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[admin_email.strip()],
                fail_silently=False,
            )
            logger.info("Successfully sent low-water alert email to %s", admin_email)
            return True
        except Exception as exc:
            # Log failure safely without exposing passwords
            logger.error("Failed to send low-water email alert: %s", str(exc))
            return False


# Singleton instance shared across requests
water_alert_tracker = WaterAlertTracker()


def get_blynk_credentials() -> Tuple[str, str]:
    """
    Retrieves Blynk token and base URL from Django settings or environment.
    Django settings takes precedence, honoring explicit empty strings (e.g. in tests).
    """
    token = getattr(settings, "BLYNK_DEVICE_TOKEN", None)
    if token is None:
        token = os.getenv("BLYNK_DEVICE_TOKEN", "")
    server_url = getattr(settings, "BLYNK_SERVER_URL", None)
    if not server_url:
        server_url = os.getenv("BLYNK_SERVER_URL", "https://blynk.cloud")
    return str(token).strip().strip("'").strip('"'), str(server_url).strip().strip("'").strip('"').rstrip("/")


def _parse_blynk_error_payload(resp: requests.Response) -> str:
    """Helper to extract clean error message from Blynk response."""
    try:
        data = resp.json()
        if isinstance(data, dict):
            err_obj = data.get("error", {})
            if isinstance(err_obj, dict) and "message" in err_obj:
                return err_obj["message"]
            if isinstance(err_obj, str):
                return err_obj
            if "description" in data:
                return data["description"]
    except Exception:
        pass
    text = resp.text.strip()
    return text if text and len(text) < 120 else f"HTTP {resp.status_code}"


def fetch_blynk_water_data() -> Dict[str, Any]:
    """
    Fetches V0 (percentage) and V1 (height cm) from Blynk Cloud REST API only when
    hardware connection is confirmed live via `isHardwareConnected`.
    If hardware is offline or connection unknown, stale values are not returned.
    """
    token, server_url = get_blynk_credentials()

    if not token:
        return {
            "error": "Blynk device token is not configured.",
            "detail": "Please configure BLYNK_DEVICE_TOKEN in backend/.env to view live ESP32 readings.",
            "source": "Blynk",
            "configured": False,
            "status": "Unavailable",
            "device_status": "Unknown",
            "percentage": None,
            "water_level_cm": None,
            "timestamp": timezone.now().isoformat(),
        }

    headers = {"User-Agent": "HostelSenseAI/1.0", "Accept": "application/json, text/plain, */*"}
    timeout_sec = 2.5

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: Verify actual ESP32 hardware connection status
    # ─────────────────────────────────────────────────────────────────────────
    try:
        hw_url = f"{server_url}/external/api/isHardwareConnected?token={token}"
        hw_resp = requests.get(hw_url, headers=headers, timeout=timeout_sec, allow_redirects=True)

        if hw_resp.status_code in (400, 401, 403, 404):
            err_detail = _parse_blynk_error_payload(hw_resp)
            return {
                "error": "Invalid or Unauthorized Blynk Token",
                "detail": f"Blynk Cloud responded with HTTP {hw_resp.status_code}: {err_detail}. Verify BLYNK_DEVICE_TOKEN.",
                "source": "Blynk",
                "configured": True,
                "status": "Unavailable",
                "device_status": "Unknown",
                "percentage": None,
                "water_level_cm": None,
                "timestamp": timezone.now().isoformat(),
            }

        if hw_resp.status_code == 200:
            is_connected = hw_resp.text.strip().lower() == "true"
            if not is_connected:
                # Hardware is confirmed OFFLINE. Do NOT return stale virtual-pin values!
                return {
                    "status": "Offline",
                    "device_status": "Offline",
                    "percentage": None,
                    "water_level_cm": None,
                    "source": "Blynk",
                    "timestamp": timezone.now().isoformat(),
                    "detail": "ESP32 hardware is currently disconnected from Blynk Cloud.",
                    "alert_triggered": water_alert_tracker.alert_active,
                    "alert_sent": False,
                    "configured": True,
                }
        else:
            return {
                "error": "Telemetry Unavailable",
                "detail": f"Blynk status check returned unexpected status HTTP {hw_resp.status_code}.",
                "source": "Blynk",
                "status": "Unavailable",
                "device_status": "Unknown",
                "percentage": None,
                "water_level_cm": None,
                "timestamp": timezone.now().isoformat(),
                "configured": True,
            }

    except requests.RequestException as e:
        logger.warning("Blynk connection check failed: %s", str(e))
        return {
            "error": "Telemetry Unavailable",
            "detail": f"Could not verify Blynk device connection status: {str(e)}",
            "source": "Blynk",
            "status": "Unavailable",
            "device_status": "Unknown",
            "percentage": None,
            "water_level_cm": None,
            "timestamp": timezone.now().isoformat(),
            "configured": True,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: Hardware is confirmed ONLINE -> Fetch live V0 and V1 datastreams
    # ─────────────────────────────────────────────────────────────────────────
    v0_val: Optional[float] = None
    v1_val: Optional[float] = None

    # Multi-pin query: /external/api/get?token={token}&v0&v1
    try:
        multi_url = f"{server_url}/external/api/get?token={token}&v0&v1"
        resp = requests.get(multi_url, headers=headers, timeout=timeout_sec, allow_redirects=True)

        if resp.status_code == 200:
            try:
                data = resp.json()
                if isinstance(data, dict):
                    raw_v0 = data.get("v0", data.get("V0"))
                    raw_v1 = data.get("v1", data.get("V1"))
                    if raw_v0 is not None:
                        v0_val = float(raw_v0)
                    if raw_v1 is not None:
                        v1_val = float(raw_v1)
            except Exception:
                pass
    except requests.RequestException as e:
        logger.debug("Multi-pin query error, attempting single pin queries: %s", str(e))

    # Single-pin queries fallback
    if v0_val is None:
        for pin_name in ("v0", "V0"):
            try:
                single_url = f"{server_url}/external/api/get?token={token}&{pin_name}"
                resp = requests.get(single_url, headers=headers, timeout=timeout_sec, allow_redirects=True)
                if resp.status_code == 200:
                    text_val = resp.text.strip().strip('"').strip("'")
                    v0_val = float(text_val)
                    break
            except (ValueError, requests.RequestException):
                pass

    if v1_val is None:
        for pin_name in ("v1", "V1"):
            try:
                single_url = f"{server_url}/external/api/get?token={token}&{pin_name}"
                resp = requests.get(single_url, headers=headers, timeout=timeout_sec, allow_redirects=True)
                if resp.status_code == 200:
                    text_val = resp.text.strip().strip('"').strip("'")
                    v1_val = float(text_val)
                    break
            except (ValueError, requests.RequestException):
                pass

    # If neither pin could be retrieved
    if v0_val is None and v1_val is None:
        return {
            "error": "Telemetry Unavailable",
            "detail": "ESP32 is online in Blynk Cloud, but V0 and V1 datastreams have not reported values.",
            "source": "Blynk",
            "status": "Unavailable",
            "device_status": "Online",
            "percentage": None,
            "water_level_cm": None,
            "timestamp": timezone.now().isoformat(),
            "configured": True,
        }

    # Only provide water_level_cm if V1 was actually retrieved from telemetry
    percentage = round(float(v0_val), 1) if v0_val is not None else (round((float(v1_val) / TANK_HEIGHT_CM) * 100.0, 1) if v1_val is not None else 0.0)
    water_level_cm = round(float(v1_val), 1) if v1_val is not None else None
    status_label = compute_water_status(percentage)
    iso_timestamp = timezone.now().isoformat()

    # Process reading through alert tracker (triggers email if < 15% and not already sent)
    alert_sent = water_alert_tracker.process_reading(percentage, water_level_cm if water_level_cm is not None else 0.0, iso_timestamp)

    return {
        "percentage": percentage,
        "water_level_cm": water_level_cm,
        "status": status_label,
        "device_status": "Online",
        "source": "Blynk",
        "timestamp": iso_timestamp,
        "alert_triggered": water_alert_tracker.alert_active,
        "alert_sent": alert_sent,
        "configured": True,
    }
