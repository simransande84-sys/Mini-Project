"""
complaints/admin.py
====================
Registers all models in Django Admin.
"""
from django.contrib import admin
from .models import Complaint, ComplaintVote, StudentProfile


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display  = ("id", "short_text", "complaint_type", "category", "block",
                     "floor", "duration", "predicted_priority", "status", "support_count", "created_at")
    list_filter   = ("predicted_priority", "status", "complaint_type", "category", "block")
    search_fields = ("complaint_text",)
    readonly_fields = ("predicted_priority", "support_count", "created_at")
    ordering      = ("-created_at",)
    list_per_page = 25

    def short_text(self, obj):
        return obj.complaint_text[:80] + "…" if len(obj.complaint_text) > 80 else obj.complaint_text
    short_text.short_description = "Complaint"


@admin.register(ComplaintVote)
class ComplaintVoteAdmin(admin.ModelAdmin):
    list_display  = ("id", "complaint", "student", "created_at")
    list_filter   = ("created_at",)
    search_fields = ("student__username", "complaint__complaint_text")
    readonly_fields = ("created_at",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = ("id", "user", "roll_no", "block", "floor", "room_no", "profile_complete")
    list_filter   = ("block", "profile_complete")
    search_fields = ("user__username", "roll_no")
