# Literal Lean statements

This bundle supplies the statement excerpts referenced by the main paper's
Lean appendix. The 24 `.lean` files contain declaration statements, with proof
bodies omitted. They are excerpts for reading, not standalone compilable modules.

[sources.json](sources.json) records each excerpt's source path, declaration
names, and immutable revision in [ArkLib](https://github.com/quangvdao/ArkLib).
The mathematical and decoder sources have separate pins:

- Mathematics: `a5aa2677fee4e3a79d6bb05136631cce4a08587d`.
- Simplified decoder: `ffab000e71c5b19e8a19bebadcc0050eac1366e3`.

## Check correspondence

Use Python 3.10 or newer and Git. Supply local ArkLib checkouts whose object
databases contain the respective commits; their checked-out branches need not
match the pins. From this repository's root, run:

```console
python3 scripts/sync_lean_statements.py --math-repo /path/to/ArkLib-math --decoder-repo /path/to/ArkLib-decoder --check
```

One checkout may serve both arguments if it contains both commits. Success
prints `Checked 24 literal Lean excerpts.` The checker reads the pinned Git
objects, compares every excerpt, and verifies the source manifest. It omits
source comments and proof bodies but preserves statement tokens. A missing
commit, missing declaration, or mismatched excerpt makes the command fail.
Without `--check`, the command regenerates the excerpts and manifest.

This check establishes source correspondence. It does not run Lean, verify the
fast decoder's bit complexity, or extend the paper's formalization scope.

## Attribution

The excerpts come from ArkLib and retain its Apache-2.0 license; see
[LICENSE](LICENSE) and the authorship headers in the source files named by
the manifest. Proof bodies and source comments are omitted by the extraction
procedure above. The full source remains available at the pinned revisions.

The source notices are retained here:

> Copyright (c) 2026 ArkLib Contributors. All rights reserved.
> Released under Apache 2.0 license as described in the file LICENSE.
> Authors: Quang Dao

For `agreement-count.lean`, extracted from `Basic/Distance.lean`:

> Copyright (c) 2024 ArkLib Contributors. All rights reserved.
> Released under Apache 2.0 license as described in the file LICENSE.
> Authors: Quang Dao, Katerina Hristova, František Silváši, Julian Sutherland,
> Ilia Vlasov, Chung Thai Nguyen, Aristotle (Harmonic)
