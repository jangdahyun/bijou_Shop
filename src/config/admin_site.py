from datetime import timedelta
from decimal import Decimal
import logging

from django.contrib.admin import AdminSite
from django.db.models import F, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.shortcuts import redirect

from accounts.models import Account
from order.models import Order, OrderItem

#활성 세션 모델 임포트
from django.contrib.sessions.models import Session

# 프로젝트 전용 AdminSite 정의
class BijouAdminSite(AdminSite):
    site_header = "Bijou 관리자 센터"
    site_title = "Bijou Admin"
    index_title = "대시보드"
    index_template = "admin/dashboard.html"


    def each_context(self, request):
        # AdminSite가 넘겨주는 컨텍스트(예: site_header, has_permission, title, 템플릿에서 쓰는 여러 flag) 가져오기
        context = super().each_context(request)
        # 메인 대시보드에서 사용할 통계 데이터
        if request.resolver_match and request.resolver_match.url_name == "index":
            context.update(self._build_dashboard_context())
        #템플릿에 값 전달
        return context
    
    #일반함수처럼 쓰기 위해서, staticmethod 데코레이터 사용, self 인자 제거
    @staticmethod
    def count_active_sessions():
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        user_ids = []
        for session in active_sessions:
            data = session.get_decoded()
            uid = data.get("_auth_user_id")
            if uid:
                user_ids.append(uid)
        return len(set(user_ids))

    # 대시보드에 표시할 통계 데이터 생성 딕셔너리로 돌려주는 내부 헬퍼
    def _build_dashboard_context(self):
        now = timezone.localtime()
        #이번달 1일 0시 0분 0초
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        #다음달 1일 0시 0분 0초
        start_next_month = (start_of_month + timedelta(days=32)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        #이번주 일요일 0시 0분 0초
        start_of_week = (now - timedelta(days=6)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        #다음주 일요일 0시 0분 0초
        end_of_week = (start_of_week + timedelta(days=7)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        #이번달 주문들
        monthly_orders = Order.objects.filter(
            placed_at__gte=start_of_month, placed_at__lt=start_next_month
        )
        #활성 사용자 수
        active_user_count = self.count_active_sessions()


        canceled_statuses = [
            Order.Status.CANCELED,
            Order.Status.REFUNDED,
        ]
        confirmed_status = Order.Status.DELIVERED
        sales_statuses = [
            Order.Status.PAID,
            Order.Status.PREPARING,
            Order.Status.SHIPPED,
            Order.Status.DELIVERED,
        ]
        #이번달 통계
        total_orders = monthly_orders.count()
        #취소된 주문
        canceled_orders = monthly_orders.filter(status__in=canceled_statuses).count()
        #확정된 주문
        confirmed_orders = monthly_orders.filter(status=confirmed_status).count()
        #매출 합계
        monthly_sales_total = (
            monthly_orders.filter(status__in=sales_statuses).aggregate(
                total=Sum("payment_amount")
            )["total"]
            or Decimal("0")
        )
        #이번주 일별 매출 집계 쿼리셋
        weekly_sales_queryset = (
            Order.objects.filter(
                placed_at__gte=start_of_week,
                placed_at__lt=end_of_week,
                status__in=sales_statuses,
            )
            .annotate(day=TruncDate("placed_at"))
            .values("day")
            .annotate(total=Sum("payment_amount"))
            .order_by("day")
        )
        logging.info("이번주 매출"+str(weekly_sales_queryset))
        #일별 매출 딕셔너리로 변환
        sales_by_day = {entry["day"]: entry["total"] for entry in weekly_sales_queryset}
        #그래프에 넘길 컨테이너
        weekly_sales_series = []
        for offset in range(7):
            current_day = (start_of_week + timedelta(days=offset)).date()
            amount = float(sales_by_day.get(current_day, Decimal("0")))
            weekly_sales_series.append(
                {
                    "date": current_day.isoformat(),
                    "label": current_day.strftime("%m/%d"),
                    "total": amount,
                }
            )
        #이번주 카테고리별 매출 집계 쿼리셋
        category_sales_queryset = (
            OrderItem.objects.filter(
                order__placed_at__gte=start_of_week,
                order__placed_at__lt=end_of_week,
                order__status__in=sales_statuses,
                product__category__isnull=False,
            )
            .values(name=F("product__category__name"))
            .annotate(total=Sum("total_price"))
            .order_by("-total")
        )
        #카테고리별 매출 도넛에 넣을 데이터
        category_distribution = [
            {
                "label": entry["name"] or "기타",
                "value": float(entry["total"] or 0),
            }
            for entry in category_sales_queryset
        ]
        # 대시보드에 넘길 페이로드 구성
        dashboard_payload = {
            "generated_at": now,
            #카드형
            "cards": {
                "active_users": active_user_count,
                "monthly_orders": total_orders,
                "monthly_canceled": canceled_orders,
                "monthly_confirmed": confirmed_orders,
                "monthly_sales": float(monthly_sales_total),
            },
            #차트형
            "weekly_sales": weekly_sales_series,
            "weekly_category_distribution": category_distribution,
        }

        return {
            "dashboard": dashboard_payload,
        }
