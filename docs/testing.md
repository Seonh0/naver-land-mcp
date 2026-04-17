# 테스트 체크리스트

코드 변경 후 검증할 시나리오 모음. 자동화된 테스트 스위트는 아직 없으므로 수동 확인 위주.

---

## API 동작 검증

| # | 확인 항목 | 예상 결과 |
|---|-----------|----------|
| 1 | `resolve_region("강남구")` | `cortarNo: 1168000000`, `cortarType: dvsn` |
| 2 | `get_dong_list(<강남구 코드>)` | 강남구 하위 동 목록 (20개+) |
| 3 | `get_complexes(<동 코드>)` | 아파트 단지 목록 + `dealCount` |
| 4 | `get_articles(<단지 ID>, "A1")` | 매매 매물 + `dealOrWarrantPrc` 필드 |
| 5 | `parse_price("6억 5,000")` | `65000` (만원) |
| 6 | `parse_price("32억")` | `320000` |

---

## MCP 도구 호출 시나리오

MCP 클라이언트(Claude Desktop / Claude Code 등)에서 자연어 명령으로 호출한 결과.

| # | 자연어 명령 예시 | 호출되는 도구 | 확인 포인트 |
|---|-----------------|---------------|------------|
| 1 | "강남구 6억대 아파트 매물 찾아줘" | `search_apartments` | 가격 범위가 60000~69999로 채워지는지 |
| 2 | "관평동 전세 매물 알려줘" | `search_apartments` | `trade_type=B1` 처리 |
| 3 | "성남시 분당구 매물도 찾아줘" | `search_apartments` | 시 단위 지역명 동적 resolve |
| 4 | "지원하는 시/도 목록 보여줘" | `list_districts` | 17개 시/도 |
| 5 | "OO단지 단지 정보" | `get_complex_info` | 단지명 → complexNo 자동 검색 |
| 6 | "OO단지 평형별 시세와 최근 실거래가" | `get_complex_price_info` | KB + 한국부동산원 시세 동시 |
| 7 | "관심 단지 OO, △△ 매물 변동 알려줘" | `watch_complexes` | 스냅샷 비교 결과 포함 |

---

## 회귀 검증 포인트

- 가격 파싱: 억 단위 / 콤마 / 빈 문자열 / 매매·전세·월세 모두 정상 처리
- Rate Limiting: 연속 호출 시 0.5초 이상 딜레이, 429 응답 시 재시도
- JWT 토큰: 메인 페이지 응답에서 추출 성공
- 스냅샷: `~/.naver-land/snapshot.json` 생성·비교 정상
