# LambdaVM CPU Reed–Solomon anchor overhead

## Result

The production profile has no measurable end-to-end latency regression on this benchmark.

- Proving: the anchors do add real arithmetic work, but the 16-thread wall-time effect is hidden by table-level parallelism and normal run-to-run variance. The production change measured **−15.2 ms** with a paired 95% interval of **[−49.4, +18.9] ms** over 20 rounds per cell. A second run with grinding disabled for measurement produced the same conclusion: **−23.25 ms [−64.13, +8.44] ms**.
- Verification: the isolated CPU-table work becomes slightly faster overall. The average factorial anchor effect is **+0.188 ms**, while the average effect of 11 fewer queries is **−0.269 ms**, for a production net of **−0.081 ms [−0.117, −0.048] ms** in the measured components. Whole-CLI verification was unchanged at its coarser resolution: **+0.02 ms [−0.62, +0.52] ms**.
- Memory: the largest new deterministic buffer is **3.0 MiB transient** during CPU DEEP composition. Peak RSS is about 1.9 GiB and did not resolve this increment.
- Serialization: the two anchor vectors cost exactly **1,856 bytes**. Removing 11 CPU query records saves exactly **61,688 bytes**, so the net proof saving is still **59,832 bytes (0.162283%)**. Encode/decode effects are below 0.05 ms.

The practical conclusion is that the experiment trades a small amount of prover CPU work for 59.8 KB less proof data. It does not create a detectable prover wall-time penalty at 16 threads, and it slightly reduces the CPU portion of verification.

## Four-cell isolation

The benchmark crosses CPU query count with anchor presence:

| Cell | CPU queries | Anchors | Status |
|---|---:|---:|---|
| Control | 219 | 0 | production control |
| Anchor only | 219 | 2 | measurement-only counterfactual |
| Query only | 208 | 0 | measurement-only, uncertified counterfactual |
| Actual | 208 | 2 | production experiment |

All non-CPU tables remain at 219 queries. Each proof is generated and verified only by the binary with matching constants. The counterfactual cells are timing instruments, not proposed protocol profiles.

This factorial layout separates:

- anchor effect: average of `(anchor only − control)` and `(actual − query only)`;
- query effect: average of `(query only − control)` and `(actual − anchor only)`;
- interaction: difference between the two anchor effects;
- production net: `actual − control`.

Runs use a balanced four-order schedule so every cell rotates through each position.

## Proof size

| Cell | Bytes | Difference from control |
|---|---:|---:|
| Control | 36,868,888 | — |
| Anchor only | 36,870,744 | +1,856 |
| Query only | 36,807,200 | −61,688 |
| Actual | 36,809,056 | −59,832 |

The size effects are exactly additive. There is no serialization-size interaction between anchors and query count.

## Prover overhead

### End-to-end proof construction

The normal release benchmark used `RAYON_NUM_THREADS=16`, grinding factor 20, and 20 repetitions per cell.

| Cell | Mean CLI prove time | Median | Standard deviation |
|---|---:|---:|---:|
| Control | 1.5696 s | 1.5555 s | 0.0623 s |
| Anchor only | 1.5610 s | 1.5545 s | 0.0642 s |
| Query only | 1.5724 s | 1.5630 s | 0.0843 s |
| Actual | 1.5544 s | 1.5615 s | 0.0514 s |

The production contrast is **−15.2 ms [−49.4, +18.9] ms**. This interval includes zero. Process wall time agrees: **−16.0 ms [−49.5, +17.5] ms**.

Grinding dominates the short-run noise. Its CPU-table span ranged from below 1 ms to hundreds of milliseconds because it performs a random nonce search. A measurement-only grinding-factor-zero run therefore repeated the full 2×2 test for 16 rounds per cell. Its production contrast was **−23.25 ms [−64.13, +8.44] ms**, again with no detectable latency regression.

### Work added by the evaluations

The no-grinding run exposes work even when wall time stays flat:

| Counter | Anchor main effect | Query-count effect | Production net |
|---|---:|---:|---:|
| Retired instructions | +292.3 M [223.3, 359.9] | −27.9 M [−98.9, 40.8] | +264.4 M [181.0, 345.8] |
| Cycles elapsed | +207.9 M [35.4, 379.7] | +21.1 M [−95.6, 141.0] | +229.0 M [46.6, 421.7] |

The net instruction increase is about **0.1845%** of the 143.34-billion-instruction control run. It does not translate into a wall-time increase because the tables prove concurrently and the CPU table is not consistently the critical path.

Narrow timers locate the work:

