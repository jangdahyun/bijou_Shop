import meilisearch
from django.conf import settings

_client = None


def get_client():
    global _client
    if _client is None:
        _client = meilisearch.Client(settings.MEILI_URL, settings.MEILI_API_KEY)
    return _client


def get_product_index():
    #상품 인덱스 반환
    return get_client().index(settings.MEILI_PRODUCT_INDEX)
