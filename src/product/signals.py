from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from product.models import Product
from product.search import delete_product, index_product

# 상품 저장 신호 처리기
@receiver(post_save, sender=Product)
def on_product_save(sender, instance, **kwargs):
    index_product(instance)

# 상품 삭제 신호 처리기
@receiver(post_delete, sender=Product)
def on_product_delete(sender, instance, **kwargs):
    delete_product(instance.id)
