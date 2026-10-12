"""
complaints/management/commands/audit_users.py
=============================================
Read-only management command to audit user accounts in HostelSense AI.
Performs checks on emails, usernames, names, profile relations, and
specific test account dependencies.

SAFETY:
- Strictly READ-ONLY. No database modifications are performed.
- NEVER outputs passwords, hashes, tokens, or secret keys.
"""
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from complaints.models import Complaint, ComplaintVote, StudentProfile


class Command(BaseCommand):
    help = "Perform a read-only audit of User records and their dependencies."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== HOSTELSENSE AI - USER AUDIT (READ-ONLY) ===\n"))

        users = list(User.objects.all().order_by("id"))
        total_users = len(users)
        self.stdout.write(f"Total user accounts found: {total_users}\n")

        # ── 1. Duplicate emails (case-insensitive) ────────────────────────
        self.stdout.write(self.style.HTTP_INFO("[1] Case-Insensitive Duplicate Email Check:"))
        email_map = defaultdict(list)
        for u in users:
            email_normalized = (u.email or "").strip().lower()
            if email_normalized:
                email_map[email_normalized].append(u)
            else:
                email_map["<BLANK_EMAIL>"].append(u)

        dup_emails = {email: u_list for email, u_list in email_map.items() if len(u_list) > 1 and email != "<BLANK_EMAIL>"}
        if dup_emails:
            for email, u_list in dup_emails.items():
                self.stdout.write(self.style.WARNING(f"  - Duplicate email '{email}':"))
                for u in u_list:
                    self.stdout.write(f"      ID: {u.id}, username: '{u.username}', active: {u.is_active}")
        else:
            self.stdout.write(self.style.SUCCESS("  - No duplicate emails found."))

        blank_emails = email_map.get("<BLANK_EMAIL>", [])
        if blank_emails:
            self.stdout.write(self.style.WARNING(f"  - Accounts with blank email: {len(blank_emails)}"))
            for u in blank_emails:
                self.stdout.write(f"      ID: {u.id}, username: '{u.username}'")
        self.stdout.write("")

        # ── 2. Lowercase username collisions ──────────────────────────────
        self.stdout.write(self.style.HTTP_INFO("[2] Lowercase Username Collision Check:"))
        uname_map = defaultdict(list)
        for u in users:
            uname_map[u.username.lower()].append(u)

        uname_collisions = {uname: u_list for uname, u_list in uname_map.items() if len(u_list) > 1}
        if uname_collisions:
            for uname, u_list in uname_collisions.items():
                self.stdout.write(self.style.WARNING(f"  - Username collision on lower('{uname}'):"))
                for u in u_list:
                    self.stdout.write(f"      ID: {u.id}, exact username: '{u.username}', active: {u.is_active}")
        else:
            self.stdout.write(self.style.SUCCESS("  - No username collisions found when lowercased."))
        self.stdout.write("")

        # ── 3. Users with blank first_name or last_name ──────────────────
        self.stdout.write(self.style.HTTP_INFO("[3] Blank Name Check:"))
        missing_names = []
        for u in users:
            fn_blank = not bool((u.first_name or "").strip())
            ln_blank = not bool((u.last_name or "").strip())
            if fn_blank or ln_blank:
                missing_names.append((u, fn_blank, ln_blank))

        if missing_names:
            self.stdout.write(self.style.WARNING(f"  Found {len(missing_names)} user(s) with missing name parts:"))
            for u, fn_blank, ln_blank in missing_names:
                missing_desc = []
                if fn_blank:
                    missing_desc.append("first_name is blank")
                if ln_blank:
                    missing_desc.append("last_name is blank")
                self.stdout.write(f"    - ID: {u.id}, username: '{u.username}' ({', '.join(missing_desc)})")
        else:
            self.stdout.write(self.style.SUCCESS("  - All users have both first_name and last_name set."))
        self.stdout.write("")

        # ── 4. Users with no profile row ──────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO("[4] Profile Check (OneToOne to StudentProfile):"))
        no_profile_users = []
        for u in users:
            has_profile = False
            try:
                has_profile = hasattr(u, "profile") and u.profile is not None
            except StudentProfile.DoesNotExist:
                has_profile = False
            if not has_profile:
                no_profile_users.append(u)

        if no_profile_users:
            self.stdout.write(self.style.WARNING(f"  Found {len(no_profile_users)} user(s) without a profile row:"))
            for u in no_profile_users:
                self.stdout.write(f"    - ID: {u.id}, username: '{u.username}', is_staff: {u.is_staff}, is_superuser: {u.is_superuser}")
        else:
            self.stdout.write(self.style.SUCCESS("  - All users have an associated profile row."))
        self.stdout.write("")

        # ── 5. Dependency check for 'student' and 'rahul_btech' ───────────
        self.stdout.write(self.style.HTTP_INFO("[5] Target Account Dependency Analysis ('student' & 'rahul_btech'):"))
        target_usernames = ["student", "rahul_btech"]
        for target_uname in target_usernames:
            target_user = User.objects.filter(username=target_uname).first()
            if not target_user:
                self.stdout.write(self.style.NOTICE(f"  - User '{target_uname}': NOT FOUND in database."))
                continue

            complaints_count = target_user.complaints.count()
            votes_count = target_user.votes.count()
            has_profile = False
            roll_no = "N/A"
            try:
                if hasattr(target_user, "profile") and target_user.profile:
                    has_profile = True
                    roll_no = target_user.profile.roll_no
            except StudentProfile.DoesNotExist:
                has_profile = False

            log_entries_count = 0
            if hasattr(target_user, "logentry_set"):
                log_entries_count = target_user.logentry_set.count()

            self.stdout.write(f"  - User '{target_uname}' (ID: {target_user.id}, is_active: {target_user.is_active}):")
            self.stdout.write(f"      * Complaints submitted: {complaints_count}")
            self.stdout.write(f"      * Complaint votes cast: {votes_count}")
            self.stdout.write(f"      * StudentProfile row:   {'Yes (roll_no=' + roll_no + ')' if has_profile else 'None'}")
            self.stdout.write(f"      * Admin LogEntry rows:  {log_entries_count}")
            total_deps = complaints_count + votes_count + (1 if has_profile else 0) + log_entries_count
            self.stdout.write(f"      * TOTAL related rows:  {total_deps}")
        self.stdout.write("")

        # ── 6. Full User Summary (No credentials) ─────────────────────────
        self.stdout.write(self.style.HTTP_INFO("[6] Full User Directory (Sanitized - No Credentials):"))
        header = f"{'ID':<4} {'Username':<15} {'Email':<35} {'First Name':<12} {'Last Name':<12} {'Active':<8} {'Staff':<7} {'Super':<7} {'Profile':<7}"
        self.stdout.write(header)
        self.stdout.write("-" * len(header))
        for u in users:
            try:
                prof_str = "Yes" if hasattr(u, "profile") and u.profile else "No"
            except StudentProfile.DoesNotExist:
                prof_str = "No"
            row = (
                f"{u.id:<4} "
                f"{u.username:<15} "
                f"{(u.email or ''):<35} "
                f"{(u.first_name or ''):<12} "
                f"{(u.last_name or ''):<12} "
                f"{str(u.is_active):<8} "
                f"{str(u.is_staff):<7} "
                f"{str(u.is_superuser):<7} "
                f"{prof_str:<7}"
            )
            self.stdout.write(row)

        self.stdout.write(self.style.SUCCESS("\nAudit complete. No changes made to database."))
