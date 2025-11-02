from django.contrib import admin

from .models import (
    Banner,
    FAQ,
    FAQCategory,
    Notice,
    NoticeAttachment,
    PolicyAcknowledgement,
    PolicyDocument,
    SiteSetting,
)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "raw_value", "created_at", "updated_at")
    search_fields = ("key",)
    list_filter = ("created_at",)


class NoticeAttachmentInline(admin.TabularInline):
    model = NoticeAttachment
    extra = 1


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_pinned",
        "is_active",
        "starts_at",
        "ends_at",
        "created_at",
    )
    list_filter = ("is_pinned", "is_active", "starts_at")
    search_fields = ("title", "content")
    inlines = [NoticeAttachmentInline]


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "placement",
        "is_active",
        "starts_at",
        "ends_at",
        "display_order",
    )
    list_filter = ("placement", "is_active")
    search_fields = ("title",)


class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "display_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    inlines = [FAQInline]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "category",
        "is_active",
        "display_order",
        "view_count",
    )
    list_filter = ("category", "is_active")
    search_fields = ("question", "answer")


@admin.register(PolicyDocument)
class PolicyDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "policy_type",
        "version",
        "effective_from",
        "is_active",
    )
    list_filter = ("policy_type", "is_active")
    search_fields = ("title", "content", "version")


@admin.register(PolicyAcknowledgement)
class PolicyAcknowledgementAdmin(admin.ModelAdmin):
    list_display = ("user", "policy", "agreed_at", "ip_address")
    list_filter = ("policy__policy_type", "agreed_at")
    search_fields = ("user__username", "user__email")
