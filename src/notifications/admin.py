from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "notification_type",
        "channel",
        "status",
        "scheduled_for",
        "sent_at",
        "created_at",
    )
    list_filter = ("notification_type", "channel", "status")
    search_fields = ("user__username", "user__email", "product__name")
