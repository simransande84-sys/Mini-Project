"""
complaints/urls.py
==================
All URL routes. Mounted under /api/ in hostelSenseAI/urls.py.
"""
from django.urls import path
from .views import (
    api_root,
    RegisterView,
    MeView,
    StudentProfileView,
    PredictView,
    ComplaintListCreateView,
    ComplaintDetailView,
    ComplaintStatusUpdateView,
    MyComplaintsView,
    PublicComplaintsView,
    ComplaintVoteView,
    dashboard_view,
    water_level_view,
)

urlpatterns = [
    # ── API Root ───────────────────────────────────────────────────────
    path("", api_root, name="api-root"),

    # ── Auth ───────────────────────────────────────────────────────────
    path("auth/register/", RegisterView.as_view(),       name="auth-register"),
    path("auth/me/",       MeView.as_view(),             name="auth-me"),
    path("auth/profile/",  StudentProfileView.as_view(), name="auth-profile"),

    # ── ML Prediction (no DB save) ─────────────────────────────────────
    path("predict/", PredictView.as_view(), name="predict"),

    # ── Complaints ─────────────────────────────────────────────────────
    path("complaints/",             ComplaintListCreateView.as_view(),  name="complaint-list-create"),
    path("complaints/mine/",        MyComplaintsView.as_view(),         name="complaint-mine"),
    path("complaints/public/",      PublicComplaintsView.as_view(),     name="complaint-public"),
    path("complaints/<int:pk>/",    ComplaintDetailView.as_view(),      name="complaint-detail"),
    path("complaints/<int:pk>/status/", ComplaintStatusUpdateView.as_view(), name="complaint-status"),
    path("complaints/<int:pk>/vote/",   ComplaintVoteView.as_view(),        name="complaint-vote"),

    # ── Dashboard & Monitoring (admin only) ────────────────────────────
    path("dashboard/",   dashboard_view,   name="dashboard"),
    path("water-level/", water_level_view, name="water-level"),
]

