# -*- coding: utf-8 -*-
"""Запускний модуль Taxo v8.41.

Актуальний пакет програми зберігається у releases/Taxo_v8_41_source.zip.
Під час першого запуску або після оновлення архів розпаковується локально,
після чого запускається основний main.py.
"""
from pathlib import Path
import hashlib
import runpy
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "releases" / "Taxo_v8_41_source.zip"
RUNTIME = ROOT / ".taxo_runtime_v8_41"
MARKER = RUNTIME / ".source_sha256"

if not ARCHIVE.exists():
    raise FileNotFoundError(f"Не знайдено файл програми: {ARCHIVE}")

archive_sha = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
need_extract = not (RUNTIME / "main.py").exists()

if not need_extract:
    try:
        need_extract = MARKER.read_text(encoding="utf-8").strip() != archive_sha
    except OSError:
        need_extract = True

if need_extract:
    if RUNTIME.exists():
        shutil.rmtree(RUNTIME)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, "r") as zf:
        zf.extractall(RUNTIME)
    MARKER.write_text(archive_sha, encoding="utf-8")

runpy.run_path(str(RUNTIME / "main.py"), run_name="__main__")
