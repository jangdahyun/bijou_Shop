from decimal import Decimal
import random

from django.core.management.base import BaseCommand
from django.db.models import ProtectedError

from catalog.models import Category
from product.models import Product, ProductOption
from cart.models import CartItem
from order.models import OrderItem
from cart.models import WishlistItem


class Command(BaseCommand):
    help = "의류 상품/옵션 더미 데이터 생성"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="생성할 상품 수(기본 100)",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="기존 상품을 모두 삭제 후 생성",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="reset 시 관련 참조 데이터(CartItem/WishlistItem/OrderItem)까지 삭제",
        )

    def handle(self, *args, **options):
        from faker import Faker  # lazy import to keep command lightweight

        faker = Faker("ko_KR")
        count = options["count"]
        reset = options["reset"]
        force = options["force"]

        if reset:
            if force:
                self.stdout.write("참조 데이터 삭제 중... (CartItem/WishlistItem/OrderItem)")
                CartItem.objects.all().delete()
                WishlistItem.objects.all().delete()
                OrderItem.objects.all().delete()
            try:
                self.stdout.write("기존 상품 삭제 중...")
                Product.objects.all().delete()
            except ProtectedError as exc:
                self.stderr.write(
                    "상품 삭제가 차단되었습니다. 주문/장바구니 등 상품을 참조하는 데이터가 남아 있습니다."
                )
                self.stderr.write(str(exc))
                return

        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write("카테고리가 없어 기본 카테고리를 생성합니다.")
            categories = [
                Category.objects.create(name="탑", slug="top"),
                Category.objects.create(name="바텀", slug="bottom"),
                Category.objects.create(name="아우터", slug="outer"),
                Category.objects.create(name="원피스", slug="onepiece"),
            ]

        colors = ["블랙", "화이트", "네이비", "베이지", "그레이", "카키"]
        sizes = ["XS", "S", "M", "L", "XL"]

        for _ in range(count):
            base_price = random.randint(19000, 99000)
            discount = random.choice([0, 0, random.randint(2000, base_price // 3)])

            product = Product.objects.create(
                name=faker.unique.catch_phrase()[:150],
                sku=f"BJ-{faker.unique.bothify('???-#####')}",
                category=random.choice(categories),
                price=Decimal(base_price),
                discount_price=Decimal(base_price - discount) if discount else None,
                stock=random.randint(10, 80),
                description=faker.text(200),
                is_active=True,
            )

            for color in random.sample(colors, k=random.randint(2, len(colors))):
                for size in random.sample(sizes, k=random.randint(2, len(sizes))):
                    ProductOption.objects.create(
                        product=product,
                        color=color,
                        size=size,
                        extra_price=Decimal("0"),
                        stock=random.randint(5, 40),
                        is_active=True,
                    )

        self.stdout.write(self.style.SUCCESS(f"{count}건 생성 완료"))
