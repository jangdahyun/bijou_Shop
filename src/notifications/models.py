from django.conf import settings
from django.db import models

from common.models import TimeStampedModel
from product.models import Product, ProductOption

class Notification(TimeStampedModel):
    """알림 예약 및 발송 기록"""

    class NotificationType(models.TextChoices):
        RESTOCK = "RESTOCK", "재입고 알림"
        PRICE_DROP = "PRICE_DROP", "가격 변동 알림"
        PROMOTION = "PROMOTION", "프로모션 알림"

    class Status(models.TextChoices): #알람처리
        PENDING = "PENDING", "대기"
        SCHEDULED = "SCHEDULED", "예약됨"
        SENT = "SENT", "발송 완료"
        CANCELED = "CANCELED", "취소"
        FAILED = "FAILED", "실패"

    class Channel(models.TextChoices):
        IN_APP = "IN_APP", "앱 알림"
        EMAIL = "EMAIL", "이메일"
        SMS = "SMS", "문자"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    product_option = models.ForeignKey(
        ProductOption,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    channel = models.CharField(
        max_length=10,
        choices=Channel.choices,
        default=Channel.IN_APP,
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.CharField(max_length=255, blank=True)
    extra_payload = models.JSONField(blank=True, default=dict)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["notification_type", "status"]),
            models.Index(fields=["scheduled_for"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_notification_type_display()} -> {self.user}"
