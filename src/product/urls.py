from django.urls import path

from product.views import ProductSearchView

app_name = "product"

urlpatterns = [
    path("search/", ProductSearchView.as_view(), name="search"),
]
