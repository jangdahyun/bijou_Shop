from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("product", "product_option")
    readonly_fields = ("product_name", "sku", "total_price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "status",
        "payment_amount",
        "placed_at",
        "updated_at",
    )
    list_filter = ("status", "payment_method", "placed_at")
    search_fields = (
        "order_number",
        "user__username",
        "user__email",
        "shipping_name",
        "shipping_phone",
    )
    date_hierarchy = "placed_at"
    autocomplete_fields = ("user", "delivery")
    inlines = [OrderItemInline]
    list_select_related = ("user", "delivery")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "quantity", "total_price", "created_at")
    list_filter = ("order__status",)
    search_fields = ("order__order_number", "product_name", "sku")
    autocomplete_fields = ("order", "product", "product_option")
