from decimal import Decimal
from typing import Dict, List

from product.models import Product
from common.meili import get_product_index


def _document(product: Product) -> Dict:
    # 인스턴스 dictionary 변환
    colors = list(product.options.values_list("color", flat=True).distinct())
    sizes = list(product.options.values_list("size", flat=True).distinct())
    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "category": product.category.slug if product.category else "",
        "price": float(product.price),
        "discount_price": float(product.discount_price) if product.discount_price else None,
        "discount_rate": float(product.discount_rate) if isinstance(product.discount_rate, Decimal) else 0.0,
        "is_active": product.is_active,
        "in_stock": product.stock > 0,
        "colors": colors,
        "sizes": sizes,
        "view_count": product.view_count,
        "sales_count": product.sales_count,
        "review_count": product.review_count,
        "created_at": product.created_at.isoformat(),
        "description": product.description,
    }


def index_product(product: Product):
    get_product_index().add_documents([_document(product)])


def delete_product(product_id: int):
    get_product_index().delete_documents([product_id])


def bulk_index():
    #모든 상품 색인
    docs: List[Dict] = [_document(p) for p in Product.objects.all()]
    get_product_index().add_documents(docs)
