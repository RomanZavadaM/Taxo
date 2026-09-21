from __future__ import annotations

import re
from pathlib import Path


def version_from_file(path: str | Path = "VERSION.txt") -> str:
    text = Path(path).read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return "candidate"



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
    print(start_archive_stem(version_from_file()))
