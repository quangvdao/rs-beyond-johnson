# ZisK compressed-final proof-size experiment

This bundle records an actual ZisK `v1.2.0-alpha` minimal proof and a verified
54-to-51-query revision. The measured native serialization shrinks from
**286,013 bytes** to **272,783 bytes**: **13,230 bytes (4.625663868426%)**.

`proof.bin` is ZisK's native `zisk_common::Proof`, encoded by bincode 2 with
`bincode::config::standard()`. This is the headline metric. The flat field-vector
sizes, 254,032 and 242,272 bytes, are included only as a layout diagnostic; they
are not the native serialized file sizes.

## What was run

- ZisK release/tag commit: `fbbc69bcd2ea9a78d1a438b4a897bc48ff0b00a3`.
- Pinned Proofman commit: `0f3fef8cd1897df469532996e72e0c84ef69d6fb`.
- CPU-only macOS arm64 release binary; official `1.2.0-alpha` proving key.
- Benchmark: `elf-regressions/prebuilt-elfs/cpp_static_init.elf`, SHA-256
  `29f81d9d49b420d4c89b1cacb0aba7b9e9448fad7a94b02de55ec6d71913a476`,
  no input, 679 execution steps.
- Proof flavor: `Minimal`, i.e. the actual Poseidon1
  `vadcop_final_compressed` proof.

The baseline was generated with:

```sh
cargo-zisk-dev program-setup -e elf-regressions/prebuilt-elfs/cpp_static_init.elf
cargo-zisk-dev prove -e elf-regressions/prebuilt-elfs/cpp_static_init.elf \
  -o baseline-q54/proof.bin --minimal --verify-proofs -vv
cargo-zisk verify -p baseline-q54/proof.bin -vv
```

The baseline generation log contains `GENERATE_VADCOP_FINAL_COMPRESSED_PROOF`
and an internal verification success. The separate verification log ends with
`STARK proof was verified`.

## Q51 construction and verification

The Q51 artifact was produced from that generated proof by retaining the first
51 entries in every query-indexed values/path array. The converter preserves
the exact publics, commitments, evaluations, shared partial-Merkle-tree tables,
FRI commitments, final polynomial, and proof-of-work nonce. This is valid because
the query permutation is sampled after those transcript values and the first 51
queries are the exact prefix of the 54-query stream.

The matching verifier changes only generated parameter `n_fri_queries` from 54
to 51; the matching proving-key `starkinfo.json` changes only `nQueries` from 54
to 51. See `proofman-verifier.patch`, `zisk-cargo.patch`, and
`truncate_fri_queries.rs`.

The converter performs the full final-compressed verification before saving,
then reloads the saved native `Proof` and performs the same verification again.
Starting with pinned sibling checkouts, reproduce that check as follows (replace
the first value with this bundle's absolute path):

```sh
ZISK_EXPERIMENT_BUNDLE=/absolute/path/to/zisk-compressed-final
git clone https://github.com/0xPolygonHermez/pil2-proofman.git pil2-proofman-v1.2-measure
git -C pil2-proofman-v1.2-measure checkout 0f3fef8cd1897df469532996e72e0c84ef69d6fb
git -C pil2-proofman-v1.2-measure apply "$ZISK_EXPERIMENT_BUNDLE/proofman-verifier.patch"
git clone https://github.com/0xPolygonHermez/zisk.git zisk
git -C zisk checkout fbbc69bcd2ea9a78d1a438b4a897bc48ff0b00a3
git -C zisk apply "$ZISK_EXPERIMENT_BUNDLE/zisk-cargo.patch"
mkdir -p zisk/common/examples
cp "$ZISK_EXPERIMENT_BUNDLE/truncate_fri_queries.rs" zisk/common/examples/
cd zisk
MAKEFLAGS=-e SDKPATH=/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk \
  cargo build --release -p zisk-common --example truncate_fri_queries
target/release/examples/truncate_fri_queries \
  "$ZISK_EXPERIMENT_BUNDLE/baseline-q54/proof.bin" \
  "$ZISK_EXPERIMENT_BUNDLE/reproduced-q51.bin"
shasum -a 256 "$ZISK_EXPERIMENT_BUNDLE/reproduced-q51.bin"
```

The final checksum must be
`293e3badd207000f95d87f760e4e8ea9f2d8e923f2cb6c26312045439de613a0`.
The ZisK checkout patches `proofman-verifier` to the pinned sibling Proofman
checkout. On a Command Line Tools-only macOS installation, `MAKEFLAGS=-e` lets
the valid `SDKPATH` override Proofman's full-Xcode default.

To regenerate the Q54 baseline, download the official macOS-arm64 release and
public proving key:

```sh
curl -fLO https://github.com/0xPolygonHermez/zisk/releases/download/v1.2.0-alpha/cargo_zisk_darwin_arm64.tar.gz
curl -fLO https://storage.googleapis.com/zisk-setup/zisk-provingkey-1.2.0-alpha.tar.gz
mkdir -p /absolute/path/to/zisk-bin /absolute/path/to/ziskhome
tar -xzf cargo_zisk_darwin_arm64.tar.gz -C /absolute/path/to/zisk-bin
tar -xzf zisk-provingkey-1.2.0-alpha.tar.gz -C /absolute/path/to/ziskhome
```

The released binaries require Homebrew `libsodium`, `gmp`, `libomp`, and
`open-mpi`; building the local verifier also requires `nlohmann-json`. Put
`/absolute/path/to/zisk-bin/bin` on `PATH`, set
`ZISK_HOME=/absolute/path/to/ziskhome`, and run the three baseline commands
shown above from the pinned ZisK checkout.

This experiment does not claim a Q51 proving-time measurement or a second full
Q51 prover execution. It claims the serialized size of a canonically shortened
real proof and successful acceptance by the matching Q51 verifier.

The archived logs replace the measurement host name and machine-local checkout
and proving-key paths with descriptive placeholders. The substantive command
output is unchanged.

## Artifacts

- `measurements.json`: machine-readable result and provenance.
- `baseline-q54/proof.bin`: generated native Q54 proof.
- `baseline-q54/prove.log`: complete generation and internal-verification log.
- `baseline-q54/verify.log`: separate saved-proof verification log.
- `baseline-q54/vadcop_final_compressed.starkinfo.json`: official Q54 parameters.
- `revised-q51/proof.bin`: verified native Q51 proof.
- `revised-q51/verify-and-convert.log`: metadata assertions plus in-memory and
  reload verification.
- `revised-q51/vadcop_final_compressed.starkinfo.json`: Q51 prover parameters.
- `truncate_fri_queries.rs`: audited native proof converter.
- `proofman-verifier.patch`: applyable one-line Q51 verifier change.
- `zisk-cargo.patch`: applyable Cargo override to the pinned sibling verifier.
