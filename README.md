# Bijou (Django 커머스)

## 무엇을 제공하나요
- 상품 검색/필터/정렬: Meilisearch 연동, 자동완성 엔드포인트
- 상품 상세: 이미지/옵션/설명, 바로구매 버튼
- 홈 → 상세 이동: 카드 클릭 시 상세 페이지로 이동
- 주문/결제 테스트 플로우: 토스 결제 준비/성공/실패 엔드포인트 및 팝업 연동 코드(테스트 키 필요)
- 커머스 도메인: 상품/옵션/이미지, 장바구니·위시리스트, 주문/배송, 리뷰/문의

## 기술 스택 (핵심)
- 백엔드: Django 5, MySQL(utf8mb4)
- 검색: Meilisearch
- 캐시: Redis(127.0.0.1:6379/1)
- 보안/요청 보호: reCAPTCHA, `django-axes`(로그인 시도 제한), `django-ratelimit`(요청 제한), 프로덕션 시 HTTPS/HSTS/쿠키 보안 스위치
- 로깅: `TimedRotatingFileHandler`(일자별 회전) + 콘솔 핸들러, verbose 포맷
- 데이터 무결성/성능: 모델 제약(Unique/Check), 인덱스 다수

## 결제 플로우 (테스트)
- `/orders/prepare/` → 주문/주문상품 생성 후 결제 데이터 반환
- `/orders/success/`, `/orders/fail/` → 토스 confirm 및 결과 표시
- `product/detail.html` → “바로 구매하기” 클릭 시 결제 팝업 호출(JS 연동)
- 토스 결제위젯 전용 키(사업자 필요) 또는 다른 PG 테스트 키가 있어야 401 없이 동작
- confirm은 시크릿 키를 Base64 Basic Auth로 호출

## 검색 플로우
- `/products/search/` 검색/필터/정렬/페이징
- `/products/autocomplete/` 자동완성 JSON
- 검색 결과 → 상품 상세 링크

## 설정
- `.env` 예: `TOSS_CLIENT_KEY`, `TOSS_SECRET_KEY`, `TOSS_SUCCESS_URL`, `TOSS_FAIL_URL`, Meili 관련 키
- `config/settings.py`에서 Redis 캐시, Meili, 토스 키 로드
- 타임존: `USE_TZ=True`로 UTC 저장, 표시 시 KST 변환(템플릿/`timezone.localtime`). DB를 KST로 보고 싶으면 쿼리 전에 `SET time_zone = '+09:00';`

## 현재 보안/운영 포인트
- reCAPTCHA, axes, ratelimit로 인증/요청 보호
- 프로덕션 시 HTTPS/HSTS/쿠키 보안 설정 자동 적용
- 로그 회전 + 콘솔 출력
- 모델 제약/인덱스로 무결성 및 쿼리 성능 확보

## TODO (우선순위)
1) 결제: 결제위젯 전용 키 발급(또는 다른 PG 테스트 키) 후 401 해소, 실 배송지/금액 검증·재고 차감 트랜잭션, 실패 롤백
2) 주문 중복 방지: PENDING 주문 재사용/디바운스, 게스트 식별 보완
3) 결제 UI 안정화: 결제수단/약관 UI 정상 렌더 확인 또는 결제창 방식 전환
4) 검색 고도화: facet UI, 인기 검색어/자동완성 개선
5) 테스트/운영: 통합 테스트, Sentry/APM, 캐시 정책 정교화
