# -*- coding: utf-8 -*-
"""Fail a build when a banned (AGPL) component reaches an executable bundle.

PROJECT_RULES.md §17: PyMuPDF / fitz / MuPDF are banned permanently. The PDF
engine is PDFium (pypdfium2), whose native library must be present instead.

Usage: python scripts/check_bundle_licenses.py <bundle-dir>
"""
import re
import sys
from pathlib import Path

BANNED = re.compile(r"(?:^|[\\/._-])(?:fitz|pymupdf|mupdf)(?:[\\/._-]|$)", re.I)
PDFIUM = re.compile(r"(?:^|[\\/])(?:lib)?pdfium\.(?:dll|dylib|so)$", re.I)


def main(argv):
    if len(argv) != 2:
        raise SystemExit("usage: check_bundle_licenses.py <bundle-dir>")
    root = Path(argv[1])
    if not root.exists():
        raise SystemExit(f"Bundle not found: {root}")
    paths = [p.relative_to(root).as_posix() for p in root.rglob("*")]
    banned = sorted(p for p in paths if BANNED.search(p))
    pdfium = [p for p in paths if PDFIUM.search(p)]
    print(f"Bundle entries checked: {len(paths)}; PDFium: {pdfium[:1]}")
    if banned:
        raise SystemExit("Banned AGPL component in bundle (PyMuPDF/MuPDF): " + ", ".join(banned[:20]))
    if not pdfium:
        raise SystemExit("PDFium native library missing from bundle")


if __name__ == "__main__":
    main(sys.argv)
