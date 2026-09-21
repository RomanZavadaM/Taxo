# -*- coding: utf-8 -*-
"""Generate/check the direct-dependency CycloneDX SBOM tracked by Taxo."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

LICENSES = {
    "python-docx": "MIT",
    "openpyxl": "MIT",
    "reportlab": "BSD-3-Clause",
    "pillow": "MIT-CMU",
    "pypdf": "BSD-3-Clause",
    "pypdfium2": "Apache-2.0 OR BSD-3-Clause",
    "opencv-python-headless": "MIT",
    "pywin32": "NOASSERTION",
}


def app_version(version_file):
    text = Path(version_file).read_text("utf-8")
    match = re.search(r"^Version:\s*(.+)$", text, re.MULTILINE)
    if not match:
        raise SystemExit("Version not found")
    return match.group(1).strip()


def requirements(path):
    rows = []
    for raw in Path(path).read_text("utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        req, _, marker = line.partition(";")
        if "==" not in req:
            raise SystemExit(f"Unpinned runtime requirement: {line}")
        name, version = [x.strip() for x in req.split("==", 1)]
        rows.append((name, version, marker.strip()))
    return rows


def build():
    version = app_version("VERSION.txt")
    components = []
    for name, dep_version, marker in requirements("requirements.txt"):
        key = name.lower()
        license_value = LICENSES.get(key, "NOASSERTION")
        license_entry = (
            {"expression": license_value}
            if " OR " in license_value
            else {"license": {"id": license_value}}
        )
        component = {
            "type": "library",
            "name": name,
            "version": dep_version,
            "purl": f"pkg:pypi/{name}@{dep_version}",
            "licenses": [license_entry],
        }
        if marker:
            component["properties"] = [{"name": "python:environment-marker", "value": marker}]
        components.append(component)
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": "urn:uuid:taxo-10-2-r9-direct-dependencies",
        "version": 1,
        "metadata": {
            "timestamp": "2026-09-21T00:00:00Z",
            "component": {
                "type": "application",
                "name": "Taxo / Driver Worktime",
                "version": version,
                "copyright": "Copyright © 2026 Roman Zavada (Роман Завада)",
            },
            "properties": [
                {"name": "taxo:sbom-scope", "value": "direct runtime dependencies"},
                {"name": "taxo:owner", "value": "Roman Zavada (Роман Завада)"},
            ],
        },
        "components": components,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="SBOM.cdx.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = build()
    path = Path(args.output)
    if args.check:
        current = json.loads(path.read_text("utf-8"))
        if current != expected:
            raise SystemExit(f"{path} is out of date")
        print(f"{path} is current")
        return
    path.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(path)


if __name__ == "__main__":
    main()
