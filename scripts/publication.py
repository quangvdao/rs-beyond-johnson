#!/usr/bin/env python3
"""Explicit one-way PDF/reference import and public checksum verification."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PAPER = 'rs-beyond-johnson'


def published_files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file()
                  and not any(part in {'.git', '__pycache__', 'build'}
                              for part in p.relative_to(ROOT).parts)
                  and p.name != 'manifest.json'
                  and (p.suffix in {'.pdf', '.tex', '.md', '.py', '.rs', '.lean', '.json', '.tsv'}
                       or (p.relative_to(ROOT).parts[:2]
                           == ('experiments', 'zisk-compressed-final')
                           and (p.suffix in {'.bin', '.log', '.patch', '.txt', '.lock', '.toml'}
                                or p.name == 'SHA256SUMS'))
                       or p.name == 'LICENSE' or p.name.startswith('LICENSE-')
                       or p.name in {'Makefile', '.gitignore', PAPER + '.aux'}))


def hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in published_files()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['import-paper', 'manifest', 'verify'])
    parser.add_argument('source', nargs='?', type=Path)
    args = parser.parse_args()
    if args.operation == 'import-paper':
        if args.source is None:
            parser.error('import-paper needs an approved manuscript directory')
        if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT).strip():
            parser.error('public checkout must be clean before importing')
        source = args.source.resolve()
        pdf = source / (PAPER + '.pdf')
        if not pdf.read_bytes().startswith(b'%PDF-'):
            parser.error('source is not a PDF')
        companion = (ROOT / 'certificates-and-obstructions.tex').read_text()
        labels = set(re.findall(r'M-((?:thm|prop|lem|eq|sec):[\w-]+)', companion))
        lines = (source / (PAPER + '.aux')).read_text().splitlines()
        records = []
        for label in sorted(labels):
            selected = [line for line in lines if any(
                line.startswith('\\newlabel{' + key + '}')
                for key in (label, label + '@cref'))]
            if not any(line.startswith('\\newlabel{' + label + '}') for line in selected):
                parser.error(f'missing main-paper label: {label}')
            records.extend(selected)
        shutil.copyfile(pdf, ROOT / pdf.name)
        (ROOT / (PAPER + '.aux')).write_text('\n'.join(records) + '\n')
        print('Imported main PDF and reference map only; review before committing.')
    elif args.operation == 'manifest':
        (ROOT / 'manifest.json').write_text(json.dumps(
            {'algorithm': 'sha256', 'files': hashes()}, indent=2) + '\n')
        print('Updated manifest.json')
    else:
        expected = json.loads((ROOT / 'manifest.json').read_text())['files']
        if hashes() != expected:
            raise SystemExit('FAIL: published files differ from manifest')
        print(f'PASS: {len(expected)} published file checksums')


if __name__ == '__main__':
    main()
