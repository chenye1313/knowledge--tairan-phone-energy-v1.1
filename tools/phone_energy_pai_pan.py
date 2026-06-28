#!/usr/bin/env python3
"""Deterministic phone energy plate parser.

This script only performs fixed table lookup and structural decomposition.
It does not produce fate, medical, legal, investment, finance, or marriage judgments.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "phone_energy_fixed_rules.json"


def load_rules() -> dict[str, Any]:
    with RULES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_pair_map(rules: dict[str, Any]) -> dict[str, dict[str, Any]]:
    pair_map: dict[str, dict[str, Any]] = {}
    for field_id, field in rules["fields"].items():
        for rank, group in enumerate(field["strength_groups"], start=1):
            for pair in group:
                pair_map[pair] = {
                    "field_id": field_id,
                    "label": field["label"],
                    "polarity": field["polarity"],
                    "theme": field["theme"],
                    "strength_rank": rank,
                }
    return pair_map


def normalize_phone(raw: str) -> str:
    phone = re.sub(r"\D", "", raw)
    if len(phone) != 11:
        raise ValueError(f"expected 11 digits after normalization, got {len(phone)}: {phone}")
    return phone


def classify_pair(pair: str, pair_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if "0" in pair or "5" in pair:
        return {
            "pair": pair,
            "field_id": "special",
            "label": "特殊",
            "special_digits": [d for d in pair if d in {"0", "5"}],
            "note": "contains 0/5; evaluate through special A0B/A5B or tail rules",
        }
    if pair not in pair_map:
        return {
            "pair": pair,
            "field_id": "unknown",
            "label": "未归类",
            "note": "not found in fixed pair map; verify rules",
        }
    return {"pair": pair, **pair_map[pair]}


def special_outer_triplet(triplet: str, pair_map: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    a, mid, b = triplet
    if mid not in {"0", "5"}:
        return None
    if a in {"0", "5"} or b in {"0", "5"}:
        return {
            "type": "multi_special",
            "modifier": mid,
            "note": "multiple special digits; requires cautious human review",
        }
    outer = a + b
    outer_info = classify_pair(outer, pair_map)
    modifier = "zero_blocks_or_hides" if mid == "0" else "five_amplifies_or_delays"
    return {
        "type": "outer_pair_modifier",
        "modifier": mid,
        "outer_pair": outer,
        "outer_pair_info": outer_info,
        "modifier_rule": modifier,
    }


def parse_phone(raw: str, rules: dict[str, Any]) -> dict[str, Any]:
    phone = normalize_phone(raw)
    pair_map = build_pair_map(rules)
    prefix3 = phone[:3]
    tail8 = phone[3:]
    digits = list(tail8)

    yang = {"1", "3", "5", "7", "9"}
    yin = {"0", "2", "4", "6", "8"}
    yin_yang = {
        "yang_count": sum(d in yang for d in digits),
        "yin_count": sum(d in yin for d in digits),
    }

    pair_windows = []
    for i in range(len(tail8) - 1):
        pair = tail8[i : i + 2]
        pair_windows.append({
            "index": i + 1,
            "position": [i + 1, i + 2],
            **classify_pair(pair, pair_map),
        })

    triplet_windows = []
    for i in range(len(tail8) - 2):
        triplet = tail8[i : i + 3]
        first_pair = triplet[:2]
        second_pair = triplet[1:]
        known = rules["known_triplets"].get(triplet)
        triplet_windows.append({
            "index": i + 1,
            "position": [i + 1, i + 3],
            "triplet": triplet,
            "first_pair": classify_pair(first_pair, pair_map),
            "second_pair": classify_pair(second_pair, pair_map),
            "outer_special": special_outer_triplet(triplet, pair_map),
            "known_triplet": known,
            "source_status": known["source_status"] if known else "derived_by_pair_flow",
        })

    counts = Counter(w["label"] for w in pair_windows)
    return {
        "phone": phone,
        "prefix3_common_segment": prefix3,
        "tail8_focus": tail8,
        "digits": digits,
        "yin_yang": yin_yang,
        "pair_windows": pair_windows,
        "triplet_windows": triplet_windows,
        "tail": {
            "last_digit": tail8[-1],
            "tail2": pair_windows[-1],
            "tail3": triplet_windows[-1],
            "tail4": tail8[-4:],
        },
        "pair_field_counts": dict(counts),
        "boundary": rules["ai_boundary"],
    }


def verify_rules(rules: dict[str, Any]) -> dict[str, Any]:
    pair_map = build_pair_map(rules)
    expected_digits = rules["digit_set_for_pair_fields"]
    expected_pairs = {a + b for a in expected_digits for b in expected_digits}
    missing = sorted(expected_pairs - set(pair_map))
    extra = sorted(set(pair_map) - expected_pairs)
    return {
        "expected_pair_count": len(expected_pairs),
        "actual_pair_count": len(pair_map),
        "missing_pairs": missing,
        "extra_pairs": extra,
        "ok": not missing and not extra,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse mobile phone number by fixed energy rules.")
    parser.add_argument("phone", nargs="?", help="11-digit Chinese mainland mobile number")
    parser.add_argument("--verify-rules", action="store_true", help="verify fixed pair table coverage")
    parser.add_argument("--compact", action="store_true", help="print compact JSON")
    args = parser.parse_args()

    rules = load_rules()
    if args.verify_rules:
        payload = verify_rules(rules)
    else:
        if not args.phone:
            parser.error("phone is required unless --verify-rules is used")
        payload = parse_phone(args.phone, rules)

    print(json.dumps(payload, ensure_ascii=False, indent=None if args.compact else 2))


if __name__ == "__main__":
    main()

