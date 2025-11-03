import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

try:
    from faker import Faker
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise CommandError("Install Faker to use this command: pip install Faker") from exc

from accounts.models import Account
from cart.models import Cart, CartItem, Wishlist, WishlistItem
from catalog.models import Category
from common.models import (
    Banner,
    FAQ,
    FAQCategory,
    Notice,
    NoticeAttachment,
    PolicyAcknowledgement,
    PolicyDocument,
    SiteSetting,
)
from delivery.models import Delivery
from notifications.models import Notification
from order.models import Order, OrderItem
from product.models import Product, ProductImage, ProductOption
from social.models import Inquiry, InquiryMessage, Review, ReviewImage

fake = Faker("ko_KR")


class Command(BaseCommand):
    help = "Seed demo data across core models for development/testing."

    def add_arguments(self, parser):
        parser.add_argument("--categories", type=int, default=6)
        parser.add_argument("--products", type=int, default=24)
        parser.add_argument("--users", type=int, default=8)
        parser.add_argument("--orders", type=int, default=10)
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Remove previously seeded demo data before creating new records.",
        )

    def handle(self, *args, **options):
        categories_count = options["categories"]
        products_count = options["products"]
        user_count = options["users"]
        order_count = options["orders"]
        flush = options["flush"]

        if flush:
            self.stdout.write("Clearing existing demo data...")
            self._flush_data()
        fake.unique.clear()

        with transaction.atomic():
            owner = self._ensure_owner_account()
            members = self._create_members(user_count)
            categories = self._create_categories(categories_count)
            products = self._create_products(products_count, categories)
            self._create_product_images(products)
            self._create_site_content(owner)
            self._create_reviews(products, members)
            self._create_inquiries(products, members)
            self._create_carts_and_wishlists(products, members)
            self._create_notifications(products, members)
            self._create_orders(products, members, owner, order_count)

        self.stdout.write(self.style.SUCCESS("Demo data successfully generated."))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _flush_data(self):
        models_in_order = [
            Notification,
            OrderItem,
            Order,
            CartItem,
            Cart,
            WishlistItem,
            Wishlist,
            ReviewImage,
            Review,
            InquiryMessage,
            Inquiry,
            ProductImage,
            ProductOption,
            Product,
            FAQ,
            FAQCategory,
            NoticeAttachment,
            Notice,
            Banner,
            PolicyAcknowledgement,
            PolicyDocument,
            SiteSetting,
            Delivery,
        ]
        for model in models_in_order:
            model.objects.all().delete()

    def _ensure_owner_account(self):
        owner = Account.objects.filter(role=Account.Role.OWNER).first()
        if owner:
            return owner
        username = "admin"
        suffix = 1
        while Account.objects.filter(username=username).exists():
            suffix += 1
            username = f"admin{suffix}"

        owner = Account.objects.create_superuser(
            username=username,
            email=f"admin{suffix}@example.com",
            password="Admin1234!",
            name="관리자",
            birth_date=fake.date_of_birth(minimum_age=25, maximum_age=50),
            phone=self._generate_phone(),
            address=fake.address().replace("\n", " "),
        )
        self.stdout.write(self.style.SUCCESS(f"Created owner account '{owner.username}'"))
        return owner

    def _create_members(self, count):
        members = []
        for _ in range(count):
            username = fake.unique.user_name()
            member = Account.objects.create_user(
                username=username,
                email=fake.unique.email(),
                password="User1234!",
                name=fake.name(),
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=50),
                phone=self._generate_phone(),
                address=fake.address().replace("\n", " "),
            )
            members.append(member)
        return members

    def _create_categories(self, count):
        categories = []
        for _ in range(count):
            name = fake.unique.word().title()
            category = Category.objects.create(name=name)
            categories.append(category)
        return categories

    def _create_products(self, count, categories):
        products = []
        for _ in range(count):
            category = random.choice(categories)
            price = Decimal(random.randrange(10000, 150000))
            discount_price = None
            if random.random() < 0.5:
                discount_price = price - Decimal(random.randrange(1000, 20000))
                discount_price = max(discount_price, Decimal("1000"))

            product = Product.objects.create(
                name=fake.unique.catch_phrase(),
                sku=fake.unique.bothify(text="SKU-####"),
                category=category,
                price=price,
                discount_price=discount_price,
                stock=random.randrange(0, 300),
                description=fake.text(max_nb_chars=250),
                view_count=random.randrange(0, 500),
                sales_count=random.randrange(0, 300),
                review_count=random.randrange(0, 120),
            )

            option_variants = random.randint(0, 3)
            for _ in range(option_variants):
                ProductOption.objects.create(
                    product=product,
                    color=fake.safe_color_name(),
                    size=random.choice(["XS", "S", "M", "L", "XL"]),
                    extra_price=Decimal(random.randrange(0, 15000)),
                    stock=random.randrange(0, 100),
                )

            products.append(product)
        return products

    def _create_product_images(self, products):
        for product in products:
            for idx in range(random.randint(1, 3)):
                ProductImage.objects.create(
                    product=product,
                    image=f"products/{timezone.now():%Y/%m}/demo_{product.pk}_{idx}.jpg",
                    alt_text=fake.sentence(nb_words=6),
                    is_main=(idx == 0),
                    display_order=idx,
                )

    def _create_site_content(self, owner):
        SiteSetting.objects.get_or_create(
            key="CUSTOMER_SERVICE_PHONE",
            defaults={
                "raw_value": "02-1234-5678",
                "description": "고객센터 대표 전화",
            },
        )
        SiteSetting.objects.get_or_create(
            key="DEFAULT_DELIVERY_FEE",
            defaults={"raw_value": "3000", "description": "기본 배송비"},
        )

        for idx in range(3):
            Notice.objects.create(
                title=fake.sentence(nb_words=6),
                content=fake.paragraph(nb_sentences=6),
                is_pinned=idx == 0,
                is_active=True,
                display_order=idx,
                starts_at=timezone.now() - timedelta(days=7),
                ends_at=timezone.now() + timedelta(days=30),
            )

        Banner.objects.create(
            title="메인 프로모션",
            image=f"banners/{timezone.now():%Y/%m}/main.jpg",
            link_url="https://example.com/promo",
            placement=Banner.Placement.HOME_MAIN,
            is_active=True,
            display_order=0,
            starts_at=timezone.now() - timedelta(days=3),
            ends_at=timezone.now() + timedelta(days=10),
        )

        faq_category, _ = FAQCategory.objects.get_or_create(
            name="배송 안내",
            defaults={"display_order": 0, "is_active": True},
        )
        FAQ.objects.get_or_create(
            category=faq_category,
            question="배송은 얼마나 걸리나요?",
            defaults={
                "answer": "평균 2-3일 내 도착하며, 도서/산간 지역은 추가 소요됩니다.",
                "display_order": 0,
            },
        )

        policy, _ = PolicyDocument.objects.get_or_create(
            policy_type=PolicyDocument.PolicyType.TERMS,
            version="1.0",
            defaults={
                "title": "이용약관",
                "content": fake.text(max_nb_chars=1000),
                "effective_from": timezone.now().date(),
                "is_active": True,
                "published_at": timezone.now(),
                "created_by": owner,
            },
        )

        PolicyAcknowledgement.objects.get_or_create(
            user=owner,
            policy=policy,
            defaults={"ip_address": "127.0.0.1"},
        )

    def _create_reviews(self, products, members):
        for product in random.sample(products, min(len(products), 10)):
            reviewers = random.sample(members, min(len(members), random.randint(2, 5)))
            for member in reviewers:
                review = Review.objects.create(
                    product=product,
                    product_option=product.options.order_by("?").first(),
                    user=member,
                    rating=random.randint(3, 5),
                    title=fake.sentence(nb_words=4),
                content=fake.paragraph(nb_sentences=5),
                is_public=True,
                is_verified_purchase=random.choice([True, False]),
                helpful_count=random.randint(0, 50),
                reported_count=random.randint(0, 5),
                published_at=timezone.now() - timedelta(days=random.randint(1, 60)),
            )
            if random.random() < 0.4:
                ReviewImage.objects.create(
                    review=review,
                    image=f"reviews/{timezone.now():%Y/%m}/review_{review.pk}.jpg",
                        alt_text=fake.sentence(nb_words=5),
                        display_order=0,
                    )

    def _create_inquiries(self, products, members):
        for _ in range(10):
            product = random.choice(products)
            user = random.choice(members)
            inquiry = Inquiry.objects.create(
                product=product,
                product_option=product.options.order_by("?").first(),
                user=user,
                email=user.email,
                category=random.choice(list(Inquiry.Category)),
                title=fake.sentence(nb_words=6),
                question=fake.paragraph(nb_sentences=4),
                status=random.choice(list(Inquiry.Status)),
                is_public=random.choice([True, False]),
            )
            InquiryMessage.objects.create(
                inquiry=inquiry,
                author=user,
                is_staff_reply=False,
                message=fake.sentence(nb_words=12),
            )
            InquiryMessage.objects.create(
                inquiry=inquiry,
                author=None,
                is_staff_reply=True,
                message="안녕하세요, 문의 감사합니다. 확인 후 연락드리겠습니다.",
            )

    def _create_carts_and_wishlists(self, products, members):
        for member in members:
            cart = Cart.objects.create(user=member, is_active=True)
            wishlist = Wishlist.objects.create(user=member, name="기본 찜 목록", is_default=True)

            for product in random.sample(products, min(5, len(products))):
                option = product.options.order_by("?").first()
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    product_option=option,
                    quantity=random.randint(1, 3),
                    unit_price=product.sale_price,
                    discount_amount=Decimal("0"),
                )
                WishlistItem.objects.get_or_create(
                    wishlist=wishlist,
                    product=product,
                    product_option=option,
                )

    def _create_notifications(self, products, members):
        for member in members:
            product = random.choice(products)
            Notification.objects.create(
                user=member,
                notification_type=random.choice(list(Notification.NotificationType)),
                product=product,
                product_option=product.options.order_by("?").first(),
                channel=random.choice(list(Notification.Channel)),
                status=random.choice(list(Notification.Status)),
                scheduled_for=timezone.now() + timedelta(days=random.randint(1, 7)),
            )

    def _create_orders(self, products, members, owner, count):
        deliveries = []
        for member in members:
            delivery = Delivery.objects.create(
                user=member,
                recipient_name=member.name,
                phone=member.phone,
                postcode=fake.postcode(),
                address_line1=fake.address().replace("\n", " "),
                address_line2=self._secondary_address(),
                is_default=True,
                request_note="문 앞에 놓아주세요.",
            )
            deliveries.append(delivery)

        for _ in range(count):
            customer = random.choice(members)
            delivery = random.choice([d for d in deliveries if d.user == customer])
            order = Order.objects.create(
                order_number=fake.unique.bothify(text="ORD#####"),
                user=customer,
                delivery=delivery,
                shipping_name=delivery.recipient_name,
                shipping_phone=delivery.phone,
                shipping_postcode=delivery.postcode,
                shipping_address1=delivery.address_line1,
                shipping_address2=delivery.address_line2,
                status=random.choice(list(Order.Status)),
                payment_method=random.choice(list(Order.PaymentMethod)),
                payment_amount=Decimal("0"),
                shipping_fee=Decimal("3000"),
                order_note=random.choice(["", "빠른 배송 부탁드립니다."]),
            )

            total = Decimal("0")
            for product in random.sample(products, k=random.randint(1, 3)):
                option = product.options.order_by("?").first()
                quantity = random.randint(1, 2)
                price = product.sale_price
                line_total = price * quantity
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    sku=product.sku,
                    product_option=option,
                    quantity=quantity,
                    discount_amount=Decimal("0"),
                    total_price=line_total,
                )
                total += line_total

            order.payment_amount = total + order.shipping_fee
            order.save(update_fields=["payment_amount"])

    def _generate_phone(self):
        middle = random.randint(1000, 9999)
        last = random.randint(1000, 9999)
        return f"010-{middle:04d}-{last:04d}"

    def _secondary_address(self):
        secondary = getattr(fake, "secondary_address", None)
        value = secondary() if callable(secondary) else f"{random.randint(101, 999)}호"
        return str(value).replace("\n", " ")
