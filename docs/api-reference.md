# 네이버 부동산 API 레퍼런스

네이버는 부동산 API를 공식 제공하지 않는다. 웹 프론트엔드에서 내부적으로 호출하는 API를 사용한다.

## 주요 엔드포인트 (new.land.naver.com)

| 단계 | 엔드포인트 | 설명 |
|------|-----------|------|
| 1 | `/api/regions/list?cortarNo={code}` | 시도 → 구/군 → 동 목록 |
| 2 | `/api/regions/complexes?cortarNo={dong}&realEstateType=APT` | 동별 아파트 단지 목록 |
| 3 | `/api/articles?complexNo={id}&tradeType=A1` | 단지별 매매 매물 목록 |
| 4 | `/api/complexes/{id}` | 단지 상세 정보 |

## Fallback 엔드포인트 (m.land.naver.com)

new.land API가 실패할 경우, 모바일 버전 API로 fallback한다.
좌표 기반 검색이라 지역 코드 대신 위도/경도 범위를 사용한다.

```
m.land.naver.com/cluster/ajax/articleList?rletTpCd=APT&tradTpCd=A1&dprcMin=60000&dprcMax=79999&...
```

## 필수 헤더

네이버 내부 API는 적절한 헤더 없이 호출하면 **차단**된다.

```python
HEADERS = {
    "Host": "new.land.naver.com",
    "Referer": "https://new.land.naver.com/complexes",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}
```

## 주요 파라미터 코드

| 파라미터 | 값 | 의미 |
|---------|---|------|
| rletTpCd / realEstateType | APT | 아파트 |
| tradTpCd / tradeType | A1 | 매매 (B1=전세, B2=월세) |
| cortarNo | 1168000000 | 법정동 코드 (예: 강남구) |
| dprcMin / dprcMax | 60000 / 79999 | 매매가 범위 (만원 단위, 6억~7.9억) |

## Rate Limiting 규칙

- 요청 간 **최소 1초** 딜레이 필수
- 429 응답 시 **5초 대기** 후 재시도 (최대 3회)
- 하루 1~2회 크롤링 권장 (아침 8시 + 저녁 6시)
- 구 간 **2초** 딜레이로 rate limiting 방지
