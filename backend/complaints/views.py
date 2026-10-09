"""
complaints/views.py
====================
All REST API views for HostelSense AI.

Endpoint map:
  POST   /api/auth/register/          → RegisterView
  GET    /api/auth/me/                → MeView
  GET    PATCH /api/auth/profile/     → StudentProfileView

  GET    /api/                        → api_root
  POST   /api/predict/                → PredictView
  GET    POST /api/complaints/        → ComplaintListCreateView
  GET    PUT DELETE /api/complaints/<id>/   → ComplaintDetailView
  PATCH  /api/complaints/<id>/status/ → ComplaintStatusUpdateView
  GET    /api/complaints/mine/        → MyComplaintsView
  GET    /api/complaints/public/      → PublicComplaintsView
  GET    POST DELETE /api/complaints/<id>/vote/ → ComplaintVoteView
  GET    /api/dashboard/              → dashboard_view
"""
import logging
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Complaint, ComplaintVote, StudentProfile
from .serializers import (
    ComplaintCreateSerializer,
    ComplaintSerializer,
    ComplaintStatusUpdateSerializer,
    ComplaintVoteSerializer,
    DashboardSerializer,
    PredictOnlySerializer,
    RegisterSerializer,
    StudentProfileSerializer,
    UserSerializer,
)
from .utils import apply_priority_update, get_model_info, is_model_loaded, predict_priority

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# API Root
# ─────────────────────────────────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    """GET /api/ — returns a directory of all endpoints."""
    base = request.build_absolute_uri("/api/")
    return Response({
        "service":  "HostelSense AI REST API",
        "version":  "2.0",
        "endpoints": {
            "register":          base + "auth/register/",
            "login":             base + "auth/login/",
            "refresh":           base + "auth/refresh/",
            "me":                base + "auth/me/",
            "profile":           base + "auth/profile/",
            "predict":           base + "predict/",
            "complaints":        base + "complaints/",
            "my_complaints":     base + "complaints/mine/",
            "public_complaints": base + "complaints/public/",
            "vote":              base + "complaints/<id>/vote/",
            "status_update":     base + "complaints/<id>/status/",
            "dashboard":         base + "dashboard/",
        },
        "admin":  request.build_absolute_uri("/admin/"),
        "health": request.build_absolute_uri("/health/"),
    })


