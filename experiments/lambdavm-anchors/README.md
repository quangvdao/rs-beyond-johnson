# LambdaVM: measured CPU-subproof savings

The implemented experimental CPU profile reduces the complete CPU subproof
of the 32,768-instruction benchmark from **1,233,024** to **1,173,192 bytes**:
**59,832 bytes (59.832 decimal KB, 4.85%)**. This comparison includes all
CPU commitments, claims, openings, and the added evaluations. It excludes
the unchanged VM-level wrapper.

Both complete VM proofs were generated, deserialized, and verified under
their matching profiles. Their sizes are **36,868,888** and **36,809,056 bytes**,
respectively, so the absolute saving is also 59,832 bytes for the whole proof.
All 26 table subproofs are included; only the CPU profile changes.

The CPU query count is 219 versus 208. Every non-CPU table retains 219 queries.
Two early vectors of 38 cubic-Goldilocks values add 1,856 serialized bytes;
eleven removed query records save 61,688 bytes.

## Evidence and checks

- [Measurement record](measurement.json): exact sizes, source pins, workload and proof hashes.
- [CPU-subproof breakdown](cpu-size-breakdown.json): complete CPU sizes and independent wrapper-allocation cross-check.
- [Overhead report](overhead-report.md): four-cell measurements, timing, memory, and limitations.
- [Compact results](benchmark-summary.tsv): estimates and reported confidence intervals.
- [Build and binary record](reproducibility.md): build variants and executable hashes.
- [Complete-proof experiment and reproduction commands](https://github.com/quangvdao/lambda_vm/blob/c40323c85432d939567a96b6b00ec1e7f7067db0/docs/experiments/cpu_rs_anchors_v1.md).

From the repository root, run:

```console
python3 scripts/check_lambda_measurements.py
```

The checker verifies byte arithmetic, four-cell proof sizes, round counts,
and paired mean proving/verification contrasts from the supplied TSV files.
It does not rerun the prover or regenerate the reported bootstrap intervals.
The principal certificate checker also calls this check, separately from
the exact mathematical CPU error certificate.

### Reproduce the CPU denominator

At LambdaVM revision `c40323c85432d939567a96b6b00ec1e7f7067db0`, place
[profile_size_breakdown.rs](profile_size_breakdown.rs) in
`bin/cli/examples/profile_size_breakdown.rs`. From that checkout, run:

```console
cargo run --locked -p cli --release --example profile_size_breakdown -- /path/to/control.rkyv /path/to/cpu-rs-anchors-v1.rkyv
```

Use the verified proof pair identified by the SHA-256 hashes in
`measurement.json`. The extractor deserializes each VM proof and serializes
its entire CPU `StarkProof`, including the added evaluations. It also measures
a singleton-CPU VM proof and subtracts an empty VM wrapper. Both methods give
1,233,024 and 1,173,192 bytes; the wrapper occupies 176 bytes in each arm.
The CPU saving is therefore 59,832 / 1,233,024 = 4.85246%.
This extraction does not rerun the prover or verifier. The proof files are
retained by the authors and are not vendored here; the pinned fork documents
how to generate and verify the benchmark.

## Workload and implementation

The implementation lives on the authors' fork, not the upstream release:
[implementation 7310d1e8](https://github.com/quangvdao/lambda_vm/commit/7310d1e8ad1cf7818a749731db2e3930c4df6627),
with [measurement record c40323c8](https://github.com/quangvdao/lambda_vm/commit/c40323c85432d939567a96b6b00ec1e7f7067db0).
The source baseline is 8064a8efee4bd3edc9f064337d4e1d8bad54ae1a.

Both arms use the same corrected `bench_32k.s` assembly program, identical
ELF, and empty input. The CPU trace has 32,768 rows and the proof contains
26 subproofs. The profile enforces one CPU chunk of that size; this is not
a claim about arbitrary executions or a workload-wide mean.

The fixed field is cubic Goldilocks, blowup is two, grinding is 20 bits,
and the terminal codeword length is 256. The CPU retains 51 DEEP terms
and powers degree 50. The paper's 128.063-bit bound is local to the changed
CPU component, not a new complete-VM soundness theorem.

## Timing interpretation

On an Apple M4 Max with 16 threads, the normal-grinding actual-versus-control
proving contrast is -15.2 ms, with reported 95% interval [-49.4, +18.9] ms
over 20 paired rounds. Whole verification changes by +0.02 ms
[-0.62, +0.52] ms over 50 paired rounds. Neither resolves an end-to-end
latency change on this benchmark.

The extra arithmetic is real: diagnostic no-grinding runs record
+264.4 million retired instructions overall, about +0.1845%.
Single-thread component measurements attribute roughly 305 ms to the
added evaluation and DEEP work. Those diagnostic runs are not estimates
of a 16-thread latency penalty. The largest new transient buffer is 3 MiB.

The supplied overhead report calls the actual normal-grinding arm
"production" to distinguish it from timing counterfactuals. All these
profiles were run on the experimental fork. The 208-query/no-anchor cell
is uncertified and must not be used as a protocol profile.

## Data provenance

The Markdown overhead report, reproduction record, and eight TSV files were
supplied with the experiment and are retained unchanged. The TSVs include
normal and no-grinding process runs, component markers, and codec samples.
Measurement-only source snapshots and raw process logs are retained by the
experiment authors; they are not included here. The release CLI source and
complete-proof reproduction instructions are available at the pinned fork.

Peak-memory and codec observations have different evidentiary strength from
the paired timing contrasts. See the report before using them in comparisons.
