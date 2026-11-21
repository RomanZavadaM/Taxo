# -*- coding: utf-8 -*-
"""Atomic persistence for read-only document inventory batches.

This module writes only into the managed Taxo workspace. It never modifies the
scanned source archive. A completed batch directory is published atomically.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import threading
import uuid
from pathlib import Path

from document_import_inventory import INVENTORY_FORMAT


BATCH_FORMAT = "taxo.document-import-batch.v1"
MANIFEST_NAME = "inventory.json"
REPORT_NAME = "report.json"
_BATCH_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_WRITE_LOCK = threading.RLock()


def import_batches_root(workspace_root):
    return Path(workspace_root) / "Data" / "DocumentLibrary" / "import_batches"


def _canonical_json_bytes(data):
    return (
        json.dumps(
            data,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def _validate_report(report):
    if not isinstance(report, dict):
        raise ValueError("Некоректний dry-run inventory")
    if report.get("format") != INVENTORY_FORMAT or report.get("read_only") is not True:
        raise ValueError("Несумісний формат dry-run inventory")
    batch_id = str(report.get("import_batch_id") or "")
    if _BATCH_ID.fullmatch(batch_id) is None:
        raise ValueError("Некоректний import_batch_id")
    source_root = Path(str(report.get("root") or "")).expanduser()
    if not source_root.is_absolute():
        raise ValueError("Inventory не містить абсолютного source root")
    if not isinstance(report.get("files"), list):
        raise ValueError("Inventory не містить списку файлів")
    if not isinstance(report.get("summary"), dict):
        raise ValueError("Inventory не містить summary")
    return batch_id, source_root.resolve()


def _report_payload(report, manifest_sha256):
    return {
        "format": BATCH_FORMAT,
        "inventory_format": report["format"],
        "import_batch_id": report["import_batch_id"],
        "source_root": report["root"],
        "read_only": True,
        "manifest_sha256": manifest_sha256,
        "summary": report["summary"],
        "exact_duplicate_groups": report.get("exact_duplicate_groups", []),
        "skipped_symlinks": report.get("skipped_symlinks", []),
        "errors": report.get("errors", []),
    }


def _inside(child, parent):
    try:
        Path(child).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False


def _existing_matches(target, manifest_payload, report_payload):
    manifest = target / MANIFEST_NAME
    report = target / REPORT_NAME
    if (
        not target.is_dir()
        or target.is_symlink()
        or not manifest.is_file()
        or manifest.is_symlink()
        or not report.is_file()
        or report.is_symlink()
    ):
        raise ValueError("Пошкоджений або неповний import batch")
    if manifest.read_bytes() != manifest_payload or report.read_bytes() != report_payload:
        raise ValueError("Import batch з таким ID вже існує з іншим вмістом")
    return {
        "batch_dir": target,
        "manifest": manifest,
        "report": report,
        "reused": True,
    }


def persist_inventory_batch(workspace_root, inventory):
    """Atomically persist one completed dry-run batch under Taxo workspace.

    Repeating the exact same batch is idempotent. Reusing a batch ID with
    different content is rejected. The destination is forbidden from being
    inside the scanned source root.
    """
    batch_id, source_root = _validate_report(inventory)
    root = import_batches_root(workspace_root).resolve()
    target = root / batch_id

    if _inside(root, source_root) or _inside(target, source_root):
        raise ValueError(
            "Сховище import batch не може бути всередині source-архіву"
        )

    manifest_payload = _canonical_json_bytes(inventory)
    manifest_sha256 = _sha256_bytes(manifest_payload)
    report_payload = _canonical_json_bytes(
        _report_payload(inventory, manifest_sha256)
    )

    with _WRITE_LOCK:
        if target.exists():
            return _existing_matches(
                target, manifest_payload, report_payload
            )

        data_dir = root.parent.parent
        library_dir = root.parent
        for path, label in (
            (data_dir, "Data"),
            (library_dir, "DocumentLibrary"),
            (root, "import_batches"),
        ):
            if path.exists() and (not path.is_dir() or path.is_symlink()):
                raise ValueError("Некоректне сховище %s" % label)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=False)

        temporary = root / (
            ".%s.%s.tmp" % (batch_id, uuid.uuid4().hex)
        )
        temporary.mkdir(parents=False, exist_ok=False)
        try:
            manifest = temporary / MANIFEST_NAME
            summary = temporary / REPORT_NAME
            for path, payload in (
                (manifest, manifest_payload),
                (summary, report_payload),
            ):
                with path.open("xb") as stream:
                    stream.write(payload)
                    stream.flush()
                    os.fsync(stream.fileno())

            os.rename(str(temporary), str(target))
            return {
                "batch_dir": target,
                "manifest": target / MANIFEST_NAME,
                "report": target / REPORT_NAME,
                "reused": False,
            }
        finally:
            if temporary.exists():
                shutil.rmtree(temporary, ignore_errors=True)


def read_inventory_batch(workspace_root, batch_id):
    """Read a completed batch and verify report ↔ manifest integrity."""
    batch_id = str(batch_id or "")
    if _BATCH_ID.fullmatch(batch_id) is None:
        raise ValueError("Некоректний import_batch_id")
    target = import_batches_root(workspace_root) / batch_id
    manifest = target / MANIFEST_NAME
    report = target / REPORT_NAME
    if (
        not target.is_dir()
        or target.is_symlink()
        or not manifest.is_file()
        or manifest.is_symlink()
        or not report.is_file()
        or report.is_symlink()
    ):
        raise ValueError("Import batch не знайдено або пошкоджено")
    try:
        inventory = json.loads(manifest.read_text("utf-8"))
        summary = json.loads(report.read_text("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Пошкоджений import batch") from exc
    if summary.get("format") != BATCH_FORMAT:
        raise ValueError("Несумісний формат import batch")
    expected = str(summary.get("manifest_sha256") or "")
    actual = _sha256_bytes(manifest.read_bytes())
    if expected != actual:
        raise ValueError("Контрольна сума inventory manifest не збігається")
    if str(summary.get("import_batch_id") or "") != batch_id:
        raise ValueError("Import batch має невірний ID")
    return {"inventory": inventory, "report": summary}
