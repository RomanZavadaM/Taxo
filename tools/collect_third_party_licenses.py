# -*- coding: utf-8 -*-
"""Collect upstream license/NOTICE files from installed Taxo runtime packages."""
from __future__ import annotations

import argparse
import importlib.metadata as metadata
import re
import shutil
from pathlib import Path

TARGETS = {
    "python-docx", "openpyxl", "reportlab", "pillow", "pypdf",
    "pypdfium2", "opencv-python-headless", "pywin32",
}
KEYWORDS = ("license", "licence", "copying", "notice", "thirdparty", "third_party")


def norm(name):
    return re.sub(r"[-_.]+", "-", (name or "").lower())


def collect(output):
    output = Path(output)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    copied = 0
    seen = set()

    for dist in metadata.distributions():
        name = dist.metadata.get("Name") or ""
        key = norm(name)
        if key not in TARGETS and not key.startswith("pypdfium2"):
            continue
        seen.add(key)
        version = dist.version or "unknown"
        dest_dir = output / f"{key}-{version}"
        for rel in dist.files or ():
            rel_text = str(rel).replace("\\", "/")
            low = rel_text.lower()
            base = Path(rel_text).name.lower()
            if not (
                any(word in base for word in KEYWORDS)
                or "/licenses/" in low
                or "/license/" in low
                or "build_licenses" in low
            ):
                continue
            src = Path(dist.locate_file(rel))
            if not src.is_file():
                continue
            safe = rel_text.replace("../", "").replace("/", "__").replace("\\", "__")
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest_dir / safe)
            copied += 1

    if "pypdfium2" not in seen:
        raise SystemExit("pypdfium2 is not installed; cannot collect PDFium notices")
    if copied == 0:
        raise SystemExit("No third-party license files were collected")
    print(f"Collected {copied} license/NOTICE files into {output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="third_party_licenses")
    args = parser.parse_args()
    collect(args.output)


if __name__ == "__main__":
    main()
