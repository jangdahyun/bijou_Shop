from django.conf import settings
from django.db import models
from django.db.models import Q

from common.models import TimeStampedModel
from product.models import Product, ProductOption


class Review(TimeStampedModel):
    """상품 리뷰"""

    class Rating(models.IntegerChoices):
        ONE = 1, "1점"
        TWO = 2, "2점"
        THREE = 3, "3점"
        FOUR = 4, "4점"
        FIVE = 5, "5점"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    product_option = models.ForeignKey(
        ProductOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        choices=Rating.choices,
        default=Rating.FIVE,
    )
    title = models.CharField(max_length=150, blank=True)
    content = models.TextField()
    is_public = models.BooleanField(default=True)
    is_verified_purchase = models.BooleanField(
        default=False,
        help_text="주문 이력이 검증된 리뷰 여부",
    )
    helpful_count = models.PositiveIntegerField(default=0)
    reported_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                condition=Q(product_option__isnull=True),
                name="unique_review_per_product_without_option",
            ),
            models.UniqueConstraint(
                fields=["user", "product", "product_option"],
                condition=Q(product_option__isnull=False),
                name="unique_review_per_product_option",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.product} 리뷰 by {self.user}"

    @property
    def score(self) -> int:
        return self.rating


class ReviewImage(TimeStampedModel):
    """리뷰 첨부 이미지"""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="reviews/%Y/%m/")
    alt_text = models.CharField(max_length=150, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["review", "display_order", "id"]

    def __str__(self) -> str:
        return f"ReviewImage<{self.review_id}>"


class Inquiry(TimeStampedModel):
    """상품 문의 및 고객 질문"""

    class Category(models.TextChoices):
        PRODUCT = "PRODUCT", "상품"
        DELIVERY = "DELIVERY", "배송"
        ORDER = "ORDER", "주문/결제"
        RETURN = "RETURN", "반품/교환"
        ETC = "ETC", "기타"

    class Status(models.TextChoices):
        PENDING = "PENDING", "답변 대기"
        ANSWERED = "ANSWERED", "답변 완료"
        CLOSED = "CLOSED", "종료"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inquiries",
    )
    email = models.EmailField(blank=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inquiries",
    )
    product_option = models.ForeignKey(
        ProductOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inquiries",
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.PRODUCT,
    )
    title = models.CharField(max_length=150)
    question = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    is_public = models.BooleanField(
        default=False,
        help_text="다른 고객에게 공개할지 여부",
    )
    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="answered_inquiries",
    )
    answered_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        target = self.product or "일반 문의"
        return f"{target} 문의 ({self.get_status_display()})"


class InquiryMessage(TimeStampedModel):
    """문의에 대한 추가 대화(고객/관리자)"""

    inquiry = models.ForeignKey(
        Inquiry,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inquiry_messages",
    )
    is_staff_reply = models.BooleanField(default=False) # 관리자 답변 여부
    message = models.TextField()

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        role = "관리자" if self.is_staff_reply else "고객"
        return f"{role} 메시지 #{self.pk}"
