
from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "owner",
        "task_type",
        "priority",
        "status",
        "due_date",
        "created_at",
    )

    list_filter = (
        "task_type",
        "priority",
        "status",
    )

    search_fields = (
        "title",
        "description",
        "owner__username",
    )

    ordering = ("due_date",)
