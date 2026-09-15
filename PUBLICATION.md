# Publish a reviewed update

The main manuscript is authored privately. This repository receives its PDF
and a minimal reference map, never its source tree or Git history. The
companion is edited and built here. Do not synchronize whole directories
between the two repositories.

## Update the main paper

1. Build and approve the main PDF in the private workspace. Resolve any
   publication gates there before importing it.
2. Start from a clean public checkout and run:

   ```console
   python3 scripts/publication.py import-paper /absolute/path/to/approved/manuscript
   ```

   This copies only the named main PDF and the reference records used by the
   companion. It neither edits the companion nor commits or pushes anything.
3. Run `make all`. Inspect the companion's references and rendered pages;
   matching label names alone does not establish that the cited claim is
   unchanged. Review the main PDF for publication readiness.
4. Run `make manifest`, then `python3 scripts/publication.py verify`.
   Review the complete Git diff, including the PDF changes, before committing
   and pushing. Have another reader check any changed scientific claims.

The importer deliberately has no reverse-sync operation. If a public
correction also affects the private main paper, carry the correction over
explicitly; do not merge public companion files into the private source tree.

## Update the companion or calculations

Edit the public source or scripts directly. Preserve hypotheses, citations,
and the distinction between measured proofs and analytical byte counts.
Run `make all`, inspect the rebuilt companion, regenerate the manifest, and
review before pushing. Keep historical fixtures unchanged unless correcting
a documented fixture error. Fixture agreement is a regression check, not an
independent mathematical proof.

## Create a versioned release

After review, tag the approved public commit (for example `v2026.09.14`).
Create a GitHub draft release for that tag and attach both PDFs and
`manifest.json`. Check the draft's files and links, then publish it.
GitHub's source archive supplies the companion source and certificate scripts.
Use a tagged release or commit link when citing a specific version; links to
the default branch track subsequent revisions.

There is no automatic publication on a private push, and no credential or
private-repository access is needed to build these public materials.
