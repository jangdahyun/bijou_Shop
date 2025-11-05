from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

import re
from django.core.exceptions import ValidationError

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
    username = forms.CharField(label="아이디", max_length=150, required=True)
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
        return phone
    
    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            raise ValidationError("닉네임을 입력해주세요.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("이미 사용 중인 닉네임입니다.")
        return username

    def _save_extra_to_user(self, user):
        cd = self.cleaned_data
        user.username = cd["username"]
        user.email = cd["email"]
        if hasattr(user, "name"):
            user.name = cd["name"]
        if hasattr(user, "phone"):
            user.phone = cd["phone"]
        if hasattr(user, "birth_date"):
            user.birth_date = cd["birth_date"]
        if hasattr(user, "address"):
            user.address = cd["address"]
        user.save()
        return user
    
# class SignUpForm(UserCreationForm):