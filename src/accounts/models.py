from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import RegexValidator


class AccountManager(UserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", self.model.Role.MEMBER)
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", self.model.Role.OWNER)
        if extra_fields.get("role") != self.model.Role.OWNER:
            raise ValueError("Superuser must have role of OWNER")
        return super().create_superuser(username, email, password, **extra_fields)


class Account(AbstractUser):
    REQUIRED_FIELDS = ["email", "name", "birth_date", "phone", "address"]
    class Role(models.TextChoices):
        OWNER = "OWNER", "사장"
        MANAGER = "MANAGER", "관리자"
        MEMBER = "MEMBER", "회원"

    phone_validator = RegexValidator(
        regex=r"^01[0-9]-?\d{3,4}-?\d{4}$",
        message="전화번호는 010-1234-5678 형식으로 입력해 주세요.",
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50, db_collation="utf8mb4_0900_ai_ci")
    birth_date = models.DateField()
    phone = models.CharField(
        max_length=16,
        validators=[phone_validator],
        unique=True,
    )
    address = models.CharField(max_length=255)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
        help_text="사장/관리자/회원 구분",
    )
    objects = AccountManager()

    def save(self, *args, **kwargs):
        if self.role == self.Role.OWNER:
            self.is_staff = True
            self.is_superuser = True
        elif self.role == self.Role.MANAGER:
            self.is_staff = True
            self.is_superuser = False
        else:
            self.is_staff = False
            self.is_superuser = False
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.username
