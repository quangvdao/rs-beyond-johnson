#!/usr/bin/env python3
"""Exact arithmetic for ordinary polynomial-curve MCA transfer budgets.

``exceptional_bound`` is the legacy ``L=D+1`` evaluator used by stored
certificates.  ``exceptional_bound_at_threshold`` is the free-witness-threshold
version.  Keeping both entry points makes certificate provenance explicit.
"""

from fractions import Fraction


def psi(D: int, B: int) -> int:
    """Coefficient of the challenge degree in the joint-image bound."""
    if D < 1 or B < 1:
        raise ValueError("require D >= 1 and B >= 1")
    return 1 + (2 * D - 1) * (2 * B - 1) + 2 * max(0, B - 2 * D - 1)


def joint_degree(D: int, B: int, H: int, ell: int = 1) -> int:
    if H < 0 or ell < 1:
        raise ValueError("require H >= 0 and ell >= 1")
    return ell * B + H * psi(D, B)


def exceptional_bound(
    n: int, D: int, A: int, B: int, H: int, ell: int = 1
) -> Fraction:
    """Legacy all-characteristic bound at the threshold ``L=D+1``."""
    return exceptional_bound_at_threshold(n, D, A, B, H, D + 1, ell)


def exceptional_bound_at_threshold(
    n: int, D: int, A: int, B: int, H: int, L: int, ell: int = 1
) -> Fraction:
    """Free-threshold ordinary degree-``ell`` exceptional-count bound.

    The nonconstant ordinary theorem has ``1 <= D <= n-2`` and permits every
    integral witness threshold ``D+1 <= L <= A``.  A constant ordinary tail
    (``B=0``) costs ``H`` and is handled before calling ``psi``.
    """
    if not (1 <= D <= n - 2 and D + 1 <= A <= n):
        raise ValueError("require 1 <= D <= n-2 and D+1 <= A <= n")
    if not (D + 1 <= L <= A):
        raise ValueError("require D+1 <= L <= A")
    if B < 0 or H < 0 or ell < 1:
        raise ValueError("require B,H >= 0 and ell >= 1")
    if B == 0:
        return Fraction(H)
    lam = Fraction(n - L + 1, A - L + 1)
    return (
        (2 * B - 1) * H
        + lam * joint_degree(D, B, H, ell)
        + ell * (n - L) * B
    )


def constant_code_exceptional_count(n: int, A: int, ell: int = 1) -> int:
    """All-characteristic incidence bound for dimension-one RS codes."""
    if not (n >= 1 and 1 <= A <= n and ell >= 1):
        raise ValueError("require n >= 1, 1 <= A <= n, and ell >= 1")
    collisions = ell * n * (n - 1) // 2
    return collisions if A == 1 else collisions // (A - 1)


def constant_code_list_size(n: int, A: int) -> int:
    """Dimension-one list bound, including the full-set ``A=1`` endpoint."""
    if not (n >= 1 and 1 <= A <= n):
        raise ValueError("require n >= 1 and 1 <= A <= n")
    return n // A


def coarse_joint_degree(D: int, B: int, H: int, ell: int = 1) -> int:
    """A simple unconditional joint bound, retained for comparisons."""
    return H + ell * B + 4 * D * B * H
