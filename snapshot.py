"""매물 스냅샷 저장/비교 모듈.

이전 스냅샷과 현재 매물을 비교하여 신규/삭제/가격변동을 감지한다.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from config import SNAPSHOT_DIR, SNAPSHOT_PATH


def _ensure_dir() -> None:
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def load_snapshot() -> dict[str, Any]:
    """이전 스냅샷 로드. 없으면 빈 dict."""
    if not os.path.exists(SNAPSHOT_PATH):
        return {}
    with open(SNAPSHOT_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_snapshot(articles: list[dict]) -> None:
    """현재 매물 목록을 스냅샷으로 저장."""
    _ensure_dir()
    data = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "articles": {},
    }
    for a in articles:
        key = a.get("articleNo", "")
        if not key:
            continue
        data["articles"][key] = {
            "complexName": a.get("complexName") or a.get("_complexName", ""),
            "price": a.get("price"),
            "priceStr": a.get("priceStr") or a.get("dealOrWarrantPrc", ""),
            "floor": a.get("floor") or a.get("floorInfo", ""),
            "areaName": a.get("areaName", ""),
            "direction": a.get("direction", ""),
            "building": a.get("building") or a.get("buildingName", ""),
        }
    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def compare_with_previous(current_articles: list[dict]) -> dict[str, Any]:
    """현재 매물과 이전 스냅샷을 비교하여 변동분 반환 후, 새 스냅샷 저장.

    반환:
        new: 새로 올라온 매물 리스트
        removed: 사라진 매물 리스트
        price_changed: 가격이 변동된 매물 리스트
        unchanged_count: 변동 없는 매물 수
        previous_timestamp: 이전 스냅샷 시각
        is_first_run: 이전 스냅샷이 없었는지
    """
    prev = load_snapshot()
    prev_articles = prev.get("articles", {})
    prev_timestamp = prev.get("timestamp", "")
    is_first = len(prev_articles) == 0

    # 현재 매물을 articleNo 기준으로 매핑
    current_map: dict[str, dict] = {}
    for a in current_articles:
        key = a.get("articleNo", "")
        if not key:
            continue
        current_map[key] = a

    current_keys = set(current_map.keys())
    prev_keys = set(prev_articles.keys())

    # 신규
    new_keys = current_keys - prev_keys
    new_articles = [current_map[k] for k in new_keys]

    # 삭제
    removed_keys = prev_keys - current_keys
    removed_articles = [
        {**prev_articles[k], "articleNo": k} for k in removed_keys
    ]

    # 가격 변동
    price_changed = []
    unchanged = 0
    for k in current_keys & prev_keys:
        cur_price = current_map[k].get("price") or current_map[k].get("dealOrWarrantPrc", "")
        prev_price = prev_articles[k].get("price") or prev_articles[k].get("priceStr", "")
        # 문자열/숫자 모두 비교
        if str(cur_price) != str(prev_price):
            price_changed.append({
                **current_map[k],
                "prevPrice": prev_articles[k].get("priceStr", str(prev_price)),
            })
        else:
            unchanged += 1

    # 새 스냅샷 저장
    save_snapshot(current_articles)

    return {
        "is_first_run": is_first,
        "previous_timestamp": prev_timestamp,
        "new": new_articles,
        "new_count": len(new_articles),
        "removed": removed_articles,
        "removed_count": len(removed_articles),
        "price_changed": price_changed,
        "price_changed_count": len(price_changed),
        "unchanged_count": unchanged,
        "total_current": len(current_map),
    }
