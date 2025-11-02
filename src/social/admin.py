from django.contrib import admin

from .models import Inquiry, InquiryMessage, Review, ReviewImage


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "product_option",
        "user",
        "rating",
        "is_public",
        "is_verified_purchase",
        "created_at",
    )
    list_filter = ("rating", "is_public", "is_verified_purchase", "created_at")
    search_fields = ("product__name", "user__username", "content")
    inlines = [ReviewImageInline]


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ("review", "image", "display_order", "created_at")
    list_filter = ("created_at",)


class InquiryMessageInline(admin.TabularInline):
    model = InquiryMessage
    extra = 0


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "product",
        "category",
        "status",
        "is_public",
        "created_at",
    )
    list_filter = ("category", "status", "is_public")
    search_fields = ("title", "question", "user__username")
    inlines = [InquiryMessageInline]


@admin.register(InquiryMessage)
class InquiryMessageAdmin(admin.ModelAdmin):
    list_display = ("inquiry", "author", "is_staff_reply", "created_at")
    list_filter = ("is_staff_reply", "created_at")
