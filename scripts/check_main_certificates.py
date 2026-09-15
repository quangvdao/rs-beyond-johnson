#!/usr/bin/env python3
"""Read-only principal exact certificate and application report.

Run from the repository root with::

    python3 scripts/check_main_certificates.py

The checker reads vendored legacy snapshots from the pinned manuscript commit,
exercises the versioned free-threshold evaluators on bounded exact cases, and
calls the read-only entry points of selected application checkers.  It never
writes a certificate or application report.
"""

from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_lambda_cpu as lambda_cpu  # noqa: E402
import check_lambda_measurements as lambda_measurements  # noqa: E402
import check_provekit_applications as provekit  # noqa: E402
import check_zisk_final as zisk  # noqa: E402
import ordinary_mca_budget as ordinary  # noqa: E402
import tune_combination_protocol as combination  # noqa: E402
import tune_first_order_mca as first_order  # noqa: E402
import tune_powers_mca as powers  # noqa: E402


LEGACY_COMMIT = '8972b99c703801c95271e85fab79c61e6f7854b2'


def _base_json(path):
    return json.loads(
        (SCRIPTS / 'baselines' / Path(path).name).read_text()
    )


def _json_hashes():
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((SCRIPTS / 'examples').rglob('*.json'))
    }


def check_legacy_snapshots():
    checked = []
    for filename in (
        'combination-protocol-quarter-rate.json',
        'combination-protocol-half-rate.json',
        'larger-domain-affine-screens.json',
    ):
        data = _base_json(f'scripts/examples/{filename}')
        rows = data.get('frontier', data.get('rows'))
        for row in rows:
            saved = row['certificate']
            fresh = combination.certificate(
                row.get('n', data.get('n')), row.get('k', data.get('k')),
                row['A'], saved['m'], saved['M'], saved['mu'], method='capped'
            )
            assert combination.extends_saved_certificate(saved, fresh)
            checked.append(f'{filename}:{row.get("gap", row["A"])}')

    data = _base_json('scripts/examples/beyond-johnson-powers.json')
    for row in data['rows']:
        saved = row['certificate']
        fresh = powers.certificate(
            *(saved[key] for key in
              ('n','k','A','m','M','mu','batch_degree')), method='capped'
        )
        assert combination.extends_saved_certificate(saved, fresh)
        checked.append(f'beyond-johnson-powers.json:{row["gap"]}')
    return checked


