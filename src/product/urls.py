from django.urls import path

from product.views import (
    ProductAutocompleteView,
    ProductDetailView,
    ProductSearchView,
)

app_name = "product"

urlpatterns = [
    path("search/", ProductSearchView.as_view(), name="search"),
    path("autocomplete/", ProductAutocompleteView.as_view(), name="autocomplete"),
    path("<int:pk>/", ProductDetailView.as_view(), name="detail"),
]
