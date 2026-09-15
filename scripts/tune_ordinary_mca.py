#!/usr/bin/env python3
"""Exact finite ordinary-interpolation MCA tuning.

Uses the manuscript's characteristic-free ordinary transfer. Powers curves use
its dimension-one lifted-curve extension, documented with the reopening report;
this extension is a mathematical derivation, not a Lean-verified interface.
This is a coding certificate, not a complete protocol soundness calculation.
"""
from fractions import Fraction as F
from math import log2
import argparse
import json
from pathlib import Path
import sys

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from ordinary_mca_budget import (
    coarse_joint_degree,
    exceptional_bound as ordinary_exceptional_bound,
    joint_degree as ordinary_joint_degree,
    psi as ordinary_psi,
)


def ceil(x):
    return -(-x.numerator // x.denominator)


def certificate(n, k, A, m, mu, ell=1):
    """Support i+D*j<m*A, 0<=j<=mu, Z-degree<=H-ell*j.

    Translation by a degree-ell received curve preserves ell*j+Z-degree.
    Each local row with Y-degree b and X-degree a<m-b has degree <=H-ell*b.
    The minimal admissible H below follows from this exact scalar count.
    """
    if not (2 <= k < n and k <= A <= n and m >= 1 and mu >= 1 and ell >= 1):
        return None
    D = k - 1
    if D*mu >= m*A:
        return None
    N = (mu+1)*m*A - D*mu*(mu+1)//2
    N1 = m*A*mu*(mu+1)//2 - D*mu*(mu+1)*(2*mu+1)//6
    b = min(mu, m-1)
    r = (b+1)*m - b*(b+1)//2
    r1 = m*b*(b+1)//2 - b*(b+1)*(2*b+1)//6
    surplus, moment = N-n*r, N1-n*r1
    H = ell*mu
    if surplus > 0:
        H = max(H, (ell*moment)//surplus)
    elif (H+1)*surplus <= ell*moment:
        return None
    variables = (H+1)*N - ell*N1
    equations = n*((H+1)*r - ell*r1)
    if variables <= equations:
        return None
    theta = F(n-D, A-D)
    joint = ordinary_joint_degree(D, mu, H, ell)
    E = ordinary_exceptional_bound(n, D, A, mu, H, ell)
    coarse = ((2*mu-1)*H + theta*coarse_joint_degree(D,mu,H,ell)
              +ell*(n-D-1)*mu)
    return dict(n=n,k=k,A=A,m=m,mu=mu,ell=ell,H=H,
                variables=variables,equations=equations,surplus=variables-equations,
                list_bound=mu,exceptional_bound=str(E),exceptional_count=E.numerator//E.denominator,
                ordinary_psi=ordinary_psi(D,mu),joint_degree=joint,
                coarse_bound=str(coarse),
                transfer='ordinary line theorem' if ell==1 else 'derived ordinary powers extension')


def frontier(n,k,A,max_m=128,ell=1):
    """Pareto frontier in list bound and exceptional count over bounded m search."""
    best_by_mu = {}
    for m in range(1,max_m+1):
        for mu in range(1,(m*A-1)//(k-1)+1):
            c=certificate(n,k,A,m,mu,ell)
            if c is not None:
                old=best_by_mu.get(mu)
                if old is None or (c['exceptional_count'],c['H'],m)<(old['exceptional_count'],old['H'],old['m']):
                    best_by_mu[mu]=c
    result=[]
    best=None
    for mu,c in sorted(best_by_mu.items()):
        if best is None or c['exceptional_count']<best:
            result.append(c);best=c['exceptional_count']
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['n','k','agreement']:
        p.add_argument('--'+name,type=int,required=True)
    p.add_argument('--max-m',type=int,default=128)
    p.add_argument('--batch-degree',type=int,default=1)
    p.add_argument('--field-size',type=int)
    p.add_argument('--output')
    a=p.parse_args();rows=frontier(a.n,a.k,a.agreement,a.max_m,a.batch_degree)
    if a.field_size:
        for c in rows:
            err=F(c['exceptional_count'],a.field_size)
            c['mca_probability_bound']=str(err)
            c['mca_bits']=log2(err.denominator)-log2(err.numerator) if err else None
    result=dict(search_max_m=a.max_m,frontier=rows)
    out=json.dumps(result,indent=2)+'\n'
    if a.output:
        with open(a.output,'w') as f:f.write(out)
    else: print(out,end='')

if __name__=='__main__':main()
