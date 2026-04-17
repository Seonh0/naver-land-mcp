# naver-land-mcp — 기여자 가이드

이 문서는 코드를 수정·확장하려는 기여자를 위한 가이드입니다. 사용자용 설치/사용 안내는 [README.md](README.md) 를 참고하세요.

---

## 1. 프로젝트 개요

네이버 부동산 내부 API를 활용한 부동산 검색 MCP(Model Context Protocol) 서버.
네이버 API 한 곳에서 매물 + 한국부동산원시세 + KB시세 + 실거래가를 조회한다.

---

## 2. 기술 스택

| 항목 | 선택 |
|------|------|
| 언어 | Python 3.10+ |
| 패키지 관리 | uv (pyproject.toml) |
| MCP 프레임워크 | FastMCP |
| HTTP | requests |
| 데이터 소스 | 네이버 부동산 내부 API |

---

## 3. 환경 설정

- 패키지 매니저: [uv](https://docs.astral.sh/uv/)
- 실행: 저장소 루트에서 `uv run server.py` (의존성 자동 설치)
- 의존성은 `pyproject.toml` 에 정의

---

## 4. 프로젝트 구조

```
naver-land-mcp/
├── server.py        # MCP 서버 메인 (FastMCP 도구 6개)
├── naver_land.py    # 네이버 부동산 API 클라이언트
├── filter.py        # 매물 필터링 + 포맷팅
├── report.py        # 마크다운 리포트 포맷터 (watch_complexes 결과)
├── snapshot.py      # 매물 변동 감지 (신규/삭제/가격변동)
├── config.py        # API 헤더, 가격 기본값, 스냅샷 경로 등 상수
├── pyproject.toml   # 프로젝트 메타데이터 + 의존성
├── docs/            # 상세 문서
└── README.md
```

---

## 5. 주요 모듈

| 모듈 | 책임 |
|---|---|
| `server.py` | FastMCP 도구 등록 (`search_apartments`, `watch_complexes`, `get_complex_info`, `get_complex_price_info`, `resolve_district`, `list_districts`) |
| `naver_land.py` | API 호출, JWT 토큰 자동 추출, Rate Limiting, 429 재시도, 지역 동적 resolve |
| `filter.py` | 가격 파싱(억/만원), 매물 표준 포맷 변환, 가격 범위 필터, 정렬 |
| `report.py` | watch_complexes 결과 → 마크다운 리포트 변환 |
| `snapshot.py` | `~/.naver-land/snapshot.json` 에 이전 매물 저장, 변동 감지 |
| `config.py` | API URL, 헤더, Rate Limiting 파라미터, 가격 기본값, 스냅샷 경로 |

---

## 6. 상세 문서 (참조)

@docs/api-reference.md
@docs/mcp-tools.md
@docs/module-guide.md
@docs/testing.md
@docs/deployment.md

---

## 7. 주의사항

- 네이버 부동산 내부 API는 **비공식**이므로 응답 구조가 사전 통보 없이 변경될 수 있음.
  필드명 불일치 시 `naver_land.py` 파싱 로직을 우선 점검할 것.
- 지역코드는 `resolve_region()` 으로 동적 조회한다 (하드코딩 없음).
- Rate Limiting 규칙을 반드시 준수할 것. → @docs/api-reference.md
- 상업적 이용 금지. 개인 학습·조회 용도로만 사용.
