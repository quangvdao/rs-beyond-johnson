# Find and check the paper's calculations

Use this guide to connect the main paper's tables and security calculations
to the public artifact. Names identify results across manuscript renumbering.
Run commands from the repository root with Python 3.10 or newer. The numerical
checkers use the standard library; they need neither Lean nor a prover build.

## Complete certificate check

```console
python3 scripts/check_main_certificates.py > /tmp/rs-certificate-check.json
```

The output is a JSON report with `status: "PASS"`, 17 reproduced historical
snapshots, 1,584 evaluator comparisons, scalar-boundary checks, and application
results. The command does not rewrite saved certificate data. Exact arithmetic
checks the parameter inequalities; the manuscript supplies the mathematical
proofs that turn those inequalities into list and MCA bounds.

## Map from results to commands and records

| Paper result or table | Checker command | Record and interpretation |
|---|---|---|
| Uniform first-order gap 0.24; list bound `307n` and exceptional count `1325775n²`; multiplicity-300 finite loss | `python3 scripts/check_uniform_capacity_revision.py` | Prints the rationally certified breakpoints, margins, exceptional coefficient, and logarithmic slack. Included in the complete check. |
| Quantitative Johnson constants | `python3 scripts/check_johnson_constants.py` | Prints the closed-constant check results. Included in the complete check. |
| Uniform reconstruction and length parameters | `python3 scripts/check_reconstruction_parameters.py` | Prints boundary-check results. Included in the complete check. |
| ProveKit round-by-round certificate table, local security equations, and expected authentication savings | `python3 scripts/check_provekit_applications.py --compare-only` | [checked-budgets.json](scripts/examples/provekit-applications/checked-budgets.json), [passport outer](scripts/examples/provekit-applications/bn254-passport-certificate.json), and [passport internal](scripts/examples/provekit-applications/passport-zk-certificate.json). Checks exact inequalities and expected raw bytes, not the compressed sample means. |
| ZisK query-count comparison and nested powers/fold security calculations | `python3 scripts/check_zisk_final.py --compare-only` | [zisk-final.json](scripts/examples/zisk-final.json). Its `bytes_saved` is the 11,760-byte field/hash-vector calculation, distinct from the 13,230-byte native serialized saving. |
| LambdaVM CPU local error sum, powers degree 50, and eight fold certificates | `python3 scripts/check_lambda_cpu.py` | Regenerates [lambda-cpu.json](scripts/examples/lambda-cpu.json). Its 55,992-byte field/hash saving is distinct from the 59,832-byte serialized CPU saving. The complete checker above evaluates this calculation without rewriting the record. |
| LambdaVM measured CPU-subproof reduction and complete-VM denominator; paired timing contrasts | `python3 scripts/check_lambda_measurements.py` | Reads [measurement.json](experiments/lambdavm-anchors/measurement.json), [cpu-size-breakdown.json](experiments/lambdavm-anchors/cpu-size-breakdown.json), and the experiment TSV files. Prints both percentage denominators and paired mean changes. Does not rerun benchmarks or recompute bootstrap intervals. |
| Lean appendix's literal theorem statements | `python3 scripts/sync_lean_statements.py --math-repo /path/to/ArkLib-math --decoder-repo /path/to/ArkLib-decoder --check` | [Statement bundle and instructions](scripts/lean-statements/README.md); [source manifest](scripts/lean-statements/sources.json). Requires the pinned Git objects and checks excerpts, not proof compilation. |

Omitting `--compare-only` from the ProveKit or ZisK command regenerates its
saved JSON report. Preserve the selected certificate inputs when reproducing
published results; a new bounded search answers a different question.

## Finite application values

The application checkers explicitly select the tight first-order Taylor-degree
model. The engine's default remains the historical model so that saved baselines
remain reproducible. These are certificate calculations, separate from the
proof-size measurements below.

| System | Certificate value | Interpretation |
|---|---|---|
| ProveKit lookup, second code `(n,k,A)=(2048,128,453)` | List bound `2659384185/326`; integer floor `8157620` | One out-of-domain evaluation gives approximately 137.082 separation bits. The saved generic ceiling is `8157621`; the successive-stage ceiling is `93954343`, giving approximately 130.030 bits. |
| ZisK, 51 queries and 22 grinding bits | Batching error `4073087021134687044 / (2^64-2^32+1)^3` | Approximately 130.179 batching bits and 128.000336 query bits under the checker's independent-uniform-output model. |
| LambdaVM CPU, 208 queries and 20 grinding bits | List bound `367473974837/3230`; ceiling `113769033` | Approximately 128.063 bits for the changed-component error bound. The field/hash accounting saves 55,992 bytes; serialization gives the separately measured 59,832 bytes. |

The linked checker reports above retain exact arithmetic. The companion PDF
focuses on mathematical refinements and obstructions; application reproduction
and implementation details live here and in the experiment directories.

## Measured sizes and their baselines

- **ProveKit passport and lookup proofs:** the main paper's measurement table
  reports compressed means over ten and thirty proofs per configuration,
  respectively. The certificate checker establishes the local error budgets
  and expected raw-byte calculations, not those sample means. Implementation
  revisions are recorded in the [source manifest](scripts/examples/implemented-source-pins.json)
  and the passport certificate records.
- **ZisK compressed final proof:** [measurements.json](experiments/zisk-compressed-final/measurements.json)
  records one 54-query proof generated with the released prover and its verified 51-query prefix
  conversion: 286,013 and 272,783 native bytes. The 4.63% denominator is the
  original native proof size. [Reproduction instructions](experiments/zisk-compressed-final/README.md)
  cover the saved proofs, converter, and matching verifier. No runtime
  comparison or second full prover execution is claimed.
- **LambdaVM CPU subproof:** [the measurement record](experiments/lambdavm-anchors/measurement.json)
  records 1,233,024 and 1,173,192 serialized CPU bytes, giving 4.85% relative
  to the original CPU subproof. The same 59,832-byte saving is approximately
  0.162% of the original 36,868,888-byte complete VM proof. This is one
  benchmark A/B size comparison. The [separate timing experiment](experiments/lambdavm-anchors/README.md)
  uses 20 paired proving rounds and 50 paired verification rounds.

## Artifact integrity

```console
python3 scripts/publication.py verify
```

This checks the published files against [manifest.json](manifest.json).
It checks file integrity, not the mathematical claims. Cite this repository
at the immutable commit used by the paper; default-branch links may change.
