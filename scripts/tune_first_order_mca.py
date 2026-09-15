#!/usr/bin/env python3
"""Exact, received-word-independent first-order MCA certificate search.

Search is bounded, not a claim of global optimality.  The selected certificate
records its own positive-characteristic guard and transfer theorem.  Both line
and polynomial-curve received families are supported.
"""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
import sys

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from ordinary_mca_budget import (
    constant_code_exceptional_count,
    constant_code_list_size,
    exceptional_bound as ordinary_exceptional_bound,
    exceptional_bound_at_threshold as ordinary_exceptional_bound_at_threshold,
    joint_degree as ordinary_joint_degree,
)

LEGACY_TAYLOR_DEGREE_MODEL = 'legacy-2D-minus-1'
TIGHT_TAYLOR_DEGREE_MODEL = 'tight-2D-minus-3-v3'
TAYLOR_DEGREE_MODELS = (
    LEGACY_TAYLOR_DEGREE_MODEL,
    TIGHT_TAYLOR_DEGREE_MODEL,
)


def first_order_taylor_exponent(D, model=LEGACY_TAYLOR_DEGREE_MODEL):
    """Return the common Taylor exponent for a versioned degree model.

    The default is frozen for historical certificate reproduction.  The v3
    model uses the sharp exponent from the paper revision; at message degree
    one its zero exponent records the identity map on the initial jet pair.
    """
    if D < 1:
        raise ValueError('require message degree D >= 1')
    if model == LEGACY_TAYLOR_DEGREE_MODEL:
        return 2 * D - 1
    if model == TIGHT_TAYLOR_DEGREE_MODEL:
        return max(0, 2 * D - 3)
    raise ValueError(f'unknown Taylor degree model: {model}')


