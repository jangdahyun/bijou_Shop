from django.conf import settings
from django.db import models
from delivery.models import Delivery
from product.models import Product, ProductOption

class Order(models.Model):
    """주문 및 배송 정보"""

    class Status(models.TextChoices):
        PENDING = "PENDING", "주문 대기"
        PAID = "PAID", "결제 완료"
        PREPARING = "PREPARING", "상품 준비중"
        SHIPPED = "SHIPPED", "배송중"
        DELIVERED = "DELIVERED", "배송 완료"
        CANCELED = "CANCELED", "취소"
        REFUNDED = "REFUNDED", "환불 완료"

    class PaymentMethod(models.TextChoices):
        CARD = "CARD", "신용/체크카드"
        BANK_TRANSFER = "BANK_TRANSFER", "계좌 이체"
        VIRTUAL_ACCOUNT = "VIRTUAL_ACCOUNT", "가상계좌"
        MOBILE = "MOBILE", "모바일 결제"
        ETC = "ETC", "기타"

    order_number = models.CharField(max_length=32, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    shipping_name = models.CharField(max_length=50) # 수취인 이름
    shipping_phone = models.CharField(max_length=16) # 수취인 연락처
    shipping_postcode = models.CharField(max_length=10) # 수취인 우편번호
    shipping_address1 = models.CharField(max_length=255) # 수취인 주소
    shipping_address2 = models.CharField(max_length=255, blank=True) # 수취인 상세주소
    status = models.CharField(  # 주문 상태
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    ) 
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD,
    )
    payment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_fee = models.DecimalField( # 배송비
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    order_note = models.CharField(max_length=255, blank=True) # 주문 메모
    tracking_number = models.CharField(max_length=40, blank=True) # 운송장 번호
    courier_name = models.CharField(max_length=40, blank=True)  # 택배사 이름
    placed_at = models.DateTimeField(auto_now_add=True) # 주문 생성 시각
    paid_at = models.DateTimeField(null=True, blank=True) # 결제 완료 시각 
    shipped_at = models.DateTimeField(null=True, blank=True) # 배송 시작 시각
    delivered_at = models.DateTimeField(null=True, blank=True) # 배송 완료 시각
    canceled_at = models.DateTimeField(null=True, blank=True) # 주문 취소 시각
    refunded_at = models.DateTimeField(null=True, blank=True) # 환불 완료
    updated_at = models.DateTimeField(auto_now=True) # 마지막 수정 시각

    class Meta:
        ordering = ["-placed_at"]
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["placed_at"]),
        ]

    def __str__(self) -> str:
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    """주문별 상품 상세"""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    product_name = models.CharField(max_length=150)
    sku = models.CharField(max_length=30)
    product_option = models.ForeignKey(
        ProductOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(default=1) # 주문 수량
    discount_amount = models.DecimalField( # 할인 금액
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2) # (할인 적용된) 총 가격
    created_at = models.DateTimeField(auto_now_add=True) 

    class Meta:
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product"]),
        ]
        unique_together = ("order", "product", "product_option")

    def __str__(self) -> str:
        return f"{self.order.order_number} - {self.product_name}"
