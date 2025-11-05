from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from .forms import LoginForm

# Django 기본 인증 뷰를 상속하여 커스터마이징
class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    # 중복 로그인 방지
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("home")


class SignUpView(TemplateView):
    template_name = "accounts/signup.html"
