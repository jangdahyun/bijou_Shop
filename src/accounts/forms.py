from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

import re
from django.core.exceptions import ValidationError


import secrets, hashlib  # 난수,해시함수 사용
from datetime import date, timedelta
from django.utils import timezone
from django.utils.crypto import constant_time_compare # 안전한 문자열 비교

#----------------------------------이메일 인증용----------------------------------
SIGNUP_SESSION_KEY = "signup_verification"

def _hash_code(raw_code: str) -> str:
    """Return SHA-256 hash of the verification code."""
    return hashlib.sha256(raw_code.encode()).hexdigest()

def save_signup_session(request, payload):
    request.session[SIGNUP_SESSION_KEY] = payload
    request.session.modified = True

def get_signup_session(request):
    return request.session.get(SIGNUP_SESSION_KEY)

def clear_signup_session(request):
    request.session.pop(SIGNUP_SESSION_KEY, None)
    request.session.modified = True
User = get_user_model()


class LoginForm(AuthenticationForm):
    # username = forms.EmailField(
    #     label="Email",
    #     max_length=150,
    #     widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    # )
    username = forms.CharField(label="아이디", max_length=150)
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_recaptcha = getattr(settings, "ENABLE_RECAPTCHA", False)
        if self.use_recaptcha:
            self.fields["captcha"] = ReCaptchaField(widget=ReCaptchaV2Checkbox)

def normalize_phone(raw: str) -> str:
        digits = re.sub(r"\D", "", raw or "")
        if digits.startswith("82"):
            digits = "0" + digits[2:]
        return digits

class ExtraFieldsMixin(forms.Form):
    username = forms.CharField(label="닉네임", max_length=150, required=True)
    name = forms.CharField(label="이름", max_length=50, required=True)
    email = forms.EmailField(label="이메일", required=True)
    phone = forms.CharField(label="휴대폰 번호", max_length=16, required=True,
                            widget=forms.TextInput(attrs={"autocomplete": "tel"}))
    birth_date = forms.DateField(label="생년월일", required=True,
                                 widget=forms.DateInput(attrs={"type": "date"}))
    address = forms.CharField(label="주소", max_length=255, required=True)
    
    

    def clean_phone(self):
        phone = normalize_phone(self.cleaned_data.get("phone", ""))
        if not phone:
            raise ValidationError("전화번호를 입력해 주세요.")
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("이미 사용 중인 전화번호입니다.")
        return phone
    
    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            raise ValidationError("닉네임을 입력해주세요.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("이미 사용 중인 닉네임입니다.")
        return username

    @staticmethod
    def _save_extra_to_user(user, data):
        """Persist extra profile fields onto the user model."""
        cd = data or {}
        username = cd.get("username")
        email = cd.get("email")
        name = cd.get("name")
        phone = cd.get("phone")
        birth_date = cd.get("birth_date")
        address = cd.get("address")

        if username:
            user.username = username
        if email:
            user.email = email
        if name and hasattr(user, "name"):
            user.name = name
        if phone and hasattr(user, "phone"):
            user.phone = phone
        if birth_date and hasattr(user, "birth_date"):
            if isinstance(birth_date, str):
                try:
                    birth_date = date.fromisoformat(birth_date)
                except ValueError:
                    birth_date = None
            if birth_date:
                user.birth_date = birth_date
        if address and hasattr(user, "address"):
            user.address = address
        user.save()
        return user
    
class SignUpForm(ExtraFieldsMixin):
    password1 = forms.CharField(
        label="비밀번호",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="비밀번호 확인",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    terms_agreed = forms.BooleanField(label="필수 약관 동의", required=True)

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("비밀번호가 일치하지 않습니다.")
        if password1:
            password_validation.validate_password(password1)
        return cleaned

    def to_session_payload(self):
        fields = (
            "username",
            "name",
            "email",
            "phone",
            "birth_date",
            "address",
            "password1",
        )
        data = {field: self.cleaned_data[field] for field in fields}
        birth = data.get("birth_date")
        if birth:
            data["birth_date"] = birth.isoformat()
        return data

    @staticmethod
    def create_user_from_payload(data):
        """Create and persist a user from stored signup data."""
        data = data or {}
        user = User(
            username=data["username"],
            email=data["email"],
        )
        user.set_password(data["password1"])
        ExtraFieldsMixin._save_extra_to_user(user, data)
        return user


class VerificationForm(forms.Form):
    code = forms.CharField(
        label="이메일 인증번호", max_length=6, min_length=6, strip=True
    )
