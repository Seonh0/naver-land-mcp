"""설정 상수: API URL, 헤더, 거래 유형, 기본값."""

import os

API_BASE = "https://new.land.naver.com/api"
MAIN_PAGE_URL = "https://new.land.naver.com/complexes"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

BROWSER_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://new.land.naver.com/complexes",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

# Rate limiting
REQUEST_DELAY_SEC = 0.5       # 요청 간 최소 딜레이
RETRY_DELAY_SEC = 5.0         # 429 시 재시도 대기
MAX_RETRIES = 3
REQUEST_TIMEOUT_SEC = 10

# 스냅샷 저장 경로 (변동 감지용)
SNAPSHOT_DIR = os.path.expanduser("~/.naver-land")
SNAPSHOT_PATH = os.path.join(SNAPSHOT_DIR, "snapshot.json")

# MCP 타임아웃(60초) 에 맞춘 기본 한도.
# crawl_district 한 번에 처리할 최대 단지 수. dealCount 내림차순으로 선택.
DEFAULT_MAX_COMPLEXES = 5

# 가격 기본 범위 (만원 단위) — 가격 명시 안 한 호출 시 전 범위 검색
DEFAULT_PRICE_MIN = 0
DEFAULT_PRICE_MAX = 999999

TRADE_TYPES = {
    "A1": "매매",
    "B1": "전세",
    "B2": "월세",
}

# 지역코드는 네이버 검색 API (/search) 로 동적 조회 — 하드코딩 제거.
# naver_land.resolve_region() / crawl_district() 참조.
