from django.conf import settings
from django.db import models
from django.db.models import Q

from common.models import TimeStampedModel
from product.models import Product, ProductOption


class Cart(TimeStampedModel):
    """고객별 장바구니"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
        null=True,
        blank=True,
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        db_index=True,
        help_text="비회원 장바구니 세션",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(user__isnull=False) | Q(session_key__gt=""),
                name="cart_requires_user_or_session", 
            ),
            models.UniqueConstraint( 
                fields=["user"],
                condition=Q(user__isnull=False, is_active=True),
                name="cart_unique_active_user", #중복 방지
            ),
            models.UniqueConstraint(
                fields=["session_key"],
                condition=Q(session_key__gt="", is_active=True),
                name="cart_unique_active_session", #중복 세션 방지
            ),
        ]
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        owner = self.user or f"session:{self.session_key}"
        return f"Cart<{owner}>"


class CartItem(TimeStampedModel):
    """장바구니 내 상품"""

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="cart_items",
    )
    product_option = models.ForeignKey(
        ProductOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="담을 당시 상품 가격",
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="수량당 할인 금액",
    )

    class Meta:
        unique_together = ("cart", "product", "product_option")
        ordering = ["cart", "id"]

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"

    @property
    def line_total(self):
        return (self.unit_price - self.discount_amount) * self.quantity


class Wishlist(TimeStampedModel): #컨테이너 역할
    """사용자 찜 목록"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlists",
    )
    name = models.CharField(max_length=100, blank=True)
    is_default = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(is_default=True),
                name="wishlist_unique_default",
            ),
        ]
        ordering = ["user", "-updated_at"]

    def __str__(self) -> str:
        label = self.name or "기본 찜 목록"
        return f"{self.user} - {label}"


class WishlistItem(TimeStampedModel):
    """찜 목록 상품"""

    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="wishlist_items",
    )
    product_option = models.ForeignKey(
        ProductOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wishlist_items",
    )

    class Meta:
        unique_together = ("wishlist", "product", "product_option")
        ordering = ["wishlist", "id"]

    def __str__(self) -> str:
        return f"{self.wishlist} - {self.product.name}"

