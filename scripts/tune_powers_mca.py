#!/usr/bin/env python3
"""Exact finite powers-MCA certificates from the proved lifted-family transfer.

Produces a full-agreement exceptional count, not a full FRI/WHIR security bound.
"""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
import tune_first_order_mca as scalar


def certificate(n,k,A,m,M,mu,ell,method='best'):
    """Use the same finite engine for lines and polynomial received curves."""
    c=scalar.certificate(n,k,A,m,M,mu,ell=ell,method=method)
    return None if c is None else dict(n=n,k=k,A=A,batch_degree=ell,**c)


def split_support_certificate(
    n, k, A, list_support, mca_support, ell,
    list_method='best', mca_method='best'
):
    """Polynomial-curve certificate with explicit list/MCA support records."""
    c = scalar.split_application_certificate(
        n, k, A, list_support, mca_support, ell,
        list_method=list_method, mca_method=mca_method
    )
    return c


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--n',type=int,required=True);p.add_argument('--k',type=int,required=True)
    p.add_argument('--agreement',type=int,required=True)
    p.add_argument('--certificate',type=int,nargs=3,metavar=('m','M','mu'),required=True)
    p.add_argument('--batch-degree',type=int,required=True)
    p.add_argument('--method', choices=(
        'best', 'capped', 'sharp', 'hybrid-v2',
        'ordinary', 'ordinary-free', 'endpoint'), default='best')
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    try: result=certificate(args.n,args.k,args.agreement,*args.certificate,
                            args.batch_degree,args.method)
    except ValueError as e: p.error(str(e))
    content=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(content)
    else:print(content,end='')

if __name__=='__main__':main()
