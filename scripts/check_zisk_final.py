#!/usr/bin/env python3
"""Exact parameter-only replacement for ZisK's compressed final STARK.

Each original phase keeps its separate 128-bit allocation. The field, nested
powers challenges, folding schedule, and 22 grinding bits are unchanged.
The legacy proof-byte fields count the pinned release's unencoded u64
field/hash vector, not its native serialized proof file. Native measured
sizes and verification evidence are in experiments/zisk-compressed-final/.
"""
from fractions import Fraction as F
import argparse
import json
from pathlib import Path
from tune_first_order_mca import (
    certificate,
    LEGACY_TAYLOR_DEGREE_MODEL,
    TIGHT_TAYLOR_DEGREE_MODEL,
)
from zisk_scope_audit import ARTIFACT_METADATA, Q, P, raw_proof_bytes, bits

TARGET = F(1, 2**128)


def check():
    meta = next(m for m in ARTIFACT_METADATA if m['name'] == 'vadcop_final_compressed')
    n, k, A = 524288, 32768, 124136
    support = (10, 6, 37)
    assert (2**meta['n_bits_ext'], 2**meta['n_bits'], meta['pow_bits']) == (n, k, 22)
    assert meta['opening_group_sizes'] == [2, 3, 104, 25, 1]
    assert meta['steps'] == [19, 16, 13, 10]
    assert P > max(k-1, support[2]) and A*A < n*(k-1)
    components = []
    legacy_capped_components = []
    for degree in [103, 4]:
        c = certificate(
            n, k, A, *support, ell=degree,
            taylor_degree_model=TIGHT_TAYLOR_DEGREE_MODEL)
        assert c is not None
        components.append(dict(degree=degree, certificate=c))
        legacy_capped = certificate(
            n, k, A, *support, ell=degree, method='capped',
            taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL)
        assert legacy_capped is not None
        legacy_capped_components.append(legacy_capped)
    batch = F(sum(c['certificate']['exceptional_count_upper'] for c in components), Q)
    capped_batch_count = sum(
        c['exceptional_count_upper'] for c in legacy_capped_components)
    assert capped_batch_count == 13338599545603089507
    capped_batch = F(capped_batch_count, Q)
    assert batch < TARGET
    assert capped_batch < TARGET
    folds = []
    ni, ki = n, k
    for _ in range(3):
        ni //= 8
        ki //= 8
        Ai = (A*ni+n-1)//n
        c = certificate(
            ni, ki, Ai, *support, ell=7,
            taylor_degree_model=TIGHT_TAYLOR_DEGREE_MODEL)
        assert c is not None
        error = F(c['exceptional_count_upper'], Q)
        legacy_capped = certificate(
            ni, ki, Ai, *support, ell=7, method='capped',
            taylor_degree_model=LEGACY_TAYLOR_DEGREE_MODEL)
        assert legacy_capped is not None
        capped_error = F(legacy_capped['exceptional_count_upper'], Q)
        assert error < TARGET
        assert capped_error < TARGET
        folds.append(dict(n=ni, k=ki, A=Ai, certificate=c, error=str(error),
                          bits=bits(error),legacy_capped_error=str(capped_error),
                          legacy_capped_bits=bits(capped_error)))
    query = F(A, n)**51 / 2**22
    assert query < TARGET
    assert F(A, n)**50 / 2**22 >= TARGET
    assert F(k-1, n)**52 / 2**44 > TARGET**2
    assert F(k-1, n)**53 / 2**44 <= TARGET**2
    old, new = raw_proof_bytes(meta, 54), raw_proof_bytes(meta, 51)
    assert (old, new, old-new) == (254032, 242272, 11760)
    return dict(n=n, k=k, A=A, queries=51, grinding_bits=22, support=support,
                components=components, nested_error=str(batch), nested_bits=bits(batch),
                legacy_capped_nested_error=str(capped_batch),
                legacy_capped_nested_bits=bits(capped_batch),
                folds=folds, query_error=str(query), query_bits=bits(query),
                finite_johnson_query_floor=53, original_proof_bytes=old,
                revised_proof_bytes=new, bytes_saved=old-new)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compare-only', action='store_true',
                        help='run exact checks without rewriting the stored report')
    args = parser.parse_args()
    result = check()
    if not args.compare_only:
        target = Path(__file__).parent/'examples/zisk-final.json'
        target.write_text(json.dumps(result, indent=2)+'\n')
    print('ZisK: 54 -> 51 queries; 11,760 field/hash bytes saved; exact phase checks pass.')
