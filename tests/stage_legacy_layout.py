# -*- coding: utf-8 -*-
"""Stage the pre-r10 flat repository layout for historical regression tests.

Taxo 10.9-r10 moves runtime modules, packaging files and templates into
structured directories. A large part of the historical regression suite
intentionally reads source files by their old repository paths to verify
immutable implementation contracts. This helper recreates those old paths
*only in the CI working tree* before the tests run.

The generated files are untracked and are never included in git archives or
release packages. Runtime and packaging continue to use the structured paths.
"""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _copy_files(source_dir: Path, destination_dir: Path, pattern: str) -> int:
    destination_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for source in sorted(source_dir.glob(pattern)):
        if not source.is_file():
            continue
        destination = destination_dir / source.name
        if destination.exists():
            continue
        shutil.copy2(source, destination)
        copied += 1
    return copied


def main() -> int:
    copied = 0

    # Historical flat Python module paths.
    copied += _copy_files(ROOT / "src" / "taxo", ROOT, "*.py")

    # Historical PyInstaller spec paths.
    copied += _copy_files(ROOT / "packaging", ROOT, "*.spec")
    copied += _copy_files(ROOT / "packaging" / "history", ROOT, "*.spec")

    # Historical Inno Setup directory.
    copied += _copy_files(ROOT / "packaging" / "installer", ROOT / "installer", "*.iss")

    # Historical template locations used by old regression tests.
    copied += _copy_files(ROOT / "assets", ROOT, "*.docx")
    copied += _copy_files(ROOT / "assets", ROOT, "*.pdf")

    print(f"Staged {copied} legacy-layout files for historical regression tests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
