# MCP 도구 스펙

`server.py` 에서 정의된 6개 도구의 상세 명세.

---

## search_apartments

지역 + 가격 범위로 아파트 매물을 검색한다 (매매/전세/월세). **핵심 도구**.

```python
@mcp.tool
def search_apartments(
    district: str,              # 동/구/군 ("관평동", "강남구", "성남시 분당구")
    price_min: int = 60000,     # 최소 가격 (만원). 기본: 6억
    price_max: int = 79999,     # 최대 가격 (만원). 기본: 7.9억
    trade_type: str = "A1",     # A1=매매, B1=전세, B2=월세
) -> str:
```

**반환**: 매물 리스트 (JSON) — 단지명, 주소, 가격, 면적, 층수, 방향, 평당가, 링크.
월세의 경우 `price` 는 보증금, `rentPrice` 는 월세(만원/월).

---

## watch_complexes

관심 단지 목록의 매물 + 시세 + 실거래가를 일괄 조회하고, 이전 스냅샷과 비교해 변동 내역을 함께 반환한다.

```python
@mcp.tool
def watch_complexes(
    complex_names: list[str],   # 단지명 목록 (예: ["가천대역두산위브", "광교해모로"])
    price_min: int = 60000,
    price_max: int = 75000,
) -> str:
```

**반환**: 마크다운 리포트 — 단지별 매물·시세·실거래가, 신규/삭제/가격변동.

---

## get_complex_info

특정 아파트 단지의 상세 정보를 조회한다.

```python
@mcp.tool
def get_complex_info(
    complex_id: str | None = None,
    complex_name: str | None = None,
) -> str:
```

`complex_id` 또는 `complex_name` 중 하나 필수.

**반환**: 단지 상세 (JSON) — 세대수, 준공일, 평형별 면적, 현재 매물 수, 위치 좌표.

---

## get_complex_price_info

단지 평형별 시세(네이버) + 최근 실거래가를 조회한다.

```python
@mcp.tool
def get_complex_price_info(
    complex_id: str | None = None,
    complex_name: str | None = None,
) -> str:
```

`complex_id` 또는 `complex_name` 중 하나 필수.

**반환**: 평형별 매매/전세 시세, 현재 호가 범위, 최근 실거래 내역 (JSON).

---

## resolve_district

지역명으로 네이버 cortarNo를 조회한다.

```python
@mcp.tool
def resolve_district(query: str) -> str:
```

**반환**: `cortarNo`, `cortarName`, `cortarType` (city/dvsn/sec), 좌표 (JSON).

---

## list_districts

전국 시/도 17개 목록을 반환한다. 더 구체적인 지역(구/동)은 `search_apartments` 의 `district` 에 직접 입력하면 동적 조회된다.

```python
@mcp.tool
def list_districts() -> str:
```

**반환**: 시/도 이름 + cortarNo 리스트 (JSON).
