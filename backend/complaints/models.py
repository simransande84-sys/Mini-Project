"""
complaints/models.py
====================
Three models:

1. Complaint      — A hostel complaint with ML-predicted priority
2. ComplaintVote  — One-vote-per-student support system
3. StudentProfile — Extended student info linked to Django User
"""
from django.db import models
from django.contrib.auth.models import User


# ─────────────────────────────────────────────────────────────────────────────
# Complaint
# ─────────────────────────────────────────────────────────────────────────────
class Complaint(models.Model):

    # ── Choice constants ──────────────────────────────────────────────────────
    class ComplaintType(models.TextChoices):
        PUBLIC  = "Public",  "Public"
        PRIVATE = "Private", "Private"

    class Block(models.TextChoices):
        A = "A", "Block A"
        B = "B", "Block B"
        C = "C", "Block C"
        D = "D", "Block D"

    class Floor(models.TextChoices):
        GROUND = "Ground", "Ground Floor"
        FIRST  = "First",  "First Floor"
        SECOND = "Second", "Second Floor"
        THIRD  = "Third",  "Third Floor"

    class Category(models.TextChoices):
        CLEANLINESS  = "Cleanliness",  "Cleanliness"
        MESS         = "Mess",         "Mess"
        WASHROOM     = "Washroom",     "Washroom"
        FURNITURE    = "Furniture",    "Furniture"
        WATER_COOLER = "Water Cooler", "Water Cooler"
        SECURITY     = "Security",     "Security"
        ELECTRICITY  = "Electricity",  "Electricity"
        WIFI         = "WiFi",         "WiFi"
        OTHER        = "Other",        "Other"

    class Priority(models.TextChoices):
        CRITICAL = "Critical", "Critical"
        HIGH     = "High",     "High"
        MEDIUM   = "Medium",   "Medium"
        LOW      = "Low",      "Low"

    class Status(models.TextChoices):
        PENDING     = "Pending",     "Pending"
        IN_PROGRESS = "In Progress", "In Progress"
        RESOLVED    = "Resolved",    "Resolved"
        REJECTED    = "Rejected",    "Rejected"

    class Duration(models.TextChoices):
        # Values must match Duration_Standardized format in training data: "N unit"
        ONE_HOUR    = "1 hour",   "1 hour"
        TWO_HOURS   = "2 hours",  "2 hours"
        THREE_HOURS = "3 hours",  "3 hours"
        FOUR_HOURS  = "4 hours",  "4 hours"
        FIVE_HOURS  = "5 hours",  "5 hours"
        SIX_HOURS   = "6 hours",  "6 hours"
        EIGHT_HOURS = "8 hours",  "8 hours"
        ONE_DAY     = "1 day",    "1 day"
        TWO_DAYS    = "2 days",   "2 days"
        THREE_DAYS  = "3 days",   "3 days"
        FOUR_DAYS   = "4 days",   "4 days"
        SIX_DAYS    = "6 days",   "6 days"
        EIGHT_DAYS  = "8 days",   "8 days"
        TWELVE_DAYS = "12 days",  "12 days"
        ONE_WEEK    = "1 week",   "1 week"
        TWO_WEEKS   = "2 weeks",  "2 weeks"
        FOUR_WEEKS  = "4 weeks",  "4 weeks"

    # ── Core fields ───────────────────────────────────────────────────────────
    complaint_text = models.TextField(
        help_text="Raw complaint text submitted by the student."
    )
    complaint_type = models.CharField(
        max_length=10,
        choices=ComplaintType.choices,
        default=ComplaintType.PUBLIC,
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
    )
    block = models.CharField(
        max_length=1,
        choices=Block.choices,
    )
    floor = models.CharField(
        max_length=10,
        choices=Floor.choices,
    )
    room_no = models.CharField(
        max_length=10,
        blank=True,
        default="",
        help_text="Room number (optional).",
    )
    students_affected = models.PositiveIntegerField(default=1)
    duration = models.CharField(
        max_length=30,
        choices=Duration.choices,
        blank=True,
        null=True,
        help_text="How long the issue has persisted. NULL for legacy complaints.",
    )
    support_count = models.PositiveIntegerField(
        default=0,
        help_text="Incremented each time a student clicks Support.",
    )

    # ── ML + status fields ────────────────────────────────────────────────────
    predicted_priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        blank=True,
        default="",
        help_text=(
            "Single source of truth for priority. "
            "Updated by ML prediction AND support escalation rules."
        ),
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Current resolution status, managed by admin.",
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="complaints",
        help_text="The student who submitted this complaint. NULL for CSV-imported rows.",
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        help_text="Timestamp when the complaint was submitted.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Complaint"
        verbose_name_plural = "Complaints"

    def __str__(self):
        return f"[{self.predicted_priority or 'UNSCORED'}] {self.complaint_text[:60]}"


# ─────────────────────────────────────────────────────────────────────────────
# ComplaintVote  — Public support system
# ─────────────────────────────────────────────────────────────────────────────
class ComplaintVote(models.Model):
    """
    Each student can support (vote on) a public complaint exactly once.
    The unique_together constraint enforces this at the database level.
    """
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name="votes",
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="votes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Database-level uniqueness — one student, one support per complaint
        unique_together = ("complaint", "student")
        verbose_name = "Complaint Support"
        verbose_name_plural = "Complaint Supports"

    def __str__(self):
        return f"{self.student.username} supported Complaint #{self.complaint_id}"


# ─────────────────────────────────────────────────────────────────────────────
# StudentProfile  — Extended hostel info for each student user
# ─────────────────────────────────────────────────────────────────────────────
class StudentProfile(models.Model):
    """
    Extended profile for students.
    Linked 1-to-1 with Django's built-in User model.
    Students fill this in after their first login.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    roll_no = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique college roll number.",
    )
    block = models.CharField(
        max_length=1,
        blank=True,
        default="",
        help_text="Hostel block (A/B/C/D). Filled after first login.",
    )
    floor = models.CharField(
        max_length=10,
        blank=True,
        default="",
    )
    room_no = models.CharField(
        max_length=10,
        blank=True,
        default="",
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        default="",
        help_text="Optional phone number.",
    )
    profile_complete = models.BooleanField(
        default=False,
        help_text="False until the student completes block/floor/room details.",
    )

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

    def __str__(self):
        return f"{self.user.username} — {self.roll_no}"
