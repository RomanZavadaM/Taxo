from __future__ import annotations

import re
from pathlib import Path


def version_from_file(path: str | Path = "VERSION.txt") -> str:
    text = Path(path).read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return "candidate"


def _safe_build_id(build_id: str | None) -> str:
    raw = str(build_id or "").strip()
    if not raw:
        return ""
    return re.sub(r"[^A-Za-z0-9_-]+", "_", raw).strip("_")[:16]


def start_archive_stem(version: str, build_id: str | None = None) -> str:
    candidate = re.search(r"(\d+)\.(\d+).*?r(\d+(?:\.\d+)*)", version, re.I)
    stable = re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?", version.strip())
    suffix = _safe_build_id(build_id)
    if candidate:
        revision = candidate.group(3).replace(".", "_")
        base = f"Taxo_v{candidate.group(1)}_{candidate.group(2)}_candidate_r{revision}"
        return f"{base}_{suffix}_START" if suffix else f"{base}_START"
    if stable:
        parts = [stable.group(1), stable.group(2)]
        if stable.group(3) is not None:
            parts.append(stable.group(3))
        base = "Taxo_v" + "_".join(parts)
        return f"{base}_{suffix}_START" if suffix else f"{base}_START"
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", version).strip("_") or "candidate"
    base = f"Taxo_{safe}"
    return f"{base}_{suffix}_START" if suffix else f"{base}_START"


if __name__ == "__main__":
    print(start_archive_stem(version_from_file()))
