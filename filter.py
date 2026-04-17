"""매물 가격 파싱, 표준 포맷 변환, 필터링/정렬."""

from __future__ import annotations

import re
from typing import Optional

_EOK_RE = re.compile(r"(?:(\d+)\s*억)?\s*([\d,]+)?")


def parse_price(price_str: str) -> Optional[int]:
    """한글 가격 문자열을 만원 단위 int로 변환.

    예시:
      "32억"          -> 320000
      "6억 5,000"     -> 65000
      "6억 5천"       -> 65000  (천 단위는 미지원, 콤마 표기만 지원)
      "9,500"         -> 9500   (억 없음 = 그대로 만원)
      ""              -> None
    """
    if not price_str:
        return None
    s = price_str.strip()
    if not s:
        return None

    total = 0
    # "N억" 부분
    m_eok = re.search(r"(\d+)\s*억", s)
    if m_eok:
        total += int(m_eok.group(1)) * 10000
        s = s[m_eok.end():].strip()

    # 남은 숫자 (만원 단위)
    s = s.replace(",", "").strip()
    if s:
        m_num = re.match(r"\d+", s)
        if m_num:
            total += int(m_num.group(0))

    return total if total > 0 else None


def format_article(article: dict) -> dict:
    """원본 매물 dict → 표준 포맷.

    거래유형별 의미:
    - 매매(A1): price = 매매가 (만원), rentPrice = None
    - 전세(B1): price = 전세보증금 (만원), rentPrice = None
    - 월세(B2): price = 보증금 (만원), rentPrice = 월세 (만원/월)
    """
    price_str = article.get("dealOrWarrantPrc", "")
    price = parse_price(price_str)
    # 월세 (만원 단위 int)
    rent_prc = article.get("rentPrc")
    rent_price: Optional[int] = None
    if isinstance(rent_prc, int):
        rent_price = rent_prc
    elif isinstance(rent_prc, str) and rent_prc.strip():
        rent_price = parse_price(rent_prc)

    trade_type_code = article.get("tradeTypeCode", "")  # A1/B1/B2
    trade_type_name = article.get("tradeTypeName", "")  # 매매/전세/월세

    area_supply = article.get("area1")   # 공급 (㎡)
    area_excl = article.get("area2")     # 전용 (㎡)

    # 평당가 (매매만 의미있음)
    price_per_pyeong: Optional[int] = None
    if trade_type_code == "A1" and price and area_supply:
        pyeong = area_supply / 3.3058
        if pyeong > 0:
            price_per_pyeong = int(price / pyeong)

    article_no = article.get("articleNo", "")
    link = (
        article.get("cpPcArticleBridgeUrl")
        or (f"https://new.land.naver.com/complexes?articleNo={article_no}" if article_no else "")
    )

    return {
        "articleNo": article_no,
        "complexNo": article.get("_complexNo"),
        "name": article.get("_complexName") or article.get("articleName", ""),
        "dong": article.get("_dongName"),
        "address": article.get("_cortarAddress"),
        "building": article.get("buildingName"),
        "floor": article.get("floorInfo"),
        "areaSupply": area_supply,   # ㎡
        "areaExclusive": area_excl,  # ㎡
        "direction": article.get("direction"),
        "tradeType": trade_type_code,
        "tradeTypeName": trade_type_name,
        "priceStr": price_str,
        "price": price,              # 만원 (매매가/전세보증금/월세보증금)
        "rentPrice": rent_price,     # 만원 (월세에만 있음)
        "pricePerPyeong": price_per_pyeong,
        "tags": article.get("tagList", []),
        "feature": article.get("articleFeatureDesc", ""),
        "confirmYmd": article.get("articleConfirmYmd"),
        "link": link,
    }


def filter_and_rank(
    articles: list[dict],
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
) -> list[dict]:
    """포맷 + 가격 범위 필터 + 정렬.

    가격 필터 기준:
    - 매매(A1): 매매가
    - 전세(B1): 전세보증금
    - 월세(B2): 보증금 (월세는 rentPrice에 별도 저장)

    정렬: 매매는 평당가 오름차순, 전세/월세는 가격 오름차순.
    """
    formatted = [format_article(a) for a in articles]
    filtered: list[dict] = []
    for item in formatted:
        p = item.get("price")
        if p is None:
            continue
        if price_min is not None and p < price_min:
            continue
        if price_max is not None and p > price_max:
            continue
        filtered.append(item)

    # 매매면 평당가, 그 외는 가격 기준 오름차순
    has_pyeong_price = any(x.get("pricePerPyeong") for x in filtered)
    if has_pyeong_price:
        filtered.sort(
            key=lambda x: (x.get("pricePerPyeong") is None, x.get("pricePerPyeong") or 0)
        )
    else:
        filtered.sort(key=lambda x: x.get("price") or 0)
    return filtered
