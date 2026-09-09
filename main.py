# -*- coding: utf-8 -*-
"""Запускний модуль Taxo v8.29.

Повний пакет програми знаходиться у releases/Taxo_v8_29_source.zip.
Цей файл локально розпаковує пакет і запускає основну програму.
"""
from pathlib import Path
import runpy
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "releases" / "Taxo_v8_29_source.zip"
RUNTIME = ROOT / ".taxo_runtime_v8_29"

if not ARCHIVE.exists():
    raise FileNotFoundError(f"Не знайдено архів програми: {ARCHIVE}")

# Повторно розпаковуємо пакет, якщо локальна копія відсутня або застаріла.
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
