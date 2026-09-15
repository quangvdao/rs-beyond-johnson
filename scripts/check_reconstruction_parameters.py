#!/usr/bin/env python3
"""Exact boundary checks for the shortened higher-order length recipes.

The manuscript proves the inequalities uniformly. These rational instances
exercise ceilings, the rate split, and minimal reconstruction dimensions.
"""
from fractions import Fraction as F


def ceil(x):
    return -(-x.numerator // x.denominator)


def check_uniform():
    count = 0
    for delta in (F(1, 100), F(1, 17), F(1, 5), F(239, 1000)):
        for d, m in ((1, 2), (500, 501), (519, 10**9)):
            N = ceil(m / delta**2)
            B = N - 1
            for n in (N, N + 1, N + 37):
                split = delta**2 * n
                for k in {1, max(1, split.numerator // split.denominator - 1),
                          ceil(split), n - ceil(delta * n)}:
                    A = k + ceil(delta * n)
                    if A > n:
                        continue
                    if F(k, n) >= delta**2:
                        rho, D, a = F(k, n), k, F(k, n) + delta
                    else:
                        rho = 2 * delta**2
                        D = (rho * n).numerator // (rho * n).denominator
                        a = delta
                    A0 = ceil(a * n)
                    Krec = max(k, d + 1)
                    assert k <= D <= rho * n
                    assert D >= split and D >= m > d
                    assert Krec <= D + 1 <= n and A0 <= A <= n
                    assert F(m * A0, D) <= m / delta**2
                    assert B < n and n > 2 * m and 2 * m * A0 < n * n
                    count += 1
    return count


def check_fixed_rate():
    count = 0
    for rho in (F(1, 100), F(1, 4), F(1, 2), F(9, 10), F(999, 1000)):
        for d in (500, 519, 1000):
            for m in (1, 501, 10**9):
                B = ceil(2 * m / rho)
                N = ceil(max((d + 1) / rho, F(B + 1), 1 / (1 - rho)))
                old = ceil(max(2 * (d + 2) / rho, 4 * m / rho,
                               2 / (1 - rho), F(B + 1), F(2)))
                assert N <= old
                for n in (N, N + 1, N + 37):
                    D = (rho * n).numerator // (rho * n).denominator
                    assert D >= d + 1 and D >= rho * n / 2
                    assert D + 1 <= n and B < n and n > 2 * m
                    for k in {1, d, d + 1, D}:
                        assert max(k, d + 1) <= D + 1
                    count += 1
    return count


if __name__ == '__main__':
    uniform = check_uniform()
    fixed = check_fixed_rate()
    print(f'PASS: {uniform} uniform and {fixed} fixed-rate exact boundary cases')
