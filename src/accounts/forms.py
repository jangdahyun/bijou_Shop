from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginForm(AuthenticationForm):
    email = forms.EmailField(
        label="Email",max_length=150)
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput)