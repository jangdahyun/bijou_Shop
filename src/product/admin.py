from django.contrib import admin
from django.db.models import Count, Q, Sum
from django.utils.html import format_html

from .models import Product, ProductImage, ProductOption


class ProductOptionInline(admin.TabularInline):
    model = ProductOption #Product와 외래키로 연결된 옵션 자동 로딩
    extra = 0 #추가 옵션 폼 개수


class ProductImageInline(admin.TabularInline):
    model = ProductImage #ProductImage와 외래키로 연결된 이미지 자동 로딩
    extra = 1 #추가 이미지 폼 개수


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    change_list_template = "admin/product/change_list.html"
    list_display = (
        "thumbnail_preview",
        "name",
        "sku",
        "category",
        "status_badge",
        "price",
        "discount_price",
        "stock",
        "is_active",
        "created_at",
    )
    list_display_links = ("name",)
    list_filter = ("is_active", "category")
    search_fields = ("name", "sku", "description")
    autocomplete_fields = ("category",)
    inlines = [ProductOptionInline, ProductImageInline]
    list_select_related = ("category",)
    actions = ["mark_as_active", "mark_as_inactive"]

    def thumbnail_preview(self, obj):
        main_image = obj.images.filter(is_main=True).first() or obj.images.first()
        if not main_image:
            return format_html('<span class="admin-thumb admin-thumb--empty">No image</span>')
        return format_html(
            '<span class="admin-thumb" style="background-image:url({url});"></span>',
            url=main_image.image.url,
        )

    thumbnail_preview.short_description = "대표 이미지"

    def status_badge(self, obj):
        if not obj.is_active:
            color, label = "danger", "숨김"
        elif obj.stock <= 0:
            color, label = "warning", "품절"
        else:
            color, label = "success", "판매중"
        return format_html(
            '<span class="status-badge status-badge--{}">{}</span>', color, label
        )

    status_badge.short_description = "상태"

    @admin.action(description="선택 상품 판매중 처리")
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated}개의 상품을 판매중으로 전환했습니다.")

    @admin.action(description="선택 상품 숨김 처리")
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated}개의 상품을 숨김 처리했습니다.")

    def changelist_view(self, request, extra_context=None):
        dashboard = self._build_dashboard_context()
        extra_context = extra_context or {}
        extra_context["dashboard"] = dashboard
        return super().changelist_view(request, extra_context=extra_context)

    def _build_dashboard_context(self):
        queryset = Product.objects.all()
        active_count = queryset.filter(is_active=True).count()
        hidden_count = queryset.filter(is_active=False).count()
        sold_out_count = queryset.filter(stock__lte=0, is_active=True).count()
        discounted_count = queryset.filter(discount_price__isnull=False).count()

        low_stock_products = (
            queryset.filter(stock__lte=5)
            .order_by("stock", "name")[:5]
        )
        top_sellers = queryset.order_by("-sales_count")[:5]

        total_stock = queryset.aggregate(total=Sum("stock"))["total"] or 0
        total_sales = queryset.aggregate(total=Sum("sales_count"))["total"] or 0

        return {
            "cards": [
                {"label": "판매중", "value": active_count},
                {"label": "숨김", "value": hidden_count},
                {"label": "품절", "value": sold_out_count},
                {"label": "할인 진행", "value": discounted_count},
            ],
            "inventory": {
                "total_stock": total_stock,
                "total_sales": total_sales,
                "low_stock_products": low_stock_products,
            },
            "top_sellers": top_sellers,
        }


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ("product", "color", "size", "stock", "is_active")
    list_filter = ("is_active",)
    search_fields = ("product__name", "color", "size")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "display_order", "is_main", "created_at")
    list_filter = ("is_main",)
    search_fields = ("product__name",)
    autocomplete_fields = ("product",)
