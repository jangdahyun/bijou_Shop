from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """소프트 삭제 지원"""

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        update_fields = ["is_deleted", "deleted_at"]
        if hasattr(self, "updated_at"):
            self.updated_at = timezone.now()
            update_fields.append("updated_at")
        self.save(update_fields=update_fields)

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)


class SiteSetting(TimeStampedModel):
    """전역 환경 설정 (키-값)"""

    key = models.CharField(max_length=120, unique=True)
    raw_value = models.TextField(blank=True)
    json_value = models.JSONField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["key"]

    def __str__(self) -> str:
        return f"{self.key}"


class Notice(TimeStampedModel):
    """사이트 공지사항"""

    title = models.CharField(max_length=200)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-is_pinned", "display_order", "-created_at"]

    def __str__(self) -> str:
        return self.title


class NoticeAttachment(TimeStampedModel):
    """공지사항 첨부 파일"""

    notice = models.ForeignKey(
        Notice,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(upload_to="notices/%Y/%m/")
    original_name = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["notice", "display_order", "id"]

    def __str__(self) -> str:
        return f"Attachment<{self.pk}> for {self.notice_id}"


class Banner(TimeStampedModel):
    """배너/팝업 이미지"""

    class Placement(models.TextChoices):
        HOME_MAIN = "HOME_MAIN", "메인 상단"
        HOME_SIDEBAR = "HOME_SIDEBAR", "메인 사이드"
        PRODUCT_LIST = "PRODUCT_LIST", "상품 목록"
        CHECKOUT = "CHECKOUT", "결제/장바구니"
        ETC = "ETC", "기타"

    title = models.CharField(max_length=150)
    image = models.ImageField(upload_to="banners/%Y/%m/")
    link_url = models.URLField(blank=True)
    placement = models.CharField(
        max_length=20,
        choices=Placement.choices,
        default=Placement.HOME_MAIN,
    )
    is_active = models.BooleanField(default=True)
    open_in_new_tab = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["placement", "display_order", "-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.placement})"


class FAQCategory(TimeStampedModel):
    """FAQ 카테고리"""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class FAQ(TimeStampedModel):
    """자주 묻는 질문"""

    category = models.ForeignKey(
        FAQCategory,
        on_delete=models.CASCADE,
        related_name="faqs",
    )
    question = models.CharField(max_length=200)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["category", "display_order", "id"]

    def __str__(self) -> str:
        return self.question


class PolicyDocument(TimeStampedModel):
    """약관/정책 버전"""

    class PolicyType(models.TextChoices):
        TERMS = "TERMS", "이용약관"
        PRIVACY = "PRIVACY", "개인정보 처리방침"
        REFUND = "REFUND", "환불 규정"
        SHIPPING = "SHIPPING", "배송 정책"
        ETC = "ETC", "기타"

    policy_type = models.CharField(
        max_length=20,
        choices=PolicyType.choices,
    )
    version = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    content = models.TextField()
    effective_from = models.DateField()
    is_active = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policy_documents",
    )

    class Meta:
        unique_together = ("policy_type", "version")
        ordering = ["policy_type", "-effective_from"]

    def __str__(self) -> str:
        return f"{self.get_policy_type_display()} v{self.version}"


class PolicyAcknowledgement(TimeStampedModel):
    """사용자 약관 동의 이력"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="policy_acknowledgements",
    )
    policy = models.ForeignKey(
        PolicyDocument,
        on_delete=models.CASCADE,
        related_name="acknowledgements",
    )
    agreed_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "policy")
        ordering = ["-agreed_at"]

    def __str__(self) -> str:
        return f"{self.user} agreed to {self.policy}"
