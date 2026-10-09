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


class PredictOnlySerializer(serializers.Serializer):
    """
    Lightweight serializer for POST /api/predict/ — no DB save.
    Validates the fields needed for ML inference only.
    """
    complaint_text    = serializers.CharField(min_length=10)
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
    students_affected = serializers.IntegerField(min_value=1, default=1)
    support_count     = serializers.IntegerField(min_value=0, default=0)

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
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

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
    """
    submitted_by_username = serializers.SerializerMethodField()
    user_has_voted        = serializers.SerializerMethodField()
    predicted_priority    = serializers.CharField(read_only=True)
    support_count         = serializers.IntegerField(read_only=True)
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
            "students_affected",
            "duration",
            "support_count",
            "predicted_priority",
            "status",
            "submitted_by_username",
            "user_has_voted",
            "created_at",
        ]

    def get_submitted_by_username(self, obj):
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


class ComplaintCreateSerializer(serializers.ModelSerializer):
    """
    Write serializer — used only for POST /api/complaints/.
    submitted_by is NOT accepted from the client; it is set from the JWT token.
    predicted_priority and status are set by the server.
    """
    block   = serializers.CharField(required=False, allow_blank=True)
    floor   = serializers.CharField(required=False, allow_blank=True)
    room_no = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model  = Complaint
        fields = [
            "complaint_text",
            "complaint_type",
            "category",
            "block",
            "floor",
            "room_no",
            "students_affected",
            "duration",
        ]

    def validate_complaint_text(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Complaint text must be at least 10 characters."
            )
        return value.strip()

    def validate_students_affected(self, value):
        if value < 1:
            raise serializers.ValidationError("students_affected must be at least 1.")
        return value

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
