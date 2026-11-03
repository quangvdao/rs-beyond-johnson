#!/usr/bin/env python3
"""Extract the appendix declarations from the cited Lean revisions, or check exact agreement."""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATH_REV = '6aa8b6fe8059cecc0e53607ca811a933a0f8e0b7'
DECODER_REV = 'ffab000e71c5b19e8a19bebadcc0050eac1366e3'
BASE = 'ArkLib/Data/CodingTheory/ReedSolomon/'
SPECS = {
    'first-order-finite-slack': ('math', 'MutualCorrelatedAgreement/FirstOrder/Branchwise.lean',
        ['firstOrderBranch_finiteLength_finiteSlack_bounds']),
    'first-order-rate': ('math', 'MutualCorrelatedAgreement/FirstOrder/Branchwise.lean',
        ['firstOrderBranch_finiteLength_rate_bounds', 'firstOrderBranch_finiteLength_mcaError_le']),
    'johnson-list': ('math', 'ListDecodability/PairwiseJohnson.lean',
        ['closePolynomialSet_finite_and_ncard_le_pairwiseJohnson']),
    'johnson-mca': ('math', 'MutualCorrelatedAgreement/Johnson/Agreement.lean',
        ['exists_johnson_line_exactCorrelatedPair']),
    'johnson-mca-error': ('math', 'MutualCorrelatedAgreement/Johnson/Probability.lean',
        ['mcaError_affineLine_johnson_le']),
    'fixed-order-list': ('math', 'ListDecodability/Capacity/RatePartition.lean',
        ['exists_ratePartition_list_bound']),
    'fixed-order-mca': ('math', 'MutualCorrelatedAgreement/Capacity/RatePartition.lean',
        ['exists_ratePartition_line_exactCorrelatedPair_parameters']),
    'list-property': ('math', 'ListDecodability/Capacity/ExactLists.lean', ['HasCapacityLists']),
    'list-theorem': ('math', 'ListDecodability/Capacity/ExactLists.lean', ['exists_rateCapacity_list']),
    'capacity-list': ('math', 'ListDecodability/Capacity/MathematicalUniformRate.lean',
        ['mathematicalUniform_capacity_list_bound']),
    'capacity-mca': ('math', 'MutualCorrelatedAgreement/Capacity/MathematicalUniformRate.lean',
        ['exists_mathematicalUniformRatePartition_line_exactCorrelatedPair']),
    'sharp-mca-property': ('math', 'MutualCorrelatedAgreement/Capacity.lean',
        ['HasCapacityLineAgreement']),
    'sharp-mca-theorem': ('math', 'MutualCorrelatedAgreement/Capacity.lean',
        ['exists_capacity_lineAgreement']),
    'sharp-mca-error': ('math', 'MutualCorrelatedAgreement/Capacity.lean',
        ['exists_capacity_mcaError']),
    'sharp-affine-theorem': ('math', 'MutualCorrelatedAgreement/Capacity.lean',
        ['exists_capacity_affineAgreement']),
    'sharp-power-theorem': ('math', 'MutualCorrelatedAgreement/Capacity.lean',
        ['exists_capacity_powerBatchingAgreement']),
    'hybrid-curve': ('math', 'MutualCorrelatedAgreement/FirstOrder/HybridCurveProfile.lean',
        ['exists_exceptional_exactPowerAgreement_best']),
    'hybrid-curve-optimized': ('math',
        'MutualCorrelatedAgreement/FirstOrder/HybridCurveProfile.lean',
        ['exists_exceptional_exactPowerAgreement_bestOptimized']),
    'squarefree-curve': ('math',
        'MutualCorrelatedAgreement/FirstOrder/Squarefree/SharpCurve.lean',
        ['exists_exceptional_retainedSquarefreeCurveAgreement_sharpAt',
         'exists_exceptional_retainedSquarefreeCurveAgreement_sharpOptimized']),
    'interleaved-power': ('math', 'Interleaved/PowerAgreement.lean',
        ['uniformExactInterleavedPowerAgreement_of_scalar']),
    'tensor-fold': ('math',
        'ArkLib/Data/CodingTheory/ProximityGenerator/BinaryTensorFoldAgreement.lean',
        ['tensorFoldBad_card_le']),
    'interleaved-tensor-fold': ('math', 'Interleaved/TensorFoldAgreement.lean',
        ['fullSetLevelWitness_interleaved_of_exactAgreement',
         'interleavedRS_tensorFoldBad_card_le_heightThree']),
    'decoder-theorem': ('decoder', 'ListDecoding/CapacityDecoder.lean',
        ['capacity_decoder_exact_output_and_primitive_work']),
    'agreement-count': ('math', 'ArkLib/Data/CodingTheory/Basic/Distance.lean', ['agree']),
    'agreement-sets': ('math', 'Agreement.lean',
        ['polynomialAgreementSet', 'commonPolynomialAgreementSet']),
}


def extract(source, name):
    match = re.search(r'^(?:def|structure|theorem) ' + re.escape(name) + r'\b', source, re.M)
    if match is None:
        raise ValueError(f'Declaration not found: {name}')
    tail = source[match.start():]
    if tail.startswith('theorem '):
        # The checked sources use tactic proofs or a term on the next line at
        # two-space indentation. Do not stop at a `let ... := ...` in the type.
        boundary = re.search(r" :=(?: by\b|(?=\n {2}\S))", tail)
        if boundary is None:
            raise ValueError(f'Unsupported theorem proof layout: {name}')
        excerpt = tail[:boundary.start()]
    else:
        excerpt = re.split(r'\n(?=/--|/-!|@\[|(?:end|open|namespace|section)\b|(?:def|structure|theorem|lemma)\s)',
                           tail, maxsplit=1)[0]
    # Only source comments and blank comment separators are omitted. Identifiers, types,
    # hypotheses, and expression tokens are retained verbatim; proof bodies are not printed.
    lines = [line.rstrip() for line in excerpt.splitlines()
             if not line.lstrip().startswith('--')]
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip() + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--math-repo', type=Path, required=True)
    parser.add_argument('--decoder-repo', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    repos = {'math': args.math_repo, 'decoder': args.decoder_repo}
    revs = {'math': MATH_REV, 'decoder': DECODER_REV}
    dest = ROOT / 'scripts/lean-statements'
    dest.mkdir(exist_ok=True)
    manifest = {}
    for stem, (kind, suffix, names) in SPECS.items():
        path = suffix if suffix.startswith('ArkLib/') else BASE + suffix
        source = subprocess.check_output(
            ['git', '-C', str(repos[kind]), 'show', f'{revs[kind]}:{path}'], text=True)
        excerpt = '\n'.join(extract(source, name) for name in names)
        output = dest / (stem + '.lean')
        if args.check:
            if not output.exists() or output.read_text() != excerpt:
                raise SystemExit(f'Stale Lean excerpt: {output.relative_to(ROOT)}')
        else:
            output.write_text(excerpt)
        manifest[stem] = {'revision': revs[kind], 'source': path, 'declarations': names}
    rendered = json.dumps(manifest, indent=2, ensure_ascii=False) + '\n'
    manifest_path = dest / 'sources.json'
    if args.check:
        if manifest_path.read_text() != rendered:
            raise SystemExit('Stale Lean source manifest')
    else:
        manifest_path.write_text(rendered)
    print(f'{"Checked" if args.check else "Extracted"} {len(SPECS)} literal Lean excerpts.')


if __name__ == '__main__':
    main()
