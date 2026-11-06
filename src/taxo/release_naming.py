from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Union


def version_from_file(path: Union[str, Path] = "VERSION.txt") -> str:
    text = Path(path).read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return "candidate"




_CANDIDATE_RE = re.compile(r"^(\d+)\.(\d+)-r(\d+)$", re.I)


def candidate_stem(version: str) -> str:
    """Canonical release filename prefix for a candidate version."""
    match = _CANDIDATE_RE.fullmatch(str(version).strip())
    if not match:
        raise ValueError(f"Некоректна candidate-версія: {version}")
    major, minor, revision = match.groups()
    return f"Taxo_v{major}_{minor}_candidate_r{revision}"


def checksum_stem(version: str) -> str:
    """Canonical version token used in SHA256SUMS filenames."""
    match = _CANDIDATE_RE.fullmatch(str(version).strip())
    if not match:
        raise ValueError(f"Некоректна candidate-версія: {version}")
    major, minor, revision = match.groups()
    return f"{major}_{minor}_r{revision}"


def github_env_lines(version: str):
    """Environment lines shared by active build workflows."""
    version = str(version).strip()
    return (
        f"TAXO_VERSION={version}",
        f"TAXO_CANDIDATE_STEM={candidate_stem(version)}",
        f"TAXO_CHECKSUM_STEM={checksum_stem(version)}",
    )

def next_candidate_version(version: str) -> str:
    """Return the next development revision using the Taxo project rule.

    Each completed development step consumes exactly one revision:
    r1 ... r10.  After r10 the minor version increments and revision restarts
    at r1, e.g. 10.2-r10 -> 10.3-r1.  Major-version changes are intentionally
    not automatic and require an explicit owner decision.
    """
    match = re.fullmatch(r"(\d+)\.(\d+)-r(\d+)", str(version).strip(), re.I)
    if not match:
        raise ValueError(f"Некоректна candidate-версія: {version}")
    major, minor, revision = map(int, match.groups())
    if not 1 <= revision <= 10:
        raise ValueError("Ревізія має бути в межах r1 ... r10.")
    if revision < 10:
        return f"{major}.{minor}-r{revision + 1}"
    return f"{major}.{minor + 1}-r1"

def start_archive_stem(version: str) -> str:
    candidate = re.search(r"(\d+)\.(\d+).*?r(\d+(?:\.\d+)*)", version, re.I)
    stable = re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?", version.strip())
    if candidate:
        revision = candidate.group(3).replace(".", "_")
        return f"Taxo_v{candidate.group(1)}_{candidate.group(2)}_candidate_r{revision}_START"
    if stable:
        parts = [stable.group(1), stable.group(2)]
        if stable.group(3) is not None:
            parts.append(stable.group(3))
        return "Taxo_v" + "_".join(parts) + "_START"
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", version).strip("_") or "candidate"
    return f"Taxo_{safe}_START"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--github-env", metavar="PATH")
    parser.add_argument(
        "--field",
        choices=("version", "candidate_stem", "checksum_stem", "start_archive_stem"),
    )
    args = parser.parse_args()
    version = version_from_file()
    if args.github_env:
        path = Path(args.github_env)
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            for line in github_env_lines(version):
                handle.write(line + "\n")
    elif args.field == "version":
        print(version)
    elif args.field == "candidate_stem":
        print(candidate_stem(version))
    elif args.field == "checksum_stem":
        print(checksum_stem(version))
    else:
        print(start_archive_stem(version))
