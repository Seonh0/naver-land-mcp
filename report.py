"""리포트 포맷팅 모듈.

watch_complexes 결과를 마크다운 리포트로 변환한다.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def _price_str(price_man: int | None) -> str:
    """만원 단위 int → 한글 가격 문자열."""
    if not price_man:
        return "?"
    eok = price_man // 10000
    remainder = price_man % 10000
    if eok and remainder:
        return f"{eok}억 {remainder:,}"
    if eok:
        return f"{eok}억"
    return f"{remainder:,}"


def _get_market_low(pyeongs: list[dict]) -> int | None:
    """평형 목록에서 시세 하한 (dealLow) 최솟값. KB시세 우선."""
    lows = []
    for py in pyeongs:
        # KB시세 우선, 없으면 한국부동산원
        mp = py.get("kbMarketPrice") or py.get("marketPrice", {})
        if mp and mp.get("dealLow"):
            lows.append(mp["dealLow"])
    return min(lows) if lows else None


def _market_range_text(pyeongs: list[dict], key: str) -> str:
    """시세 범위 텍스트. key는 'marketPrice' 또는 'kbMarketPrice'."""
    lows = [p[key]["dealLow"] for p in pyeongs if p.get(key, {}).get("dealLow")]
    highs = [p[key]["dealHigh"] for p in pyeongs if p.get(key, {}).get("dealHigh")]
    if lows and highs:
        return f"{_price_str(min(lows))} ~ {_price_str(max(highs))}"
    return ""


def _get_latest_real_deal(pyeongs: list[dict]) -> str:
    """평형 목록에서 가장 최근 실거래가 1건 텍스트."""
    latest_date = ""
    latest_info = ""
    for py in pyeongs:
        for deal in py.get("realDeals", []):
            d = deal.get("date", "")
            if d > latest_date:
                latest_date = d
                price = deal.get("price")
                floor = deal.get("floor")
                floor_s = f"{floor}층, " if floor else ""
                latest_info = f"{_price_str(price)}({floor_s}{d})"
    return latest_info or "없음"


def format_report(
    complexes: list[dict],
    changes: dict[str, Any],
) -> str:
    """watch_complexes 결과 → 마크다운 리포트."""
    today = datetime.now().strftime("%Y-%m-%d")
    lines: list[str] = []

    lines.append(f"**아파트 매물 리포트** ({today})")
    lines.append("")

    # 변동 요약
    if changes.get("is_first_run"):
        total = changes.get("total_current", 0)
        lines.append(f"첫 실행 — 전체 {total}건 조회")
    else:
        prev_ts = changes.get("previous_timestamp", "")[:16].replace("T", " ")
        new_c = changes.get("new_count", 0)
        rm_c = changes.get("removed_count", 0)
        pc_c = changes.get("price_changed_count", 0)
        uc = changes.get("unchanged_count", 0)
        lines.append(f"이전 조회: {prev_ts}")
        parts = []
        if new_c:
            parts.append(f"신규 {new_c}건")
        if rm_c:
            parts.append(f"삭제 {rm_c}건")
        if pc_c:
            parts.append(f"가격변동 {pc_c}건")
        if parts:
            lines.append("변동: " + " | ".join(parts))
        else:
            lines.append(f"변동 없음 (총 {uc}건 동일)")

        # 신규 매물 상세
        for a in changes.get("new", []):
            name = a.get("name") or a.get("complexName") or a.get("_complexName", "")
            lines.append(
                f"  + {name} {a.get('building','')} {a.get('floor','')} "
                f"{a.get('priceStr','')} {a.get('areaExclusive','?')}㎡"
            )
        # 삭제 매물
        for a in changes.get("removed", []):
            name = a.get("complexName", "")
            lines.append(
                f"  - {name} {a.get('building','')} {a.get('floor','')} "
                f"{a.get('priceStr','')}"
            )
        # 가격 변동
        for a in changes.get("price_changed", []):
            name = a.get("name") or a.get("complexName") or a.get("_complexName", "")
            lines.append(
                f"  ~ {name} {a.get('building','')} {a.get('floor','')} "
                f"{a.get('prevPrice','')} → {a.get('priceStr','')}"
            )

    lines.append("")

    # 단지별 현황
    highlights: list[str] = []
    total_count = 0

    for cx in complexes:
        if "error" in cx:
            lines.append(f"**{cx['name']}**: {cx['error']}")
            lines.append("")
            continue

        count = cx.get("articleCount", 0)
        total_count += count
        articles = cx.get("articles", [])
        pyeongs = cx.get("pyeongs", [])

        market_low = _get_market_low(pyeongs)
        real_deal = _get_latest_real_deal(pyeongs)

        # 시세 범위 텍스트 (한국부동산원 + KB 각각)
        kab_text = _market_range_text(pyeongs, "marketPrice")
        kb_text = _market_range_text(pyeongs, "kbMarketPrice")

        addr = cx.get("address", "")

        lines.append(f"**{cx['name']}** ({count}건)")
        if addr:
            lines.append(addr)

        # 시세 (네이버=한국부동산원, KB)
        if kab_text:
            lines.append(f"[한국부동산원] {kab_text} | 실거래: {real_deal}")
        if kb_text:
            lines.append(f"[KB부동산] {kb_text}")
        lines.append("")

        # 매물 테이블 (중복 제거: 동+층+가격 동일하면 1건만)
        if articles:
            seen = set()
            unique_articles = []
            for a in articles:
                key = (a.get("building", ""), a.get("floor", ""), a.get("priceStr", ""))
                if key not in seen:
                    seen.add(key)
                    unique_articles.append(a)

            for idx, a in enumerate(unique_articles[:20], 1):  # 단지당 최대 20건
                building = a.get("building", "")
                floor = a.get("floor", "?")
                price_s = a.get("priceStr", "?")
                area = a.get("areaExclusive", "?")
                area_s = f"{area}㎡" if area else "?"
                direction = a.get("direction", "")
                feature = a.get("feature", "")
                tags = ", ".join(a.get("tags", []))

                # 시세 하한 이하면 표시
                badge = ""
                price_val = a.get("price")
                if market_low and price_val and price_val <= market_low:
                    badge = "⭐"
                    highlights.append(f"{cx['name']} {building} {floor} {price_s}")

                lines.append(f"{badge}{idx}. {building} {floor} | **{price_s}** | {area_s} | {direction}")
                desc_parts = []
                if feature:
                    desc_parts.append(feature[:60])
                if tags:
                    desc_parts.append(f"[{tags}]")
                if desc_parts:
                    lines.append(f"   {' / '.join(desc_parts)}")
            if len(unique_articles) > 20:
                lines.append(f"  ... 외 {len(unique_articles) - 20}건 (중복 제외 총 {len(unique_articles)}건)")
            elif len(articles) > len(unique_articles):
                lines.append(f"  (중복 제외 {len(unique_articles)}건 / 원본 {len(articles)}건)")
        lines.append("")

    # 전체 요약
    lines.append(f"**전체 요약**: 총 {total_count}건")
    if highlights:
        lines.append("시세 이하 매물:")
        for h in highlights:
            lines.append(f"  ⭐ {h}")

    return "\n".join(lines)
