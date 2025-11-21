from django.views.generic import TemplateView

from common.meili import get_product_index


class ProductSearchView(TemplateView):
    template_name = "product/search.html"
    default_sort = "created_at:desc"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "")
        category = self.request.GET.get("category")
        colors = self.request.GET.getlist("color")
        sizes = self.request.GET.getlist("size")
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        sort = self.request.GET.get("sort") or self.default_sort

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

        params = {
            "q": q,
            "filter": filter_str,
            "sort": [sort] if sort else [self.default_sort],
            "limit": 24,
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

        search_res = get_product_index().search(**params)
        ctx["results"] = search_res.get("hits", [])
        ctx["nb_hits"] = search_res.get("estimatedTotalHits", 0)
        ctx["q"] = q
        ctx["sort"] = sort
        ctx["category"] = category
        ctx["colors"] = colors
        ctx["sizes"] = sizes
        ctx["min_price"] = min_price
        ctx["max_price"] = max_price
        return ctx
