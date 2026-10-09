"""
HostelSenseAI — Root URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


def root_redirect(request):
    return redirect("/api/")


def health_check(request):
    return JsonResponse({"status": "ok", "service": "HostelSenseAI API"})


urlpatterns = [
    # Root redirect
    path("", root_redirect, name="root_redirect"),

    # Django admin
    path("admin/", admin.site.urls),

    # Health check
    path("health/", health_check, name="health_check"),

    # JWT Auth — provided by simplejwt
    path("api/auth/login/",   TokenObtainPairView.as_view(),  name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(),     name="token_refresh"),
    path("api/auth/verify/",  TokenVerifyView.as_view(),      name="token_verify"),

    # All other API routes (register, me, profile, complaints, vote, dashboard)
    path("api/", include("complaints.urls")),
]
