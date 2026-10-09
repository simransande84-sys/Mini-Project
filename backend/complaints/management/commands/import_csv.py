"""
complaints/management/commands/import_csv.py
============================================
Django management command to bulk-import the hostel complaints CSV
into the PostgreSQL database.

Usage:
    python manage.py import_csv
    python manage.py import_csv --file path/to/other.csv
    python manage.py import_csv --clear   # deletes existing records first

Strategy:
    - Uses the Priority column from the CSV as predicted_priority
      (these are the ground-truth labels used during ML training).
    - Parses Complaint_Date from the CSV as created_at.
    - Skips rows with missing required fields.
    - Uses bulk_create() for fast insertion.
"""
import os
import csv
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from complaints.models import Complaint


# Map CSV column values → model choice values
FLOOR_MAP = {
    "ground": "Ground",
    "first":  "First",
    "second": "Second",
    "third":  "Third",
}

CATEGORY_MAP = {
    "cleanliness":  "Cleanliness",
    "mess":         "Mess",
    "washroom":     "Washroom",
    "furniture":    "Furniture",
    "water cooler": "Water Cooler",
    "security":     "Security",
    "electricity":  "Electricity",
    "wifi":         "WiFi",
}

PRIORITY_MAP = {
    "critical": "Critical",
    "high":     "High",
    "medium":   "Medium",
    "low":      "Low",
}

TYPE_MAP = {
    "public":  "Public",
    "private": "Private",
}


class Command(BaseCommand):
    help = "Import hostel complaints from the CSV file into PostgreSQL."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default=None,
            help="Path to the CSV file. Defaults to the project-root CSV.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            default=False,
            help="Delete all existing complaints before importing.",
        )

    def handle(self, *args, **options):
        # ── Resolve CSV path ───────────────────────────────────────────
        if options["file"]:
            csv_path = options["file"]
        else:
            # Default: two levels up from manage.py (project root)
            base = os.path.dirname(  # backend/
                os.path.dirname(     # complaints/
                    os.path.dirname( # management/
                        os.path.abspath(__file__)
                    )
                )
            )
            csv_path = os.path.join(
                os.path.dirname(base),  # hostelSenseAi/
                "hostel_complaints_800_final (1).csv"
            )

        if not os.path.isfile(csv_path):
            raise CommandError(f"CSV file not found: {csv_path}")

        self.stdout.write(f"Reading: {csv_path}")

        # ── Optionally clear existing records ──────────────────────────
        if options["clear"]:
            count = Complaint.objects.count()
            Complaint.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"Cleared {count} existing complaint(s).")
            )

        # ── Parse CSV and build model instances ────────────────────────
        complaints  = []
        skipped     = 0
        row_num     = 0

        with open(csv_path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)

            for row in reader:
                row_num += 1

                try:
                    complaint_text = row.get("Complaint_Text", "").strip()
                    if not complaint_text or len(complaint_text) < 5:
                        skipped += 1
                        continue

                    # Normalise and map each field
                    complaint_type = TYPE_MAP.get(
                        row.get("Complaint_Type", "Public").strip().lower(),
                        "Public"
                    )
                    block = row.get("Block", "A").strip().upper()
                    if block not in ("A", "B", "C", "D"):
                        block = "A"

                    floor_raw = row.get("Floor", "Ground").strip().lower()
                    floor = FLOOR_MAP.get(floor_raw, "Ground")

                    category_raw = row.get("Category", "Other").strip().lower()
                    category = CATEGORY_MAP.get(category_raw, "Other")

                    try:
                        students_affected = int(row.get("Students_Affected", 1))
                    except (ValueError, TypeError):
                        students_affected = 1

                    try:
                        support_count = int(row.get("Support_Count", 0))
                    except (ValueError, TypeError):
                        support_count = 0

                    priority_raw = row.get("Priority", "Low").strip().lower()
                    predicted_priority = PRIORITY_MAP.get(priority_raw, "Low")

                    # Parse date (DD-MM-YYYY format in the CSV)
                    date_str = row.get("Complaint_Date", "").strip()
                    try:
                        naive_dt = datetime.strptime(date_str, "%d-%m-%Y")
                        created_at = timezone.make_aware(naive_dt)
                    except (ValueError, TypeError):
                        created_at = timezone.now()

                    complaints.append(
                        Complaint(
                            complaint_text=complaint_text,
                            complaint_type=complaint_type,
                            category=category,
                            block=block,
                            floor=floor,
                            students_affected=students_affected,
                            support_count=support_count,
                            predicted_priority=predicted_priority,
                            created_at=created_at,
                        )
                    )

                except Exception as exc:
                    self.stderr.write(f"  Row {row_num} skipped — {exc}")
                    skipped += 1

        self.stdout.write(
            f"Parsed {len(complaints)} valid rows, skipped {skipped}."
        )

        # ── Bulk insert in one transaction ─────────────────────────────
        with transaction.atomic():
            # ignore_conflicts=False so we see any errors immediately
            Complaint.objects.bulk_create(complaints, batch_size=100)

        final_count = Complaint.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! {len(complaints)} records imported. "
                f"Total in DB: {final_count}"
            )
        )
