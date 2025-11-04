from django.contrib import admin

from .models import Delivery


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipient_name",
        "phone",
        "postcode",
        "is_default",
        "created_at",
    )
    list_filter = ("is_default", "created_at")
    search_fields = ("user__username", "recipient_name", "phone", "postcode")
    autocomplete_fields = ("user",)
