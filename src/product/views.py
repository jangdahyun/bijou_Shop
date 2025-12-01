from django.conf import settings
from django.core.paginator import Paginator, EmptyPage 
# Paginator 리스트 or queryset를 페이지 단위로 나누기 위해 사용
#EmptyPage 페이지 번호가 유효하지 않을 때 발생하는 예외
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView

from common.meili import get_product_index
from product.models import Product



class ProductSearchView(TemplateView):
    template_name = "product/search.html"
    default_sort = "created_at:desc"
    sort_whitelist = [
        "created_at:desc",
        "sales_count:desc",
        "view_count:desc",
        "price:asc",
        "price:desc",
        "review_count:desc",
        "discount_rate:desc",
    ]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        request=self.request
        q = self.request.GET.get("q", "")
        category = self.request.GET.get("category")
        if category in (None, "", "None"):
            category = None

        colors = [c for c in self.request.GET.getlist("color") if c]
        sizes = [s for s in self.request.GET.getlist("size") if s]

        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        if not min_price or min_price == "None":
            min_price = None
        if not max_price or max_price == "None":
            max_price = None
        sort = self.request.GET.get("sort") or self.default_sort
        if sort not in self.sort_whitelist:
            sort = self.default_sort

        try:
            page=int(request.GET.get("page", "1"))
            per_page=int(request.GET.get("per_page", "24"))
        except ValueError:
            raise Http404("잘못된 페이지입니다")
        if per_page > 100:
            per_page = 100

        filters = ["is_active = true"]
        if category:
            filters.append(f'category = "{category}"')
        if colors:
            filters.append("(" + " OR ".join([f'colors = "{c}"' for c in colors]) + ")")
        if sizes:
            filters.append("(" + " OR ".join([f'sizes = "{s}"' for s in sizes]) + ")")

        price_filters = []
        if min_price:
            price_filters.append(f"price >= {min_price}")
        if max_price:
            price_filters.append(f"price <= {max_price}")
        if price_filters:
            filters.append(" AND ".join(price_filters))

        filter_str = " AND ".join(filters) if filters else None

        search_params = {
            "filter": filter_str,
            "sort": [sort],
            "limit": per_page,
            "offset": (page - 1) * per_page,
            "attributesToRetrieve": [
                "id",
                "name",
                "price",
                "discount_price",
                "discount_rate",
                "colors",
                "sizes",
                "view_count",
                "sales_count",
                "review_count",
                "category",
            ],
        }

        search_res = get_product_index().search(q, search_params)
        hits = search_res.get("hits", []) # 검색 결과 리스트
        total = search_res.get("estimatedTotalHits", 0) # 검색된 총 결과 수
        processing_ms = search_res.get("processingTimeMs") # 검색 처리 시간 (밀리초)

        # 페이징 객체 생성 (템플릿에서 page_obj 사용 가능)
        paginator = Paginator(range(total), per_page)  # 더미 리스트로 페이지 정보만 생성
        try:
            page_obj = paginator.page(page) #요청된 페이지 객체
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages) #마지막 페이지 객체

        qs = request.GET.copy()
        qs.pop("page", None)
        base_querystring = qs.urlencode()

        ctx.update(
            results=hits,
            nb_hits=total,
            processing_ms=processing_ms,
            q=q,
            sort=sort,
            category=category,
            colors=colors,
            sizes=sizes,
            min_price=min_price,
            max_price=max_price,
            page_obj=page_obj,
            per_page=per_page,
            base_querystring=base_querystring,
        )
        return ctx


class ProductAutocompleteView(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get("q", "")
        if not q:
            return JsonResponse({"hits": []})
        res = get_product_index().search(q, {
            "limit": 5,
            "attributesToRetrieve": ["id", "name", "sku"],
        })
        return JsonResponse({"hits": res.get("hits", [])})


class ProductDetailView(TemplateView):
    template_name = "product/detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product_id = kwargs.get("pk")
        product = get_object_or_404(
            Product.objects.prefetch_related("images", "options", "category"),
            pk=product_id,
        )
        images = list(product.images.order_by("-is_main", "display_order", "id"))
        options = product.options.filter(is_active=True)
        ctx.update(
            product=product,
            images=images,
            options=options,
            toss_client_key=getattr(settings, "TOSS_CLIENT_KEY", ""),
            order_prepare_url=reverse_lazy("order:prepare"),
        )
        return ctx
