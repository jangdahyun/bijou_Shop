from decimal import Decimal

from django.db import models
from catalog.models import Category


class Product(models.Model):
    """쇼핑몰 상품 정보"""

    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=30, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="할인 가격이 없으면 기본 가격으로 노출됩니다.",
    )
    stock = models.PositiveIntegerField(default=0) # 전체 재고 수량
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    
    view_count = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "sku"]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"

    @property
    def sale_price(self):
        """할인 가격이 설정된 경우 그 값을, 아니면 기본 가격을 반환"""
        return self.discount_price or self.price

    @property
    def discount_rate(self) -> Decimal:
        """할인율(%)을 반환. 할인 가격이 없으면 0"""
        if self.discount_price and self.price:
            return (self.price - self.discount_price) / self.price * Decimal("100")
        return Decimal("0")


class ProductOption(models.Model):
    """상품 옵션(색상, 사이즈 등)"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="options",
    )
    color = models.CharField(max_length=30, blank=True)
    size = models.CharField(max_length=30, blank=True)
    extra_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="옵션별 추가 금액 (없으면 0)",
    )
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "color", "size")
        ordering = ["product", "color", "size"]

    def __str__(self) -> str:
        option = ", ".join(filter(None, [self.color, self.size]))
        return f"{self.product.name} ({option or '기본'})"


class ProductImage(models.Model):
    """상품 이미지 테이블"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/%Y/%m/")
    alt_text = models.CharField(
        max_length=150,
        blank=True,
        help_text="이미지가 로드되지 않을 때 대신 노출할 문구",
    )
    is_main = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0) # 이미지 노출 순서
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_main", "display_order", "id"]
        indexes = [
            models.Index(fields=["product", "display_order"]),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} 이미지 #{self.pk}"
