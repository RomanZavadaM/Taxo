# -*- coding: utf-8 -*-
"""Bootstrap launcher for Taxo v8.29.

The full source package lives in releases/Taxo_v8_29_source.zip.
This file extracts it locally and executes the real application entry point.
"""
from pathlib import Path
import runpy
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "releases" / "Taxo_v8_29_source.zip"
RUNTIME = ROOT / ".taxo_runtime_v8_29"

if not ARCHIVE.exists():
    raise FileNotFoundError(f"Release archive not found: {ARCHIVE}")

# Refresh runtime if missing or older than the release archive.
need_extract = not (RUNTIME / "main.py").exists()
if not need_extract:
    try:
        need_extract = (RUNTIME / "main.py").stat().st_mtime < ARCHIVE.stat().st_mtime
    except OSError:
        need_extract = True

if need_extract:
    if RUNTIME.exists():
        shutil.rmtree(RUNTIME)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, "r") as zf:
        zf.extractall(RUNTIME)

runpy.run_path(str(RUNTIME / "main.py"), run_name="__main__")
