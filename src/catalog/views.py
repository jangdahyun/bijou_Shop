from django.db.models import DecimalField, ExpressionWrapper, F, Value ,Q
from decimal import Decimal
from django.shortcuts import render
from django.utils import timezone

from common.models import Banner, Notice
from product.models import Product


def home(request):
    """홈 대시보드: 배너, 공지, 추천 상품 등 모음"""

    query = request.GET.get("q", "").strip()
    now = timezone.now()

    banners = (
        Banner.objects.filter(is_active=True)
        .filter(
            Q(starts_at__lte=now) | Q(starts_at__isnull=True),
            Q(ends_at__gte=now) | Q(ends_at__isnull=True),
        )
        .order_by("placement", "display_order", "-created_at")
    )

    notices = (
        Notice.objects.filter(is_active=True)
        .filter(
            Q(starts_at__lte=now) | Q(starts_at__isnull=True),
            Q(ends_at__gte=now) | Q(ends_at__isnull=True),
        )
        .order_by("-is_pinned", "display_order", "-created_at")[:5]
    )

    new_products = (
        Product.objects.filter(is_active=True)
        .order_by("-created_at")[:10]
    )
    sale_products = (
        Product.objects.filter(is_active=True, discount_price__isnull=False)
        .order_by("-updated_at")[:10]
    )
    popular_products = (
        Product.objects.filter(is_active=True)
        .annotate(
            popularity_score=ExpressionWrapper( #xpressionWrapper로 “이 산출값은 어떤 필드 타입이다”라고 알려줍니다.
                F("view_count") * Value(Decimal("0.4")) +
                F("sales_count") * Value(Decimal("0.3")) +
                F("review_count") * Value(Decimal("0.3")),
                output_field=DecimalField(max_digits=12, decimal_places=4), # output_field로 산출값의 필드 타입을 지정합니다.
                )
            )
        .order_by("-popularity_score", "-view_count", "-sales_count","review_count")[:10]
    )

    search_results = None
    if query:
        search_results = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True,
        ).order_by("name")[:20]

    context = {
        "query": query,
        "banners": banners,
        "notices": notices,
        "new_products": new_products,
        "sale_products": sale_products,
        "search_results": search_results,
        "popular_products": popular_products,
    }
    return render(request, "catalog/home.html", context)