def check_new_evaluators():
    pointwise = 0
    for n,k,A in ((8,2,4),(12,3,7),(12,6,11),(20,19,20)):
        for B in (1,3,6):
            for M in (0,min(2,B),B):
                for H in (0,1,4):
                    for ell in (1,3):
                        for d in range(M+1):
                            for L in {k,A,(k+A)//2}:
                                new = first_order.hybrid_exceptional_bound_at_degree(
                                    n,k,A,B,M,H,d,L,ell)
                                legacy = first_order.transfer(
                                    n,k,A,B,H,L,M,ell)
                                assert new <= legacy
                                pointwise += 1

    # Independently enumerate both finite thresholds: the regular-family
    # threshold does not constrain the ordinary tail's choice.
    for n, k, A in ((8, 2, 4), (12, 3, 7), (12, 6, 11), (20, 3, 20)):
        for B, M, H in ((1, 1, 0), (3, 2, 1), (6, 3, 4)):
            for ell in (1, 3):
                new = first_order._sharp_transfer(
                    n, k, A, B, M, H, ell, optimize_tail=True)
                old = first_order._sharp_transfer(n, k, A, B, M, H, ell)
                D = k - 1
                candidates = []
                for L in range(k, A + 1):
                    for L0 in range(k, A + 1):
                        tail = ordinary.exceptional_bound_at_threshold(
                            n, D, A, new['ordinary_degree_upper'],
                            new['ordinary_challenge_degree_upper'], L0, ell)
                        value = (tail + F(n-L+1, A-L+1)*F(n-D, A-D)
                                 *new['joint_degree_order_one']
                                 +ell*(n-L)*F(n-D, L-D)
                                 *new['fiber_degree_order_one'])
                        candidates.append(value)
                assert F(new['exact_exceptional_bound']) == min(candidates)
                assert F(new['exact_exceptional_bound']) <= F(old['exact_exceptional_bound'])

    optimized = []
    for ell in (1,3,7):
        old = first_order.certificate(
            20,4,15,3,3,8,ell=ell,method='capped')
        new = first_order.certificate(
            20,4,15,3,3,8,ell=ell,method='hybrid-v2')
        assert F(new['exact_exceptional_bound']) <= F(old['exact_exceptional_bound'])
        optimized.append({
            'ell': ell,
            'legacy': old['exact_exceptional_bound'],
            'new': new['exact_exceptional_bound'],
        })

    # A concrete powers-batching application support, evaluated without
    # changing the stored ZisK record.
    application_dominance = []
    for ell in (103,4):
        old = first_order.certificate(
            524288,32768,124136,10,6,37,ell=ell,method='capped',
            taylor_degree_model=first_order.LEGACY_TAYLOR_DEGREE_MODEL)
        new = first_order.certificate(
            524288,32768,124136,10,6,37,ell=ell,method='hybrid-v2',
            taylor_degree_model=first_order.TIGHT_TAYLOR_DEGREE_MODEL)
        assert F(new['exact_exceptional_bound']) <= F(old['exact_exceptional_bound'])
        application_dominance.append({
            'application': 'ZisK final compressed', 'ell': ell,
            'legacy_count': old['exceptional_count_upper'],
            'new_count': new['exceptional_count_upper'],
        })

    assert ordinary.exceptional_bound_at_threshold(20,3,15,0,11,4,7) == 11
    endpoints = {
        'constant_A1': first_order.certificate(20,1,1,1,0,1,ell=3),
        'constant_A5': first_order.certificate(20,1,5,1,0,1,ell=3),
        'full_code': first_order.certificate(20,20,20,1,0,1,ell=7),
    }
    assert (endpoints['constant_A1']['exceptional_count_upper'],
            endpoints['constant_A5']['exceptional_count_upper'],
            endpoints['full_code']['exceptional_count_upper']) == (570,142,0)

    k2_list = first_order.height_certificate(
        64,2,18,12,4,22,weighted=False)
    k2_mca = first_order.height_certificate(
        64,2,18,12,4,23,weighted=False)
    assert (k2_list['dimension'],
            k2_list['dimension']-64*k2_list['local_rank_upper'],
            k2_list['row_height'],k2_list['column_height'],k2_list['height']) \
        == (21425,2225,68,95,68)
    assert (k2_mca['dimension'],
            k2_mca['dimension']-64*k2_mca['local_rank_upper'],
            k2_mca['row_height'],k2_mca['column_height'],k2_mca['height']) \
        == (22390,3190,54,72,54)
    assert k2_list['height'] <= 276 and k2_mca['height'] <= 276
    split = first_order.split_application_certificate(
        20,4,15,(2,0,5),(3,1,8),ell=3,mca_method='hybrid-v2')
    assert split['list_support_record']['M'] != split['mca_support_record']['M']
    strict_best = first_order.certificate(5,2,4,2,1,3)
    assert strict_best['selected_transfer_method'] == \
        'hybrid-free-threshold-v2-line'
    strict_bound = F(strict_best['exact_exceptional_bound'])
    assert all(
        strict_bound <= F(row['exact_exceptional_bound'])
        for row in strict_best['transfer_alternatives'].values())
    return {
        'pointwise_comparisons': pointwise,
        'optimized_comparisons': optimized,
        'application_dominance': application_dominance,
        'k2_uniform_supports': {
            'list_mu22': {
                'dimension': 21425, 'rank': 300, 'surplus': 2225,
                'row_height': 68, 'column_height': 95, 'height': 68,
            },
            'mca_mu23': {
                'dimension': 22390, 'rank': 300, 'surplus': 3190,
                'row_height': 54, 'column_height': 72, 'height': 54,
            },
            'uniform_height_upper': 276,
        },
        'distinct_support_example': {
            'list_size_upper': split['list_size_upper'],
            'exceptional_count_upper': split['exceptional_count_upper'],
        },
        'default_best_strict_v2_case': {
            'parameters': [5,2,4,2,1,3],
            'selected_transfer_method':
                strict_best['selected_transfer_method'],
            'exact_exceptional_bound': strict_best['exact_exceptional_bound'],
        },
    }


def check_applications():
    zisk_result = zisk.check()
    # Pinned native sampler: 16 low-63-bit field words for 51 19-bit
    # indices, plus one field output for the grinding predicate. This
    # bounds extraction bias under independent uniform field outputs;
    # it does not establish a concrete-hash pseudorandomness claim.
    zisk_scope = json.loads((SCRIPTS / 'examples' /
                            'zisk-full-scope-2026-09-07.json').read_text())
    assert zisk_scope['source']['proofman_commit'] == (
        '0f3fef8cd1897df469532996e72e0c84ef69d6fb')
    compressed = next(record for record in zisk_scope['artifact_inventory']
                      if record['name'] == 'vadcop_final_compressed')
    assert (compressed['n_bits_ext'], compressed['pow_bits'],
            compressed['transcript_arity']) == (19, 22, 4)
    # Arity four uses width 16 for the query transcript, distinct from
    # the direct width-8 grinding permutation at this source pin.
    sampler_words = (51 * compressed['n_bits_ext'] + 62) // 63
    assert sampler_words == 16
    goldilocks_prime = 2**64 - 2**32 + 1
    zisk_corrected_query = (
        F(124136, 2**19)**51 * F(2**42, goldilocks_prime)
        * F(2**64, goldilocks_prime)**sampler_words
    )
    assert zisk_corrected_query < F(1, 2**128)
    lambda_result = lambda_cpu.check()
    lambda_measured = lambda_measurements.check()
    passport = provekit.check_passport()
    passport_internal = provekit.check_passport_internal()
    goldilocks = provekit.check_goldilocks()
    # Sharper analysis of the existing second Goldilocks code. Keep the
    # benchmark's frozen certificate and measurements intact; list cardinality
    # permits flooring the exact rational bound used in the paper.
    goldilocks_second = first_order.certificate(
        2048,128,453,38,23,133,method='sharp',
        taylor_degree_model=first_order.TIGHT_TAYLOR_DEGREE_MODEL)
    goldilocks_exact = F(goldilocks_second['exact_list_bound'])
    assert goldilocks_exact == F(2659384185,326)
    goldilocks_list = goldilocks_exact.numerator // goldilocks_exact.denominator
    assert goldilocks_list == 8157620
    goldilocks_stage_exact = F(
        goldilocks_second['list_alternatives']['legacy-stage-sum'][
            'exact_list_bound'])
    assert goldilocks_stage_exact == F(15314557817,163)
    goldilocks_stage_list = -(
        -goldilocks_stage_exact.numerator // goldilocks_stage_exact.denominator)
    assert goldilocks_stage_list == 93954343
    goldilocks_collision = F(
        goldilocks_list*(goldilocks_list-1)//2*1023,
        (2**64-2**32+1)**3)
    assert goldilocks_collision < F(1,2**137)
    goldilocks_collision_bits = zisk.bits(goldilocks_collision)
    assert 137.081975 < goldilocks_collision_bits < 137.081977
    assert zisk_result['bytes_saved'] == 11760
    assert lambda_result['net_field_and_hash_bytes'] == 55992
    assert passport['expected_raw_saving'] > 47000
    assert passport_internal['expected_full_raw_saving'] > 79000
    assert goldilocks['expected_raw_saving']['24']['bytes'] > 24000
    return {
        'ZisK_saved_bytes': zisk_result['bytes_saved'],
        'LambdaVM_measurement': lambda_measured,
        'Passport_expected_saved_bytes': passport['expected_raw_saving'],
        'Passport_full_expected_saved_bytes':
            passport_internal['expected_full_raw_saving'],
        'Goldilocks_expected_saved_bytes':
            goldilocks['expected_raw_saving']['24']['bytes'],
        'Goldilocks_second_code_sharp_exact_list': str(goldilocks_exact),
        'Goldilocks_second_code_sharp_list': goldilocks_list,
        'Goldilocks_second_code_stage_exact_list': str(goldilocks_stage_exact),
        'Goldilocks_second_code_stage_list_upper': goldilocks_stage_list,
        'Goldilocks_second_code_collision': str(goldilocks_collision),
        'Goldilocks_second_code_separation_bits': goldilocks_collision_bits,
        'ZisK_current_nested_error': zisk_result['nested_error'],
        'ZisK_sampler_corrected_query': str(zisk_corrected_query),
    }


def check_principal_scalar_boundaries():
    scripts = (
        'check_johnson_constants.py',
        'check_uniform_capacity_revision.py',
        'check_reconstruction_parameters.py',
    )
    results = {}
    for script in scripts:
        run = subprocess.run(
            [sys.executable, str(SCRIPTS/script)], cwd=ROOT,
            check=True, capture_output=True, text=True
        )
        lines = [line for line in run.stdout.splitlines() if line.strip()]
        results[script] = {
            'status': 'PASS',
            'last_output_line': lines[-1] if lines else '',
        }
    return results


def main():
    before = _json_hashes()
    legacy = check_legacy_snapshots()
    evaluators = check_new_evaluators()
    scalar_boundaries = check_principal_scalar_boundaries()
    applications = check_applications()
    after = _json_hashes()
    assert before == after, 'read-only report changed a stored JSON artifact'
    report = {
        'status': 'PASS',
        'legacy_commit': LEGACY_COMMIT,
        'legacy_snapshots_reproduced': len(legacy),
        'legacy_snapshot_comparison': 'all stored certificate fields',
        'new_evaluator_checks': evaluators,
        'principal_scalar_boundaries': scalar_boundaries,
        'applications': applications,
        'stored_json_files_changed': 0,
    }
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
