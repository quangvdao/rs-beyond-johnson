#!/usr/bin/env python3
"""Bounded exact comparison of the paper's finite certificates with better.codes.

Run from the repository root:

  python3 scripts/examples/proximity-prize/search_paper.py

The first-order search is over a declared finite heuristic support family.  It
does not claim global optimality.  All certificate and protocol-budget
comparisons use integer or Fraction arithmetic.
"""

import json
from math import log2
import sys

sys.path.insert(0, "scripts")
import tune_combination_protocol as combination
import tune_first_order_mca as first


N = 2**18
K = 2**17
P = 2_130_706_433
Q = P**6
SECURITY_BITS = 128
REDUCTION_BUDGET = Q // 2**SECURITY_BITS
CURRENT_A = 181_284


def record(c):
    if c is None:
        return None
    numerator = c["exceptional_count_upper"] + c["list_size_upper"]
    keys = (
        "m", "M", "mu", "support", "height", "dimension",
        "local_rank_upper", "selected_transfer_method",
        "selected_transfer_theorem", "selected_list_method",
        "selected_list_theorem", "L", "exceptional_count_upper",
        "list_size_upper", "characteristic_strictly_greater_than",
    )
    out = {key: c[key] for key in keys}
    out.update(
        reduction_numerator=numerator,
        reduction_budget=REDUCTION_BUDGET,
        meets_reduction_budget=numerator <= REDUCTION_BUDGET,
        reduction_bits=log2(Q) - log2(numerator),
    )
    return out


def first_order_pool(A):
    """Finite support family fixed by this report's search declaration."""
    return sorted({
        (m, M, mu)
        for m, M, mu in combination.adaptive_support_pool(N, K, A, 1000)
        if m <= 128
    })


def best_first_order(A):
    best = None
    feasible = 0
    for m, M, mu in first_order_pool(A):
        dimension, rank = first.support_counts(N, K, A, m, M, mu, True)
        if dimension <= N * rank:
            continue
        feasible += 1
        c = first.certificate(
            N, K, A, m, M, mu,
            weighted=True,
            method="sharp-v2",
            taylor_degree_model=first.TIGHT_TAYLOR_DEGREE_MODEL,
        )
        if c is None:
            continue
        numerator = c["exceptional_count_upper"] + c["list_size_upper"]
        key = (numerator, c["exceptional_count_upper"], c["list_size_upper"], m, M, mu)
        if best is None or key < best[0]:
            best = (key, c)
    return feasible, None if best is None else best[1]


def first_order_threshold(lo=183_200, hi=183_300):
    """Find adjacent checked failure/pass points by bisection.

    The support pool depends on A, so this is not a proof that the passing A is
    minimal even for the heuristic that generated the pools.
    """
    checked = {}

    def check(A):
        if A not in checked:
            feasible, cert = best_first_order(A)
            checked[A] = (feasible, cert)
        cert = checked[A][1]
        return cert is not None and (
            cert["exceptional_count_upper"] + cert["list_size_upper"]
            <= REDUCTION_BUDGET
        )

    assert not check(lo)
    assert check(hi)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if check(mid):
            hi = mid
        else:
            lo = mid
    assert not check(lo) and check(hi)
    return {
        "adjacent_checked_failing_A": lo,
        "failing_A_feasible_supports": checked[lo][0],
        "failing_A_certificate": record(checked[lo][1]),
        "adjacent_checked_passing_A": hi,
        "passing_A_feasible_supports": checked[hi][0],
        "passing_A_certificate": record(checked[hi][1]),
        "minimality_claim": False,
        "agreements_checked": sorted(checked),
    }


def main():
    current_feasible, current = best_first_order(CURRENT_A)
    result = {
        "scope": {
            "n": N,
            "k": K,
            "base_prime": P,
            "field_cardinality": Q,
            "interleaving_width": 8,
            "protocol_list_interleaving_width": 16,
            "queries": 128,
            "reduction_target": "2^-128",
            "exact_reduction_condition": "(E + Lambda) / q <= 2^-128",
            "integer_reduction_budget": REDUCTION_BUDGET,
            "bridge": (
                "line MCA transfers to width 8 without loss; the scalar list "
                "bound transfers by extension-field encoding to the doubled "
                "width 16 list used by the extractor"
            ),
        },
        "search": {
            "claim": "bounded heuristic search, not global optimality",
            "support_profile": "adaptive_support_pool clipped to m <= 128 and max jet degree 1000",
            "support_weights": "derivative-weighted only",
            "transfer": "sharp-v2",
            "taylor_degree_model": first.TIGHT_TAYLOR_DEGREE_MODEL,
        },
        "current_leader_agreement": {
            "A": CURRENT_A,
            "feasible_supports": current_feasible,
            "certificate": record(current),
        },
        "bounded_first_order_adjacent_points": first_order_threshold(),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
