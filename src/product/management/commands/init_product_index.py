from django.core.management.base import BaseCommand
from django.conf import settings

from common.meili import get_product_index


class Command(BaseCommand):
    help = "상품 인덱스(Meilisearch) 초기화"

    # 설정 업데이트
    def handle(self, *args, **options):
        index = get_product_index()

        #필터 및 정렬 속성 설정
        index.update_filterable_attributes(
            ["category", "colors", "sizes", "is_active", "in_stock", "price"]
        )
        index.update_sortable_attributes(
            [
                "price",
                "discount_rate",
                "created_at",
                "view_count",
                "sales_count",
                "review_count",
            ]
        )
        #검색 가능 속성 설정
        index.update_searchable_attributes(["name", "description", "sku"])
        self.stdout.write(
            self.style.SUCCESS(f"{settings.MEILI_PRODUCT_INDEX} 인덱스 설정 완료")
        )
