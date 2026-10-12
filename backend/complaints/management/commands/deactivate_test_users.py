"""
complaints/management/commands/deactivate_test_users.py
=======================================================
Management command to safely deactivate user accounts by setting `is_active=False`.

SAFETY:
- Default mode is strictly DRY-RUN. Database is only modified when `--apply` is specified.
- Uses a database transaction during apply operations.
- Refuses to proceed and aborts if any supplied username does not exist.
- Never deletes User, Profile, Complaint, Vote, or LogEntry rows.
- Never logs, displays, or exposes passwords, password hashes, or secrets.
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.db import transaction
from complaints.models import StudentProfile


class Command(BaseCommand):
    help = "Safely deactivate user accounts (is_active=False). Defaults to dry-run mode."

    def add_arguments(self, parser):
        parser.add_argument(
            "usernames",
            nargs="+",
            type=str,
            help="One or more usernames to deactivate (e.g. student rahul_btech).",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Actually apply changes to the database. If omitted, runs in dry-run mode.",
        )

    def handle(self, *args, **options):
        usernames = options["usernames"]
        apply_mode = options["apply"]
        is_dry_run = not apply_mode

        self.stdout.write(self.style.MIGRATE_HEADING("=== USER DEACTIVATION AUDIT & TOOL ==="))
        if is_dry_run:
            self.stdout.write(self.style.WARNING("Mode: DRY-RUN (Default). No database changes will be made.\n"))
        else:
            self.stdout.write(self.style.SUCCESS("Mode: APPLY. Changes will be committed to database.\n"))

        # Step 1: Pre-validation — check all usernames exist before proceeding
        missing_users = []
        user_objects = []
        for uname in usernames:
            user = User.objects.filter(username=uname).first()
            if not user:
                missing_users.append(uname)
            else:
                user_objects.append(user)

        if missing_users:
            err_msg = (
                f"Aborting: The following username(s) do not exist in the database: "
                f"{', '.join(missing_users)}. No accounts were modified."
            )
            raise CommandError(err_msg)

        # Step 2: Display account details and related-record counts
        plan = []
        for user in user_objects:
            complaints_count = user.complaints.count()
            votes_count = user.votes.count()

            has_profile = False
            roll_no = "N/A"
            try:
                if hasattr(user, "profile") and user.profile:
                    has_profile = True
                    roll_no = user.profile.roll_no
            except StudentProfile.DoesNotExist:
                has_profile = False

            log_count = LogEntry.objects.filter(user=user).count()
            total_related = complaints_count + votes_count + (1 if has_profile else 0) + log_count

            plan.append({
                "user": user,
                "complaints": complaints_count,
                "votes": votes_count,
                "has_profile": has_profile,
                "roll_no": roll_no,
                "log_count": log_count,
                "total_related": total_related,
            })

            self.stdout.write(self.style.HTTP_INFO(f"[*] Account: '{user.username}' (ID: {user.id})"))
            self.stdout.write(f"    Current status:    is_active = {user.is_active}")
            self.stdout.write(f"    Staff / Superuser: is_staff = {user.is_staff}, is_superuser = {user.is_superuser}")
            self.stdout.write(f"    Related records:")
            self.stdout.write(f"      - Complaints:       {complaints_count}")
            self.stdout.write(f"      - Votes:            {votes_count}")
            self.stdout.write(f"      - Student Profile:  {'Yes (roll_no=' + roll_no + ')' if has_profile else 'None'}")
            self.stdout.write(f"      - Admin Logs:       {log_count}")
            self.stdout.write(f"      - TOTAL DEPENDENT:  {total_related}")

            if not user.is_active:
                self.stdout.write(self.style.NOTICE("    Notice: Account is ALREADY inactive (is_active=False).\n"))
            else:
                action_text = "Would set is_active=False" if is_dry_run else "Will set is_active=False"
                self.stdout.write(f"    Action: {action_text}\n")

        # Step 3: Execution (Dry-Run vs. Apply in Transaction)
        if is_dry_run:
            self.stdout.write(self.style.WARNING("DRY-RUN COMPLETE: 0 database modifications made."))
            self.stdout.write("To apply these changes, run the command with the '--apply' flag.\n")
            return

        with transaction.atomic():
            updated_count = 0
            for item in plan:
                user = item["user"]
                if user.is_active:
                    user.is_active = False
                    user.save(update_fields=["is_active"])
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"[APPLIED] Deactivated user '{user.username}' (is_active: True -> False)."))
                else:
                    self.stdout.write(f"[SKIPPED] User '{user.username}' was already inactive.")

            self.stdout.write(self.style.SUCCESS(f"\nTransaction committed successfully. {updated_count} user(s) updated."))
