"""
complaints/management/commands/import_csv.py
============================================
Django management command to bulk-import the hostel complaints CSV
into the PostgreSQL database.

Usage:
    python manage.py import_csv
    python manage.py import_csv --file path/to/other.csv
    python manage.py import_csv --clear   # deletes existing records first
    python manage.py import_csv --dry-run # parses CSV and shows counts without saving

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


class Command(BaseCommand):
    help = "Import hostel complaints from the CSV file into PostgreSQL."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default=None,
            help="Path to the CSV file. Defaults to the project-root Dataset_duration.csv.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            default=False,
            help="Delete all existing complaints before importing.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Parse CSV and validate mappings without modifying the database.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # ── Resolve CSV path ───────────────────────────────────────────
        if options["file"]:
            csv_path = options["file"]
        else:
            # Default: project root (above backend)
            import_csv_dir = os.path.dirname(os.path.abspath(__file__))
            commands_dir = import_csv_dir
            management_dir = os.path.dirname(commands_dir)
            complaints_dir = os.path.dirname(management_dir)
            backend_dir = os.path.dirname(complaints_dir)
            project_root = os.path.dirname(backend_dir)

            csv_path = os.path.join(
                project_root,
                "Dataset_duration.csv"
            )

        if not os.path.isfile(csv_path):
            raise CommandError(f"CSV file not found: {csv_path}")

        self.stdout.write(f"Reading: {csv_path}")
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE ENABLED. Database will not be modified."))

        # ── Optionally clear existing records ──────────────────────────
        if options["clear"] and not dry_run:
            count = Complaint.objects.count()
            Complaint.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"Cleared {count} existing complaint(s).")
            )

        # ── Parse CSV and build model instances ────────────────────────
        complaints  = []
        skipped     = 0
        row_num     = 0

        # Build dynamic maps from model choices for case-insensitive lookup
        category_map = {choice[0].lower(): choice[0] for choice in Complaint.Category.choices}
        floor_map = {choice[0].lower(): choice[0] for choice in Complaint.Floor.choices}
        priority_map = {choice[0].lower(): choice[0] for choice in Complaint.Priority.choices}
        status_map = {choice[0].lower(): choice[0] for choice in Complaint.Status.choices}
        duration_map = {choice[0].lower(): choice[0] for choice in Complaint.Duration.choices}
        type_map = {choice[0].lower(): choice[0] for choice in Complaint.ComplaintType.choices}

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
                    complaint_type_raw = row.get("Complaint_Type", "Public").strip().lower()
                    complaint_type = type_map.get(complaint_type_raw, "Public")
                    
                    block = row.get("Block", "A").strip().upper()
                    if block not in ("A", "B", "C", "D"):
                        block = "A"

                    floor_raw = row.get("Floor", "Ground").strip().lower()
                    floor = floor_map.get(floor_raw, "Ground")

                    category_raw = row.get("Category", "Other").strip().lower()
                    category = category_map.get(category_raw, "Other")

                    priority_raw = row.get("Priority", "Low").strip().lower()
                    predicted_priority = priority_map.get(priority_raw, "Low")
                    
                    status_raw = row.get("Status", "Pending").strip().lower()
                    status = status_map.get(status_raw, "Pending")
                    
                    room_no = row.get("Room_No", "").strip()
                    
                    duration_raw = row.get("Duration_Standardized", "").strip().lower()
                    duration = duration_map.get(duration_raw, None)

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
                            room_no=room_no,
                            duration=duration,
                            status=status,
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

        if dry_run:
            self.stdout.write(self.style.SUCCESS("Dry run complete. No records were imported."))
            return

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