- Two early evaluations cost **4.788 ms [4.617, 4.977] ms** of 16-thread wall time.
- The CPU DEEP span is heavily affected by concurrent table scheduling at 16 threads, so its paired wall-time estimate is not stable.
- A three-round single-thread isolation removes that contention. The median anchor effect is about **13.3 ms** for early evaluation plus **291.7 ms** for DEEP, or roughly **305 ms of serial anchor-specific work**.
- FRI query-list generation and Merkle opening construction are sub-millisecond prover operations here. The reduction from 219 to 208 queries does not produce a stable prover-time saving.

The single-thread figure is an attribution measurement, not the expected 16-thread latency penalty.

## Verifier overhead

The component run used 50 repetitions per cell. The verifier timers cover early transcript replay, CPU DEEP reconstruction, CPU FRI verification, and CPU trace/composition Merkle openings.

| Component | Anchor main effect | Query-count effect | Production net |
|---|---:|---:|---:|
| Early transcript and claims | +0.0028 ms | ~0 | +0.0028 ms |
| CPU DEEP reconstruction | +0.1947 ms | −0.0299 ms | +0.1648 ms |
| CPU FRI verification | −0.0005 ms | −0.1402 ms | −0.1407 ms |
| CPU Merkle openings | −0.0086 ms | −0.0994 ms | −0.1080 ms |
| **Measured component total** | **+0.1884 ms** | **−0.2695 ms** | **−0.0811 ms** |

Paired 95% intervals for the totals are:

- anchors: **[+0.1695, +0.2077] ms**;
- query reduction: **[−0.2976, −0.2450] ms**;
- production net: **[−0.1170, −0.0484] ms**.

There is a small interaction of **−0.0422 ms**, approximately **[−0.0807, −0.0040] ms**. The anchor overhead is **+0.2095 ms** at 219 queries and **+0.1673 ms** at 208 queries; equivalently, the query saving is **−0.2484 ms** without anchors and **−0.2906 ms** with anchors. The main-effect row above averages across the two levels.

The whole CLI reports milliseconds, and total verification is about 130 ms across all tables. At that level the production contrast is **+0.02 ms [−0.62, +0.52] ms**, so the 0.081 ms component saving is too small to see reliably end to end.

## Memory and codec overhead

The structural memory cost is more informative than process RSS:

- Each early evaluation temporarily holds two trace-length vectors of cubic field elements: inverse denominators plus scales. At 32,768 rows and 24 bytes per cubic element, that is about **1.5 MiB**. The two evaluations run sequentially.
- Anchored CPU DEEP allocates two LDE-length denominator arrays. `2 × 65,536 × 24` is exactly **3,145,728 bytes (3.0 MiB)**.
- The two retained 38-element evaluation vectors are small: 1,824 raw payload bytes and 1,856 serialized bytes including container overhead.

Fresh-process maximum RSS is about 1.9 GiB. In the no-grinding factorial run, the estimated anchor effect was **+1.70 MiB [−4.21, +7.76] MiB**, so RSS does not resolve the known 3 MiB transient allocation.

The CLI prove timer stops before rkyv serialization and file writing. The verify timer starts after file reading and rkyv deserialization, so codec work was measured separately with preloaded aligned buffers, 40 repetitions per proof:

| Operation | Control median | Actual median | Difference of medians |
|---|---:|---:|---:|
| rkyv archive access/validation | 0.0809 ms | 0.0796 ms | −0.0013 ms |
| Full decode | 1.9112 ms | 1.8983 ms | −0.0129 ms |
| Encode | 3.5748 ms | 3.5353 ms | −0.0395 ms |

The proof files were measured in separate, non-interleaved runs, so these are descriptive differences rather than paired causal estimates. They are operationally negligible. The slightly smaller actual proof is, if anything, marginally cheaper to encode and access.

## Method and limitations

- Source commit: `c40323c85432d939567a96b6b00ec1e7f7067db0`.
- Production implementation commit: `7310d1e8ad1cf7818a749731db2e3930c4df6627`.
- Build: Cargo release profile, Rust 1.94.0.
- Host: Apple M4 Max, 16 logical CPUs, 64 GiB RAM, macOS arm64.
- Confidence intervals: paired, round-level percentile bootstrap of the mean with a fixed seed.
- Sample sizes: normal prove 20/cell; whole verify 50/cell; component prove 16/cell; component verify 50/cell; no-grinding prove 16/cell; single-thread attribution 3/cell; codec 40/proof/operation.
- The no-grinding and single-thread runs are diagnostic counterfactuals. Production continues to use grinding factor 20 and 16-thread execution in the headline comparison.
- Peak RSS cannot reliably reveal allocations that are a few MiB against a roughly 1.9 GiB process peak. The 3.0 MiB figure comes from the exact allocated vector lengths and element size.
- The original CLI TSV left `user_seconds` and `sys_seconds` blank because macOS `/usr/bin/time` emits real/user/sys on one line. The raw logs preserve those fields; the final analysis reparsed them directly.

No measurement-only constants or timers were added to the pushed production branch.
