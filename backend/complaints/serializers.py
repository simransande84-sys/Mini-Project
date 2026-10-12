"""
complaints/serializers.py
==========================
All DRF serializers for HostelSense AI.

Serializers:
  RegisterSerializer         → Student self-registration
  UserSerializer             → Current user info (/api/auth/me/)
  StudentProfileSerializer   → Profile view + update
  ComplaintSerializer        → Full complaint (list / detail / admin)
  ComplaintCreateSerializer  → Used on POST — sets submitted_by from JWT
  ComplaintVoteSerializer    → Vote create (POST /api/complaints/<id>/vote/)
  DashboardSerializer        → Dashboard stats (read-only)
"""
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Complaint, ComplaintVote, StudentProfile


def validate_complaint_text_content(value: str) -> str:
    """
    Validates complaint_text length and quality:
    - Must be between 10 and 1,000 characters.
    - Rejects excessive character repetition (e.g. 'aaaaaaa').
    - Rejects unpronounceable gibberish tokens >= 3 letters with zero vowels ('a,e,i,o,u,y')
      unless listed in common allowed technical abbreviations (e.g. AC, TV, RO, MCB).
    - Rejects strings made predominantly of single-letter noise (e.g. 'm h gh g').
    """
    if not isinstance(value, str):
        raise serializers.ValidationError("Complaint text must be a string.")

    stripped = value.strip()
    if len(stripped) < 10:
        raise serializers.ValidationError("Complaint text must be at least 10 characters.")
    if len(stripped) > 1000:
        raise serializers.ValidationError("Complaint text cannot exceed 1,000 characters.")

    import re
    if re.search(r"(.)\1{4,}", stripped.lower()):
        raise serializers.ValidationError("Complaint description contains invalid repeated characters.")

    words = re.findall(r"\b[a-zA-Z]+\b", stripped.lower())
    if not words:
        raise serializers.ValidationError("Complaint text must contain valid descriptive words.")

    allowed_abbreviations = {
        "ac", "tv", "ro", "mc", "mcb", "wc", "led", "usb", "id", "dvd", "fps",
        "rgb", "lan", "wifi", "pm", "am", "dr", "mr", "mrs", "sr", "jr", "st", "nd", "rd", "th"
    }
    vowel_pattern = re.compile(r"[aeiouy]")

    gibberish_words = []
    single_letter_count = 0

    for w in words:
        if len(w) >= 3 and not vowel_pattern.search(w) and w not in allowed_abbreviations:
            gibberish_words.append(w)
        elif len(w) == 1 and w not in {"a", "i"}:
            single_letter_count += 1

    if gibberish_words:
        raise serializers.ValidationError("Complaint description contains invalid or meaningless text.")

    if single_letter_count > 0 and single_letter_count >= len(words) / 2:
        raise serializers.ValidationError("Complaint description contains invalid or meaningless text.")

    meaningful_words = [
        w for w in words
        if len(w) >= 3 or w in {
            "no", "on", "in", "at", "to", "is", "my", "ro", "ac", "tv", "a", "i",
            "up", "or", "so", "if", "be", "do", "we", "he", "me"
        }
    ]
    if not meaningful_words:
        raise serializers.ValidationError("Complaint description contains invalid or meaningless text.")

    return stripped


class PredictOnlySerializer(serializers.Serializer):
    """
    Lightweight serializer for POST /api/predict/ — no DB save.
    Validates the fields needed for ML inference only.
    """
    complaint_text    = serializers.CharField(min_length=10, max_length=1000)
    complaint_type    = serializers.ChoiceField(
        choices=Complaint.ComplaintType.choices,
        default=Complaint.ComplaintType.PUBLIC,
    )
    category          = serializers.ChoiceField(
        choices=Complaint.Category.choices,
        default=Complaint.Category.OTHER,
    )
    block             = serializers.ChoiceField(choices=Complaint.Block.choices, required=False, allow_blank=True)
    floor             = serializers.ChoiceField(choices=Complaint.Floor.choices, required=False, allow_blank=True)
    duration          = serializers.ChoiceField(
        choices=Complaint.Duration.choices,
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )
    support_count     = serializers.IntegerField(min_value=0, default=0)

    def validate_complaint_text(self, value):
        return validate_complaint_text_content(value)

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            try:
                profile = request.user.profile
                if not profile.block or not profile.floor or not profile.room_no or not profile.profile_complete:
                    raise serializers.ValidationError(
                        "Please complete your hostel profile before submitting a complaint."
                    )
                attrs["block"] = profile.block
                attrs["floor"] = profile.floor
            except AttributeError:
                raise serializers.ValidationError(
                    "Please complete your hostel profile before submitting a complaint."
                )
        else:
            if not attrs.get("block") or not attrs.get("floor"):
                raise serializers.ValidationError(
                    "Hostel block and floor are required for priority prediction."
                )
        return attrs


