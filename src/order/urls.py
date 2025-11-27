from django.urls import path
from .views import PrepareOrderView, TossSuccessView, TossFailView

app_name = "order"

urlpatterns = [
    path("prepare/", PrepareOrderView.as_view(), name="prepare"),
    path("success/", TossSuccessView.as_view(), name="success"),
    path("fail/", TossFailView.as_view(), name="fail"),
]
