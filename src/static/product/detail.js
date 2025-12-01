document.addEventListener("DOMContentLoaded", () => {
  const buyBtn = document.getElementById("btn-buy-now");
  if (!buyBtn) return;

  const optionSelect = document.getElementById("product-option");

  // ✅ B안: 결제창은 API 개별 연동 키(test_ck)를 사용
  const clientKey = window.TOSS_CLIENT_KEY || "";
  let tossPayments = null;

  // ✅ 결제창 SDK는 전역 TossPayments가 있어야 함 (템플릿에서 v1 SDK 스크립트 로드 필요)
  if (clientKey && typeof TossPayments !== "undefined") {
    tossPayments = TossPayments(clientKey);
  } else {
    console.warn("TOSS_CLIENT_KEY not set or TossPayments SDK not loaded; payment window will not work.");
  }

  buyBtn.addEventListener("click", async () => {
    const productId = buyBtn.dataset.productId;
    const optionId = optionSelect ? optionSelect.value : buyBtn.dataset.optionId || "";
    const quantity = buyBtn.dataset.defaultQty || 1;

    const formData = new FormData();
    formData.append("product_id", productId);
    formData.append("option_id", optionId);
    formData.append("quantity", quantity);

    const res = await fetch(window.ORDER_PREPARE_URL, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      body: formData,
    });

    if (!res.ok) {
      alert("주문 생성에 실패했습니다. 잠시 후 다시 시도해 주세요.");
      return;
    }

    const data = await res.json();

    if (!tossPayments) {
      alert("결제 모듈을 불러올 수 없습니다. 관리자에게 문의하세요.");
      return;
    }

    // ✅ 결제창(v1) 결제 요청: requestPayment(결제수단, 결제정보)
    // 결제수단 예: '카드', '가상계좌', '계좌이체', '휴대폰' 등 :contentReference[oaicite:1]{index=1}
    try {
      tossPayments.requestPayment("카드", {
        orderId: data.orderId,
        orderName: data.orderName,
        amount: data.amount,
        successUrl: data.successUrl,
        failUrl: data.failUrl,
        customerName: data.customerName,
      });
    } catch (e) {
      console.error(e);
      alert("결제창 호출 중 오류가 발생했습니다.");
    }
  });
});

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return "";
}
