#!/usr/bin/env python3
"""Exact checks for the revised uniform and capacity constants."""

from fractions import Fraction as F


def rank_profile(m, M, B):
    result = []
    for t in range(B + 1):
        rank = 0
        for s in range(m):
            source = max(0, min(t, s) - max(0, t - M) + 1)
            rank += min(m - s, source)
        result.append(rank)
    return result


def uniform_margins():
    m, M, B, H, delta = 12, 4, 23, 276, F(6, 25)
    ranks = rank_profile(m, M, B)
    assert ranks == [12, 22, 30, 36, 40, 35, 30, 25, 20, 16, 12,
                     9, 6, 4, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    points = {F(0), F(19, 25)}
    points.update(F(72, 25*s) for s in range(4, 12))

    rows = []
    for rho in sorted(points):
        source = [(min(t, M)+1) * max(F(0), m*delta+rho*(m-t))
                  for t in range(B + 1)]
        coefficient = sum(source) - sum(ranks)
        height = sum((Nt-rt)*(H-t+1)
                     for t, (Nt, rt) in enumerate(zip(source, ranks)))
        rows.append((rho, coefficient, height))
    expected = (F(72, 275), F(204, 55), F(14, 5))
    assert min(rows, key=lambda row: row[1]) == expected
    assert min(rows, key=lambda row: row[2]) == expected
    return rows


def positive_order_budgets(D, B, actual, H):
    """The J1 and B1 sums in the canonical first-order hybrid lemma."""
    tau, challenge_lift = 2*D-1, 1+(2*D-1)*H
    joint = fiber = 0
    for j in range(B-actual+1, B+1):
        r = j-(B-actual)
        b = 1+tau*(j-1)
        c = min(b, tau*(r-1)+D)
        stage_fiber = j*c+r*(b-c)
        joint += H*(2*b*c-c*c)+2*challenge_lift*stage_fiber
        fiber += stage_fiber
    return joint, fiber


def quadratic(values):
    a = F(values[2]-2*values[1]+values[0], 2)
    b = values[1]-values[0]-3*a
    return a, b, values[0]-a-b


def stage_expansions():
    expected_joint = [
        (0, 0, 0),
        (96_876, -71_076, 11_550),
        (329_544, -277_780, 56_966),
        (684_756, -606_880, 132_944),
        (1_149_264, -1_045_144, 236_180),
    ]
    expected_fiber = [
        (0, 0), (66, -21), (214, -83), (436, -182), (724, -314)
    ]
    for actual in range(5):
        values = [positive_order_budgets(D, 23, actual, 276)
                  for D in (1, 2, 3)]
        joint = quadratic([value[0] for value in values])
        fiber = (values[1][1]-values[0][1],
                 2*values[0][1]-values[1][1])
        assert joint == expected_joint[actual]
        assert fiber == expected_fiber[actual]

    # At each positive-order stage, b-c=37D-18>0 for D>=1. Thus the
    # minimum branch is fixed and the degree-two interpolations above are
    # symbolic identities. Check the resulting monotonic caps as well.
    for D in range(1, 50):
        budgets = [positive_order_budgets(D, 23, r, 276)
                   for r in range(5)]
        assert all(budgets[r][0] <= budgets[r+1][0] and
                   budgets[r][1] <= budgets[r+1][1]
                   for r in range(4))
        joint, fiber = budgets[4]
        assert joint == 1_149_264*D*D-1_045_144*D+236_180
        assert fiber == 724*D-314
        assert joint <= 1_149_264*D*D and fiber <= 724*D


def uniform_bounds():
    delta, B, H = F(6, 25), 23, 276
    exceptional = (F((2*B-1)*H, 4) + F(H+B, 1)/(4*delta)
                   + F(B*H, 1)/(2*delta) + F(B, 2)
                   + F(42, 41)*F(1_149_264, 1)/(16*delta*delta)
                   + F(42*724, 1)/(4*delta))
    assert exceptional == F(1_304_562_211, 984) < 1_325_775

    # The 307n comparison after canceling the equal quadratic terms.
    assert F(30_529, 25)*2 > 16
    return exceptional


def log_interval(x, terms=160):
    """Rigorous rational lower and upper bounds for log(x), for x >= 1."""
    x = F(x)
    assert x >= 1
    z = (x-1)/(x+1)
    partial = 2*sum((z**(2*j+1))/F(2*j+1) for j in range(terms))
    tail = 2*z**(2*terms+1)/F((2*terms+1)*(1-z*z))
    return partial, partial+tail


def log_lower(x, terms=160):
    return log_interval(x, terms)[0]


def log_upper(x, terms=160):
    return log_interval(x, terms)[1]


def capacity_loss():
    c, d = 300, 519
    epsilon = F(1, c*d**3)
    loss = (F(2, c*d*d)
            + F(d+1, d)/F(2*c)*(1/(1-epsilon))
            + F(d+1, d)/F(c*d)*(1/(1-epsilon)))
    assert loss < F(1677, 10**6)

    # Use upper bounds on both logarithms to certify the strict scalar margin.
    margin_lower = (F(3, 2)-F(1677, 10**6)
                    -log_upper(F(40, 9))-log_upper(F(151, 150)))
    assert margin_lower > 0
    return loss, margin_lower


def main():
    rows = uniform_margins()
    stage_expansions()
    exceptional = uniform_bounds()
    loss, margin = capacity_loss()
    print("uniform breakpoints:", len(rows))
    print("minimum margins:", min(r[1] for r in rows),
          min(r[2] for r in rows))
    print("exceptional coefficient:", exceptional)
    print("multiplicity-300 loss:", f"{float(loss):.12f}")
    print("certified logarithmic slack:", f"{float(margin):.12f}")


if __name__ == "__main__":
    main()
