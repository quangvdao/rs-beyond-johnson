# Publish a reviewed update

This repository contains the main paper PDF and supporting calculations,
experiment records, and source pins. The manuscript is authored privately;
its source and development history are not imported here.

## Update the paper

1. Build and review `rs-beyond-johnson.pdf` in the private manuscript workspace.
2. Start from a clean public checkout and run:

   ```console
   python3 scripts/publication.py import-paper /absolute/path/to/approved/manuscript
   ```

   The importer copies only `rs-beyond-johnson.pdf`. It requires no TeX source,
   auxiliary reference map, or TeX installation, and does not commit or push.
3. Check that the paper's artifact references match the supplied records. If
   claims or parameters changed, update the corresponding guides and checks.
4. Run the checks and regenerate the manifest:

   ```console
   make check
   make manifest
   make verify
   ```

5. Review the complete diff and PDF. Obtain independent review of changed
   scientific claims, then commit and push normally to preserve history.

Do not synchronize whole directories from the private workspace. Importing a
PDF must not copy source files, private research notes, or Git history.

## Update calculations or experiment records

Edit these materials here. Preserve hypotheses, source pins, selected
certificate inputs, and the distinction between measured proofs and analytical
byte counts. Keep historical fixtures unchanged unless correcting a documented
fixture error. Fixture agreement is a regression check, not an independent
mathematical proof.

Run `make check`, review the changed documentation and outputs, then run
`make manifest` and `make verify`. Commit and push normally. If an artifact
correction changes a paper claim, also correct and rebuild the private manuscript
before publishing the updated PDF. A private push does not publish a PDF here.

## Create a versioned release

After review, tag the approved public commit (for example `v2026.09.15`).
Create a GitHub draft release for that tag and attach `rs-beyond-johnson.pdf`
and `manifest.json`. GitHub's source archive supplies the scripts and data.
Check the draft's files and links, then publish it.

Use a tagged release or commit link when citing a specific artifact version;
default-branch links track subsequent revisions.
