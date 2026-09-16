# Proximity Prize paper certificates and source concordance

Snapshot: September 15, 2026. This accompanies the detailed related-work subsection “Ideas from the Proximity Prize submissions.”

At this snapshot, the leading lower-track source is `cdb451f13fdc6c84f5fe363e77ee13a89bd30974` (PR #567, BitWonka). The earlier inventory through #517 is retained below, followed by the five subsequent promotions.

## Scope

This inventory includes all 77 promoted lower-track entries displayed by better.codes at the snapshot. The source audit inspected representative mechanisms in PRs #45, #64, #72, #122, #219, #241, #255, #343, #517 and #551–#567, and public source/attribution for additional ancestors. It did not independently rebuild every submission. Public acceptance records and a source audit are distinct from a fresh kernel replay.

The benchmark fixes length 2^18, scalar message dimension 2^17, interleaving width eight, 128 queries, and the sextic extension of KoalaBear (base cardinality 2130706433). Its lower-track contract bounds the algebraic reduction error by 2^-128 and separately scores the query error at the certified radius. The listed score is therefore not a full-protocol security claim. See [TargetLower](https://github.com/proximity-prize/proximity-prize/blob/bac8e813cd07f0b73ff7d68402e3b1944b0927f3/ProximityPrize/Benchmark/TargetLower.lean).

## Paper-only finite benchmark

Using only the paper's existing certificate formulas, the bounded search found the following attained points. Both meet the same reduction-error requirement as the prize. Neither is claimed optimal or submitted to the prize verifier.

| Method | Required agreements A | Error radius used for scoring | MCA numerator E | List bound Lambda | Score (bits) |
|---|---:|---|---:|---:|---:|
| Paper's ordinary Johnson transfer | 185372 | 76772/262144 | 168519951717387772 | 5792 | 63.99 |
| Paper's first-order transfer | 183210 | 78934/262144 | 274498710692409102 | 285674919 | 66.15 |
| Promoted #567, for comparison | 181284 | 331206655/1073741824 | 274980720549750805 | 7561644282 | 68.11 |

The exact common reduction budget is

```text
floor(2130706433^6 / 2^128) = 274980728111395087.
```

The ordinary and first-order sums `E + Lambda` are respectively `168519951717393564` and `274498710978084021`. For width eight, the scalar MCA bound transfers without a width factor. The reduction's list term pairs two words, giving width sixteen; extension-field encoding transfers the scalar list bound without a width factor there either. These are the paper's interleaving theorems, not additional benchmark assumptions.

For a radius `tau`, required agreement is `A = n - floor(tau*n)`. The paper points use the conservative radius `(n-A)/n`; #567 uses a radius near the top of the same integer-error cell. Scores are rounded down to hundredths. The replay certifies each paper score `b/100` by the exact integer inequality `A^12800 * 2^b <= n^12800`, and checks that the next hundredth fails at that particular radius. Floating-point logarithms are not used to accept a certificate.

### Reproduce the certificates

From this repository root, using Python 3.10 or newer and its standard library:

```sh
python3 scripts/examples/proximity-prize/check_points.py
```

The command checks interpolation feasibility, the computed bounds, the reduction budget, the first-order characteristic guard, and both score inequalities. It also rejects any drift from [paper-points.json](paper-points.json). This is exact numerical evaluation of the manuscript's theorems, not a fresh Lean formalization of the prize entrypoint.

The ordinary certificate uses multiplicity `m=4096`, message-variable degree bound `mu=5792`, and challenge degree `H=22992660`, with ordinary threshold `L=k`. The first-order certificate uses `(m,M,mu)=(26,7,36)`, challenge degree `H=485`, and regular threshold `L=131851`. Its characteristic requirement is `p>131071`, satisfied by the benchmark prime. It uses the derivative-weighted support, tight Taylor degree estimates, squarefree regular/singular transfer, and independent ordinary-tail threshold selection already in the paper.

### Reproduce and interpret the bounded search

```sh
python3 scripts/examples/proximity-prize/search_paper.py
python3 scripts/tune_ordinary_mca.py --n 262144 --k 131072 --agreement 185372 --max-m 4096
```

The first command evaluates derivative-weighted adaptive support pools with `m<=128` and maximum jet degree 1000, using the existing `sharp-v2` transfer and tight Taylor degree model. It records results at the snapshot leader's agreement and at several agreements between 183200 and 183300. The output is [paper-search.json](paper-search.json). This search is much slower than point replay. The second command searches ordinary certificates with multiplicity at most 4096 at the displayed agreement, rather than invoking the rounded asymptotic theorem.

The first-order bisection found an adjacent checked failure at 183209 and success at 183210. The support pool depends on agreement, and monotonicity of this heuristic search has not been proved; adjacency does not establish a global minimum, even within the heuristic. Other paper-supported transfer choices and support searches may improve these points.

At the snapshot leader's `A=181284`, the searched family gives `E+Lambda=407671721486965194763`, about 1482.5 times the permitted budget. This fails the prize condition despite satisfying the interpolation and characteristic requirements. The comparison therefore identifies substantial finite slack, not an obstruction to the paper's first-order curve. The two passing paper points differ by 2162 agreement positions and 2.16 displayed score bits.

No benchmark calculation here uses the NTT subgroup structure or the particular representation of the sextic field. Multiple-equation, whole-kernel, extra Taylor-tail, and collective component arguments from the later submissions have not been added to this search.

## Promoted lower-track entries

The radius is an error fraction; a larger certified radius permits a smaller agreement threshold. Links identify the promoted source revision.

| Submission and contributor | Query score (bits) | Certified radius | Source |
|---|---:|---|---|
| [#1](https://github.com/proximity-prize/proximity-prize/pull/1) @saucegodbased | 53.12 | 1/4 | [207eb2212d94](https://github.com/proximity-prize/proximity-prize/tree/207eb2212d947e27871c25e60dd3c1ad927955a1/ProximityPrize/SubmissionLower)  |
| [#21](https://github.com/proximity-prize/proximity-prize/pull/21) @gin | 53.13 | 262167/1048576 | [4153de48531d](https://github.com/proximity-prize/proximity-prize/tree/4153de48531d6c3c495ad955d56a7ed4e6ce2006/ProximityPrize/SubmissionLower)  |
| [#45](https://github.com/proximity-prize/proximity-prize/pull/45) @recmo | 63.58 | 305433/1048576 | [e4c8dfbf73ba](https://github.com/proximity-prize/proximity-prize/tree/e4c8dfbf73ba1cc152e72d67c63435aae1021397/ProximityPrize/SubmissionLower)  |
| [#49](https://github.com/proximity-prize/proximity-prize/pull/49) @xadahiya | 63.59 | 305475/1048576 | [9cde12c5d2e5](https://github.com/proximity-prize/proximity-prize/tree/9cde12c5d2e5fee15bee0e6fa4c6d23ca9d9b1e0/ProximityPrize/SubmissionLower)  |
| [#51](https://github.com/proximity-prize/proximity-prize/pull/51) @xadahiya | 63.60 | 305515/1048576 | [25c5da296bc3](https://github.com/proximity-prize/proximity-prize/tree/25c5da296bc3b4403d0801798b8d107b372fd8f6/ProximityPrize/SubmissionLower)  |
| [#52](https://github.com/proximity-prize/proximity-prize/pull/52) @BitWonka | 63.81 | 306377/1048576 | [ce0719cfd2e4](https://github.com/proximity-prize/proximity-prize/tree/ce0719cfd2e47bada696793958997087cee84660/ProximityPrize/SubmissionLower)  |
| [#63](https://github.com/proximity-prize/proximity-prize/pull/63) @mirinda-cmd | 63.82 | 306399/1048576 | [9af43b58783a](https://github.com/proximity-prize/proximity-prize/tree/9af43b58783a3e24574c3296da270488c379b138/ProximityPrize/SubmissionLower)  |
| [#64](https://github.com/proximity-prize/proximity-prize/pull/64) @BitWonka | 63.94 | 306887/1048576 | [adb0ec321bf4](https://github.com/proximity-prize/proximity-prize/tree/adb0ec321bf4ce572b7150ee13f921e3c6f679f9/ProximityPrize/SubmissionLower)  |
| [#72](https://github.com/proximity-prize/proximity-prize/pull/72) @jieyilong | 63.99 | 307083/1048576 | [19bc7d3e21b2](https://github.com/proximity-prize/proximity-prize/tree/19bc7d3e21b2261257e1961acd720b2c395d87e1/ProximityPrize/SubmissionLower)  |
| [#122](https://github.com/proximity-prize/proximity-prize/pull/122) Bartosz Naskręcki | 64.01 | 307163/1048576 | [b3fac81ad2b1](https://github.com/proximity-prize/proximity-prize/tree/b3fac81ad2b1ee609672b04bd3c3ee1ca5c06884/ProximityPrize/SubmissionLower)  |
| [#126](https://github.com/proximity-prize/proximity-prize/pull/126) @CrystallineButterfly | 64.23 | 308067/1048576 | [4c2f897ffc98](https://github.com/proximity-prize/proximity-prize/tree/4c2f897ffc98de3fff64ff41c86f164b81bbc270/ProximityPrize/SubmissionLower)  |
| [#129](https://github.com/proximity-prize/proximity-prize/pull/129) @saucegodbased | 64.26 | 308183/1048576 | [de4ef80ab50e](https://github.com/proximity-prize/proximity-prize/tree/de4ef80ab50e8d492da63042af938d6d7bebc06c/ProximityPrize/SubmissionLower)  |
| [#130](https://github.com/proximity-prize/proximity-prize/pull/130) @erdkocak | 64.30 | 308327/1048576 | [b55c8175d1fa](https://github.com/proximity-prize/proximity-prize/tree/b55c8175d1fa796faf151ef83a72885d41515831/ProximityPrize/SubmissionLower)  |
| [#132](https://github.com/proximity-prize/proximity-prize/pull/132) @newjordan | 64.52 | 309207/1048576 | [f3580223b640](https://github.com/proximity-prize/proximity-prize/tree/f3580223b640afbedb43f9045a6ef199b207f2a6/ProximityPrize/SubmissionLower)  |
| [#141](https://github.com/proximity-prize/proximity-prize/pull/141) @BitWonka | 64.54 | 309299/1048576 | [5895910f31e9](https://github.com/proximity-prize/proximity-prize/tree/5895910f31e9052b6f00845214ece35fcd4e8f8e/ProximityPrize/SubmissionLower)  |
| [#143](https://github.com/proximity-prize/proximity-prize/pull/143) @jieyilong | 64.62 | 309635/1048576 | [575ceeb9d945](https://github.com/proximity-prize/proximity-prize/tree/575ceeb9d945b56d79b90cd53f90cc17994a0f34/ProximityPrize/SubmissionLower)  |
| [#147](https://github.com/proximity-prize/proximity-prize/pull/147) @saucegodbased | 64.64 | 309699/1048576 | [370deaf250d6](https://github.com/proximity-prize/proximity-prize/tree/370deaf250d6f81fe07acbadc7079550bb7fc59b/ProximityPrize/SubmissionLower)  |
| [#152](https://github.com/proximity-prize/proximity-prize/pull/152) @i34-9 | 64.88 | 310663/1048576 | [503fc2f477b2](https://github.com/proximity-prize/proximity-prize/tree/503fc2f477b294ed07845e5d3f5459962d9e94fb/ProximityPrize/SubmissionLower)  |
| [#156](https://github.com/proximity-prize/proximity-prize/pull/156) @i34-9 | 64.89 | 310719/1048576 | [cd5399ab8ac4](https://github.com/proximity-prize/proximity-prize/tree/cd5399ab8ac4e90446c562c28a1ce1a2c11baccb/ProximityPrize/SubmissionLower)  |
| [#161](https://github.com/proximity-prize/proximity-prize/pull/161) @jieyilong | 64.92 | 310807/1048576 | [fbad76c8cbd8](https://github.com/proximity-prize/proximity-prize/tree/fbad76c8cbd8beb23407639842f237ebee9cbd3f/ProximityPrize/SubmissionLower)  |
| [#168](https://github.com/proximity-prize/proximity-prize/pull/168) @saucegodbased | 65.33 | 312471/1048576 | [2275a4d88051](https://github.com/proximity-prize/proximity-prize/tree/2275a4d88051f34f87d9d44097b2b86b716220c6/ProximityPrize/SubmissionLower)  |
| [#170](https://github.com/proximity-prize/proximity-prize/pull/170) @i34-9 | 65.56 | 313375/1048576 | [a2326a9a560d](https://github.com/proximity-prize/proximity-prize/tree/a2326a9a560dba4d996476137013dca8ea1f947e/ProximityPrize/SubmissionLower)  |
| [#173](https://github.com/proximity-prize/proximity-prize/pull/173) @BitWonka | 65.58 | 313467/1048576 | [2e19c354e0aa](https://github.com/proximity-prize/proximity-prize/tree/2e19c354e0aadeedf0b3ff85d39e213bdcaa8ce8/ProximityPrize/SubmissionLower)  |
| [#175](https://github.com/proximity-prize/proximity-prize/pull/175) @BitWonka | 65.60 | 313547/1048576 | [1faab677f52f](https://github.com/proximity-prize/proximity-prize/tree/1faab677f52f2465c681ad12ce44fafd26173a03/ProximityPrize/SubmissionLower)  |
| [#181](https://github.com/proximity-prize/proximity-prize/pull/181) @BitWonka | 65.68 | 313851/1048576 | [075fa89dbbd5](https://github.com/proximity-prize/proximity-prize/tree/075fa89dbbd5a11fcce0e4250b5e9448d7ee7c19/ProximityPrize/SubmissionLower)  |
| [#184](https://github.com/proximity-prize/proximity-prize/pull/184) @erdkocak | 65.69 | 313895/1048576 | [86fe70ce041b](https://github.com/proximity-prize/proximity-prize/tree/86fe70ce041b819a4d6bf651d117ffac667398c3/ProximityPrize/SubmissionLower)  |
| [#187](https://github.com/proximity-prize/proximity-prize/pull/187) @saucegodbased | 66.00 | 315111/1048576 | [6f2353a4130c](https://github.com/proximity-prize/proximity-prize/tree/6f2353a4130cc46f2776f92595ac66b5fd18ee14/ProximityPrize/SubmissionLower)  |
| [#194](https://github.com/proximity-prize/proximity-prize/pull/194) @BitWonka | 66.18 | 315835/1048576 | [8df254f4bc7b](https://github.com/proximity-prize/proximity-prize/tree/8df254f4bc7b8c91f85e4b48e5a27e9758ffbd0c/ProximityPrize/SubmissionLower)  |
| [#219](https://github.com/proximity-prize/proximity-prize/pull/219) @erdkocak | 66.42 | 316779/1048576 | [a35b31c89ca9](https://github.com/proximity-prize/proximity-prize/tree/a35b31c89ca9236cb2d4a4f9810e5840d16f5378/ProximityPrize/SubmissionLower)  |
| [#241](https://github.com/proximity-prize/proximity-prize/pull/241) @BitWonka | 66.74 | 318059/1048576 | [41d6b4f66b01](https://github.com/proximity-prize/proximity-prize/tree/41d6b4f66b015cd1f88d0f5199be2be87d2174f6/ProximityPrize/SubmissionLower)  |
| [#251](https://github.com/proximity-prize/proximity-prize/pull/251) @jieyilong | 66.75 | 318083/1048576 | [29dd62f8e136](https://github.com/proximity-prize/proximity-prize/tree/29dd62f8e136fdcb33a506eab548e8d0c8445c94/ProximityPrize/SubmissionLower)  |
| [#255](https://github.com/proximity-prize/proximity-prize/pull/255) @BitWonka | 66.96 | 318923/1048576 | [a9b9386312f0](https://github.com/proximity-prize/proximity-prize/tree/a9b9386312f00dd52e575c33f055fb98db8ae5a6/ProximityPrize/SubmissionLower)  |
| [#261](https://github.com/proximity-prize/proximity-prize/pull/261) @BitWonka | 66.97 | 318983/1048576 | [20c52526326d](https://github.com/proximity-prize/proximity-prize/tree/20c52526326d3897a8e3fc23828b472ad718ea53/ProximityPrize/SubmissionLower)  |
| [#262](https://github.com/proximity-prize/proximity-prize/pull/262) @BitWonka | 67.00 | 319075/1048576 | [25a4faf7b4bd](https://github.com/proximity-prize/proximity-prize/tree/25a4faf7b4bd2334281636d0a1bacdfc25cd7ee2/ProximityPrize/SubmissionLower)  |
| [#263](https://github.com/proximity-prize/proximity-prize/pull/263) @jieyilong | 67.10 | 319467/1048576 | [e482ff00afcd](https://github.com/proximity-prize/proximity-prize/tree/e482ff00afcd5df997ffafa370d3635745f4aabe/ProximityPrize/SubmissionLower)  |
| [#269](https://github.com/proximity-prize/proximity-prize/pull/269) @jieyilong | 67.19 | 319823/1048576 | [4e1259bd2fcc](https://github.com/proximity-prize/proximity-prize/tree/4e1259bd2fcc2d1c7080c5c6060e335ef7382ead/ProximityPrize/SubmissionLower)  |
| [#276](https://github.com/proximity-prize/proximity-prize/pull/276) @jieyilong | 67.31 | 320295/1048576 | [b0f1caa19d92](https://github.com/proximity-prize/proximity-prize/tree/b0f1caa19d9266f185d23681bcfe703a4f48f5bd/ProximityPrize/SubmissionLower)  |
| [#279](https://github.com/proximity-prize/proximity-prize/pull/279) @CrystallineButterfly | 67.32 | 10250623/33554432 | [baf2c0c2a54f](https://github.com/proximity-prize/proximity-prize/tree/baf2c0c2a54fbb4072e4c7006c09660b546def26/ProximityPrize/SubmissionLower)  |
| [#303](https://github.com/proximity-prize/proximity-prize/pull/303) @jieyilong | 67.33 | 10251903/33554432 | [973ec7ef5839](https://github.com/proximity-prize/proximity-prize/tree/973ec7ef583986d504d946371ac65ff89b845f70/ProximityPrize/SubmissionLower)  |
| [#320](https://github.com/proximity-prize/proximity-prize/pull/320) @kongtaoxing | 67.34 | 10253183/33554432 | [fe40c648e7bf](https://github.com/proximity-prize/proximity-prize/tree/fe40c648e7bfc8c9f586b21dac606cdbd37cd50a/ProximityPrize/SubmissionLower)  |
| [#331](https://github.com/proximity-prize/proximity-prize/pull/331) @alxkzmn | 67.35 | 10254463/33554432 | [dfd7b315f826](https://github.com/proximity-prize/proximity-prize/tree/dfd7b315f826b02faef3a8f6e495bda016b16dbe/ProximityPrize/SubmissionLower)  |
| [#335](https://github.com/proximity-prize/proximity-prize/pull/335) @kongtaoxing | 67.37 | 10257919/33554432 | [ffb75b2a2a81](https://github.com/proximity-prize/proximity-prize/tree/ffb75b2a2a81d09d4a53ca8d7a91d3a471ea5cdb/ProximityPrize/SubmissionLower)  |
| [#337](https://github.com/proximity-prize/proximity-prize/pull/337) @Inah-choi | 67.40 | 10260735/33554432 | [dbdb09a05881](https://github.com/proximity-prize/proximity-prize/tree/dbdb09a05881f77192438197a90ab547be33d32b/ProximityPrize/SubmissionLower)  |
| [#343](https://github.com/proximity-prize/proximity-prize/pull/343) @jacklightChen | 67.41 | 10261977/33554432 | [b6f09ed98ce5](https://github.com/proximity-prize/proximity-prize/tree/b6f09ed98ce52de87d2fbd5160c70aed46d0695d/ProximityPrize/SubmissionLower)  |
| [#345](https://github.com/proximity-prize/proximity-prize/pull/345) @BitWonka | 67.42 | 10263295/33554432 | [fa3f8be2dbd8](https://github.com/proximity-prize/proximity-prize/tree/fa3f8be2dbd82cb24eb9659258c2d112c250747d/ProximityPrize/SubmissionLower)  |
| [#347](https://github.com/proximity-prize/proximity-prize/pull/347) @BitWonka | 67.43 | 10264575/33554432 | [3b52d121bb93](https://github.com/proximity-prize/proximity-prize/tree/3b52d121bb9317d0eb1d45287cbb2dac1d981397/ProximityPrize/SubmissionLower)  |
| [#351](https://github.com/proximity-prize/proximity-prize/pull/351) @saucegodbased | 67.50 | 10273407/33554432 | [2b3a4878f304](https://github.com/proximity-prize/proximity-prize/tree/2b3a4878f304d981da3da7bf7e0d3dc1d87f8dfe/ProximityPrize/SubmissionLower)  |
| [#356](https://github.com/proximity-prize/proximity-prize/pull/356) @jacklightChen | 67.51 | 10274587/33554432 | [f4392a3903ff](https://github.com/proximity-prize/proximity-prize/tree/f4392a3903ffcd44e3cf27a40318894e44898c1e/ProximityPrize/SubmissionLower)  |
| [#360](https://github.com/proximity-prize/proximity-prize/pull/360) @jieyilong | 67.53 | 10277109/33554432 | [fb2f0832cf33](https://github.com/proximity-prize/proximity-prize/tree/fb2f0832cf33f2386a3a38a9eb540188f8c16cba/ProximityPrize/SubmissionLower)  |
| [#363](https://github.com/proximity-prize/proximity-prize/pull/363) @zkfriendly | 67.54 | 10278369/33554432 | [4fd6f30fe21a](https://github.com/proximity-prize/proximity-prize/tree/4fd6f30fe21a9d5816dc2bb0221470285e26c24a/ProximityPrize/SubmissionLower)  |
| [#367](https://github.com/proximity-prize/proximity-prize/pull/367) @jacklightChen | 67.60 | 10285930/33554432 | [625f2c09c8ac](https://github.com/proximity-prize/proximity-prize/tree/625f2c09c8ac826ba67c1f336b15348f87f52d4d/ProximityPrize/SubmissionLower)  |
| [#371](https://github.com/proximity-prize/proximity-prize/pull/371) @hadakang | 67.61 | 10287190/33554432 | [42364a74d210](https://github.com/proximity-prize/proximity-prize/tree/42364a74d210aafbb2b5f357c7fbd2173fdb097a/ProximityPrize/SubmissionLower)  |
| [#377](https://github.com/proximity-prize/proximity-prize/pull/377) @kongtaoxing | 67.63 | 10289710/33554432 | [4b084c549824](https://github.com/proximity-prize/proximity-prize/tree/4b084c549824d8b31a22018cad85c1e5dc4a05c1/ProximityPrize/SubmissionLower)  |
| [#383](https://github.com/proximity-prize/proximity-prize/pull/383) @jacklightChen | 67.64 | 10290970/33554432 | [d375771f839b](https://github.com/proximity-prize/proximity-prize/tree/d375771f839b077a2a4d48aa0fb8f75d37058f19/ProximityPrize/SubmissionLower)  |
| [#387](https://github.com/proximity-prize/proximity-prize/pull/387) @alexanderlhicks | 67.65 | 10292230/33554432 | [ec6f4f493655](https://github.com/proximity-prize/proximity-prize/tree/ec6f4f493655c61c900961685275334f709edcfe/ProximityPrize/SubmissionLower)  |
| [#389](https://github.com/proximity-prize/proximity-prize/pull/389) @jieyilong | 67.66 | 10293489/33554432 | [40a16bda0452](https://github.com/proximity-prize/proximity-prize/tree/40a16bda0452d7ae67294c4058d33af3567f7b42/ProximityPrize/SubmissionLower)  |
| [#398](https://github.com/proximity-prize/proximity-prize/pull/398) @BitWonka | 67.67 | 10294749/33554432 | [de2469b23ad4](https://github.com/proximity-prize/proximity-prize/tree/de2469b23ad4d94a6eaa52d326d791cb2b8fbfb7/ProximityPrize/SubmissionLower)  |
| [#441](https://github.com/proximity-prize/proximity-prize/pull/441) @i34-9 | 67.75 | 10304823/33554432 | [b955129e2999](https://github.com/proximity-prize/proximity-prize/tree/b955129e29997e5c1d8701423112c146cda4f3ce/ProximityPrize/SubmissionLower)  |
| [#446](https://github.com/proximity-prize/proximity-prize/pull/446) @i34-9 | 67.76 | 10306082/33554432 | [2afbe6f7a894](https://github.com/proximity-prize/proximity-prize/tree/2afbe6f7a894459a215d679c69ba19dc06a58cb5/ProximityPrize/SubmissionLower)  |
| [#451](https://github.com/proximity-prize/proximity-prize/pull/451) @jieyilong | 67.77 | 10307341/33554432 | [01c1a60466db](https://github.com/proximity-prize/proximity-prize/tree/01c1a60466db35eb1c0e0afea103f02de7051135/ProximityPrize/SubmissionLower)  |
| [#456](https://github.com/proximity-prize/proximity-prize/pull/456) @i34-9 | 67.78 | 10308600/33554432 | [49925450bb54](https://github.com/proximity-prize/proximity-prize/tree/49925450bb54d4791180865b8a58d4e110f6442d/ProximityPrize/SubmissionLower)  |
| [#462](https://github.com/proximity-prize/proximity-prize/pull/462) @ercumentyildirim | 67.80 | 10311118/33554432 | [4a4110c62736](https://github.com/proximity-prize/proximity-prize/tree/4a4110c62736264fa86532c6a7f4d95dea9f4f6f/ProximityPrize/SubmissionLower)  |
| [#465](https://github.com/proximity-prize/proximity-prize/pull/465) @BitWonka | 67.82 | 10313727/33554432 | [87972ffc0b13](https://github.com/proximity-prize/proximity-prize/tree/87972ffc0b134d672021013c287870e2d87d9756/ProximityPrize/SubmissionLower)  |
| [#471](https://github.com/proximity-prize/proximity-prize/pull/471) @jieyilong | 67.84 | 10316152/33554432 | [db5c25937e3e](https://github.com/proximity-prize/proximity-prize/tree/db5c25937e3edd068c063e92a847b645c1f16c88/ProximityPrize/SubmissionLower)  |
| [#472](https://github.com/proximity-prize/proximity-prize/pull/472) @ercumentyildirim | 67.85 | 10317410/33554432 | [9202efb4f739](https://github.com/proximity-prize/proximity-prize/tree/9202efb4f739415e4a94c0b1bc5bd22e9d73779c/ProximityPrize/SubmissionLower)  |
| [#478](https://github.com/proximity-prize/proximity-prize/pull/478) @nethoxa | 67.86 | 10318719/33554432 | [7bbca7cc17ab](https://github.com/proximity-prize/proximity-prize/tree/7bbca7cc17ab666379465cabfa58498ecd4a3bec/ProximityPrize/SubmissionLower)  |
| [#484](https://github.com/proximity-prize/proximity-prize/pull/484) @nethoxa | 67.87 | 10319999/33554432 | [4a7cb14a9b65](https://github.com/proximity-prize/proximity-prize/tree/4a7cb14a9b6547ac26fd94fb96a8d789bbf0dffc/ProximityPrize/SubmissionLower)  |
| [#492](https://github.com/proximity-prize/proximity-prize/pull/492) @saucegodbased | 68.00 | 10336383/33554432 | [b5d8590afb90](https://github.com/proximity-prize/proximity-prize/tree/b5d8590afb90a85a78026a93194826e255555b0d/ProximityPrize/SubmissionLower)  |
| [#502](https://github.com/proximity-prize/proximity-prize/pull/502) @i34-9 | 68.01 | 10337535/33554432 | [01c716772b84](https://github.com/proximity-prize/proximity-prize/tree/01c716772b84d6e3ca056cd998277066e3847b11/ProximityPrize/SubmissionLower)  |
| [#503](https://github.com/proximity-prize/proximity-prize/pull/503) @DaniiRix | 68.02 | 10338815/33554432 | [b34c0131cfa3](https://github.com/proximity-prize/proximity-prize/tree/b34c0131cfa36b51111521541d7d3e35c8791082/ProximityPrize/SubmissionLower)  |
| [#505](https://github.com/proximity-prize/proximity-prize/pull/505) @BitWonka | 68.03 | 10340095/33554432 | [032154395c51](https://github.com/proximity-prize/proximity-prize/tree/032154395c51fd6f77715a7f42d9a987ab9fb48a/ProximityPrize/SubmissionLower)  |
| [#517](https://github.com/proximity-prize/proximity-prize/pull/517) @nethoxa | 68.04 | 10341375/33554432 | [1b2ca03c8b0a](https://github.com/proximity-prize/proximity-prize/tree/1b2ca03c8b0ad8a53d647f1eb13aa60b928b8a2c/ProximityPrize/SubmissionLower)  |
| [#551](https://github.com/proximity-prize/proximity-prize/pull/551) | 68.06 | 10343935/33554432 | [e639cd0c8f94](https://github.com/proximity-prize/proximity-prize/tree/e639cd0c8f94f1946eb02718123aadb6b0dafabc/ProximityPrize/SubmissionLower) |
| [#561](https://github.com/proximity-prize/proximity-prize/pull/561) | 68.07 | 10345087/33554432 | [d13ae10217ee](https://github.com/proximity-prize/proximity-prize/tree/d13ae10217ee0e3878d25462994ce15af29d8007/ProximityPrize/SubmissionLower) |
| [#563](https://github.com/proximity-prize/proximity-prize/pull/563) | 68.08 | 10346334/33554432 | [b8d02988ce51](https://github.com/proximity-prize/proximity-prize/tree/b8d02988ce51142b4ae6e576c3fdf648d34ea475/ProximityPrize/SubmissionLower) |
| [#565](https://github.com/proximity-prize/proximity-prize/pull/565) | 68.10 | 10348847/33554432 | [09d8a2ae2e99](https://github.com/proximity-prize/proximity-prize/tree/09d8a2ae2e99404c556888cc18918afb03a94800/ProximityPrize/SubmissionLower) |
| [#567](https://github.com/proximity-prize/proximity-prize/pull/567) @BitWonka | 68.11 | 331206655/1073741824 | [cdb451f13fdc](https://github.com/proximity-prize/proximity-prize/tree/cdb451f13fdc6c84f5fe363e77ee13a89bd30974/ProximityPrize/SubmissionLower) |

Unpromoted ancestors include recmo #245, alexanderlhicks #439, jsign #506, jacklightChen #513, and the #542/#546 contributions incorporated in #551. Their absence from the promoted table does not diminish the contributions credited by descendants. The upper track proves obstructions and is not included in this lower-bound inventory.

The main paper discusses the mathematical mechanisms and attribution. This
guide supplies the finite certificate replay and the dated submission sources.