def ceil(x):
    return -(-x.numerator // x.denominator)


def minimize_convex_integer(lo, hi, objective):
    """Return the leftmost integer minimizer of a convex objective."""
    while lo < hi:
        mid = (lo + hi) // 2
        if objective(mid + 1) < objective(mid):
            lo = mid + 1
        else:
            hi = mid
    return lo, objective(lo)


def support_profiles(n, k, A, m, M, mu, weighted=True):
    """Counts of source coefficients and local rows, by total jet degree."""
    D = max(k, 2) - 1
    Ns, rs = [], []
    for t in range(mu + 1):
        cap = min(t, M)
        base = m*A-D*t
        lo = max(0, 1-base) if weighted else 0
        Nt = ((cap-lo+1)*base+(lo+cap)*(cap-lo+1)//2
              if weighted and lo<=cap else 0)
        if not weighted: Nt=(cap+1)*max(0,base)
        Ns.append(Nt)
        rt=0
        for u in range(max(0,t-M),m):
            low, high=max(0,t-M),min(t,u)
            if weighted:
                if u+(D-1)*t>=m*A: continue
            else: low=max(low,u+D*t-m*A+1)
            rt+=min(max(0,high-low+1),m-u)
        rs.append(rt)
    return Ns,rs


def support_counts(n,k,A,m,M,mu,weighted=True):
    Ns,rs=support_profiles(n,k,A,m,M,mu,weighted)
    return sum(Ns),sum(rs)


def column_profile(k, A, m, M, mu, weighted=True):
    D = max(k, 2) - 1
    step = D - 1 if weighted else D
    result = []
    for a in range(mu + 1):
        base = m*A-D*a
        cap = min(M,mu-a)
        if base <= 0:
            result.append(0)
            continue
        if step:
            cap = min(cap,(base-1)//step)
        result.append((cap+1)*base-step*cap*(cap+1)//2)
    return result


def shifted_height(Ns, rs, n, ell):
    """First strict positive surplus, found on its affine pieces.

    Row-profile surpluses need not be monotone. A degree-t term becomes
    active at H=ell*t; inspect every such segment, including the tail.
    """
    slope=intercept=0
    for t,(Nt,rt) in enumerate(zip(Ns,rs)):
        coeff=Nt-n*rt
        start=ell*t
        slope+=coeff
        intercept+=coeff*(1-start)
        end=ell*(t+1)-1
        if slope*start+intercept>0:return start
        if slope>0:
            candidate=max(start,(-intercept)//slope+1)
            if t==len(Ns)-1 or candidate<=end:return candidate
    raise ValueError('nonpositive total interpolation surplus')


def height_certificate(n,k,A,m,M,mu,weighted=True,ell=1):
    Ns,rs=support_profiles(n,k,A,m,M,mu,weighted)
    N,r=sum(Ns),sum(rs)
    if N<=n*r: return None
    profile=column_profile(k,A,m,M,mu,weighted)
    W=sum(a*c for a,c in enumerate(profile))
    lo,hi=0,ell*W//(N-n*r)
    def valid(H):
        return sum(c*max(0,H-ell*a+1) for a,c in enumerate(profile))>n*r*(H+1)
    assert valid(hi)
    while lo<hi:
        mid=(lo+hi)//2
        if valid(mid):hi=mid
        else:lo=mid+1
    row=shifted_height(Ns,rs,n,ell)
    return dict(height=min(row,lo),row_height=row,column_height=lo,
                height_method='row' if row<=lo else 'column',
                dimension=N,local_rank_upper=r,column_degree_sum=W,
                source_jet_degree_sum=sum(t*c for t,c in enumerate(Ns)),
                row_jet_degree_sum=sum(t*c for t,c in enumerate(rs)))


def kernel_height(n,k,A,m,M,mu,r,weighted=True):
    h=height_certificate(n,k,A,m,M,mu,weighted)
    assert h is not None and r==h['local_rank_upper']
    return h['height'],h['column_degree_sum']


def stage_budgets(
    k, mu, M, h, ell=1,
    taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL,
):
    """Retain total and separate derivative degrees in each Taylor image.

    These are the joint and fixed-challenge degrees in the manuscript's
    first-order transfer lemma. The separate degree decreases at every
    derivative stage, removing monomials from the total-degree triangle.
    """
    D=max(k,2)-1
    tau=first_order_taylor_exponent(D, taylor_degree_model)
    a=ell+tau*h
    M=min(M,mu)
    J0=J1=B0=B1=0
    for j in range(1,mu+1):
        b=1+tau*(j-1)
        if j>mu-M:
            derivative_degree=j-(mu-M)
            c=min(b,tau*(derivative_degree-1)+D)
            fiber=j*c+derivative_degree*(b-c)
            J1+=h*(2*b*c-c*c)+2*a*fiber
            B1+=fiber
        else:
            J0+=h*b+j*a;B0+=j
    return J0,J1,B0,B1


def degrees(k,mu,M,h,taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL):
    J0,J1,B0,B1=stage_budgets(
        k,mu,M,h,taylor_degree_model=taylor_degree_model)
    return J0+J1,B0+B1


def transfer(
    n, k, A, mu, h, L, M=None, ell=1,
    taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL,
):
    if M is None:M=mu
    J0,J1,B0,B1=stage_budgets(
        k,mu,M,h,ell,taylor_degree_model)
    l1=F(n-L+1,A-L+1);l2=F(n-k+1,L-k+1);eta=F(n-k+1,A-k+1)
    return F(h)+l1*(eta*J1+J0)+ell*(n-L)*(l2*B1+B0)


def best_threshold(
    n, k, A, mu, h, M=None, ell=1,
    taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL,
):
    return minimize_convex_integer(
        k, A, lambda L: transfer(
            n,k,A,mu,h,L,M,ell,taylor_degree_model))


def _ordinary_curve_transfer(n, k, A, B, H, ell):
    """Legacy all-characteristic ordinary transfer at ``L=k``."""
    D = k - 1
    joint = ordinary_joint_degree(D, B, H, ell)
    bound = ordinary_exceptional_bound(n, D, A, B, H, ell)
    return dict(
        method='ordinary-factorwise-curve',
        theorem='ordinary Frobenius curve transfer (R3)',
        characteristic_strictly_greater_than=0,
        L=k,
        exact_exceptional_bound=str(bound),
        exceptional_count_upper=ceil(bound),
        preliminary_exception_upper=(2*B-1)*H,
        ordinary_degree_upper=B,
        ordinary_challenge_degree_upper=H,
        joint_degree_upper=joint,
        generic_fiber_degree_upper=B,
        joint_degree_order_zero=joint,
        joint_degree_order_one=0,
        fiber_degree_order_zero=B,
        fiber_degree_order_one=0,
        degree_metadata_scope='ordinary Frobenius image')


def _ordinary_free_threshold_transfer(n, k, A, B, H, ell):
    """Versioned free-threshold ordinary degree-``ell`` transfer."""
    D = k - 1

    def objective(L):
        return ordinary_exceptional_bound_at_threshold(
            n, D, A, B, H, L, ell
        )

    L, bound = minimize_convex_integer(k, A, objective)
    joint = ordinary_joint_degree(D, B, H, ell)
    return dict(
        method=('ordinary-free-threshold-v2-curve' if ell > 1
                else 'ordinary-free-threshold-v2-line'),
        theorem='free-witness-threshold ordinary curve transfer',
        characteristic_strictly_greater_than=0,
        L=L,
        exact_exceptional_bound=str(bound),
        exceptional_count_upper=ceil(bound),
        preliminary_exception_upper=(2*B-1)*H,
        ordinary_degree_upper=B,
        ordinary_challenge_degree_upper=H,
        joint_degree_upper=joint,
        generic_fiber_degree_upper=B,
        joint_degree_order_zero=joint,
        joint_degree_order_one=0,
        fiber_degree_order_zero=B,
        fiber_degree_order_one=0,
        degree_metadata_scope='free-threshold ordinary Frobenius image')


def _sharp_transfer(
    n, k, A, B, M, H, ell, *, optimize_tail=False,
    taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL,
):
    """Squarefree one-chart/resultant transfer (R2+R3)."""
    D = k - 1
    lam = F(n-D, A-D)
    tau = first_order_taylor_exponent(D, taylor_degree_model)
    u = 1 + tau*(B-1)
    v = min(u, tau*(M-1)+D)
    fiber = B*v + M*(u-v)
    ordinary_degree = max(B, (2*M-1)*B-M*M)
    ordinary_height = (2*M-1)*H
    regular_joint = H*(2*u*v-v*v) + 2*(ell+tau*H)*fiber
    ordinary_joint = ordinary_joint_degree(
        D, ordinary_degree, ordinary_height, ell
    )
    tail_L = k
    ordinary = ordinary_exceptional_bound(
        n, D, A, ordinary_degree, ordinary_height, ell
    )
    if optimize_tail:
        tail_L, ordinary = _ordinary_tail_minimum(
            n, D, A, ordinary_degree, ordinary_height, ell
        )

    def objective(L):
        return (ordinary
                +F(n-L+1, A-L+1)*lam*regular_joint
                +ell*(n-L)*F(n-D, L-D)*fiber)

    L, bound = minimize_convex_integer(k, A, objective)
    return dict(
        method=(('sharp-squarefree-free-tail-' if optimize_tail
                 else 'sharp-squarefree-')
                + ('taylor-tight-v3-' if
                   taylor_degree_model == TIGHT_TAYLOR_DEGREE_MODEL else '')
                + ('curve' if ell > 1 else 'line')),
        theorem='squarefree one-chart/resultant transfer (R2+R3)',
        ordinary_tail_L=tail_L,
        exact_ordinary_tail_bound=str(ordinary),
        characteristic_strictly_greater_than=max(D, M),
        L=L,
        exact_exceptional_bound=str(bound),
        exceptional_count_upper=ceil(bound),
        preliminary_exception_upper=(2*ordinary_degree-1)*ordinary_height,
        ordinary_degree_upper=ordinary_degree,
        ordinary_challenge_degree_upper=ordinary_height,
        regular_total_degree_upper=u,
        regular_derivative_degree_upper=v,
        joint_degree_upper=ordinary_joint+regular_joint,
        generic_fiber_degree_upper=ordinary_degree+fiber,
        joint_degree_order_zero=ordinary_joint,
        joint_degree_order_one=regular_joint,
        fiber_degree_order_zero=ordinary_degree,
        fiber_degree_order_one=fiber,
        degree_metadata_scope='ordinary eliminant plus one regular squarefree chart')


def _hybrid_stage_sums(
    D, B, H, derivative_degree, ell=1,
    taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL,
):
    tau = first_order_taylor_exponent(D, taylor_degree_model)
    fiber = joint = 0
    for r in range(1, derivative_degree+1):
        j = B-derivative_degree+r
        b = 1+tau*(j-1)
        c = min(b, tau*(r-1)+D)
        stage_fiber = j*c+r*(b-c)
        fiber += stage_fiber
        joint += H*(2*b*c-c*c)+2*(ell+tau*H)*stage_fiber
    return fiber, joint


def _legacy_hybrid_transfer(
    n, k, A, B, M, H,
    taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL,
):
    """Legacy line-only derivative-chain transfer retained for provenance."""
    D = k-1
    lam = F(n-D, A-D)

    def at_degree(d):
        fiber, joint = _hybrid_stage_sums(
            D, B, H, d, taylor_degree_model=taylor_degree_model)
        tail_degree = B-d
        if tail_degree:
            tail_joint = ordinary_joint_degree(D, tail_degree, H)
            tail = ordinary_exceptional_bound(
                n, D, A, tail_degree, H
            )
        else:
            tail_joint = 0
            tail = F(H)

        def objective(L):
            return (tail+F(n-L+1,A-L+1)*lam*joint
                    +(n-L)*F(n-D,L-D)*fiber)

        L, bound = minimize_convex_integer(k, A, objective)
        return bound, L, fiber, joint, tail_degree, tail_joint

    candidates = [(*at_degree(d), d) for d in range(M+1)]
    bound, L, fiber, joint, tail_degree, tail_joint, d = max(
        candidates, key=lambda row: (row[0], -row[1], row[-1]))
    return dict(
        method=('hybrid-ordinary-tail-'
                + ('taylor-tight-v3-' if
                   taylor_degree_model == TIGHT_TAYLOR_DEGREE_MODEL else '')
                + 'line'),
        theorem='first-order derivative chain with ordinary tail',
        characteristic_strictly_greater_than=max(D, M),
        L=L,
        actual_derivative_degree_worst_case=d,
        exact_exceptional_bound=str(bound),
        exceptional_count_upper=ceil(bound),
        preliminary_exception_upper=((2*tail_degree-1)*H
                                     if tail_degree else H),
        ordinary_degree_upper=tail_degree,
        ordinary_challenge_degree_upper=H,
        joint_degree_upper=tail_joint+joint,
        generic_fiber_degree_upper=tail_degree+fiber,
        joint_degree_order_zero=tail_joint,
        joint_degree_order_one=joint,
        fiber_degree_order_zero=tail_degree,
        fiber_degree_order_one=fiber,
        degree_metadata_scope='worst actual derivative stage plus ordinary tail')


def hybrid_exceptional_bound_at_degree(
    n, k, A, B, derivative_degree_cap, H, actual_degree, L, ell=1,
    taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL,
):
    """New hybrid curve budget for a fixed actual degree and threshold.

    The actual message degree is always ``D=k-1``.  The partial derivative
    degree is bounded independently by ``derivative_degree_cap``; it is never
    replaced by the ambient ordinary-tail degree ``B``.
    """
    if not (n >= 2 and 2 <= k <= A <= n):
        raise ValueError('require n >= 2 and 2 <= k <= A <= n')
    if k == n:
        if A != n:
            raise ValueError('k=n forces A=n')
        return F(0)
    if not (B >= 0 and H >= 0 and ell >= 1):
        raise ValueError('require B,H >= 0 and ell >= 1')
    if not (0 <= derivative_degree_cap <= B):
        raise ValueError('require 0 <= derivative degree cap <= B')
    if not (0 <= actual_degree <= derivative_degree_cap):
        raise ValueError('actual degree exceeds derivative degree cap')
    if not (k <= L <= A):
        raise ValueError('require k <= L <= A')
    D = k - 1
    fiber, joint = _hybrid_stage_sums(
        D, B, H, actual_degree, ell, taylor_degree_model)
    _, tail = _ordinary_tail_minimum(
        n, D, A, B-actual_degree, H, ell
    )
    lambda_off = F(n-L+1, A-L+1)
    lambda_agreement = F(n-D, A-D)
    lambda_line = F(n-D, L-D)
    return (tail + lambda_off*lambda_agreement*joint
            +ell*(n-L)*lambda_line*fiber)


def _ordinary_tail_minimum(n, D, A, B, H, ell):
    """Optimize the ordinary tail independently of the regular stages."""
    if B == 0:
        return D+1, F(H)
    return minimize_convex_integer(
        D+1, A,
        lambda L: ordinary_exceptional_bound_at_threshold(
            n, D, A, B, H, L, ell))


def _hybrid_v2_transfer(
    n, k, A, B, M, H, ell,
    taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL,
):
    """Free-threshold hybrid curve transfer with ``max_d min_L`` order."""
    D = k - 1

    def at_degree(d):
        fiber, joint = _hybrid_stage_sums(
            D, B, H, d, ell, taylor_degree_model)
        tail_degree = B-d
        tail_L, tail = _ordinary_tail_minimum(
            n, D, A, tail_degree, H, ell
        )

        def objective(L):
            lambda_off = F(n-L+1, A-L+1)
            lambda_agreement = F(n-D, A-D)
            lambda_line = F(n-D, L-D)
            return (tail + lambda_off*lambda_agreement*joint
                    +ell*(n-L)*lambda_line*fiber)

        L, bound = minimize_convex_integer(k, A, objective)
        tail_joint = (ordinary_joint_degree(D, tail_degree, H, ell)
                      if tail_degree else 0)
        return dict(
            actual_derivative_degree=d,
            L=L,
            ordinary_tail_L=tail_L,
            exact_ordinary_tail_bound=str(tail),
            exact_exceptional_bound=str(bound),
            fiber_degree_order_one=fiber,
            joint_degree_order_one=joint,
            ordinary_degree_upper=tail_degree,
            joint_degree_order_zero=tail_joint)

    actual_degree_certificates = [at_degree(d) for d in range(M+1)]
    worst = max(actual_degree_certificates,
                key=lambda row: (F(row['exact_exceptional_bound']),
                                 -row['L'], row['actual_derivative_degree']))
    bound = F(worst['exact_exceptional_bound'])
    tail_degree = worst['ordinary_degree_upper']
    return dict(
        method=(('hybrid-free-threshold-v2-')
                + ('taylor-tight-v3-' if
                   taylor_degree_model == TIGHT_TAYLOR_DEGREE_MODEL else '')
                + ('curve' if ell > 1 else 'line')),
        theorem='free-threshold first-order curve transfer with ordinary tail',
        characteristic_strictly_greater_than=max(D, M),
        message_degree_upper=D,
        partial_derivative_degree_upper=M,
        fixed_polynomial_characteristic_guard=
            'p > max(k-1, actual derivative degree)',
        support_characteristic_guard=
            'p > max(k-1, partial derivative degree upper bound)',
        L=worst['L'],
        actual_derivative_degree_worst_case=worst['actual_derivative_degree'],
        actual_degree_certificates=actual_degree_certificates,
        optimization_order=('max_actual_degree_then_min_regular_threshold; '
                            'ordinary_tail_threshold_minimized_independently'),
        exact_exceptional_bound=str(bound),
        exceptional_count_upper=ceil(bound),
        preliminary_exception_upper=((2*tail_degree-1)*H
                                     if tail_degree else H),
        ordinary_degree_upper=tail_degree,
        ordinary_challenge_degree_upper=H,
        joint_degree_upper=(worst['joint_degree_order_zero']
                            +worst['joint_degree_order_one']),
        generic_fiber_degree_upper=(tail_degree
                                    +worst['fiber_degree_order_one']),
        joint_degree_order_zero=worst['joint_degree_order_zero'],
        joint_degree_order_one=worst['joint_degree_order_one'],
        fiber_degree_order_zero=tail_degree,
        fiber_degree_order_one=worst['fiber_degree_order_one'],
        degree_metadata_scope=('worst actual derivative degree after its own '
                               'free-threshold optimization'))


def _capped_transfer(
    n, k, A, B, M, H, ell,
    taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL,
):
    L, bound = best_threshold(
        n,k,A,B,H,M,ell,taylor_degree_model)
    J0,J1,F0,F1 = stage_budgets(
        k,B,M,H,ell,taylor_degree_model)
    D = max(k,2)-1
    return dict(
        method=(('capped-')
                + ('taylor-tight-v3-' if
                   taylor_degree_model == TIGHT_TAYLOR_DEGREE_MODEL else '')
                + ('curve' if ell > 1 else 'line')),
        theorem='direct capped first-order polynomial-family transfer',
        characteristic_strictly_greater_than=max(D, B),
        L=L,
        exact_exceptional_bound=str(bound),
        exceptional_count_upper=ceil(bound),
        preliminary_exception_upper=H,
        ordinary_degree_upper=None,
        ordinary_challenge_degree_upper=None,
        joint_degree_upper=J0+J1,
        generic_fiber_degree_upper=F0+F1,
        joint_degree_order_zero=J0,
        joint_degree_order_one=J1,
        fiber_degree_order_zero=F0,
        fiber_degree_order_one=F1,
        degree_metadata_scope='sum of capped order-zero and order-one stages')


def _list_alternatives(
    n, k, A, B, M, H,
    taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL,
):
    D = max(k,2)-1
    lam = F(n-D, A-D)
    _,_,legacy_tail,hybrid_fiber = stage_budgets(
        k,B,M,H,1,taylor_degree_model)
    result = {
        'legacy-stage-sum': dict(
            method='legacy-stage-sum',
            theorem='legacy capped stage-sum list bound',
            characteristic_strictly_greater_than=max(D,M),
            exact_list_bound=str(lam*hybrid_fiber+legacy_tail))
    }
    if k >= 2:
        hybrid = lam*hybrid_fiber+B-M
        result['hybrid-interleaved'] = dict(
            method='hybrid-interleaved',
            theorem='ordinary-tail first-order list plus extension-field interleaving',
            characteristic_strictly_greater_than=max(D,M),
            exact_list_bound=str(hybrid))
        if M == 0:
            result['ordinary-root'] = dict(
                method='ordinary-root',
                theorem='ordinary polynomial root count',
                characteristic_strictly_greater_than=0,
                exact_list_bound=str(F(B)))
        else:
            tau = first_order_taylor_exponent(D, taylor_degree_model)
            u = 1+tau*(B-1)
            v = min(u,tau*(M-1)+D)
            fiber = B*v+M*(u-v)
            ordinary_degree = max(B,(2*M-1)*B-M*M)
            sharp = lam*fiber+ordinary_degree
            result['sharp-squarefree-interleaved'] = dict(
                method=('sharp-squarefree-'
                        + ('taylor-tight-v3-' if
                           taylor_degree_model == TIGHT_TAYLOR_DEGREE_MODEL
                           else '')
                        + 'interleaved'),
                theorem='squarefree one-chart/resultant list plus extension-field interleaving',
                characteristic_strictly_greater_than=max(D,M),
                exact_list_bound=str(sharp),
                regular_fiber_degree_upper=fiber,
                ordinary_degree_upper=ordinary_degree)
    for item in result.values():
        item['list_size_upper'] = ceil(F(item['exact_list_bound']))
    return result


def _endpoint_certificate(n, k, A, m, M, mu, weighted, ell):
    """Direct all-characteristic constant/full-code certificate, if applicable."""
    if k == 1:
        exceptional = constant_code_exceptional_count(n, A, ell)
        list_size = constant_code_list_size(n, A)
        transfer_method = ('constant-code-incidence-curve' if ell > 1
                           else 'constant-code-incidence-line')
        theorem = ('constant-code pair-incidence bound' if A >= 2
                   else 'constant-code collision fallback')
    elif k == n and A == n:
        exceptional, list_size = 0, 1
        transfer_method = 'full-code-endpoint'
        theorem = 'full-code endpoint'
    else:
        return None
    transfer = dict(
        method=transfer_method,
        theorem=theorem,
        characteristic_strictly_greater_than=0,
        L=A,
        exact_exceptional_bound=str(F(exceptional)),
        exceptional_count_upper=exceptional,
        preliminary_exception_upper=exceptional,
        ordinary_degree_upper=None,
        ordinary_challenge_degree_upper=None,
        joint_degree_upper=0,
        generic_fiber_degree_upper=0,
        joint_degree_order_zero=0,
        joint_degree_order_one=0,
        fiber_degree_order_zero=0,
        fiber_degree_order_one=0,
        degree_metadata_scope='direct endpoint incidence count')
    list_record = dict(
        method=('constant-code-disjoint-agreement' if k == 1
                else 'full-code-unique-message'),
        theorem=('constant-code disjoint-agreement list bound' if k == 1
                 else 'full-code unique-message endpoint'),
        characteristic_strictly_greater_than=0,
        exact_list_bound=str(F(list_size)),
        list_size_upper=list_size)
    return dict(
        m=m, M=M, effective_M=min(M, mu), mu=mu,
        support='endpoint-direct; interpolation support unused',
        height=0, row_height=0, column_height=0,
        height_method='endpoint', dimension=0, local_rank_upper=0,
        column_degree_sum=0, source_jet_degree_sum=0,
        row_jet_degree_sum=0,
        L=A, joint_degree_upper=0, generic_fiber_degree_upper=0,
        joint_degree_order_zero=0, joint_degree_order_one=0,
        fiber_degree_order_zero=0, fiber_degree_order_one=0,
        selected_transfer_method=transfer_method,
        selected_transfer_theorem=theorem,
        selected_list_method=list_record['method'],
        selected_list_theorem=list_record['theorem'],
        degree_metadata_scope=transfer['degree_metadata_scope'],
        exceptional_count_upper=exceptional,
        exact_exceptional_bound=str(F(exceptional)),
        coefficient_n_squared=str(F(exceptional, n*n)),
        list_size_upper=list_size,
        exact_list_bound=str(F(list_size)),
        characteristic_strictly_greater_than=0,
        exceptional_characteristic_strictly_greater_than=0,
        list_characteristic_strictly_greater_than=0,
        ordinary_degree_upper=None,
        ordinary_challenge_degree_upper=None,
        transfer_alternatives={'endpoint': transfer},
        list_alternatives={'endpoint': list_record})


def certificate(
    n, k, A, m, M, mu, weighted=True, ell=1, method='best',
    taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL,
):
    if not (n>=2 and 1<=k<=A<=n and m>=1 and M>=0 and mu>=1 and ell>=1):
        raise ValueError('invalid certificate parameters')
    if taylor_degree_model not in TAYLOR_DEGREE_MODELS:
        raise ValueError(f'unknown Taylor degree model: {taylor_degree_model}')
    endpoint = _endpoint_certificate(n, k, A, m, M, mu, weighted, ell)
    if endpoint is not None:
        if method not in {'best', 'endpoint'}:
            raise ValueError(f'{method} transfer is unavailable for this endpoint')
        return endpoint
    if not k < A:
        raise ValueError('nonendpoint certificates require k < A')
    data=height_certificate(n,k,A,m,M,mu,weighted,ell)
    if data is None:return None
    if method not in {'best','capped','sharp','sharp-v2','hybrid','hybrid-v2',
                      'ordinary','ordinary-free'}:
        raise ValueError('unknown certificate method')
    h=data['height'];D=max(k,2)-1;effective_M=min(M,mu)
    transfers = {'capped':_capped_transfer(
        n,k,A,mu,effective_M,h,ell,taylor_degree_model)}
    eligible = k >= 2 and D <= n-2 and A >= D+1
    if eligible:
        if effective_M == 0:
            transfers['ordinary'] = _ordinary_curve_transfer(n,k,A,mu,h,ell)
            if method in {'best','ordinary-free'}:
                transfers['ordinary-free'] = _ordinary_free_threshold_transfer(
                    n,k,A,mu,h,ell)
        else:
            transfers['sharp'] = _sharp_transfer(
                n,k,A,mu,effective_M,h,ell,
                taylor_degree_model=taylor_degree_model)
            if method in {'best','sharp-v2'}:
                transfers['sharp-v2'] = _sharp_transfer(
                    n,k,A,mu,effective_M,h,ell,optimize_tail=True,
                    taylor_degree_model=taylor_degree_model)
            if method in {'best','hybrid-v2'}:
                transfers['hybrid-v2'] = _hybrid_v2_transfer(
                    n,k,A,mu,effective_M,h,ell,taylor_degree_model)
            if ell == 1:
                transfers['hybrid'] = _legacy_hybrid_transfer(
                    n,k,A,mu,effective_M,h,taylor_degree_model)
    lists = _list_alternatives(
        n,k,A,mu,effective_M,h,taylor_degree_model)
    if method == 'best':
        selected_transfer = min(transfers.values(), key=lambda x:(
            F(x['exact_exceptional_bound']),
            x['characteristic_strictly_greater_than'],x['method']))
        selected_list = min(lists.values(), key=lambda x:(
            F(x['exact_list_bound']),
            x['characteristic_strictly_greater_than'],x['method']))
    else:
        transfer_key = 'capped' if method == 'capped' else method
        if transfer_key not in transfers:
            raise ValueError(f'{method} transfer is unavailable for these parameters')
        selected_transfer = transfers[transfer_key]
        list_key = {'capped':('ordinary-root' if effective_M == 0
                              else 'legacy-stage-sum'),
                    'hybrid':'hybrid-interleaved',
                    'hybrid-v2':'hybrid-interleaved',
                    'ordinary':'ordinary-root',
                    'ordinary-free':'ordinary-root',
                    'sharp':'sharp-squarefree-interleaved',
                    'sharp-v2':'sharp-squarefree-interleaved'}[method]
        if list_key not in lists:
            raise ValueError(f'{method} list is unavailable for these parameters')
        selected_list = lists[list_key]
    bound=F(selected_transfer['exact_exceptional_bound'])
    selected_guard=max(selected_transfer['characteristic_strictly_greater_than'],
                       selected_list['characteristic_strictly_greater_than'])
    selected_degrees={key:selected_transfer[key] for key in [
        'L','joint_degree_upper','generic_fiber_degree_upper',
        'joint_degree_order_zero','joint_degree_order_one',
        'fiber_degree_order_zero','fiber_degree_order_one']}
    selected_scope={key:selected_transfer[key] for key in (
        'message_degree_upper','partial_derivative_degree_upper',
        'fixed_polynomial_characteristic_guard','support_characteristic_guard',
        'optimization_order') if key in selected_transfer}
    result = dict(
        m=m,M=M,effective_M=effective_M,mu=mu,
        support='derivative-weighted' if weighted else 'equal-weight',
        **data,**selected_degrees,**selected_scope,
        selected_transfer_method=selected_transfer['method'],
        selected_transfer_theorem=selected_transfer['theorem'],
        selected_list_method=selected_list['method'],
        selected_list_theorem=selected_list['theorem'],
        degree_metadata_scope=selected_transfer['degree_metadata_scope'],
        exceptional_count_upper=selected_transfer['exceptional_count_upper'],
        exact_exceptional_bound=selected_transfer['exact_exceptional_bound'],
        coefficient_n_squared=str(bound/F(n*n)),
        list_size_upper=selected_list['list_size_upper'],
        exact_list_bound=selected_list['exact_list_bound'],
        characteristic_strictly_greater_than=selected_guard,
        exceptional_characteristic_strictly_greater_than=
            selected_transfer['characteristic_strictly_greater_than'],
        list_characteristic_strictly_greater_than=
            selected_list['characteristic_strictly_greater_than'],
        ordinary_degree_upper=selected_transfer['ordinary_degree_upper'],
        ordinary_challenge_degree_upper=selected_transfer['ordinary_challenge_degree_upper'],
        transfer_alternatives=transfers,
        list_alternatives=lists)
    if taylor_degree_model == TIGHT_TAYLOR_DEGREE_MODEL:
        result['taylor_degree_model'] = taylor_degree_model
        result['taylor_common_exponent'] = first_order_taylor_exponent(
            D, taylor_degree_model)
        if D == 1:
            result['degree_one_taylor_chart'] = 'identity-pair'
    return result


def split_application_certificate(
    n, k, A, list_support, mca_support, ell=1,
    list_method='best', mca_method='best', weighted=True,
    taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL,
):
    """Combine distinct list and MCA support records without losing provenance."""
    list_record = certificate(
        n, k, A, *list_support, weighted=weighted, ell=1, method=list_method,
        taylor_degree_model=taylor_degree_model,
    )
    mca_record = certificate(
        n, k, A, *mca_support, weighted=weighted, ell=ell, method=mca_method,
        taylor_degree_model=taylor_degree_model,
    )
    if list_record is None or mca_record is None:
        return None
    return dict(
        n=n, k=k, A=A, batch_degree=ell,
        list_support_record=list_record,
        mca_support_record=mca_record,
        list_size_upper=list_record['list_size_upper'],
        exceptional_count_upper=mca_record['exceptional_count_upper'],
        characteristic_strictly_greater_than=max(
            list_record['list_characteristic_strictly_greater_than'],
            mca_record['exceptional_characteristic_strictly_greater_than']))


def search(
    n, k, A, max_m=32, mu_factor=3,
    taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL,
):
    # Search both supports; every available transfer bound is at least h.
    best = None
    for m in range(1, max_m + 1):
        for M in range(m // 2 + 1):
            for mu in range(max(1, M), mu_factor * m + 1):
                for weighted in (True, False):
                    N, r = support_counts(n, k, A, m, M, mu, weighted)
                    if N <= n * r:
                        continue
                    h, column_weight = kernel_height(n,k,A,m,M,mu,r,weighted)
                    if best is not None and h >= best['exceptional_count_upper']:
                        continue
                    c = certificate(
                        n, k, A, m, M, mu, weighted,
                        taylor_degree_model=taylor_degree_model)
                    if best is None or F(c['exact_exceptional_bound']) < F(best['exact_exceptional_bound']):
                        best = c
    return best


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--n', type=int, required=True)
    p.add_argument('--k', type=int, required=True)
    p.add_argument('--agreement', type=int, required=True)
    p.add_argument('--max-m', type=int, default=32)
    p.add_argument('--mu-factor', type=int, default=3)
    p.add_argument('--security-bits', type=int, default=128)
    p.add_argument('--certificate', type=int, nargs=3, metavar=('MUL', 'CAP', 'JET'))
    p.add_argument('--equal-weight', action='store_true')
    p.add_argument('--method', choices=(
        'best', 'capped', 'sharp', 'sharp-v2', 'hybrid', 'hybrid-v2',
        'ordinary', 'ordinary-free', 'endpoint'), default='best')
    p.add_argument('--taylor-degree-model', choices=TAYLOR_DEGREE_MODELS,
                   default=LEGACY_TAYLOR_DEGREE_MODEL,
                   help=('versioned Taylor degree accounting; the default reproduces '
                         'historical certificates'))
    args = p.parse_args()
    if not (2 <= args.n and 1 <= args.k <= args.agreement <= args.n):
        p.error('require n >= 2 and 1 <= k <= agreement <= n')
    if args.max_m < 1 or args.mu_factor < 1 or args.security_bits < 0:
        p.error('positive search limits and nonnegative security bits required')
    if args.certificate:
        m,M,mu=args.certificate
        if not (m>=1 and M>=0 and mu>=1): p.error('invalid certificate parameters')
        result=certificate(args.n,args.k,args.agreement,m,M,mu,not args.equal_weight,
                           method=args.method,
                           taylor_degree_model=args.taylor_degree_model)
    else:
        result=search(args.n,args.k,args.agreement,args.max_m,args.mu_factor,
                      args.taylor_degree_model)
    if result:
        result['minimum_field_cardinality_for_line_term'] = result['exceptional_count_upper'] * 2**args.security_bits
        result['sufficient_log2_q'] = (result['minimum_field_cardinality_for_line_term']-1).bit_length()
    print(json.dumps(dict(n=args.n,k=args.k,A=args.agreement,security_bits=args.security_bits,
                         search_max_m=None if args.certificate else args.max_m,
                         search_mu_factor=None if args.certificate else args.mu_factor,
                         certificate=result),indent=2))

if __name__ == '__main__': main()
