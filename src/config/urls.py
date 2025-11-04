from django.contrib import admin
from django.urls import path, include
from catalog import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    # path("axes/", include("axes.urls"))
    
]
