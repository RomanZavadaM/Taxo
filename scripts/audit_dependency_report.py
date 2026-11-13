#!/usr/bin/env python3
"""Audit pip installation reports before preparing a reviewed Windows wheel lock.

Read-only, standard-library-only utility. It does NOT install software or
declare that a package is malware-free. It fails if the report lacks verifiable
wheel archive metadata; never silently accepts a source distribution.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

_SHA256 = re.compile(r"^[a-fA-F0-9]{64}$")


def audit_report(report):
    if not isinstance(report, dict) or not isinstance(report.get("install"), list):
        raise ValueError("pip report must contain an install array")
    rows = []
    seen = set()
    for item in report["install"]:
        meta = item.get("metadata") or {}
        name = meta.get("name")
        version = meta.get("version")
        info = item.get("download_info") or {}
        url = info.get("url") or ""
        parsed = urlparse(url)
        filename = parsed.path.rsplit("/", 1)[-1]
        archive_info = info.get("archive_info") or {}
        hashes = archive_info.get("hashes") or {}
        sha = hashes.get("sha256")
        if not sha and str(archive_info.get("hash", "")).startswith("sha256="):
            sha = archive_info["hash"].split("=", 1)[1]
        if not isinstance(name, str) or not name.strip() or not isinstance(version, str) or not version:
            raise ValueError("Package metadata name/version missing")
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("Non-HTTPS package URL for %s" % name)
        if not filename.lower().endswith(".whl"):
            raise ValueError("Non-wheel distribution for %s: %s" % (name, filename))
        if not isinstance(sha, str) or not _SHA256.fullmatch(sha):
            raise ValueError("Missing or invalid SHA256 for %s" % name)
        key = name.lower().replace("_", "-")
        if key in seen:
            raise ValueError("Duplicate package entry: %s" % name)
        seen.add(key)
        rows.append({
            "name": key,
            "version": version,
            "filename": filename,
            "url": url,
            "sha256": sha.lower(),
        })
    if not rows:
        raise ValueError("Empty pip installation report")
    return sorted(rows, key=lambda item: (item["name"], item["version"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pip_report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = audit_report(json.loads(args.pip_report.read_text(encoding="utf-8")))
    data = {
        "schema": "taxo-reviewed-wheel-candidate-v1",
        "status": "unreviewed",
        "packages": manifest,
    }
    # The script never promotes candidate manifests to an approved lock.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Recorded %d wheel references; human/hash review still required" % len(manifest))


if __name__ == "__main__":
    main()
