from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product'

    def ready(self):
        # 제품 저장/삭제 시 검색 인덱스 동기화
        import product.signals  # noqa: F401
