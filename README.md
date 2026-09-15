# Reed–Solomon Codes Beyond Johnson

Public materials for **Reed–Solomon Codes Beyond Johnson: Efficient Decoding
and Smaller Cryptographic Proofs**, by Quang Dao, Scott Duke Kominers, and
Justin Thaler.

Read the [main paper](rs-beyond-johnson.pdf) for the
list-decoding and mutual correlated agreement bounds, decoding algorithms,
and cryptographic applications. This repository supplies the certificate
calculations, experiment records, and source pins supporting that paper.

## Reproduce the calculations

With Python 3.10 or newer, run:

```console
python3 scripts/check_main_certificates.py
```

The checker uses the Python standard library and vendored inputs. It reports
`PASS`, checks 17 historical certificate snapshots and 1,584 pointwise
comparisons, and checks scalar boundary cases and application calculations.
It does not need access to the manuscript's development repository.
The first-order engine keeps its historical Taylor-degree model as the default;
the application checkers opt into the tighter model explicitly. Their
machine-readable reports are under `scripts/examples/`, including the ProveKit,
ZisK, and LambdaVM application records.

The mathematical checks use exact arithmetic. The measured proof-size results
and their reproduction paths are:

### ProveKit

The paper reports mean compressed-proof reductions of **79.4 KB (11.1%)**
for BN254 passport proofs and **16.7 KB (10.3%)** for cubic-Goldilocks lookup
proofs, over ten and thirty proofs per configuration, respectively.
Check the round-by-round security certificates and expected raw-byte savings:

```console
python3 scripts/check_provekit_applications.py --compare-only
```

This command checks the saved [ProveKit budget report](scripts/examples/provekit-applications/checked-budgets.json)
without rewriting it. It does not rerun the prover or reproduce the compressed
sample means. See the [calculation guide](CALCULATIONS.md#measured-sizes-and-their-baselines)
for measurement scope and the [implementation source pins](scripts/examples/implemented-source-pins.json).
The main paper gives the measured means, sample counts, and parameter schedules.

### ZisK

The [ZisK experiment](experiments/zisk-compressed-final/README.md) supplies
verified compressed final proofs measuring **286,013 and 272,783 bytes**,
a reduction of **13,230 bytes (4.63%)**, together with the query-conversion
and verification procedure. These are native saved-proof sizes, not
unencoded field/hash byte counts.

### LambdaVM

The measurement checker verifies the recorded CPU-subproof saving of
**59,832 bytes (4.85%)** and recomputes paired mean timing contrasts from
supplied data; it does not rerun the benchmark:

```console
python3 scripts/check_lambda_measurements.py
```

See the [LambdaVM experiment](experiments/lambdavm-anchors/README.md) for the
32,768-instruction workload, experimental fork, and measured overhead.
The experiment documentation gives the measurement details accompanying
the main paper's application analysis.

The scripts are research artifacts, not production decoders.
The [calculation guide](CALCULATIONS.md) maps the principal tables and
security calculations to checker commands, saved reports, and measurement
records. It distinguishes exact certificate checks from recorded proof sizes.

## Repository guide

| Material | Where to start |
|---|---|
| Mathematical results and proofs | [Paper](rs-beyond-johnson.pdf) |
| Paper results mapped to reproducible calculations | [Calculation guide](CALCULATIONS.md) |
| Proximity Prize benchmark certificates and submission sources | [Benchmark guide](scripts/examples/proximity-prize/README.md) |
| ProveKit certificates | [Checked budgets](scripts/examples/provekit-applications/checked-budgets.json) |
| ZisK proof files and reproduction | [ZisK experiment](experiments/zisk-compressed-final/README.md) |
| LambdaVM sizes, timing data, and reproduction | [LambdaVM experiment](experiments/lambdavm-anchors/README.md) |
| Updating and publishing artifacts | [Publication guide](PUBLICATION.md) |

Run `make check` to check both the main certificates and the Proximity Prize
paper points. Run `make verify` to check the published file checksums.
The numerical checks need only Python 3.10 or newer; TeX is not required.
The paper's source is maintained privately.

## Formalization

The paper's mathematical-source pin is
[`a5aa267` in ArkLib](https://github.com/quangvdao/ArkLib/tree/a5aa2677fee4e3a79d6bb05136631cce4a08587d).
Its separate decoder-source pin is
[`ffab000` in ArkLib](https://github.com/quangvdao/ArkLib/tree/ffab000e71c5b19e8a19bebadcc0050eac1366e3).
These pins identify the paper's source correspondence. The excerpt checker
does not certify complete decoder development or a runtime cost model. Consult the paper's formalization section and the pinned
ArkLib documentation for scope.

The [literal statement bundle](scripts/lean-statements/README.md) includes
24 excerpts and a [source manifest](scripts/lean-statements/sources.json)
recording each declaration's file and immutable revision. Its checker compares
the excerpts against those Git objects; it does not rebuild the formalization.

## Versions and contributions

This repository contains one paper and its supporting artifacts. Paper PDF
updates arrive one way from the authors' private manuscript workspace; its
source and development history remain private. Calculation guides, checkers,
and experiment records are maintained here.
See [PUBLICATION.md](PUBLICATION.md) for the reviewed update process and
[manifest.json](manifest.json) for published file checksums.

The September 2026 materials are research drafts. Please report corrections
through this repository's issues.

## License

Code and accompanying certificate data are dual-licensed under
**MIT OR Apache-2.0**, at your choice. The paper and explanatory documentation are licensed under **CC BY 4.0**.
See [LICENSE.md](LICENSE.md) for the exact scope and third-party exclusions.
