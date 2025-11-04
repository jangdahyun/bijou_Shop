from django.contrib import admin

from .models import Product, ProductImage, ProductOption


class ProductOptionInline(admin.TabularInline):
    model = ProductOption #Product와 외래키로 연결된 옵션 자동 로딩
    extra = 0 #추가 옵션 폼 개수


class ProductImageInline(admin.TabularInline):
    model = ProductImage #ProductImage와 외래키로 연결된 이미지 자동 로딩
    extra = 1 #추가 이미지 폼 개수


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "price",
        "discount_price",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "category")
    search_fields = ("name", "sku")
    autocomplete_fields = ("category",)
    inlines = [ProductOptionInline, ProductImageInline]
    list_select_related = ("category",)


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
