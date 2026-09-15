#!/usr/bin/env python3
"""Replay two exact paper-technique certificates for the better.codes profile.

Run from the repository root:

  python3 scripts/examples/proximity-prize/check_points.py
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, "scripts")
import tune_first_order_mca as first
import tune_ordinary_mca as ordinary


N = 2**18
K = 2**17
P = 2_130_706_433
Q = P**6
BUDGET = Q // 2**128
SAVED_POINTS = Path(__file__).with_name("paper-points.json")


def score_check(A, centibits):
    """Certify (A/n)^128 <= 2^(-centibits/100) by integers."""
    lhs = A**12800 * 2**centibits
    rhs = N**12800
    assert lhs <= rhs
    assert A**12800 * 2**(centibits + 1) > rhs
    return {
        "conservative_spot_term": f"({A}/{N})^128",
        "certified_score_centibits": centibits,
        "next_centibit_fails_for_this_spot_bound": True,
    }


def first_order_point():
    A = 183_210
    c = first.certificate(
        N, K, A, 26, 7, 36,
        weighted=True,
        method="sharp-v2",
        taylor_degree_model=first.TIGHT_TAYLOR_DEGREE_MODEL,
    )
    assert c is not None
    assert c["height"] == 485
    assert c["exceptional_count_upper"] == 274_498_710_692_409_102
    assert c["list_size_upper"] == 285_674_919
    numerator = c["exceptional_count_upper"] + c["list_size_upper"]
    assert numerator == 274_498_710_978_084_021
    assert numerator <= BUDGET
    assert P > c["characteristic_strictly_greater_than"]
    return {
        "method": "first-order squarefree sharp-v2, tight Taylor degree",
        "A": A,
        "support": [26, 7, 36],
        "height": c["height"],
        "regular_threshold_L": c["L"],
        "exceptional_count_upper": c["exceptional_count_upper"],
        "interleaved_list_size_upper": c["list_size_upper"],
        "reduction_numerator": numerator,
        "reduction_budget": BUDGET,
        "characteristic_guard": c["characteristic_strictly_greater_than"],
        **score_check(A, 6615),
    }


def ordinary_point():
    A = 185_372
    c = ordinary.certificate(N, K, A, 4096, 5792)
    assert c is not None
    assert c["H"] == 22_992_660
    assert c["exceptional_count"] == 168_519_951_717_387_772
    assert c["list_bound"] == 5792
    numerator = c["exceptional_count"] + c["list_bound"]
    assert numerator == 168_519_951_717_393_564
    assert numerator <= BUDGET
    return {
        "method": "ordinary Johnson certificate, legacy L=k transfer",
        "A": A,
        "support": [4096, 5792],
        "height": c["H"],
        "exceptional_count_upper": c["exceptional_count"],
        "interleaved_list_size_upper": c["list_bound"],
        "reduction_numerator": numerator,
        "reduction_budget": BUDGET,
        "characteristic_guard": 0,
        **score_check(A, 6399),
    }


def main():
    result = {
        "profile": {
            "n": N,
            "k": K,
            "base_prime": P,
            "field_cardinality": Q,
            "interleaving_width": 8,
            "extractor_list_width": 16,
            "queries": 128,
            "exact_reduction_condition": "(E + Lambda) / q <= 2^-128",
        },
        "ordinary": ordinary_point(),
        "first_order": first_order_point(),
        "comparison": {
            "agreement_positions_improved": 185_372 - 183_210,
            "certified_score_gain_centibits": 6615 - 6399,
            "scope": "two replayable points; no global optimality claim",
        },
    }
    expected = json.loads(SAVED_POINTS.read_text())
    if result != expected:
        raise SystemExit(f"replay differs from saved fixture: {SAVED_POINTS}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
