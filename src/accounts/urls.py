from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView    

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
]