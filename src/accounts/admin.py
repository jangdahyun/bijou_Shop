from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account


@admin.register(Account)
class AccountAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "name",
        "role",
        "is_active",
        "last_login",
    )
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "name", "phone")
    ordering = ("-date_joined",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "추가 정보",
            {
                "fields": (
                    "name",
                    "birth_date",
                    "phone",
                    "address",
                    "role",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "추가 정보",
            {
                "classes": ("wide",),
                "fields": (
                    "name",
                    "birth_date",
                    "phone",
                    "address",
                    "role",
                ),
            },
        ),
    )
