# -*- coding: utf-8 -*-
"""Запускний модуль Taxo v8.45.

Базовий пакет v8.41 знаходиться у releases/Taxo_v8_41_source.zip.
Зміни v8.45 зберігаються у чотирьох текстових частинах патча.
Під час запуску пакет розпаковується локально, патч застосовується до main.py,
після чого запускається актуальна програма.
"""
from pathlib import Path
import hashlib
import re
import runpy
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "releases" / "Taxo_v8_41_source.zip"
PATCH_PARTS = [
    ROOT / "releases" / "Taxo_v8_45_main.part1",
    ROOT / "releases" / "Taxo_v8_45_main.part2",
    ROOT / "releases" / "Taxo_v8_45_main.part3",
    ROOT / "releases" / "Taxo_v8_45_main.part4",
]
RUNTIME = ROOT / ".taxo_runtime_v8_45"
MARKER = RUNTIME / ".v8_45_source_sha256"

for required in [ARCHIVE, *PATCH_PARTS]:
    if not required.exists():
        raise FileNotFoundError(f"Не знайдено файл програми: {required}")


def apply_unified_diff_text(original_text, patch_text):
    original = original_text.splitlines(True)
    patch = patch_text.splitlines(True)
    out = []
    source_index = 0
    patch_index = 0

    while patch_index < len(patch) and not patch[patch_index].startswith("@@ "):
        patch_index += 1

    while patch_index < len(patch):
        header = patch[patch_index].rstrip("\n")
        match = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", header)
        if not match:
            raise RuntimeError(f"Невірний формат патча: {header}")

        old_start = int(match.group(1)) - 1
        if old_start < source_index:
            raise RuntimeError("Перекриття блоків патча")

        out.extend(original[source_index:old_start])
        source_index = old_start
        patch_index += 1

        while patch_index < len(patch) and not patch[patch_index].startswith("@@ "):
            line = patch[patch_index]
            if line.startswith("\\ No newline at end of file"):
                patch_index += 1
                continue

            tag = line[:1]
            payload = line[1:]
            if tag == " ":
                if source_index >= len(original) or original[source_index] != payload:
                    raise RuntimeError(f"Патч не відповідає базовому main.py біля рядка {source_index + 1}")
                out.append(original[source_index])
                source_index += 1
            elif tag == "-":
                if source_index >= len(original) or original[source_index] != payload:
                    raise RuntimeError(f"Патч не відповідає базовому main.py біля рядка {source_index + 1}")
                source_index += 1
            elif tag == "+":
                out.append(payload)
            else:
                raise RuntimeError(f"Невідомий рядок патча: {line!r}")
            patch_index += 1

    out.extend(original[source_index:])
    return "".join(out)


patch_text = "".join(p.read_text(encoding="utf-8") for p in PATCH_PARTS)
source_hash = hashlib.sha256(ARCHIVE.read_bytes() + patch_text.encode("utf-8")).hexdigest()
need_extract = not (RUNTIME / "main.py").exists()

if not need_extract:
    try:
        need_extract = MARKER.read_text(encoding="utf-8").strip() != source_hash
    except OSError:
        need_extract = True

if need_extract:
    if RUNTIME.exists():
        shutil.rmtree(RUNTIME)
    RUNTIME.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(ARCHIVE, "r") as zf:
        zf.extractall(RUNTIME)

    runtime_main = RUNTIME / "main.py"
    patched = apply_unified_diff_text(
        runtime_main.read_text(encoding="utf-8"),
        patch_text,
    )
    runtime_main.write_text(patched, encoding="utf-8")
    MARKER.write_text(source_hash, encoding="utf-8")

runpy.run_path(str(RUNTIME / "main.py"), run_name="__main__")