# ─────────────────────────────────────────────────────────────────────────────
# Auth Views
# ─────────────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """
    POST /api/auth/register/
    Public — no authentication required.
    Creates a User + StudentProfile. Returns user info.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    """GET /api/auth/me/ — returns the currently authenticated user's info."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class StudentProfileView(APIView):
    """
    GET  /api/auth/profile/ — view your hostel profile
    PATCH /api/auth/profile/ — update block, floor, room_no, phone
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = StudentProfile.objects.get_or_create(
            user=request.user,
            defaults={"roll_no": request.user.username},
        )
        return Response(StudentProfileSerializer(profile).data)

    def patch(self, request):
        profile, _ = StudentProfile.objects.get_or_create(
            user=request.user,
            defaults={"roll_no": request.user.username},
        )
        serializer = StudentProfileSerializer(profile, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


# ─────────────────────────────────────────────────────────────────────────────
# ML Prediction (no DB save)
# ─────────────────────────────────────────────────────────────────────────────

class PredictView(APIView):
    """
    POST /api/predict/
    Predicts priority WITHOUT saving to DB.
    Used for real-time preview in the Submit Complaint form.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        serializer = PredictOnlySerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not is_model_loaded():
            return Response(
                {"error": "ML model not loaded."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        priority = predict_priority(serializer.validated_data)
        return Response({"predicted_priority": priority, "model_loaded": True})


# ─────────────────────────────────────────────────────────────────────────────
# Complaint CRUD
# ─────────────────────────────────────────────────────────────────────────────

class ComplaintListCreateView(ListCreateAPIView):
    """
    GET  /api/complaints/ — Admin sees all; students see their own + public.
    POST /api/complaints/ — Submit a complaint (authenticated students only).
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields   = ["category", "block", "predicted_priority", "status", "complaint_type"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Complaint.objects.filter(complaint_type="Public")
        if user.is_staff:
            return Complaint.objects.all()
        # Students see their own + all public
        return Complaint.objects.filter(
            submitted_by=user
        ) | Complaint.objects.filter(complaint_type="Public")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ComplaintCreateSerializer
        return ComplaintSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        # Run ML prediction
        data = serializer.validated_data
        priority = predict_priority({
            "complaint_text" : data.get("complaint_text", ""),
            "complaint_type" : data.get("complaint_type", "Public"),
            "block"          : data.get("block", "A"),
            "floor"          : data.get("floor", "Ground"),
            "category"       : data.get("category", "Other"),
            "duration"       : data.get("duration"),   # "N unit" format → Duration_Hours
        })
        serializer.save(
            submitted_by=self.request.user,
            predicted_priority=priority,
            status="Pending",
            support_count=0,
            created_at=timezone.now(),
        )
        logger.info(
            "New complaint by %s — priority: %s | duration: %s",
            self.request.user.username, priority, data.get("duration"),
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Return full representation (with predicted_priority, status, etc.)
        instance = Complaint.objects.get(pk=serializer.instance.pk)
        return Response(
            ComplaintSerializer(instance, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class ComplaintDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET    /api/complaints/<id>/ — retrieve single complaint
    PUT    /api/complaints/<id>/ — full update (admin only)
    DELETE /api/complaints/<id>/ — delete (admin only)
    """
    queryset         = Complaint.objects.all()
    serializer_class = ComplaintSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]


class ComplaintStatusUpdateView(APIView):
    """
    PATCH /api/complaints/<id>/status/
    Admin-only endpoint to update complaint status.
    """
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            complaint = Complaint.objects.get(pk=pk)
        except Complaint.DoesNotExist:
            return Response({"error": "Complaint not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ComplaintStatusUpdateSerializer(complaint, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(
            ComplaintSerializer(complaint, context={"request": request}).data
        )


class MyComplaintsView(APIView):
    """
    GET /api/complaints/mine/
    Returns only the complaints submitted by the current student.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        complaints = Complaint.objects.filter(submitted_by=request.user)
        serializer = ComplaintSerializer(
            complaints, many=True, context={"request": request}
        )
        return Response(serializer.data)


class PublicComplaintsView(APIView):
    """
    GET /api/complaints/public/
    Returns all public complaints sorted by support_count descending.
    Accessible without authentication (for browsing trending issues).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        complaints = Complaint.objects.filter(
            complaint_type="Public"
        ).order_by("-support_count", "-created_at")
        serializer = ComplaintSerializer(
            complaints, many=True, context={"request": request}
        )
        return Response(serializer.data)


# ─────────────────────────────────────────────────────────────────────────────
# Support (Vote) System
# ─────────────────────────────────────────────────────────────────────────────

class ComplaintVoteView(APIView):
    """
    GET    /api/complaints/<id>/vote/ — check if current user has voted
    POST   /api/complaints/<id>/vote/ — cast support vote
    DELETE /api/complaints/<id>/vote/ — remove support vote

    After every vote change:
      1. support_count is updated on the Complaint
      2. ML model is re-run
      3. Escalation rules applied
      4. predicted_priority updated in DB
    """
    permission_classes = [IsAuthenticated]

    def _get_complaint(self, pk):
        try:
            return Complaint.objects.get(pk=pk)
        except Complaint.DoesNotExist:
            return None

    def get(self, request, pk):
        complaint = self._get_complaint(pk)
        if not complaint:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        voted = ComplaintVote.objects.filter(
            complaint=complaint, student=request.user
        ).exists()
        return Response({
            "user_has_voted":  voted,
            "support_count":   complaint.support_count,
        })

    def post(self, request, pk):
        complaint = self._get_complaint(pk)
        if not complaint:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if complaint.complaint_type != "Public":
            return Response(
                {"error": "You can only support public complaints."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            ComplaintVote.objects.create(complaint=complaint, student=request.user)
        except IntegrityError:
            return Response(
                {"error": "You have already supported this complaint."},
                status=status.HTTP_409_CONFLICT,
            )

        # Update support_count and re-run priority calculation
        complaint.support_count = ComplaintVote.objects.filter(complaint=complaint).count()
        complaint.predicted_priority = apply_priority_update(complaint)
        complaint.save(update_fields=["support_count", "predicted_priority"])

        return Response({
            "message":        "Support added.",
            "support_count":  complaint.support_count,
            "predicted_priority": complaint.predicted_priority,
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        complaint = self._get_complaint(pk)
        if not complaint:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        deleted, _ = ComplaintVote.objects.filter(
            complaint=complaint, student=request.user
        ).delete()

        if deleted == 0:
            return Response(
                {"error": "You have not supported this complaint."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Recalculate support count + priority
        complaint.support_count = ComplaintVote.objects.filter(complaint=complaint).count()
        complaint.predicted_priority = apply_priority_update(complaint)
        complaint.save(update_fields=["support_count", "predicted_priority"])

        return Response({
            "message":       "Support removed.",
            "support_count": complaint.support_count,
            "predicted_priority": complaint.predicted_priority,
        })


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([IsAdminUser])
def dashboard_view(request):
    """
    GET /api/dashboard/
    Admin-only aggregated statistics including monthly trend.
    """
    def qs_to_dict(queryset, key_field):
        return {item[key_field]: item["count"] for item in queryset}

    total = Complaint.objects.count()

    by_priority = qs_to_dict(
        Complaint.objects.values("predicted_priority").annotate(count=Count("id")),
        "predicted_priority",
    )
    by_category = qs_to_dict(
        Complaint.objects.values("category").annotate(count=Count("id")),
        "category",
    )
    by_block = qs_to_dict(
        Complaint.objects.values("block").annotate(count=Count("id")),
        "block",
    )
    by_complaint_type = qs_to_dict(
        Complaint.objects.values("complaint_type").annotate(count=Count("id")),
        "complaint_type",
    )

    # Monthly trend — last 12 months
    twelve_months_ago = timezone.now() - timedelta(days=365)
    monthly_trend = (
        Complaint.objects
        .filter(created_at__gte=twelve_months_ago)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    monthly_data = [
        {
            "month": item["month"].strftime("%b %Y") if item["month"] else "Unknown",
            "count": item["count"],
        }
        for item in monthly_trend
    ]

    return Response({
        "total_complaints":  total,
        "by_priority":       by_priority,
        "by_category":       by_category,
        "by_block":          by_block,
        "by_complaint_type": by_complaint_type,
        "monthly_trend":     monthly_data,
        "model_info":        get_model_info(),
    })
