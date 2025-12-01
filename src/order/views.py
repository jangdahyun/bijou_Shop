import uuid
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
import base64

from product.models import Product, ProductOption
from order.models import Order, OrderItem
from delivery.models import Delivery

def encode_key(secret_key: str) -> str:
    """Base64로 인코딩된 Basic Auth 토큰 생성 (secret:)"""
    secret_key_bytes = f"{secret_key}:".encode("ascii")
    return base64.b64encode(secret_key_bytes).decode("ascii")


class PrepareOrderView(View):
    """바로구매 시 주문 생성 후 토스 결제 위젯에 넘길 데이터 반환"""

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product_id")
        option_id = request.POST.get("option_id")
        quantity_raw = request.POST.get("quantity", "1")

        try:
            qty = max(1, int(quantity_raw))
        except ValueError:
            return HttpResponseBadRequest("invalid quantity")

        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            return HttpResponseBadRequest("invalid product")

        option = None
        if option_id:
            option = ProductOption.objects.filter(pk=option_id, product=product).first()

        price = product.sale_price
        order_name = f"{product.name}{' - ' + option.size if option else ''}"
        order_number = uuid.uuid4().hex[:16]

        # 임시 배송지: 로그인 유저가 있으면 그 유저, 없으면 첫 번째 유저로 생성 (테스트용)
        delivery_user = request.user if request.user.is_authenticated else get_user_model().objects.first()
        if not delivery_user:
            return HttpResponseBadRequest("no user for delivery")
        delivery = Delivery.objects.create(
            user=delivery_user,
            recipient_name="테스트",
            phone="010-0000-0000",
            postcode="00000",
            address_line1="테스트 주소",
            address_line2="",
            is_default=False,
        )

        order = Order.objects.create(
            order_number=order_number,
            user=request.user if request.user.is_authenticated else None,
            delivery=delivery,
            shipping_name="테스트",
            shipping_phone="010-0000-0000",
            shipping_postcode="00000",
            shipping_address1="테스트 주소",
            shipping_address2="",
            payment_amount=price * qty,
            status=Order.Status.PENDING,
            payment_method=Order.PaymentMethod.CARD,
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            sku=product.sku,
            product_option=option,
            quantity=qty,
            total_price=price * qty,
        )

        return JsonResponse(
            {
                "orderId": order.order_number,
                "orderName": order_name,
                "amount": float(price * qty),
                "customerName": request.user.username if request.user.is_authenticated else "게스트",
                "successUrl": settings.TOSS_SUCCESS_URL,
                "failUrl": settings.TOSS_FAIL_URL,
            }
        )


class TossSuccessView(TemplateView):
    template_name = "order/toss_success.html"

    def get(self, request, *args, **kwargs):
        payment_key = request.GET.get("paymentKey")
        order_id = request.GET.get("orderId")
        amount = request.GET.get("amount")
        if not (payment_key and order_id and amount):
            return JsonResponse({"error": "Missing parameters"}, status=400)

        # Toss는 Basic Auth로 secretKey: 를 base64 인코딩해 Authorization 헤더로 전달
        auth_token = encode_key(settings.TOSS_SECRET_KEY)
        headers = {"Authorization": f"Basic {auth_token}"}

        res = requests.post(
            "https://api.tosspayments.com/v1/payments/confirm",
            json={"paymentKey": payment_key, "orderId": order_id, "amount": int(amount)},
            headers=headers,
            timeout=10,
        )
        res.raise_for_status()
        data = res.json()

        order = Order.objects.get(order_number=order_id)
        order.status = Order.Status.PAID
        order.paid_at = timezone.now()
        order.save()

        return self.render_to_response({"payment": data, "order": order})


class TossFailView(TemplateView):
    template_name = "order/toss_fail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["code"] = self.request.GET.get("code")
        ctx["message"] = self.request.GET.get("message")
        return ctx
