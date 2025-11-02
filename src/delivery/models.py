from django.db import models
from django.conf import settings

# Create your models here.

class Delivery(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    recipient_name = models.CharField(max_length=50) #수령인
    phone = models.CharField(max_length=16)
    postcode = models.CharField(max_length=10) #우편번호
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    is_default = models.BooleanField(default=False) #기본 배송지 여부
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    request_note = models.CharField(max_length=255, blank=True)  #배송 요청 사항

    def __str__(self):
        return f"{self.user.username} - {self.recipient_name} ({'기본' if self.is_default else '추가'})"