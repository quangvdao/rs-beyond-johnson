#!/usr/bin/env python3
"""Exact LambdaVM all-table inventory and anchored-MCA candidate checks.

The source metadata is pinned to LambdaVM commit 8064a8e.  The arithmetic
checker is deliberately modular: it checks only the changed table-local
MCA/query/AIR-residual terms and the two-anchor list-binding term.  It does not
claim a fresh whole-VM soundness theorem or measured archive-size reduction.
"""

from dataclasses import asdict, dataclass
from fractions import Fraction as F
import json
import math
from pathlib import Path

from tune_first_order_mca import certificate, TIGHT_TAYLOR_DEGREE_MODEL


SOURCE_COMMIT = "8064a8efee4bd3edc9f064337d4e1d8bad54ae1a"
SOURCE_TREE = f"https://github.com/yetanotherco/lambda_vm/tree/{SOURCE_COMMIT}"
P = 2**64 - 2**32 + 1
Q = P**3
BASELINE_QUERIES = 219
GRINDING_BITS = 20
FINAL_POLY_LOG_DEGREE = 7


@dataclass(frozen=True)
class Table:
    name: str
    schema: str
    total_columns: int
    preprocessed_columns: int
    bus_interactions: int
    base_constraints: int
    max_degree: int
    composition_parts: int
    height_policy: str
    role: str = "monolithic/epoch VM proof"
    max_end_exemptions: int = 0
    notes: str = ""

    @property
    def committed_main_columns(self):
        return self.total_columns - self.preprocessed_columns

    @property
    def aux_columns(self):
        return (self.bus_interactions + 1) // 2

    @property
    def logup_constraints(self):
        # N<=2 is absorbed in one accumulator constraint; otherwise all but
        # the last 1--2 interactions are committed in pairs.
        n = self.bus_interactions
        return 0 if n == 0 else ((n - (2 if n % 2 == 0 else 1)) // 2 + 1 if n > 2 else 1)

    @property
    def transition_constraints(self):
        return self.base_constraints + self.logup_constraints

    @property
    def next_row_ood_columns(self):
        return int(self.bus_interactions > 0)

    @property
    def deep_terms(self):
        # Current-row values include preprocessed columns because the DEEP
        # identity still uses their fixed polynomials.  Only the dynamic main
        # columns need anchors.  The sole next-row value is the accumulator.
        return (self.total_columns + self.aux_columns
                + self.next_row_ood_columns + self.composition_parts)

    @property
    def powers_degree(self):
        return self.deep_terms - 1


TABLES = [
    Table("CPU", "CPU", 38, 0, 20, 39, 3, 2, "variable; power-of-two, min 4; split at 2^19"),
    Table("BITWISE", "BITWISE", 21, 11, 10, 0, 3, 2, "fixed 2^20"),
    Table("LT", "LT", 17, 0, 9, 6, 3, 2, "variable; power-of-two, min 4; split at 2^20"),
    Table("SHIFT", "SHIFT", 29, 0, 18, 19, 3, 2, "variable; power-of-two, min 4; split at 2^20"),
    Table("EQ", "EQ", 12, 0, 6, 4, 3, 2, "variable; power-of-two, min 4; split at 2^20"),
    Table("BYTEWISE", "BYTEWISE", 26, 0, 9, 0, 3, 2, "variable; power-of-two, min 4; split at 2^20"),
    Table("STORE", "STORE", 16, 0, 10, 6, 3, 2, "variable; power-of-two, min 4; split at 2^20"),
    Table("CPU32", "CPU32", 38, 0, 23, 32, 3, 2, "variable; power-of-two, min 4; split at 2^19"),
    Table("MEMW", "MEMW", 49, 0, 26, 15, 3, 2, "variable; power-of-two, min 4; split at 2^19"),
    Table("MEMW_A", "MEMW_A", 29, 0, 20, 8, 3, 2, "variable; power-of-two, min 4; split at 2^19"),
    Table("MEMW_R", "MEMW_R", 10, 0, 7, 3, 3, 2, "variable; power-of-two, min 4; split at 2^20"),
    Table("LOAD", "LOAD", 18, 0, 5, 13, 3, 2, "variable; power-of-two, min 4; split at 2^20"),
    Table("DECODE", "DECODE", 6, 5, 1, 0, 2, 1, "ELF-dependent; nextpow2(instructions+1), min 2"),
    Table("MUL", "MUL", 26, 0, 24, 8, 3, 2, "variable; power-of-two, min 4; split at 2^20"),
    Table("DVRM", "DVRM", 34, 0, 34, 19, 3, 2, "variable; power-of-two, min 4; split at 2^19"),
    Table("BRANCH", "BRANCH", 14, 0, 6, 5, 3, 2, "variable; power-of-two, min 4; split at 2^20"),
    Table("HALT", "HALT", 4, 0, 36, 0, 3, 2, "fixed 1", notes="omitted from non-final continuation epochs"),
    Table("HINT", "HINT", 41, 0, 27, 1, 3, 2, "variable; next power-of-two, min 4"),
    Table("COMMIT", "COMMIT", 19, 0, 18, 8, 3, 2, "variable; next power-of-two, min 4"),
    Table("PAGE", "PAGE", 5, 2, 3, 0, 3, 2, "fixed 2^18 per page", notes="private-input variant has preprocessed=1, committed-main=4"),
    Table("REGISTER", "REGISTER", 5, 2, 2, 0, 3, 2, "fixed 128", notes="continuation variant preprocesses FINI too: preprocessed=3, committed-main=2"),
    Table("KECCAK", "KECCAK", 511, 0, 134, 51, 3, 2, "variable; next power-of-two, min 4"),
    Table("KECCAK_RND", "KECCAK_RND", 1480, 0, 1031, 140, 3, 2, "variable; nextpow2(24*operations), min 4"),
    Table("KECCAK_RC", "KECCAK_RC", 10, 9, 1, 0, 2, 1, "fixed 32"),
    Table("ECSM", "ECSM", 667, 0, 579, 413, 3, 2, "variable; next power-of-two, min 4"),
    Table("ECDAS", "ECDAS", 521, 0, 388, 200, 3, 2, "variable; next power-of-two, min 4"),
    Table("GLOBAL_MEMORY", "GLOBAL_MEMORY", 4, 2, 2, 0, 3, 2, "fixed 2^18 per touched page", role="continuation global proof", notes="private-input variant has preprocessed=1, committed-main=3"),
    Table("L2G_MEMORY", "LOCAL_TO_GLOBAL", 9, 0, 6, 1, 3, 2, "variable; next power-of-two, min 1", role="continuation epoch proof", notes="same dynamic main root as L2G_GLOBAL; modified protocol must share anchors and claimed values across both proofs"),
    Table("L2G_GLOBAL", "LOCAL_TO_GLOBAL", 9, 0, 2, 0, 3, 2, "same trace height as L2G_MEMORY", role="continuation global proof", notes="same dynamic main root as L2G_MEMORY; modified protocol must share anchors and claimed values across both proofs"),
]

TABLE_BY_NAME = {t.name: t for t in TABLES}

# Same physical schemas, but a different verifier-known prefix.  The total
# DEEP width stays fixed while the dynamic main width and anchor charge change.
PREPROCESSING_VARIANTS = [
    Table("PAGE_PRIVATE", "PAGE", 5, 1, 3, 0, 3, 2,
          "fixed 2^18 per private-input page",
          notes="OFFSET preprocessed; INIT remains dynamic main"),
    Table("REGISTER_CONTINUATION", "REGISTER", 5, 3, 2, 0, 3, 2,
          "fixed 128",
          notes="INIT, ADDR, and FINI are verifier-bound preprocessing"),
    Table("GLOBAL_MEMORY_PRIVATE", "GLOBAL_MEMORY", 4, 1, 2, 0, 3, 2,
          "fixed 2^18 per private-input page", role="continuation global proof",
          notes="OFFSET preprocessed; INIT remains dynamic main"),
]

TABLE_GROUPS = [
    {
        "family": "CPU and control",
        "tables": ["CPU", "CPU32", "DECODE", "BRANCH", "HALT", "HINT", "COMMIT", "REGISTER"],
        "height_summary": "mostly execution-dependent; CPU/CPU32 split at 2^19; DECODE is ELF-dependent; HALT=1 and REGISTER=128",
    },
    {
        "family": "integer arithmetic and comparison",
        "tables": ["BITWISE", "LT", "SHIFT", "EQ", "BYTEWISE", "MUL", "DVRM"],
        "height_summary": "BITWISE=2^20; the other tables are execution-dependent and split at 2^19 or 2^20",
    },
    {
        "family": "loads, stores, and memory",
        "tables": ["STORE", "LOAD", "MEMW", "MEMW_A", "MEMW_R", "PAGE", "GLOBAL_MEMORY", "LOCAL_TO_GLOBAL"],
        "height_summary": "PAGE/GLOBAL_MEMORY=2^18 per page; the remaining tables are execution-dependent",
    },
    {
        "family": "cryptographic accelerators",
        "tables": ["KECCAK", "KECCAK_RND", "KECCAK_RC", "ECSM", "ECDAS"],
        "height_summary": "KECCAK_RC=32; other heights depend on accelerator calls (KECCAK_RND pads 24 rows per operation)",
    },
]


PROFILES = {
    # Existing checked Lambda family; useful for all current non-crypto AIRs.
    "n65536_existing": dict(n=65536, A=45910, m=22, M=6, mu=30),
    # Bounded independent-coefficient search winner: agreement values
    # 45910, 45800, 45720, 45680, 45600, and 45520 were screened with
    # max_m up to 48 (mu<=3m).  The last value regressed to 208 queries.
    "n65536_independent_bounded": dict(n=65536, A=45600, m=38, M=11, mu=52),
    # Strictly below the finite half-rate Johnson threshold, selected for the
    # four very wide accelerator AIRs.
    "n4096_near_johnson": dict(n=4096, A=2895, m=51, M=15, mu=70),
    # Bounded complete-error powers search for one-anchor crypto proofs.
    "n4096_powers_one_anchor_bounded": dict(n=4096, A=2881, m=15, M=3, mu=20),
    "n8192_near_johnson": dict(n=8192, A=5791, m=41, M=12, mu=56),
    # Actual fixed PAGE/GLOBAL_MEMORY height: T=2^18, n=2T.
    "page_fixed": dict(n=2**19, A=370726, m=12, M=3, mu=16),
    # Actual fixed BITWISE height.  This support is the best returned by the
    # documented m<=40, mu<=3m scalar search; powers degree 28 is separate.
    "bitwise_fixed_screen": dict(n=2**21, A=1482909, m=12, M=3, mu=16),
}

ORDINARY_POWERS_SCREEN = [
    ("A45910-s22", dict(n=65536, A=45910, m=22, M=6, mu=30)),
    ("A45880-s22", dict(n=65536, A=45880, m=22, M=6, mu=30)),
    ("A45850-s22", dict(n=65536, A=45850, m=22, M=6, mu=30)),
    ("A45831-s22", dict(n=65536, A=45831, m=22, M=6, mu=30)),
    ("A45810-s22", dict(n=65536, A=45810, m=22, M=6, mu=30)),
    ("A45800-s25", dict(n=65536, A=45800, m=25, M=7, mu=34)),
]

# Fixed supports used for the three exact first-order rows in the manuscript.
# The support search was performed with the older coarse envelope; these
# canaries verify the subsequent sharp R1/R2 line re-evaluation exactly.
SHARP_FIRST_ORDER_TABLE_ROWS = [
    dict(k=4096, A=14950, m=20, M=12, mu=72,
         exact_list_bound="59667354912/835", list_size_upper=71457911,
         exact_exceptional_bound="83141562239824130656626856/10975501355",
         exceptional_count_upper=7575194931933397),
    dict(k=16384, A=31379, m=28, M=12, mu=53,
         exact_list_bound="441053161880/3749", list_size_upper=117645549,
         exact_exceptional_bound="1278357725814525345597909/49493972",
         exceptional_count_upper=25828553946216428),
    dict(k=32768, A=45869, m=24, M=6, mu=33,
         exact_list_bound="365595258021/6551", list_size_upper=55807550,
         exact_exceptional_bound="200876419633749648019705809/18318312362",
         exceptional_count_upper=10965880243993061),
]


def frac_bits(x):
    return math.inf if x == 0 else -math.log2(x.numerator) + math.log2(x.denominator)


def residual_degree(table, trace_rows):
    """Conservative cleared AIR/OOD residual degree after two main anchors.

    The current source has one LogUp boundary constraint and zero end exemptions
    on every transition constraint.  Keep both sides explicit so the checker
    fails visibly if a future inventory introduces shifted zerofiers.
    """
    constraint_side = ((table.max_degree + 1) * trace_rows
                       + 2 * table.max_degree + table.max_end_exemptions)
    composition_side = ((table.composition_parts + 1) * trace_rows
                        + table.composition_parts - 1)
    return max(constraint_side, composition_side)


def query_payload_bytes(table, n):
    """Deterministic field-and-hash bytes per row-paired query at blowup 2."""
    log_n = n.bit_length() - 1
    assert n == 1 << log_n and log_n >= FINAL_POLY_LOG_DEGREE + 2
    values = 2 * table.total_columns * 8 + 2 * (
        table.aux_columns + table.composition_parts) * 24
    initial_trees = 3 + int(table.preprocessed_columns > 0)  # main, aux, H, [pre]
    initial_hashes = initial_trees * (log_n - 1) * 32
    fri_hashes = 32 * sum(range(FINAL_POLY_LOG_DEGREE + 1, log_n - 1))
    fri_siblings = 24 * max(0, log_n - FINAL_POLY_LOG_DEGREE - 2)
    return values + initial_hashes + fri_hashes + fri_siblings


def compact_certificate(c):
    return {k: c[k] for k in [
        "m", "M", "effective_M", "mu", "support", "height", "dimension",
        "local_rank_upper", "L", "exact_exceptional_bound",
        "exceptional_count_upper", "exact_list_bound", "list_size_upper",
        "selected_transfer_method", "selected_transfer_theorem",
        "selected_list_method", "selected_list_theorem",
        "characteristic_strictly_greater_than",
        "exceptional_characteristic_strictly_greater_than",
        "list_characteristic_strictly_greater_than",
        "joint_degree_upper", "generic_fiber_degree_upper",
        "ordinary_degree_upper", "ordinary_challenge_degree_upper",
        "degree_metadata_scope", "taylor_degree_model",
        "taylor_common_exponent"]}


def evaluate(table, profile, batching="powers", anchor_count=2,
             grinding_bits=GRINDING_BITS):
    n, A = profile["n"], profile["A"]
    m, M, mu = profile["m"], profile["M"], profile["mu"]
    T = n // 2
    assert A * A < n * (T - 1), "threshold must be strictly beyond finite Johnson"
    if anchor_count not in {1, 2}:
        raise ValueError("this bounded checker supports one or two main anchors")
    assert A > T + anchor_count, "preprocessed polynomial root-bound condition"

    if batching not in {"powers", "independent"}:
        raise ValueError("batching must be powers or independent")
    mca_curve_degree = table.powers_degree if batching == "powers" else 1
    initial = certificate(
        n, T, A, m, M, mu, ell=mca_curve_degree,
        taylor_degree_model=TIGHT_TAYLOR_DEGREE_MODEL)
    anchor = certificate(
        n, T + anchor_count + 1, A, m, M, mu, ell=1,
        taylor_degree_model=TIGHT_TAYLOR_DEGREE_MODEL)
    if initial is None or anchor is None:
        return {"status": "no certificate for supplied support"}
    L = anchor["list_size_upper"]

    folds = []
    ni = T
    while ni >= 256:
        Ai = (A * ni + n - 1) // n
        c = certificate(
            ni, ni // 2, Ai, m, M, mu, ell=1,
            taylor_degree_model=TIGHT_TAYLOR_DEGREE_MODEL)
        if c is None:
            return {"status": f"no fold certificate at n={ni}"}
        folds.append((ni, Ai, c))
        ni //= 2

    # Powers batching samples one full-field gamma.  Independent coefficients
    # use the affine-family theorem and its nonzero-scale denominator q-1.
    powers_error = F(initial["exceptional_count_upper"], Q if batching == "powers" else Q - 1)
    fold_error = sum((F(c["exceptional_count_upper"], Q) for _, _, c in folds), F(0))
    anchor_error = (F(L * (L - 1), 2)
                    * F(T + anchor_count, Q - n - anchor_count + 1) ** anchor_count)
    cancellation_error = F(table.transition_constraints * L, Q)
    degree = residual_degree(table, T)
    # 2n excludes z^2 in the paired LDE. The last term rejects coincidence
    # with an early anchor. Keep the two-anchor residual degree for one-anchor
    # rows as a conservative common bound.
    ood_error = F(degree * L + 2 * n + anchor_count, Q - n - T)
    fixed_error = powers_error + fold_error + anchor_error + cancellation_error + ood_error

    chosen = None
    for queries in range(1, BASELINE_QUERIES + 1):
        query_error = F(A, n) ** queries / 2**grinding_bits
        total = fixed_error + query_error
        if total < F(1, 2**128):
            chosen = (queries, query_error, total)
            break

    payload = query_payload_bytes(table, n)
    anchor_bytes = anchor_count * table.committed_main_columns * 24
    result = {
        "status": "certified" if chosen else "fixed_error_exceeds_or_leaves_no_128_bit_query_profile",
        "n": n,
        "trace_rows": T,
        "agreement": A,
        "agreement_fraction": str(F(A, n)),
        "finite_johnson_strict": True,
        "powers_degree": table.powers_degree,
        "mca_batching": batching,
        "mca_curve_degree": mca_curve_degree,
        "deep_terms": table.deep_terms,
        "anchor_width": table.committed_main_columns,
        "anchor_count": anchor_count,
        "anchor_bytes": anchor_bytes,
        "preprocessed_root_bound": f"A={A} > T+anchors={T+anchor_count}",
        "grinding_bits": grinding_bits,
        "expected_grinding_work_multiplier_vs_20_bits": 2 ** (grinding_bits - GRINDING_BITS),
        "initial_certificate": compact_certificate(initial),
        "anchor_list_certificate": compact_certificate(anchor),
        "fold_count": len(folds),
        "powers_error": str(powers_error),
        "powers_bits": frac_bits(powers_error),
        "fold_error": str(fold_error),
        "fold_bits": frac_bits(fold_error),
        "anchor_collision_error": str(anchor_error),
        "anchor_collision_bits": frac_bits(anchor_error),
        "constraint_cancellation_error": str(cancellation_error),
        "constraint_cancellation_bits": frac_bits(cancellation_error),
        "cleared_residual_degree": degree,
        "ood_error": str(ood_error),
        "ood_bits": frac_bits(ood_error),
        "fixed_error": str(fixed_error),
        "fixed_bits": frac_bits(fixed_error),
        "per_query_field_and_hash_bytes": payload,
    }
    if table.schema == "LOCAL_TO_GLOBAL":
        result["cross_proof_anchor_binding"] = (
            "required: derive one domain-separated anchor pair after the shared "
            "L2G main root and absorb/check the same claimed vectors in the epoch "
            "and global proof transcripts")
    if chosen:
        queries, query_error, total = chosen
        saved = BASELINE_QUERIES - queries
        result.update({
            "queries": queries,
            "baseline_queries": BASELINE_QUERIES,
            "queries_removed": saved,
            "query_error": str(query_error),
            "query_bits": frac_bits(query_error),
            "total_changed_component_error": str(total),
            "total_bits": frac_bits(total),
            "removed_query_payload_bytes": saved * payload,
            "net_field_and_hash_bytes": saved * payload - anchor_bytes,
        })
    return result


def table_record(t):
    d = asdict(t)
    d.update({
        "committed_main_columns": t.committed_main_columns,
        "aux_columns": t.aux_columns,
        "logup_constraints": t.logup_constraints,
        "transition_constraints": t.transition_constraints,
        "next_row_ood_columns": t.next_row_ood_columns,
        "deep_terms": t.deep_terms,
        "powers_degree": t.powers_degree,
    })
    return d


def validate_inventory():
    """Fail fast on counting or preprocessing-width drift in this snapshot."""
    assert len(TABLES) == 29
    assert len({t.name for t in TABLES}) == 29
    assert len({t.schema for t in TABLES}) == 28
    for t in TABLES + PREPROCESSING_VARIANTS:
        assert 0 <= t.preprocessed_columns <= t.total_columns
        assert t.aux_columns == (t.bus_interactions + 1) // 2
        assert t.logup_constraints == t.aux_columns
        assert t.deep_terms - 1 == t.powers_degree
    for variant in PREPROCESSING_VARIANTS:
        base = next(t for t in TABLES if t.schema == variant.schema)
        assert variant.total_columns == base.total_columns
        assert variant.aux_columns == base.aux_columns
        assert variant.deep_terms == base.deep_terms
        assert variant.transition_constraints == base.transition_constraints

    # Stable byte-layout canaries for the two examples quoted in the paper.
    assert query_payload_bytes(TABLE_BY_NAME["EQ"], 2**16) == 4504
    assert query_payload_bytes(TABLE_BY_NAME["KECCAK_RND"], 2**16) == 52616

    for expected in SHARP_FIRST_ORDER_TABLE_ROWS:
        c = certificate(
            65536, expected["k"], expected["A"], expected["m"],
            expected["M"], expected["mu"], ell=1,
            taylor_degree_model=TIGHT_TAYLOR_DEGREE_MODEL)
        assert c is not None
        assert c["selected_list_method"] == (
            "sharp-squarefree-taylor-tight-v3-interleaved")
        assert c["selected_transfer_method"] == (
            "sharp-squarefree-free-tail-taylor-tight-v3-line")
        for key in ["exact_list_bound", "list_size_upper",
                    "exact_exceptional_bound", "exceptional_count_upper"]:
            assert c[key] == expected[key], (expected, key, c[key])


def build_data():
    # All ordinary non-crypto schemas, including continuation roles, at one
    # actual supported dyadic height.  Tiny fixed tables are inventory-only:
    # their FRI terminal path differs and query removal is not size-attractive.
    noncrypto = [t.name for t in TABLES if t.name not in {
        "KECCAK", "KECCAK_RND", "ECSM", "ECDAS", "BITWISE", "PAGE",
        "GLOBAL_MEMORY", "REGISTER", "KECCAK_RC", "HALT"}]
    standard = {name: evaluate(TABLE_BY_NAME[name], PROFILES["n65536_existing"])
                for name in noncrypto}
    ordinary_powers = {}
    ordinary_powers_profiles = {}
    for name in noncrypto:
        candidates = []
        for label, profile in ORDINARY_POWERS_SCREEN:
            row = evaluate(TABLE_BY_NAME[name], profile, "powers")
            if row.get("queries") is not None:
                candidates.append(((row["queries"], -row["total_bits"]), label, profile, row))
        _, label, profile, row = min(candidates)
        row["bounded_screen_selection"] = label
        ordinary_powers[name] = row
        ordinary_powers_profiles[name] = profile
    crypto_4096 = {name: evaluate(TABLE_BY_NAME[name], PROFILES["n4096_near_johnson"])
                   for name in ["KECCAK", "KECCAK_RND", "ECSM", "ECDAS"]}
    crypto_8192 = {name: evaluate(TABLE_BY_NAME[name], PROFILES["n8192_near_johnson"])
                   for name in ["KECCAK", "KECCAK_RND", "ECSM", "ECDAS"]}
    crypto_one_anchor = {
        name: evaluate(TABLE_BY_NAME[name], PROFILES["n4096_powers_one_anchor_bounded"],
                       "powers", anchor_count=1)
        for name in ["KECCAK", "KECCAK_RND", "ECSM", "ECDAS"]
    }
    ordinary_grind21 = {
        name: evaluate(TABLE_BY_NAME[name], ordinary_powers_profiles[name], "powers",
                       grinding_bits=21)
        for name in noncrypto
    }
    ordinary_grind22 = {
        name: evaluate(TABLE_BY_NAME[name], ordinary_powers_profiles[name], "powers",
                       grinding_bits=22)
        for name in noncrypto
    }
    crypto_one_anchor_grind21 = {
        name: evaluate(TABLE_BY_NAME[name], PROFILES["n4096_powers_one_anchor_bounded"],
                       "powers", anchor_count=1, grinding_bits=21)
        for name in ["KECCAK", "KECCAK_RND", "ECSM", "ECDAS"]
    }
    crypto_one_anchor_grind22 = {
        name: evaluate(TABLE_BY_NAME[name], PROFILES["n4096_powers_one_anchor_bounded"],
                       "powers", anchor_count=1, grinding_bits=22)
        for name in ["KECCAK", "KECCAK_RND", "ECSM", "ECDAS"]
    }
    fixed_pages = {
        "PAGE": evaluate(TABLE_BY_NAME["PAGE"], PROFILES["page_fixed"]),
        "PAGE_PRIVATE": evaluate(PREPROCESSING_VARIANTS[0], PROFILES["page_fixed"]),
        "GLOBAL_MEMORY": evaluate(TABLE_BY_NAME["GLOBAL_MEMORY"], PROFILES["page_fixed"]),
        "GLOBAL_MEMORY_PRIVATE": evaluate(PREPROCESSING_VARIANTS[2], PROFILES["page_fixed"]),
    }
    bitwise = evaluate(TABLE_BY_NAME["BITWISE"], PROFILES["bitwise_fixed_screen"])
    bitwise_independent = evaluate(
        TABLE_BY_NAME["BITWISE"], PROFILES["bitwise_fixed_screen"], "independent")
    independent_ordinary = {
        name: evaluate(TABLE_BY_NAME[name], PROFILES["n65536_independent_bounded"], "independent")
        for name in noncrypto
    }
    independent_wide = {
        name: evaluate(TABLE_BY_NAME[name], PROFILES["n65536_independent_bounded"], "independent")
        for name in ["KECCAK", "KECCAK_RND", "ECSM", "ECDAS"]
    }
    return {
        "scope": "Pinned LambdaVM table inventory plus modular one/two-anchor changed-component certificates",
        "source_commit": SOURCE_COMMIT,
        "source_tree": SOURCE_TREE,
        "field_characteristic": P,
        "challenge_field_size": Q,
        "actual_default": {
            "field": "cubic extension of Goldilocks",
            "blowup": 2,
            "rate": "1/2",
            "security_target_bits": 128,
            "grinding_bits": GRINDING_BITS,
            "queries": BASELINE_QUERIES,
            "fri_final_poly_log_degree": FINAL_POLY_LOG_DEGREE,
        },
        "counting_convention": "28 physical trace schemas; LOCAL_TO_GLOBAL has two proof roles, yielding 29 primary role rows; preprocessing variants of PAGE, REGISTER, and GLOBAL_MEMORY are recorded separately",
        "table_groups": TABLE_GROUPS,
        "tables": [table_record(t) for t in TABLES],
        "preprocessing_variants": [table_record(t) for t in PREPROCESSING_VARIANTS],
        "candidate_profiles": {
            "noncrypto_at_trace_rows_32768": standard,
            "crypto_at_trace_rows_2048": crypto_4096,
            "crypto_at_trace_rows_4096": crypto_8192,
            "actual_fixed_page_height": fixed_pages,
            "least_invasive_ordinary_powers_at_trace_rows_32768": ordinary_powers,
            "least_invasive_crypto_powers_one_anchor_at_trace_rows_2048": crypto_one_anchor,
            "exploratory_ordinary_independent_coefficients_at_trace_rows_32768": independent_ordinary,
            "exploratory_wide_crypto_independent_coefficients_at_trace_rows_32768": independent_wide,
        },
        "powers_grinding_tradeoffs": {
            "scope": "Existing powers batching. Grinding 21/22 uses the supported ProofOptions field but is global in the current VmAirs construction; expected nonce-search hashes multiply by 2/4 for every table proof. Runtime impact is not benchmarked.",
            "ordinary_trace_rows_32768_grinding21": ordinary_grind21,
            "ordinary_trace_rows_32768_grinding22": ordinary_grind22,
            "crypto_trace_rows_2048_one_anchor_grinding21": crypto_one_anchor_grind21,
            "crypto_trace_rows_2048_one_anchor_grinding22": crypto_one_anchor_grind22,
        },
        "bounded_powers_search": {
            "ordinary_scope": "Six fixed (agreement,support) profiles in ORDINARY_POWERS_SCREEN; selected per table by minimum queries then largest complete-error margin. No global optimality claim.",
            "crypto_scope": "At n=4096, complete-error one-anchor powers supports were screened over m=15..35, M=3..10, mu=20..48. With (15,3,20), thresholds A=2891/2886/2881 give 215/214/213 queries for all four tables; A=2878 fails with this support. The selected A=2881 point is not a global optimum.",
        },
        "batching_and_recursion_evidence": {
            "source_fact": "The current prover and verifier each sample one cubic-extension gamma and generate every DEEP coefficient as successive powers 1,gamma,... . The source does not state why this design was chosen.",
            "recursion_cost_fact": "The default transcript documents that software ChaCha challenge expansion previously dominated recursion-guest sampling cost; Keccak is a precompile, and its 32-byte buffer amortizes four u64 candidates so one cubic element usually costs one squeeze.",
            "inference": "Replacing one gamma by b-1 independent cubic challenges would materially increase transcript sampling for wide tables and may hurt recursion. This is an engineering inference, not an implementation benchmark or an attributed rationale for powers batching.",
            "recommendation": "Keep current powers batching for the least-invasive rows. Treat independent coefficients as optional exploratory results pending recursion benchmarks.",
        },
        "fixed_bitwise_screen": {
            "search_scope": "support (12,3,16) selected by tune_first_order_mca.py m<=40, mu<=3m scalar search at the maximum integral agreement strictly below finite Johnson; powers degree checked exactly",
            "result": bitwise,
            "independent_coefficient_result": bitwise_independent,
            "conclusion": "The displayed fixed-height BITWISE powers profile has only about 124.26 fixed-error bits, so queries cannot make its modular changed-component sum 128-bit. Independent coefficients reach 128 bits but still require the baseline 219 queries and add 480 anchor bytes. The bounded m<=40 result is not an impossibility theorem.",
        },
        "bounded_independent_search": {
            "scope": "Agreements {45910,45800,45720,45680,45600,45520} at n=65536; derivative/equal supports searched by tune_first_order_mca.py with mu<=3m and max_m up to 48; the selected A=45600 run used max_m=40. This is not a global optimum.",
            "selected_profile": PROFILES["n65536_independent_bounded"],
            "selected_queries": 207,
            "lower_agreement_probe": "A=45520 with max_m=48 selected (48,14,66) but required 208 queries because fixed error worsened",
        },
        "excluded_from_byte_tuning": {
            "tables": ["HALT", "REGISTER", "KECCAK_RC"],
            "reason": "Their trace domains are below the generic n>=512 row-paired FRI payload formula; they remain fully inventoried and at the baseline policy.",
        },
        "protocol_assumptions": [
            "All dynamic main commitments for every changed table are absorbed before that table's configured one or two extension-field anchors and before shared LogUp challenges; points may be reused only when their conditional sampling law is valid for every table domain.",
            "Only committed dynamic main columns are sent at the anchors. With a anchors, preprocessed columns need no payload because A>T+a makes an extracted degree-at-most-T+a polynomial equal the verifier-bound degree-less-than-T polynomial by the root bound.",
            "Main DEEP quotients use the anchor factors and the existing (X-z) factor; auxiliary, preprocessed, and composition terms keep their existing interface. The one-anchor rows retain the two-anchor residual degree as a conservative bound.",
            "The verifier selects a deterministic per-table query policy from public trace length/schema; proof-supplied options are not trusted.",
            "Reducing the selected main tuple modulo X^T-1 preserves every trace-domain bus value, so the selected tuple is fixed before shared LogUp randomness.",
            "Each table currently has one LogUp boundary constraint and every transition constraint has zero end exemptions; the residual checker retains explicit degree/zerofier fields for source drift.",
            "The reported errors replace one table-local component allocation conditional on the shared prefix; unrelated VM and global lookup budgets are preserved, not recomputed.",
            "The optional independent-coefficient rows replace one powers challenge by a Fiat-Shamir-derived affine coefficient vector after all DEEP words are fixed; this adds transcript squeezing/computation but no proof payload.",
            "For LOCAL_TO_GLOBAL, the epoch and global sub-proofs commit the same dynamic main root. They must use one root-derived, domain-separated anchor pair and the same claimed vectors in both transcripts; independent anchors would not prove that both roles extracted the same polynomial tuple.",
            "The linked LOCAL_TO_GLOBAL proof branches must use the same trace height T and certify one common candidate family at agreement min(A_epoch,A_global); the displayed rows use identical T and A in both roles.",
        ],
        "serialization": {
            "wire_format": "rkyv with 64-bit relative pointers; serde derives are test/reference only",
            "proof_shape": "MultiProof is Vec<StarkProof>; every table proof carries roots, OOD tables, FRI roots/final coefficients, independent query/deep-opening vectors, nonce, and optional bus contribution",
            "byte_claim": "deterministic raw field-element and Merkle-hash payload only; excludes rkyv descriptors/alignment and is not a measured archive delta",
        },
    }


def md_table(data):
    out = [
        "# LambdaVM all-table anchored-MCA scope (2026-09-07)", "",
        f"Pinned source: [{SOURCE_COMMIT[:12]}]({SOURCE_TREE}). This is a source-derived inventory and exact modular arithmetic check, not a runtime patch, measured proof benchmark, or whole-VM audit.", "",
        "The current default CLI profile is cubic Goldilocks, blowup 2 (rate 1/2), 128-bit target, 20-bit grinding, 219 queries, and terminal log-degree 7. The inventory has 28 physical trace schemas. LOCAL_TO_GLOBAL is committed in an epoch-local Memory-bus AIR and again in a commitment-bound global-bus AIR, so the complete role table has 29 rows.", "",
        "| family | schemas | fixed versus variable heights |",
        "|---|---|---|",
    ]
    for group in data["table_groups"]:
        out.append(f"| {group['family']} | {', '.join(group['tables'])} | {group['height_summary']} |")
    out += [
        "", "### Complete AIR-role inventory", "",
        "The `pre` count is the verifier-bound prefix; `main` is the dynamic committed suffix that must be opened at the two anchors.", "",
        "| AIR role | total/pre/main | bus/aux | base+LogUp constraints | degree/parts | DEEP terms (powers degree) | height |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for t in TABLES:
        out.append(f"| {t.name} | {t.total_columns}/{t.preprocessed_columns}/{t.committed_main_columns} | {t.bus_interactions}/{t.aux_columns} | {t.base_constraints}+{t.logup_constraints}={t.transition_constraints} | {t.max_degree}/{t.composition_parts} | {t.deep_terms} ({t.powers_degree}) | {t.height_policy} |")
    out += [
        "", "The same physical schemas also have the following preprocessing variants. Their total, auxiliary, and DEEP widths and constraints are unchanged; only the pre/main split and anchor bytes differ.", "",
        "| variant | schema | total/pre/main | two-anchor bytes | height |",
        "|---|---|---:|---:|---|",
    ]
    for t in PREPROCESSING_VARIANTS:
        out.append(f"| {t.name} | {t.schema} | {t.total_columns}/{t.preprocessed_columns}/{t.committed_main_columns} | {48*t.committed_main_columns} | {t.height_policy} |")
    out += [
        "", "Here `total/pre/main` separates the full current-row trace width, verifier-fixed preprocessed prefix, and proof-dependent committed main suffix. With `a` early anchors, preprocessed polynomials remain DEEP terms but need no anchor payload: every checked threshold satisfies `A>T+a`, hence an extracted degree-at-most-`T+a` polynomial agreeing with the fixed degree-less-than-`T` word at `A` points is identical to it.", "",
        "All current transition metadata has zero end exemptions. Every AIR role has a nonempty bus and therefore one LogUp boundary constraint and one next-row OOD value (the accumulator). Thus the exact DEEP powers degree is `total + aux + composition_parts`; it is 17 for EQ, at most 64 for the ordinary CPU/memory/control tables, and 580/1998/959/717 for KECCAK/KECCAK_RND/ECSM/ECDAS.", "",
        "## Exact candidates", "",
        "The least-invasive recommendation keeps LambdaVM's current single-challenge powers batching and default 20-bit grinding. At `T=32768`, the bounded ordinary-table screen selects among six fixed agreement/support profiles. At `T=2048`, one early vector anchor, `A=2881`, and `(m,M,mu)=(15,3,20)` give 213 queries for all four crypto tables. Independent-coefficient rows are retained below as exploratory alternatives because the source documents that challenge sampling matters in recursion.", "",
        "The following rows use `tune_first_order_mca.py` directly for the initial curve, every binary fold, and the appropriate `T+a+1` anchor-list certificate. For each displayed fixed support and agreement threshold, the query count is the smallest integer making the changed-component sum strictly below `2^-128`; this is not a global parameter optimum.", "",
        "| profile | table | batching | anchors/grind | layout/curve degree | queries | removed | net raw bytes | changed-component bits |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    groups = data["candidate_profiles"]
    for profile_name, rows in groups.items():
        for name, row in rows.items():
            if row.get("status") == "certified" and row.get("net_field_and_hash_bytes", 0) > 0:
                out.append(f"| {profile_name} | {name} | {row['mca_batching']} | {row['anchor_count']}/{row['grinding_bits']} | {row['powers_degree']}/{row['mca_curve_degree']} | {row['queries']} | {row['queries_removed']} | {row['net_field_and_hash_bytes']} | {row['total_bits']:.3f} |")
    bit = data["fixed_bitwise_screen"]["result"]
    bit_ind = data["fixed_bitwise_screen"]["independent_coefficient_result"]
    out += [
        "", "For existing powers batching at `T=2048`, the selected one-anchor crypto profile removes six queries at default grinding. Its exact net savings are 68,616 bytes for KECCAK, 267,696 for KECCAK_RND, 144,072 for ECSM, and 105,912 for ECDAS. Since any at-or-above-Johnson half-rate agreement needs at least 216 queries from the query term alone, 213 is a genuine beyond-Johnson reduction.", "",
        "For independent coefficients at `T=32768`, the exploratory bounded screen selected `A=45600` and `(m,M,mu)=(38,11,52)`. Every eligible ordinary and wide-crypto row shown for this profile reaches 207 queries; this is the best screened point, not a global optimum. The lower-agreement `A=45520`, max-`m=48` probe regressed to 208 queries because its fixed error increased.",
        "", "At the actual fixed PAGE/GLOBAL_MEMORY height `T=2^18`, both ordinary and private-input variants admit 217 queries and positive modeled savings. Private pages have one additional dynamic main column, so their net savings are 48 bytes smaller. At the actual fixed BITWISE height `T=2^20`, the bounded support `(12,3,16)` gives only %.3f fixed-error bits with powers degree 28, so queries cannot repair it. Independent random DEEP coefficients reduce the MCA curve degree to one; the same exact support gives %.3f fixed-error bits and %s queries. This affine option adds no proof bytes, but it is a protocol/code change and must be domain-separated and verifier-replayed." % (bit["fixed_bits"], bit_ind["fixed_bits"], bit_ind.get("queries", "no certified")), "",
        "The wide crypto tables are feasible only on smaller shards under powers batching in this first screen. At `T=2048`, all four admit 217 queries and remain net-positive despite wide anchors. At `T=4096`, KECCAK, ECSM, and ECDAS remain positive at 217 while KECCAK_RND needs 219. Independent DEEP coefficients remove the width-dependent powers degree and give the 207-query path at `T=32768` recorded above.", "",
        "## Existing grinding tradeoff", "",
        "LambdaVM already implements a `grinding_factor`, but the current CLI exposes only blowup and the current `VmAirs` construction passes one `ProofOptions` value to every AIR. Each table transcript fork performs its own nonce search. Raising grinding from 20 to 21 or 22 therefore multiplies expected nonce-search hashes by 2 or 4 for every table proof, not just a selected table. The nonce remains one `u64`, so the increment changes expected proving work but adds no proof bytes. No end-to-end runtime effect is inferred here.", "",
        "| table/profile | grinding 21: queries/net bytes/bits | grinding 22: queries/net bytes/bits |",
        "|---|---:|---:|",
    ]
    grind = data["powers_grinding_tradeoffs"]
    for name in ["CPU", "EQ", "MEMW"]:
        g21 = grind["ordinary_trace_rows_32768_grinding21"][name]
        g22 = grind["ordinary_trace_rows_32768_grinding22"][name]
        out.append(f"| {name}, T=32768 | {g21['queries']} / {g21['net_field_and_hash_bytes']} / {g21['total_bits']:.3f} | {g22['queries']} / {g22['net_field_and_hash_bytes']} / {g22['total_bits']:.3f} |")
    for name in ["KECCAK", "KECCAK_RND", "ECSM", "ECDAS"]:
        g21 = grind["crypto_trace_rows_2048_one_anchor_grinding21"][name]
        g22 = grind["crypto_trace_rows_2048_one_anchor_grinding22"][name]
        out.append(f"| {name}, T=2048, one anchor | {g21['queries']} / {g21['net_field_and_hash_bytes']} / {g21['total_bits']:.3f} | {g22['queries']} / {g22['net_field_and_hash_bytes']} / {g22['total_bits']:.3f} |")
    out += [
        "", "These are size/work tradeoffs rather than the default recommendation. The default-grinding powers rows above require fewer protocol changes.", "",
        "## Batching evidence and scope", "",
        "The prover and verifier source each sample one cubic-extension `gamma` and generate all DEEP coefficients as `1,gamma,...`; the source gives no design rationale for that choice. Separately, the default transcript documents that software challenge expansion previously dominated recursion-guest sampling cost, while Keccak is a precompile and a buffered squeeze usually supplies one cubic challenge. It is therefore reasonable to expect a large independent coefficient vector to increase recursion cost, but this is an inference and has not been benchmarked. The independent rows remain exploratory; the powers rows are the concrete least-invasive recommendations.", "",
        "## Protocol and transcript interface", "",
        "The implementation first absorbs the statement, then every preprocessed and main root in table order, samples the two shared LogUp challenges, forks the transcript by table index, absorbs that table's auxiliary root and bus contribution, samples beta, absorbs the composition root, samples the OOD point, absorbs current-row values, the pruned next-row accumulator, and composition-part values, then runs powers-DEEP/FRI, grinding, and row-paired queries. A multi-table anchor extension inserts each changed table's configured one or two points and dynamic main values after the global main-root barrier and before the shared LogUp challenges. Points may be reused only when their rejection domains and conditional sampling laws agree. The point order and table/column order must be canonical and verifier-replayed.", "",
        "With `a` anchors, the reconstructed main degree is at most `T+a`, the list certificate has dimension `T+a+1`, and the checker charges collision `binom(Lambda,2)*((T+a)/(q-n-a+1))^a`. Thus the selected one-anchor crypto rows use dimension `T+2`, collision `binom(Lambda,2)*(T+1)/(q-n)`, one extension-field value per dynamic main column, and one OOD/anchor-coincidence rejection.", "",
        "For maximum constraint degree `d`, `c` composition parts, trace height `T`, and maximum transition end-exemption `e`, the two-anchor checker uses the conservative cleared residual degree `max((d+1)T+2d+e, (c+1)T+c-1)`. Here every `e=0`; all degree-3/two-part tables recover `4T+6`, while DECODE and KECCAK_RC use `3T+4`. The one-anchor rows conservatively retain this same degree, although the first branch can tighten to `(d+1)T+d+e`. A future shifted or multi-boundary AIR must update this formula and the inventory before inheriting any row.", "",
        "Wire proofs use rkyv with 64-bit relative pointers. `MultiProof` stores a vector of per-table `StarkProof` objects, and query/opening vectors are independent. Byte numbers therefore count exact field elements and Merkle hashes under the current row-paired format, excluding rkyv vector descriptors, alignment, and archive metadata.", "",
        "LOCAL_TO_GLOBAL needs an extra cross-proof rule. The source checks equality of its dynamic main root between each epoch proof and the global proof. Root equality alone does not force two list recoveries to select the same nearby polynomial. A modified continuation must derive one domain-separated anchor pair after that root is fixed, carry one pair of claimed vectors, and absorb/check their explicit equality in both transcript branches. Both branches must use the same `T` and one candidate family at agreement `min(A_epoch,A_global)`; the displayed rows use identical `T,A`. The table rows above charge the anchor payload separately to each role, so their local byte gains are conservative if the continuation bundle serializes the shared vector only once. PAGE and GLOBAL_MEMORY share verifier-known preprocessing roots, not a dynamic main root, and therefore do not need this extra equality rule.", "",
        "## Pinned primary-source map", "",
        f"- [table modules and production split caps](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/prover/src/tables/mod.rs#L67-L101)",
        f"- [AIR ordering and proof roles](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/prover/src/lib.rs#L506-L675)",
        f"- [preprocessed PAGE/REGISTER/table variants](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/prover/src/lib.rs#L684-L862)",
        f"- [fixed BITWISE height](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/prover/src/tables/bitwise.rs#L90-L105)",
        f"- [fixed PAGE height](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/prover/src/tables/page.rs#L44-L55)",
        f"- [REGISTER padding rule](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/prover/src/tables/register.rs#L203-L225)",
        f"- [fixed KECCAK_RC height](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/prover/src/tables/keccak_rc.rs#L40-L50)",
        f"- [KECCAK_RND 24-row padding rule](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/prover/src/tables/keccak_rnd.rs#L240-L255)",
        f"- [all main/aux element accounting](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/prover/src/tables/trace_builder.rs#L4060-L4310)",
        f"- [LogUp packing, constraint degrees, and sole next-row column](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/crypto/stark/src/lookup.rs#L899-L1079)",
        f"- [shared transcript and per-table forks](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/crypto/stark/src/prover.rs#L3280-L3537)",
        f"- [beta, OOD words, and DEEP/FRI challenge timing](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/crypto/stark/src/prover.rs#L4435-L4578)",
        f"- [current one-gamma powers batching](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/crypto/stark/src/prover.rs#L2159-L2182)",
        f"- [verifier replay of powers batching](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/crypto/stark/src/verifier.rs#L1530-L1549)",
        f"- [recursion-sensitive buffered Keccak transcript](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/crypto/crypto/src/fiat_shamir/default_transcript.rs#L14-L38)",
        f"- [expected grinding work is about 2^grinding_factor](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/crypto/math-cuda/src/grinding.rs#L19-L29)",
        f"- [proof shape and authoritative rkyv note](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/crypto/stark/src/proof/stark.rs#L11-L145)",
        f"- [default cubic-Goldilocks option builder](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/crypto/stark/src/proof/options.rs#L77-L134)",
        f"- [CLI default blowup](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/bin/cli/src/main.rs#L151-L170)",
        f"- [continuation L2G/global AIR roles](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/prover/src/continuation.rs#L140-L258)",
        f"- [current L2G main-root equality check](https://github.com/yetanotherco/lambda_vm/blob/{SOURCE_COMMIT}/prover/src/lib.rs#L1015-L1043)",
        "", "Exact rational values and certificate parameters are in the adjacent JSON artifact.", "",
    ]
    return "\n".join(out)


def main():
    validate_inventory()
    data = build_data()
    target = Path(__file__).parent / "examples"
    json_path = target / "lambda-table-scope-2026-09-07.json"
    md_path = target / "lambda-table-scope-2026-09-07.md"
    json_path.write_text(json.dumps(data, indent=2) + "\n")
    md_path.write_text(md_table(data))
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