# ─────────────────────────────────────────────────────────────────────────────
# Auth / User serializers
# ─────────────────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    """
    POST /api/auth/register/

    Creates a new User + StudentProfile.
    Students enter: name (first_name), roll_no, email, password.
    """
    roll_no  = serializers.CharField(write_only=True, max_length=20)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = User
        fields = ["first_name", "username", "email", "password", "roll_no"]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        cleaned_email = (value or "").strip().lower()
        if not cleaned_email:
            raise serializers.ValidationError("Email is required.")
        if User.objects.filter(email__iexact=cleaned_email).exists():
            raise serializers.ValidationError("This email is already registered.")
        return cleaned_email

    def validate_roll_no(self, value):
        if StudentProfile.objects.filter(roll_no=value).exists():
            raise serializers.ValidationError("A student with this roll number already exists.")
        return value

    def create(self, validated_data):
        roll_no = validated_data.pop("roll_no")
        password = validated_data.pop("password")

        # Create Django User
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Create StudentProfile (incomplete until student fills hostel details)
        StudentProfile.objects.create(user=user, roll_no=roll_no)

        return user


class UserSerializer(serializers.ModelSerializer):
    """Lightweight user info returned by GET /api/auth/me/"""
    roll_no          = serializers.SerializerMethodField()
    profile_complete = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = [
            "id", "username", "first_name", "email",
            "is_staff", "roll_no", "profile_complete"
        ]

    def get_roll_no(self, obj):
        try:
            return obj.profile.roll_no
        except StudentProfile.DoesNotExist:
            return None

    def get_profile_complete(self, obj):
        try:
            return obj.profile.profile_complete
        except StudentProfile.DoesNotExist:
            return False


class StudentProfileSerializer(serializers.ModelSerializer):
    """
    GET / PATCH /api/auth/profile/
    Students update their hostel block, floor, room number here.
    """
    class Meta:
        model  = StudentProfile
        fields = ["roll_no", "block", "floor", "room_no", "phone", "profile_complete"]
        read_only_fields = ["roll_no", "profile_complete"]

    def update(self, instance, validated_data):
        # Mark profile as complete if block, floor, room_no are all filled
        instance.block   = validated_data.get("block",   instance.block)
        instance.floor   = validated_data.get("floor",   instance.floor)
        instance.room_no = validated_data.get("room_no", instance.room_no)
        instance.phone   = validated_data.get("phone",   instance.phone)

        if instance.block and instance.floor and instance.room_no:
            instance.profile_complete = True

        instance.save()
        return instance


# ─────────────────────────────────────────────────────────────────────────────
# Complaint serializers
# ─────────────────────────────────────────────────────────────────────────────

class ComplaintSerializer(serializers.ModelSerializer):
    """
    Full read serializer — used for list, detail, and admin views.
    Includes computed fields: submitted_by_username, user_has_voted.

    Privacy rule (D4):
      For PUBLIC complaints, submitted_by_username is returned as "Anonymous"
      and room_no is blanked for everyone EXCEPT:
        - the complaint owner (submitted_by == request.user)
        - staff/admin (request.user.is_staff)
      Private complaints keep their existing behaviour (already restricted
      at the queryset level — non-owners never receive them).
    """
    submitted_by_username = serializers.SerializerMethodField()
    user_has_voted        = serializers.SerializerMethodField()
    predicted_priority    = serializers.CharField(read_only=True)
    support_count         = serializers.SerializerMethodField()
    created_at            = serializers.DateTimeField(read_only=True)

    class Meta:
        model  = Complaint
        fields = [
            "id",
            "complaint_text",
            "complaint_type",
            "category",
            "block",
            "floor",
            "room_no",
            "duration",
            "support_count",
            "predicted_priority",
            "status",
            "submitted_by_username",
            "user_has_voted",
            "created_at",
        ]

    def _is_privileged(self, obj):
        """True when the requester is staff or the complaint's own submitter."""
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_staff or (
            obj.submitted_by and obj.submitted_by == request.user
        )

    def get_support_count(self, obj):
        if hasattr(obj, "votes_total") and obj.votes_total is not None:
            return obj.votes_total
        return obj.votes.count()

    def get_submitted_by_username(self, obj):
        # D4: anonymise public complaints for non-privileged viewers.
        if obj.complaint_type == "Public" and not self._is_privileged(obj):
            return "Anonymous"
        if obj.submitted_by:
            return obj.submitted_by.first_name or obj.submitted_by.username
        return "Anonymous"

    def get_user_has_voted(self, obj):
        """Returns True if the current authenticated user has voted on this complaint."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return ComplaintVote.objects.filter(
                complaint=obj, student=request.user
            ).exists()
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # D4: blank room_no for public complaints viewed by non-privileged users.
        if instance.complaint_type == "Public" and not self._is_privileged(instance):
            data["room_no"] = ""
        return data

    def validate_complaint_text(self, value):
        return validate_complaint_text_content(value)


class ComplaintCreateSerializer(serializers.ModelSerializer):
    """
    Write serializer — used only for POST /api/complaints/.
    submitted_by is NOT accepted from the client; it is set from the JWT token.
    predicted_priority and status are set by the server.
    `duration` is required — the ML model uses it and the frontend always sends it.
    """
    block    = serializers.CharField(required=False, allow_blank=True)
    floor    = serializers.CharField(required=False, allow_blank=True)
    room_no  = serializers.CharField(required=False, allow_blank=True)
    # 1e: duration is required on creation; blank/missing is rejected with 400.
    duration = serializers.ChoiceField(
        choices=Complaint.Duration.choices,
        required=True,
        error_messages={"required": "duration is required.", "invalid_choice": "Invalid duration value."},
    )

    class Meta:
        model  = Complaint
        fields = [
            "complaint_text",
            "complaint_type",
            "category",
            "block",
            "floor",
            "room_no",
            "duration",
        ]

    def validate_complaint_text(self, value):
        return validate_complaint_text_content(value)

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication credentials were not provided.")

        try:
            profile = request.user.profile
        except AttributeError:
            raise serializers.ValidationError(
                "Please complete your hostel profile before submitting a complaint."
            )

        if not profile.block or not profile.floor or not profile.room_no or not profile.profile_complete:
            raise serializers.ValidationError(
                "Please complete your hostel profile before submitting a complaint."
            )

        # Do not trust Block, Floor, or Room Number values coming from the client.
        # Overwrite them with values from the StudentProfile.
        attrs["block"] = profile.block
        attrs["floor"] = profile.floor
        attrs["room_no"] = profile.room_no

        return attrs


class ComplaintStatusUpdateSerializer(serializers.ModelSerializer):
    """Used by PATCH /api/complaints/<id>/status/ — Admin only."""
    class Meta:
        model  = Complaint
        fields = ["status"]


class ComplaintVoteSerializer(serializers.ModelSerializer):
    """Returned after a vote is successfully cast."""
    class Meta:
        model  = ComplaintVote
        fields = ["id", "complaint", "student", "created_at"]
        read_only_fields = ["id", "complaint", "student", "created_at"]


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard serializer
# ─────────────────────────────────────────────────────────────────────────────

class DashboardSerializer(serializers.Serializer):
    """Read-only stats for GET /api/dashboard/"""
    total_complaints  = serializers.IntegerField()
    by_priority       = serializers.DictField(child=serializers.IntegerField())
    by_category       = serializers.DictField(child=serializers.IntegerField())
    by_block          = serializers.DictField(child=serializers.IntegerField())
    by_complaint_type = serializers.DictField(child=serializers.IntegerField())
    monthly_trend     = serializers.ListField()
    model_info        = serializers.DictField()
