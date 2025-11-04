from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

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
