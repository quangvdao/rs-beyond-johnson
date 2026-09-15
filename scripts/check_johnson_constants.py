#!/usr/bin/env python3
"""Exact finite Johnson interpolation and height comparisons."""

from decimal import Decimal, getcontext, ROUND_CEILING
from fractions import Fraction
from pathlib import Path
import importlib.util

getcontext().prec = 80

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "tune_ordinary_mca", REPO / "scripts/tune_ordinary_mca.py"
)
TUNER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(TUNER)


def ceil_dec(x: Decimal) -> int:
    return int(x.to_integral_value(rounding=ROUND_CEILING))


def transfer(n: int, D: int, A: int, B: int, H: int) -> Fraction:
    return TUNER.ordinary_exceptional_bound(n, D, A, B, H)


def counts(n: int, D: int, m: int, L: int, B: int, H: int) -> tuple[int, int]:
    nvar = sum((L - D * j) * (H - j + 1) for j in range(B + 1))
    neq = n * sum(
        (m - b) * (H - b + 1) for b in range(min(B, m - 1) + 1)
    )
    return nvar, neq


def minimal_height(n: int, D: int, m: int, L: int, B: int) -> int | None:
    if L - D * B <= 0:
        return None
    slope = sum(L - D * j for j in range(B + 1))
    bmax = min(B, m - 1)
    slope -= n * sum(m - b for b in range(bmax + 1))
    intercept = sum((L - D * j) * (1 - j) for j in range(B + 1))
    intercept -= n * sum((m - b) * (1 - b) for b in range(bmax + 1))
    H = B
    if slope > 0 and slope * H + intercept <= 0:
        H = max(H, (-intercept) // slope + 1)
    if slope * H + intercept <= 0:
        return None
    v, e = counts(n, D, m, L, B, H)
    assert v > e
    return H


def bounded_optimum(n: int, D: int, A: int, m_limit: int) -> dict[str, object]:
    best = None
    for m in range(1, m_limit + 1):
        L = m * A
        Bmax = (L - 1) // D
        for B in range(1, Bmax + 1):
            H = minimal_height(n, D, m, L, B)
            if H is None:
                continue
            canonical = TUNER.certificate(n, D + 1, A, m, B)
            assert canonical is not None
            assert canonical["H"] == H
            E = transfer(n, D, A, B, H)
            assert Fraction(canonical["exceptional_bound"]) == E
            key = (E, B, H, m)
            if best is None or key < best[0]:
                best = (key, {"m": m, "L": L, "B": B, "H": H, "E": E})
    assert best is not None
    return best[1]


def closed_recipe(n: int, D: int, A: int, eta: Decimal) -> dict[str, object]:
    x = (Decimal(D) / Decimal(n)).sqrt()
    m = max(ceil_dec(x / (2 * eta)), 3)
    t = Decimal(m) + Decimal("0.5")
    S = t * Decimal(n) * x
    L = ceil_dec(S)
    B = ceil_dec(t / x) - 1
    H = ceil_dec(t * t / (3 * x * x)) - 1
    v, e = counts(n, D, m, L, B, H)
    assert v > e and L <= m * A
    return {"m": m, "L": L, "B": B, "H": H,
            "E": transfer(n, D, A, B, H)}


def rounded_recipe(n: int, D: int, A: int) -> dict[str, object]:
    x = (Decimal(D) / Decimal(n)).sqrt()
    eta_eff = Decimal(A) / Decimal(n) - x
    return closed_recipe(n, D, A, eta_eff)


def fmt_int(x: int | Fraction) -> str:
    if isinstance(x, Fraction):
        return f"{float(x):.6g}"
    return f"{x:,}"


def pairwise_list_floor(n: int, D: int, A: int) -> int:
    assert A * A > D * n
    q = Fraction(n * (A - D), A * A - D * n)
    return q.numerator // q.denominator


def one_case(rate: Fraction, eta_s: str, n: int = 2**16) -> None:
    k = rate * n
    assert k.denominator == 1
    D = k.numerator - 1
    x = (Decimal(D) / Decimal(n)).sqrt()
    eta = Decimal(eta_s)
    A = ceil_dec((x + eta) * n)
    base = closed_recipe(n, D, A, eta)
    rounded = rounded_recipe(n, D, A)
    limit = 4 * base["m"]
    exact = bounded_optimum(n, D, A, limit)
    bmax = (exact["m"] * A - 1) // D
    asympt_ratio = Decimal(27) / 4 * x * (1 - x) ** 3

    for name, row in (("printed", base), ("rounded", rounded), ("search", exact)):
        print(
            f"  {name:7} m={row['m']:<4} B={row['B']:<5} H={row['H']:<8} "
            f"E={fmt_int(row['E']):>12}"
        )
    print(
        f"  ratios  search/printed: B={exact['B']/base['B']:.4f}, "
        f"H={exact['H']/base['H']:.4f}, "
        f"E={float(exact['E']/base['E']):.4f}; "
        f"A={A}, eta_eff={float(Decimal(A)/n-x):.8f}, "
        f"B/Bmax={exact['B']}/{bmax}, "
        f"pairwise-list={pairwise_list_floor(n,D,A)}, "
        f"asymptotic-BH-ratio={float(asympt_ratio):.4f}"
    )


if __name__ == "__main__":
    for rate in (Fraction(1, 16), Fraction(1, 4), Fraction(1, 2)):
        for eta in ("0.01", "0.02"):
            print(f"rate={rate} eta={eta} n={2**16}")
            one_case(rate, eta)
