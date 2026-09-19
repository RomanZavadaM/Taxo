from __future__ import annotations

import re
from pathlib import Path


def version_from_file(path: str | Path = "VERSION.txt") -> str:
    text = Path(path).read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return "candidate"


def start_archive_stem(version: str) -> str:
    candidate = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?.*?r(\d+(?:\.\d+)*)", version, re.I)
    stable = re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?", version.strip())
    if candidate:
        parts = [candidate.group(1), candidate.group(2)]
        if candidate.group(3) is not None:
            parts.append(candidate.group(3))
        revision = candidate.group(4).replace(".", "_")
        return "Taxo_v" + "_".join(parts) + f"_candidate_r{revision}_START"
    if stable:
        parts = [stable.group(1), stable.group(2)]
        if stable.group(3) is not None:
            parts.append(stable.group(3))
        return "Taxo_v" + "_".join(parts) + "_START"
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", version).strip("_") or "candidate"
    return f"Taxo_{safe}_START"


if __name__ == "__main__":
    print(start_archive_stem(version_from_file()))
