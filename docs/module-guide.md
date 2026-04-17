# 모듈별 구현 가이드

각 모듈의 책임과 핵심 함수를 정리한다. 코드와 함께 읽으면 빠르게 이해할 수 있다.

---

## config.py

API 엔드포인트 상수, HTTP 헤더, Rate Limiting 파라미터, 가격 기본값, 스냅샷 저장 경로를 관리한다.

| 상수 | 의미 |
|---|---|
| `API_BASE` / `MAIN_PAGE_URL` | 네이버 부동산 API 기본 URL |
| `BROWSER_HEADERS` / `USER_AGENT` | API 호출용 헤더 |
| `REQUEST_DELAY_SEC` / `RETRY_DELAY_SEC` / `MAX_RETRIES` | Rate Limiting 파라미터 |
| `SNAPSHOT_DIR` / `SNAPSHOT_PATH` | `~/.naver-land/snapshot.json` |
| `DEFAULT_PRICE_MIN` / `DEFAULT_PRICE_MAX` | 가격 기본 범위 (만원, 기본 무제한) |
| `DEFAULT_MAX_COMPLEXES` | 한 지역 호출당 처리할 최대 단지 수 |
| `TRADE_TYPES` | A1=매매, B1=전세, B2=월세 라벨 |

지역코드는 하드코딩하지 않고 `naver_land.resolve_region()` 으로 동적 조회한다.

---

## naver_land.py

네이버 부동산 API 호출 모듈. `NaverLandClient` 클래스가 세션·JWT 토큰 생명주기를 관리한다.

| 함수/메서드 | 설명 |
|------|------|
| `_ensure_session()` | 메인 페이지에서 JWT 토큰 추출, 세션 초기화 |
| `_get(path, params)` | Rate Limiting + 429 재시도 포함 GET |
| `resolve_region(query)` | 지역명 → cortarNo / cortarType / 좌표 |
| `get_dong_list(cortar_no)` | 구 → 하위 동 목록 |
| `get_complexes(dong_code)` | 동 → 아파트 단지 목록 |
| `get_articles(complex_no, trade_type)` | 단지 → 매물 목록 (페이지네이션 자동) |
| `get_complex_detail(complex_no)` | 단지 상세 + 평형 목록 병합 |
| `get_complex_prices(complex_no)` | 평형별 시세(한국부동산원·KB) + 실거래가 |
| `search_complex_by_name(name)` | 단지명 검색 → complexNo |
| `crawl_district(...)` | 지역 단위 매물 수집 (동/구 자동 분기) |
| `watch_complexes_data(...)` | 단지 목록 일괄 조회 (매물 + 시세 + 실거래가) |

`crawl_district` 흐름:
1. `resolve_region()` 으로 cortarNo 조회
2. cortarType 분기 — `sec`(동) 면 직접 단지 조회, `dvsn`(구) 면 하위 동 순회
3. 매물 수 내림차순 상위 N개 단지만 상세 수집
4. 호출 사이에 `REQUEST_DELAY_SEC` 딜레이

---

## filter.py

매물 가격 파싱, 표준 포맷 변환, 필터링/정렬을 담당한다.

| 함수 | 설명 |
|------|------|
| `parse_price(price_str)` | 한글 가격 → 만원 단위 int (`"6억 5,000"` → `65000`) |
| `format_article(article)` | 원본 매물 dict → 표준 포맷 (단지명, 가격, 면적, 평당가, 링크 등). 거래 유형별로 `price`/`rentPrice` 의미 다름 |
| `filter_and_rank(articles, price_min, price_max)` | 가격 범위 필터 + 정렬 (매매는 평당가, 전세·월세는 가격 기준) |

---

## report.py

`watch_complexes` 결과를 사람이 읽기 좋은 마크다운 리포트로 변환한다.

| 함수 | 설명 |
|---|---|
| `_price_str(price_man)` | 만원 단위 int → 한글 가격 (`65000` → `"6억 5,000"`) |
| `_get_market_low(pyeongs)` | 평형들의 시세 하한 최솟값 (KB 우선) |
| `_market_range_text(pyeongs, key)` | 시세 범위 텍스트 |
| `_get_latest_real_deal(pyeongs)` | 가장 최근 실거래가 1건 |
| `format_report(complexes, changes)` | 최종 마크다운 리포트 생성 |

---

## snapshot.py

매물 변동 감지를 위해 직전 호출 결과를 `~/.naver-land/snapshot.json` 에 저장하고 비교한다.

| 함수 | 설명 |
|---|---|
| `load_snapshot()` | 이전 스냅샷 로드 |
| `save_snapshot(articles)` | 현재 매물을 스냅샷으로 저장 |
| `compare_with_previous(current_articles)` | 신규/삭제/가격변동 감지 후 새 스냅샷 저장 |

비교 키는 `articleNo`, 가격 변경 감지는 `price` 필드 비교.

---

## server.py

FastMCP 서버 엔트리. 6개 도구를 등록한다 — 각 도구의 인자/반환 명세는 [mcp-tools.md](mcp-tools.md) 참고.

```python
from fastmcp import FastMCP

mcp = FastMCP("naver-land")

@mcp.tool
def search_apartments(district: str, ...) -> str:
    ...

if __name__ == "__main__":
    mcp.run()
```
