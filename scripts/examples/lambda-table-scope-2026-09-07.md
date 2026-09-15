# LambdaVM all-table anchored-MCA scope (2026-09-07)

Pinned source: [8064a8efee4b](https://github.com/yetanotherco/lambda_vm/tree/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a). This is a source-derived inventory and exact modular arithmetic check, not a runtime patch, measured proof benchmark, or whole-VM audit.

The current default CLI profile is cubic Goldilocks, blowup 2 (rate 1/2), 128-bit target, 20-bit grinding, 219 queries, and terminal log-degree 7. The inventory has 28 physical trace schemas. LOCAL_TO_GLOBAL is committed in an epoch-local Memory-bus AIR and again in a commitment-bound global-bus AIR, so the complete role table has 29 rows.

| family | schemas | fixed versus variable heights |
|---|---|---|
| CPU and control | CPU, CPU32, DECODE, BRANCH, HALT, HINT, COMMIT, REGISTER | mostly execution-dependent; CPU/CPU32 split at 2^19; DECODE is ELF-dependent; HALT=1 and REGISTER=128 |
| integer arithmetic and comparison | BITWISE, LT, SHIFT, EQ, BYTEWISE, MUL, DVRM | BITWISE=2^20; the other tables are execution-dependent and split at 2^19 or 2^20 |
| loads, stores, and memory | STORE, LOAD, MEMW, MEMW_A, MEMW_R, PAGE, GLOBAL_MEMORY, LOCAL_TO_GLOBAL | PAGE/GLOBAL_MEMORY=2^18 per page; the remaining tables are execution-dependent |
| cryptographic accelerators | KECCAK, KECCAK_RND, KECCAK_RC, ECSM, ECDAS | KECCAK_RC=32; other heights depend on accelerator calls (KECCAK_RND pads 24 rows per operation) |

### Complete AIR-role inventory

The `pre` count is the verifier-bound prefix; `main` is the dynamic committed suffix that must be opened at the two anchors.

| AIR role | total/pre/main | bus/aux | base+LogUp constraints | degree/parts | DEEP terms (powers degree) | height |
|---|---:|---:|---:|---:|---:|---|
| CPU | 38/0/38 | 20/10 | 39+10=49 | 3/2 | 51 (50) | variable; power-of-two, min 4; split at 2^19 |
| BITWISE | 21/11/10 | 10/5 | 0+5=5 | 3/2 | 29 (28) | fixed 2^20 |
| LT | 17/0/17 | 9/5 | 6+5=11 | 3/2 | 25 (24) | variable; power-of-two, min 4; split at 2^20 |
| SHIFT | 29/0/29 | 18/9 | 19+9=28 | 3/2 | 41 (40) | variable; power-of-two, min 4; split at 2^20 |
| EQ | 12/0/12 | 6/3 | 4+3=7 | 3/2 | 18 (17) | variable; power-of-two, min 4; split at 2^20 |
| BYTEWISE | 26/0/26 | 9/5 | 0+5=5 | 3/2 | 34 (33) | variable; power-of-two, min 4; split at 2^20 |
| STORE | 16/0/16 | 10/5 | 6+5=11 | 3/2 | 24 (23) | variable; power-of-two, min 4; split at 2^20 |
| CPU32 | 38/0/38 | 23/12 | 32+12=44 | 3/2 | 53 (52) | variable; power-of-two, min 4; split at 2^19 |
| MEMW | 49/0/49 | 26/13 | 15+13=28 | 3/2 | 65 (64) | variable; power-of-two, min 4; split at 2^19 |
| MEMW_A | 29/0/29 | 20/10 | 8+10=18 | 3/2 | 42 (41) | variable; power-of-two, min 4; split at 2^19 |
| MEMW_R | 10/0/10 | 7/4 | 3+4=7 | 3/2 | 17 (16) | variable; power-of-two, min 4; split at 2^20 |
| LOAD | 18/0/18 | 5/3 | 13+3=16 | 3/2 | 24 (23) | variable; power-of-two, min 4; split at 2^20 |
| DECODE | 6/5/1 | 1/1 | 0+1=1 | 2/1 | 9 (8) | ELF-dependent; nextpow2(instructions+1), min 2 |
| MUL | 26/0/26 | 24/12 | 8+12=20 | 3/2 | 41 (40) | variable; power-of-two, min 4; split at 2^20 |
| DVRM | 34/0/34 | 34/17 | 19+17=36 | 3/2 | 54 (53) | variable; power-of-two, min 4; split at 2^19 |
| BRANCH | 14/0/14 | 6/3 | 5+3=8 | 3/2 | 20 (19) | variable; power-of-two, min 4; split at 2^20 |
| HALT | 4/0/4 | 36/18 | 0+18=18 | 3/2 | 25 (24) | fixed 1 |
| HINT | 41/0/41 | 27/14 | 1+14=15 | 3/2 | 58 (57) | variable; next power-of-two, min 4 |
| COMMIT | 19/0/19 | 18/9 | 8+9=17 | 3/2 | 31 (30) | variable; next power-of-two, min 4 |
| PAGE | 5/2/3 | 3/2 | 0+2=2 | 3/2 | 10 (9) | fixed 2^18 per page |
| REGISTER | 5/2/3 | 2/1 | 0+1=1 | 3/2 | 9 (8) | fixed 128 |
| KECCAK | 511/0/511 | 134/67 | 51+67=118 | 3/2 | 581 (580) | variable; next power-of-two, min 4 |
| KECCAK_RND | 1480/0/1480 | 1031/516 | 140+516=656 | 3/2 | 1999 (1998) | variable; nextpow2(24*operations), min 4 |
| KECCAK_RC | 10/9/1 | 1/1 | 0+1=1 | 2/1 | 13 (12) | fixed 32 |
| ECSM | 667/0/667 | 579/290 | 413+290=703 | 3/2 | 960 (959) | variable; next power-of-two, min 4 |
| ECDAS | 521/0/521 | 388/194 | 200+194=394 | 3/2 | 718 (717) | variable; next power-of-two, min 4 |
| GLOBAL_MEMORY | 4/2/2 | 2/1 | 0+1=1 | 3/2 | 8 (7) | fixed 2^18 per touched page |
| L2G_MEMORY | 9/0/9 | 6/3 | 1+3=4 | 3/2 | 15 (14) | variable; next power-of-two, min 1 |
| L2G_GLOBAL | 9/0/9 | 2/1 | 0+1=1 | 3/2 | 13 (12) | same trace height as L2G_MEMORY |

The same physical schemas also have the following preprocessing variants. Their total, auxiliary, and DEEP widths and constraints are unchanged; only the pre/main split and anchor bytes differ.

| variant | schema | total/pre/main | two-anchor bytes | height |
|---|---|---:|---:|---|
| PAGE_PRIVATE | PAGE | 5/1/4 | 192 | fixed 2^18 per private-input page |
| REGISTER_CONTINUATION | REGISTER | 5/3/2 | 96 | fixed 128 |
| GLOBAL_MEMORY_PRIVATE | GLOBAL_MEMORY | 4/1/3 | 144 | fixed 2^18 per private-input page |

Here `total/pre/main` separates the full current-row trace width, verifier-fixed preprocessed prefix, and proof-dependent committed main suffix. With `a` early anchors, preprocessed polynomials remain DEEP terms but need no anchor payload: every checked threshold satisfies `A>T+a`, hence an extracted degree-at-most-`T+a` polynomial agreeing with the fixed degree-less-than-`T` word at `A` points is identical to it.

All current transition metadata has zero end exemptions. Every AIR role has a nonempty bus and therefore one LogUp boundary constraint and one next-row OOD value (the accumulator). Thus the exact DEEP powers degree is `total + aux + composition_parts`; it is 17 for EQ, at most 64 for the ordinary CPU/memory/control tables, and 580/1998/959/717 for KECCAK/KECCAK_RND/ECSM/ECDAS.

## Exact candidates

The least-invasive recommendation keeps LambdaVM's current single-challenge powers batching and default 20-bit grinding. At `T=32768`, the bounded ordinary-table screen selects among six fixed agreement/support profiles. At `T=2048`, one early vector anchor, `A=2881`, and `(m,M,mu)=(15,3,20)` give 213 queries for all four crypto tables. Independent-coefficient rows are retained below as exploratory alternatives because the source documents that challenge sampling matters in recursion.

The following rows use `tune_first_order_mca.py` directly for the initial curve, every binary fold, and the appropriate `T+a+1` anchor-list certificate. For each displayed fixed support and agreement threshold, the query count is the smallest integer making the changed-component sum strictly below `2^-128`; this is not a global parameter optimum.

| profile | table | batching | anchors/grind | layout/curve degree | queries | removed | net raw bytes | changed-component bits |
|---|---|---|---:|---:|---:|---:|---:|---:|
| noncrypto_at_trace_rows_32768 | CPU | powers | 2/20 | 50/50 | 211 | 8 | 40224 | 128.303 |
| noncrypto_at_trace_rows_32768 | LT | powers | 2/20 | 24/24 | 211 | 8 | 36624 | 128.324 |
| noncrypto_at_trace_rows_32768 | SHIFT | powers | 2/20 | 40/40 | 211 | 8 | 39120 | 128.311 |
| noncrypto_at_trace_rows_32768 | EQ | powers | 2/20 | 17/17 | 211 | 8 | 35456 | 128.330 |
| noncrypto_at_trace_rows_32768 | BYTEWISE | powers | 2/20 | 33/33 | 211 | 8 | 37344 | 128.317 |
| noncrypto_at_trace_rows_32768 | STORE | powers | 2/20 | 23/23 | 211 | 8 | 36544 | 128.325 |
| noncrypto_at_trace_rows_32768 | CPU32 | powers | 2/20 | 52/52 | 211 | 8 | 40992 | 128.302 |
| noncrypto_at_trace_rows_32768 | MEMW | powers | 2/20 | 64/64 | 211 | 8 | 42256 | 128.292 |
| noncrypto_at_trace_rows_32768 | MEMW_A | powers | 2/20 | 41/41 | 211 | 8 | 39504 | 128.311 |
| noncrypto_at_trace_rows_32768 | MEMW_R | powers | 2/20 | 16/16 | 211 | 8 | 35680 | 128.331 |
| noncrypto_at_trace_rows_32768 | LOAD | powers | 2/20 | 23/23 | 211 | 8 | 35936 | 128.325 |
| noncrypto_at_trace_rows_32768 | DECODE | powers | 2/20 | 8/8 | 211 | 8 | 37904 | 128.337 |
| noncrypto_at_trace_rows_32768 | MUL | powers | 2/20 | 40/40 | 211 | 8 | 40032 | 128.311 |
| noncrypto_at_trace_rows_32768 | DVRM | powers | 2/20 | 53/53 | 211 | 8 | 42592 | 128.301 |
| noncrypto_at_trace_rows_32768 | BRANCH | powers | 2/20 | 19/19 | 211 | 8 | 35616 | 128.328 |
| noncrypto_at_trace_rows_32768 | HINT | powers | 2/20 | 57/57 | 211 | 8 | 42000 | 128.298 |
| noncrypto_at_trace_rows_32768 | COMMIT | powers | 2/20 | 30/30 | 211 | 8 | 38320 | 128.319 |
| noncrypto_at_trace_rows_32768 | L2G_MEMORY | powers | 2/20 | 14/14 | 211 | 8 | 35216 | 128.332 |
| noncrypto_at_trace_rows_32768 | L2G_GLOBAL | powers | 2/20 | 12/12 | 211 | 8 | 34448 | 128.334 |
| crypto_at_trace_rows_2048 | KECCAK | powers | 2/20 | 580/580 | 216 | 3 | 15912 | 128.136 |
| crypto_at_trace_rows_2048 | KECCAK_RND | powers | 2/20 | 1998/1998 | 216 | 3 | 80568 | 128.125 |
| crypto_at_trace_rows_2048 | ECSM | powers | 2/20 | 959/959 | 216 | 3 | 48024 | 128.133 |
| crypto_at_trace_rows_2048 | ECDAS | powers | 2/20 | 717/717 | 216 | 3 | 34200 | 128.135 |
| crypto_at_trace_rows_4096 | KECCAK | powers | 2/20 | 580/580 | 216 | 3 | 17328 | 128.077 |
| crypto_at_trace_rows_4096 | KECCAK_RND | powers | 2/20 | 1998/1998 | 216 | 3 | 81984 | 128.054 |
| crypto_at_trace_rows_4096 | ECSM | powers | 2/20 | 959/959 | 216 | 3 | 49440 | 128.071 |
| crypto_at_trace_rows_4096 | ECDAS | powers | 2/20 | 717/717 | 216 | 3 | 35616 | 128.075 |
| actual_fixed_page_height | PAGE | powers | 2/20 | 9/9 | 217 | 2 | 13488 | 128.435 |
| actual_fixed_page_height | PAGE_PRIVATE | powers | 2/20 | 9/9 | 217 | 2 | 13440 | 128.435 |
| actual_fixed_page_height | GLOBAL_MEMORY | powers | 2/20 | 7/7 | 217 | 2 | 13408 | 128.449 |
| actual_fixed_page_height | GLOBAL_MEMORY_PRIVATE | powers | 2/20 | 7/7 | 217 | 2 | 13360 | 128.449 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | CPU | powers | 2/20 | 50/50 | 210 | 9 | 45480 | 128.458 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | LT | powers | 2/20 | 24/24 | 209 | 10 | 45984 | 128.006 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | SHIFT | powers | 2/20 | 40/40 | 210 | 9 | 44184 | 128.477 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | EQ | powers | 2/20 | 17/17 | 209 | 10 | 44464 | 128.016 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | BYTEWISE | powers | 2/20 | 33/33 | 210 | 9 | 42168 | 128.490 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | STORE | powers | 2/20 | 23/23 | 209 | 10 | 45872 | 128.007 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | CPU32 | powers | 2/20 | 52/52 | 210 | 9 | 46344 | 128.454 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | MEMW | powers | 2/20 | 64/64 | 210 | 9 | 47832 | 128.431 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | MEMW_A | powers | 2/20 | 41/41 | 210 | 9 | 44616 | 128.475 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | MEMW_R | powers | 2/20 | 16/16 | 209 | 10 | 44720 | 128.017 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | LOAD | powers | 2/20 | 23/23 | 209 | 10 | 45136 | 128.007 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | DECODE | powers | 2/20 | 8/8 | 209 | 10 | 47392 | 128.029 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | MUL | powers | 2/20 | 40/40 | 210 | 9 | 45192 | 128.477 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | DVRM | powers | 2/20 | 53/53 | 210 | 9 | 48120 | 128.452 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | BRANCH | powers | 2/20 | 19/19 | 209 | 10 | 44688 | 128.013 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | HINT | powers | 2/20 | 57/57 | 210 | 9 | 47496 | 128.444 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | COMMIT | powers | 2/20 | 30/30 | 210 | 9 | 43224 | 128.496 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | L2G_MEMORY | powers | 2/20 | 14/14 | 209 | 10 | 44128 | 128.020 |
| least_invasive_ordinary_powers_at_trace_rows_32768 | L2G_GLOBAL | powers | 2/20 | 12/12 | 209 | 10 | 43168 | 128.023 |
| least_invasive_crypto_powers_one_anchor_at_trace_rows_2048 | KECCAK | powers | 1/20 | 580/580 | 213 | 6 | 68616 | 128.128 |
| least_invasive_crypto_powers_one_anchor_at_trace_rows_2048 | KECCAK_RND | powers | 1/20 | 1998/1998 | 213 | 6 | 267696 | 128.125 |
| least_invasive_crypto_powers_one_anchor_at_trace_rows_2048 | ECSM | powers | 1/20 | 959/959 | 213 | 6 | 144072 | 128.127 |
| least_invasive_crypto_powers_one_anchor_at_trace_rows_2048 | ECDAS | powers | 1/20 | 717/717 | 213 | 6 | 105912 | 128.127 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | CPU | independent | 2/20 | 50/1 | 207 | 12 | 61248 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | LT | independent | 2/20 | 24/1 | 207 | 12 | 55344 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | SHIFT | independent | 2/20 | 40/1 | 207 | 12 | 59376 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | EQ | independent | 2/20 | 17/1 | 207 | 12 | 53472 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | BYTEWISE | independent | 2/20 | 33/1 | 207 | 12 | 56640 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | STORE | independent | 2/20 | 23/1 | 207 | 12 | 55200 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | CPU32 | independent | 2/20 | 52/1 | 207 | 12 | 62400 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | MEMW | independent | 2/20 | 64/1 | 207 | 12 | 64560 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | MEMW_A | independent | 2/20 | 41/1 | 207 | 12 | 59952 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | MEMW_R | independent | 2/20 | 16/1 | 207 | 12 | 53760 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | LOAD | independent | 2/20 | 23/1 | 207 | 12 | 54336 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | DECODE | independent | 2/20 | 8/1 | 207 | 12 | 56880 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | MUL | independent | 2/20 | 40/1 | 207 | 12 | 60672 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | DVRM | independent | 2/20 | 53/1 | 207 | 12 | 64704 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | BRANCH | independent | 2/20 | 19/1 | 207 | 12 | 53760 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | HINT | independent | 2/20 | 57/1 | 207 | 12 | 63984 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | COMMIT | independent | 2/20 | 30/1 | 207 | 12 | 57936 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | L2G_MEMORY | independent | 2/20 | 14/1 | 207 | 12 | 53040 | 128.300 |
| exploratory_ordinary_independent_coefficients_at_trace_rows_32768 | L2G_GLOBAL | independent | 2/20 | 12/1 | 207 | 12 | 51888 | 128.300 |
| exploratory_wide_crypto_independent_coefficients_at_trace_rows_32768 | KECCAK | independent | 2/20 | 580/1 | 207 | 12 | 162192 | 128.300 |
| exploratory_wide_crypto_independent_coefficients_at_trace_rows_32768 | KECCAK_RND | independent | 2/20 | 1998/1 | 207 | 12 | 560352 | 128.300 |
| exploratory_wide_crypto_independent_coefficients_at_trace_rows_32768 | ECSM | independent | 2/20 | 959/1 | 207 | 12 | 313104 | 128.300 |
| exploratory_wide_crypto_independent_coefficients_at_trace_rows_32768 | ECDAS | independent | 2/20 | 717/1 | 207 | 12 | 236784 | 128.300 |

For existing powers batching at `T=2048`, the selected one-anchor crypto profile removes six queries at default grinding. Its exact net savings are 68,616 bytes for KECCAK, 267,696 for KECCAK_RND, 144,072 for ECSM, and 105,912 for ECDAS. Since any at-or-above-Johnson half-rate agreement needs at least 216 queries from the query term alone, 213 is a genuine beyond-Johnson reduction.

For independent coefficients at `T=32768`, the exploratory bounded screen selected `A=45600` and `(m,M,mu)=(38,11,52)`. Every eligible ordinary and wide-crypto row shown for this profile reaches 207 queries; this is the best screened point, not a global optimum. The lower-agreement `A=45520`, max-`m=48` probe regressed to 208 queries because its fixed error increased.

At the actual fixed PAGE/GLOBAL_MEMORY height `T=2^18`, both ordinary and private-input variants admit 217 queries and positive modeled savings. Private pages have one additional dynamic main column, so their net savings are 48 bytes smaller. At the actual fixed BITWISE height `T=2^20`, the bounded support `(12,3,16)` gives only 127.309 fixed-error bits with powers degree 28, so queries cannot repair it. Independent random DEEP coefficients reduce the MCA curve degree to one; the same exact support gives 131.723 fixed-error bits and 217 queries. This affine option adds no proof bytes, but it is a protocol/code change and must be domain-separated and verifier-replayed.

The wide crypto tables are feasible only on smaller shards under powers batching in this first screen. At `T=2048`, all four admit 217 queries and remain net-positive despite wide anchors. At `T=4096`, KECCAK, ECSM, and ECDAS remain positive at 217 while KECCAK_RND needs 219. Independent DEEP coefficients remove the width-dependent powers degree and give the 207-query path at `T=32768` recorded above.

## Existing grinding tradeoff

LambdaVM already implements a `grinding_factor`, but the current CLI exposes only blowup and the current `VmAirs` construction passes one `ProofOptions` value to every AIR. Each table transcript fork performs its own nonce search. Raising grinding from 20 to 21 or 22 therefore multiplies expected nonce-search hashes by 2 or 4 for every table proof, not just a selected table. The nonce remains one `u64`, so the increment changes expected proving work but adds no proof bytes. No end-to-end runtime effect is inferred here.

| table/profile | grinding 21: queries/net bytes/bits | grinding 22: queries/net bytes/bits |
|---|---:|---:|
| CPU, T=32768 | 208 / 55992 / 128.426 | 206 / 66504 / 128.394 |
| EQ, T=32768 | 208 / 48968 / 128.489 | 206 / 57976 / 128.456 |
| MEMW, T=32768 | 208 / 58984 / 128.400 | 206 / 70136 / 128.369 |
| KECCAK, T=2048, one anchor | 211 / 95576 / 128.112 | 209 / 122536 / 128.097 |
| KECCAK_RND, T=2048, one anchor | 211 / 368768 / 128.110 | 209 / 469840 / 128.095 |
| ECSM, T=2048, one anchor | 211 / 197432 / 128.112 | 209 / 250792 / 128.096 |
| ECDAS, T=2048, one anchor | 211 / 145384 / 128.112 | 209 / 184856 / 128.097 |

These are size/work tradeoffs rather than the default recommendation. The default-grinding powers rows above require fewer protocol changes.

## Batching evidence and scope

The prover and verifier source each sample one cubic-extension `gamma` and generate all DEEP coefficients as `1,gamma,...`; the source gives no design rationale for that choice. Separately, the default transcript documents that software challenge expansion previously dominated recursion-guest sampling cost, while Keccak is a precompile and a buffered squeeze usually supplies one cubic challenge. It is therefore reasonable to expect a large independent coefficient vector to increase recursion cost, but this is an inference and has not been benchmarked. The independent rows remain exploratory; the powers rows are the concrete least-invasive recommendations.

## Protocol and transcript interface

The implementation first absorbs the statement, then every preprocessed and main root in table order, samples the two shared LogUp challenges, forks the transcript by table index, absorbs that table's auxiliary root and bus contribution, samples beta, absorbs the composition root, samples the OOD point, absorbs current-row values, the pruned next-row accumulator, and composition-part values, then runs powers-DEEP/FRI, grinding, and row-paired queries. A multi-table anchor extension inserts each changed table's configured one or two points and dynamic main values after the global main-root barrier and before the shared LogUp challenges. Points may be reused only when their rejection domains and conditional sampling laws agree. The point order and table/column order must be canonical and verifier-replayed.

With `a` anchors, the reconstructed main degree is at most `T+a`, the list certificate has dimension `T+a+1`, and the checker charges collision `binom(Lambda,2)*((T+a)/(q-n-a+1))^a`. Thus the selected one-anchor crypto rows use dimension `T+2`, collision `binom(Lambda,2)*(T+1)/(q-n)`, one extension-field value per dynamic main column, and one OOD/anchor-coincidence rejection.

For maximum constraint degree `d`, `c` composition parts, trace height `T`, and maximum transition end-exemption `e`, the two-anchor checker uses the conservative cleared residual degree `max((d+1)T+2d+e, (c+1)T+c-1)`. Here every `e=0`; all degree-3/two-part tables recover `4T+6`, while DECODE and KECCAK_RC use `3T+4`. The one-anchor rows conservatively retain this same degree, although the first branch can tighten to `(d+1)T+d+e`. A future shifted or multi-boundary AIR must update this formula and the inventory before inheriting any row.

Wire proofs use rkyv with 64-bit relative pointers. `MultiProof` stores a vector of per-table `StarkProof` objects, and query/opening vectors are independent. Byte numbers therefore count exact field elements and Merkle hashes under the current row-paired format, excluding rkyv vector descriptors, alignment, and archive metadata.

LOCAL_TO_GLOBAL needs an extra cross-proof rule. The source checks equality of its dynamic main root between each epoch proof and the global proof. Root equality alone does not force two list recoveries to select the same nearby polynomial. A modified continuation must derive one domain-separated anchor pair after that root is fixed, carry one pair of claimed vectors, and absorb/check their explicit equality in both transcript branches. Both branches must use the same `T` and one candidate family at agreement `min(A_epoch,A_global)`; the displayed rows use identical `T,A`. The table rows above charge the anchor payload separately to each role, so their local byte gains are conservative if the continuation bundle serializes the shared vector only once. PAGE and GLOBAL_MEMORY share verifier-known preprocessing roots, not a dynamic main root, and therefore do not need this extra equality rule.

## Pinned primary-source map

- [table modules and production split caps](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/prover/src/tables/mod.rs#L67-L101)
- [AIR ordering and proof roles](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/prover/src/lib.rs#L506-L675)
- [preprocessed PAGE/REGISTER/table variants](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/prover/src/lib.rs#L684-L862)
- [fixed BITWISE height](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/prover/src/tables/bitwise.rs#L90-L105)
- [fixed PAGE height](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/prover/src/tables/page.rs#L44-L55)
- [REGISTER padding rule](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/prover/src/tables/register.rs#L203-L225)
- [fixed KECCAK_RC height](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/prover/src/tables/keccak_rc.rs#L40-L50)
- [KECCAK_RND 24-row padding rule](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/prover/src/tables/keccak_rnd.rs#L240-L255)
- [all main/aux element accounting](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/prover/src/tables/trace_builder.rs#L4060-L4310)
- [LogUp packing, constraint degrees, and sole next-row column](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/crypto/stark/src/lookup.rs#L899-L1079)
- [shared transcript and per-table forks](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/crypto/stark/src/prover.rs#L3280-L3537)
- [beta, OOD words, and DEEP/FRI challenge timing](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/crypto/stark/src/prover.rs#L4435-L4578)
- [current one-gamma powers batching](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/crypto/stark/src/prover.rs#L2159-L2182)
- [verifier replay of powers batching](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/crypto/stark/src/verifier.rs#L1530-L1549)
- [recursion-sensitive buffered Keccak transcript](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/crypto/crypto/src/fiat_shamir/default_transcript.rs#L14-L38)
- [expected grinding work is about 2^grinding_factor](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/crypto/math-cuda/src/grinding.rs#L19-L29)
- [proof shape and authoritative rkyv note](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/crypto/stark/src/proof/stark.rs#L11-L145)
- [default cubic-Goldilocks option builder](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/crypto/stark/src/proof/options.rs#L77-L134)
- [CLI default blowup](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/bin/cli/src/main.rs#L151-L170)
- [continuation L2G/global AIR roles](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/prover/src/continuation.rs#L140-L258)
- [current L2G main-root equality check](https://github.com/yetanotherco/lambda_vm/blob/8064a8efee4bd3edc9f064337d4e1d8bad54ae1a/prover/src/lib.rs#L1015-L1043)

Exact rational values and certificate parameters are in the adjacent JSON artifact.
