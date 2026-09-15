# Reproducibility record

All binaries were release builds from source commit `c40323c85432d939567a96b6b00ec1e7f7067db0` using Rust/Cargo 1.94.0. The production implementation itself is commit `7310d1e8ad1cf7818a749731db2e3930c4df6627`.

The common build command was:

```sh
CARGO_TARGET_DIR=<target> cargo build --release -p cli
```

The source snapshot archive contains the measurement-only component timers and the codec example. Counterfactual builds changed these constants before rebuilding and copying each binary:

| Cell | `CPU_RS_ANCHORS_V1_CPU_QUERIES` | `CPU_RS_ANCHORS_V1_EARLY_OPENINGS` |
|---|---:|---:|
| Final/actual | 208 | 2 |
| Anchor only | 219 | 2 |
| Query only | 208 | 0 |

The no-grinding binaries additionally changed `canonical_proof_options().grinding_factor` from 20 to 0. For the control CLI path only, the measurement build selected the profile's canonical options at blowup 2 so that control also used grinding 0. These changes were reverted after copying the binaries.

## Binary hashes

| Binary | SHA-256 |
|---|---|
| `cli-final` | `ae1398ca2164e4bc9fb3d8e10c67faa214d8b642bdc09be9805707715c47fad4` |
| `cli-anchor-only` | `4d026669bbc9081488d987a6b0c69ff4a88d5439f8115bdf739a3b1191be4ef0` |
| `cli-query-only` | `3074828166e7ebc8654759dea4f86532d8204bfb05c5b80c3c37f36277e8d679` |
| `cli-timed-final` | `19fb7d9dbafb6f9fce0603840213c926143fca154bd7de40cce63e58a8c44f28` |
| `cli-timed-anchor-only` | `56ba1cd30c913b516c3ed8197c1c70bb4085619f0ede4f6ab1d05b10ca9cd9bf` |
| `cli-timed-query-only` | `440f37ab3a5d8000b6c741501641e83e8127c3c0d577c911dc2534f6d23cdeaa` |
| `cli-nogrind-final` | `4c5a59a813c2cb1761a2e0bcd3f92444f10721295268226d5c30ad37fd2ead8c` |
| `cli-nogrind-anchor-only` | `dbe0cb3bcc2badde5a209f9881c4f8ac86d9842420ca5b576ef13dc6baba6c79` |
| `cli-nogrind-query-only` | `20ed74a974a204cdcf540e872422f9a779a42c5ea6d629806884f0346dc1e8f7` |

The counterfactual and no-grinding binaries are measurement artifacts only. They are not protocol candidates and were not committed or pushed.
