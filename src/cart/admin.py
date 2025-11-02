from django.contrib import admin

from .models import Cart, CartItem, Wishlist, WishlistItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "is_active", "updated_at")
    list_filter = ("is_active", "updated_at")
    search_fields = ("user__username", "session_key")
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "product_option", "quantity", "unit_price")
    search_fields = ("cart__user__username", "product__name")
    list_filter = ("product",)


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "is_default", "updated_at")
    list_filter = ("is_default",)
    search_fields = ("user__username", "name")
    inlines = [WishlistItemInline]


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("wishlist", "product", "product_option", "created_at")
    search_fields = ("wishlist__user__username", "product__name")
    list_filter = ("product",)
