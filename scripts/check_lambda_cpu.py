#!/usr/bin/env python3
"""Exact CPU specialization of the manuscript's first-order MCA bound.

This checks the sum of the changed CPU-table error terms, with the existing
powers batching, twenty grinding bits, and the two early evaluations proved
in the manuscript. It is not a verifier implementation or a runtime benchmark.
"""
from fractions import Fraction as F
import json
from pathlib import Path
from check_lambda_table_scope import evaluate, TABLE_BY_NAME, Q, P
from tune_first_order_mca import certificate, TIGHT_TAYLOR_DEGREE_MODEL

PROFILE = dict(n=65536, A=45690, m=32, M=9, mu=44)
TARGET = F(1, 2**128)


def check():
    n, A = PROFILE['n'], PROFILE['A']
    T = n // 2
    result = evaluate(TABLE_BY_NAME['CPU'], PROFILE)
    assert result['status'] == 'certified' and result['queries'] == 208
    assert result['grinding_bits'] == 20 and result['anchor_count'] == 2
    assert result['powers_degree'] == 50 and result['anchor_width'] == 38
    # Two anchors give reconstruction dimension T+3.
    assert P > max(T+2, PROFILE['M'])
    assert F(result['total_changed_component_error']) < TARGET
    fixed = F(result['fixed_error'])
    assert fixed + F(A, n)**207 / 2**20 >= TARGET
    assert result['initial_certificate']['exceptional_count_upper'] == 2083741775464763888
    # Even the finite Johnson boundary needs 216 queries under this accounting.
    assert F(T-1, n)**215 / 2**40 > TARGET**2
    assert F(T-1, n)**216 / 2**40 <= TARGET**2
    result['support'] = PROFILE
    result['fold_certificates'] = []
    previous_A = A
    ni = T
    while ni >= 256:
        Ai = (A*ni+n-1)//n
        assert 2*Ai >= previous_A
        c = certificate(
            ni, ni//2, Ai, PROFILE['m'], PROFILE['M'], PROFILE['mu'],
            taylor_degree_model=TIGHT_TAYLOR_DEGREE_MODEL)
        assert c is not None
        result['fold_certificates'].append(dict(n=ni, k=ni//2, A=Ai, certificate=c))
        previous_A = Ai
        ni //= 2
    assert len(result['fold_certificates']) == 8
    result['raw_proof_bytes_original'] = 4640 + 219*5256
    result['raw_proof_bytes_revised'] = 4640 + 208*5256 + 1824
    assert result['net_field_and_hash_bytes'] == 55992
    old_distinct = T*(1-F(T-1, T)**219)
    new_distinct = T*(1-F(T-1, T)**208)
    expected_saving = 5256*(old_distinct-new_distinct)-1824
    result['expected_deduplicated_saving_exact'] = str(expected_saving)
    result['expected_deduplicated_saving_bytes'] = float(expected_saving)
    return result


if __name__ == '__main__':
    result = check()
    target = Path(__file__).parent/'examples/lambda-cpu.json'
    target.write_text(json.dumps(result, indent=2)+'\n')
    print('CPU: 219 -> 208 queries; 55,992 field/hash bytes saved; exact error checks pass.')
