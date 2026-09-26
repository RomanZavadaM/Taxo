from __future__ import print_function

import os
from pathlib import Path

import pefile


def main():
    root_value = os.environ.get("TAXO_WIN7_BUNDLE", "").strip()
    if not root_value:
        raise SystemExit("TAXO_WIN7_BUNDLE is not set")

    root = Path(root_value)
    forbidden = b"api-ms-win-core-path-l1-1-0.dll"
    checked = 0
    offenders = []

    for path in root.rglob("*"):
        if path.suffix.lower() not in {".exe", ".dll", ".pyd"}:
            continue
        try:
            pe = pefile.PE(str(path), fast_load=True)
            directories = [pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]]
            delay_import = pefile.DIRECTORY_ENTRY.get("IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT")
            if delay_import is not None:
                directories.append(delay_import)
            pe.parse_data_directories(directories=directories)
        except Exception:
            continue

        checked += 1
        entries = list(getattr(pe, "DIRECTORY_ENTRY_IMPORT", []))
        entries += list(getattr(pe, "DIRECTORY_ENTRY_DELAY_IMPORT", []))
        for entry in entries:
            if (entry.dll or b"").lower() == forbidden:
                offenders.append(str(path.relative_to(root)))

    print("PE files checked:", checked)
    if checked == 0:
        raise SystemExit("No PE files inspected")
    if offenders:
        raise SystemExit(
            "Forbidden Win8+ path API import found: " + ", ".join(sorted(offenders))
        )


if __name__ == "__main__":
    main()
