from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

import re
from django.core.exceptions import ValidationError

import hashlib  # 난수,해시함수 사용
from datetime import date

import requests

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
    
#----------------------------------비밀번호 유출 확인용----------------------------------
def is_pwned_password(password: str) -> bool:
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper() # 비밀번호 -> utf-8-> SHA-1 해시 생성
    prefix, suffix = digest[:5], digest[5:] # 앞 5자리와 나머지로 분리

     # Pwned Passwords API에 접속하여 앞 5자리와 일치하는 해시 목록을 가져옴
     # https://haveibeenpwned.com/API/v3#PwnedPasswords
     # 응답은 해시 뒷부분과 출현 횟수로 구성된 텍스트
     # 예: 003DF6C8D8E8F3C4F5E6A7B89C0D1E2F3:2
     # 이 중에서 뒷부분이 suffix와 일치하는지 확인
     # 일치하면 해당 비밀번호가 유출된 것으로 간주
     # 타임아웃 2초 설정
     # 예외 발생 시 호출자에게 전달
     # 일치 여부 반환
     # any() 함수 사용하여 한 줄이라도 일치하면 True 반환
     # splitlines() 함수 사용하여 응답 텍스트를 줄 단위로 분리
     # 각 줄을 ':'로 분리하여 해시 뒷부분과 출현 횟수 추출
     # 해시 뒷부분이 suffix와 일치하는지 확인
     # 일치하면 True 반환, 그렇지 않으면 False 반환
     # 최종적으로 비밀번호 유출 여부 반환
    resp = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=2)
    resp.raise_for_status()
    return any(line.split(":")[0] == suffix for line in resp.text.splitlines())
    
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
    
    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if not password:
            return password
        password_validation.validate_password(password)
        if is_pwned_password(password):
            raise ValidationError(
                "이 비밀번호는 유출된 적이 있어 사용할 수 없습니다. "
                "다른 비밀번호를 사용해 주세요."
            )
        return password


class VerificationForm(forms.Form):
    code = forms.CharField(
        label="이메일 인증번호", max_length=6, min_length=6, strip=True
    )
