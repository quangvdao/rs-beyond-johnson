#!/usr/bin/env python3
"""Bounded search for ABF constrained-combination plus spot-check error.

Certifies (E + interleaved_list)/q + (A/n)^t <= 2^-security_bits.
Field exponents b mean a LOWER BOUND q >= 2^b; admissible characteristic
must separately exceed the guard recorded in each selected certificate. This
is the interactive oracle protocol, not a complete hash/Fiat-Shamir SNARK
error calculation.
"""
import argparse
from fractions import Fraction as F
import json
from math import log2,ceil as mathceil
import tune_first_order_mca as scalar


def certificate(n,k,A,m,M,mu,method='best'):
    c=scalar.certificate(n,k,A,m,M,mu,method=method)
    return None if c is None else dict(c,numerator=c['exceptional_count_upper']+c['list_size_upper'])


def split_support_certificate(
    n, k, A, list_support, mca_support, list_method='best', mca_method='best'
):
    """Protocol record using separate supports for list and MCA bounds."""
    c = scalar.split_application_certificate(
        n, k, A, list_support, mca_support,
        list_method=list_method, mca_method=mca_method
    )
    if c is None:
        return None
    return dict(c, numerator=(c['exceptional_count_upper']
                              +c['list_size_upper']))


def extends_saved_certificate(saved, fresh):
    """Whether an expanded fresh certificate preserves an old snapshot."""
    return fresh is not None and all(fresh.get(key) == value
                                     for key, value in saved.items())


def minimum_queries(n,A,numerator,q_lower,security_bits):
    residual=F(1,2**security_bits)-F(numerator,q_lower)
    if residual<=0 or A>=n:return None
    base=F(A,n)
    # Floating point supplies only a seed; exact comparisons certify t.
    t=max(1,mathceil((log2(residual.numerator)-log2(residual.denominator))/log2(float(base))))
    while base**t>residual:t+=1
    while t>1 and base**(t-1)<=residual:t-=1
    return t


def support_pool():
    pool=set()
    for m in range(2,65):
        for M in range(max(0,round(.4*m)-1),min(m//2,round(.4*m)+1)+1):
            for mu in range(max(1,round(1.85*m)-2),round(1.85*m)+3):pool.add((m,M,mu))
    # Include ordinary (order-zero) supports for a fair nearby baseline.
    for m in range(1,129):
        for mu in range(max(1,2*m-2),2*m+3):pool.add((m,0,mu))
    pool.update([(12,5,23),(10,4,19),(24,10,45),(48,18,88),(96,36,175),
                 (256,112,459),(384,168,688),(3072,1344,5504)])
    return sorted(pool)


def adaptive_support_pool(n,k,A,max_jet_degree=8192):
    """Rate-dependent envelope heuristic; every returned support is checked."""
    D=max(k,2)-1
    result=[]
    for m in list(range(2,97))+[128,192,256,384,512,1024,2048]:
        central=min(m//2,3*(n-A)*m//(4*n-2*k))
        for M in range(max(0,central-2),min(m//2,central+2)+1):
            top=(m*A+M-1)//D
            for mu in range(max(1,top-4),min(top,max_jet_degree)+1):
                result.append((m,M,mu))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--n',type=int,default=2**20);p.add_argument('--k',type=int,default=2**18)
    p.add_argument('--field-exponents',type=int,nargs='+',default=[192,196,200,208,224,256])
    p.add_argument('--field-cardinality',type=int,help='Use this actual q instead of the field-exponent list')
    p.add_argument('--security-bits',type=int,default=128)
    p.add_argument('--support-profile',choices=['reference','adaptive'],default='reference')
    p.add_argument('--max-jet-degree',type=int,default=8192)
    p.add_argument('--min-gap',default='0.2195');p.add_argument('--max-gap',default='0.255')
    p.add_argument('--gap-step',default='0.0005');p.add_argument('--output')
    a=p.parse_args();n,k=a.n,a.k;start,end,step=map(F,(a.min_gap,a.max_gap,a.gap_step))
    if not (n>=2 and 1<=k<n and 0<start<=end and step>0 and a.security_bits>0 and a.max_jet_degree>0 and all(b>0 for b in a.field_exponents) and (a.field_cardinality is None or a.field_cardinality>1)):
        p.error('invalid parameters')
    pool=support_pool() if a.support_profile=='reference' else [];frontier={b:None for b in ([None] if a.field_cardinality else a.field_exponents)};rows=[]
    gap=start
    while gap<=end:
        A=scalar.ceil(k+gap*n)
        if A>=n:break
        best=None
        if a.support_profile=='adaptive':pool=adaptive_support_pool(n,k,A,a.max_jet_degree)
        for m,M,mu in pool:
            c=certificate(n,k,A,m,M,mu)
            if c and (best is None or c['numerator']<best['numerator']):best=c
        if best:
            row=dict(gap=str(gap),A=A,certificate=best);rows.append(row)
            for b in frontier:
                q0=a.field_cardinality if a.field_cardinality else 2**b
                t=minimum_queries(n,A,best['numerator'],q0,a.security_bits)
                if t is None:continue
                normalized=(F(best['numerator'],q0)+F(A,n)**t)*2**a.security_bits
                value=dict(**row,queries=t,field_exponent=b,field_lower_bound=q0,normalized_error=str(normalized),
                           normalized_error_decimal=float(normalized))
                old=frontier[b]
                if old is None or (t,normalized)<(old['queries'],F(old['normalized_error'])):frontier[b]=value
        gap+=step
    result=dict(n=n,k=k,security_bits=a.security_bits,agreement_spot_bound='A/n',
                search=dict(min_gap=str(start),max_gap=str(end),gap_step=str(step),support_profile=a.support_profile,
                            max_jet_degree=a.max_jet_degree,supports=pool if a.support_profile=='reference' else None,
                            adaptive_rule='m=2..96 plus128,192,256,384,512,1024,2048; M=min(floor(m/2),floor(3(n-A)m/(4n-2k))) plus -2..2 clipped 0..m/2; mu=floor((mA+M-1)/(max(k,2)-1)) plus -4..0 clipped 1..max_jet_degree' if a.support_profile=='adaptive' else None),
                frontier=list(frontier.values()),per_gap=rows)
    output=json.dumps(result,indent=2)+'\n'
    if a.output:
        from pathlib import Path
        Path(a.output).write_text(output)
        print(json.dumps(dict(frontier=result['frontier'],support_count=len(pool),gap_count=len(rows)),indent=2))
    else:print(output)

if __name__=='__main__':main()
