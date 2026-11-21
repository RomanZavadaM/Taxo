# -*- coding: utf-8 -*-
"""Read-only inventory for existing document archives.

This module deliberately has no file-writing operation. It inventories an
external folder so later AI/classification stages can work from a manifest
without moving, renaming or deleting source files.
"""
from __future__ import annotations

import hashlib
import json
import mimetypes
import uuid
from datetime import datetime, timezone
from pathlib import Path


INVENTORY_FORMAT = "taxo.document-inventory.v1"
_HASH_CHUNK = 1024 * 1024


def _sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(_HASH_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iso_mtime(stat):
    return datetime.fromtimestamp(
        stat.st_mtime, tz=timezone.utc
    ).isoformat(timespec="seconds")


def _candidate_id(relative_path, size, digest):
    raw = (
        str(relative_path).replace("\\", "/").casefold()
        + "\0" + str(int(size))
        + "\0" + str(digest)
    ).encode("utf-8")
    return "cand-" + hashlib.sha256(raw).hexdigest()[:24]


def _file_record(root, path):
    stat = path.stat()
    relative = path.relative_to(root).as_posix()
    digest = _sha256_file(path)
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return {
        "candidate_id": _candidate_id(relative, stat.st_size, digest),
        "source_path": str(path),
        "source_relpath": relative,
        "source_name": path.name,
        "sha256": digest,
        "mime_type": mime_type,
        "file_size": int(stat.st_size),
        "modified_at": _iso_mtime(stat),
        "extension": path.suffix.casefold(),
        "document_kind": "",
        "category": "",
        "document_number": "",
        "document_date": "",
        "registration_date": "",
        "received_date": "",
        "sent_date": "",
        "direction": "",
        "duplicate_of": "",
        "possible_duplicate_group": "",
        "logical_collection_ids": [],
        "tags": [],
        "ai_confidence": None,
        "ai_reason": "",
        "ai_model_or_rule": "",
        "review_state": "inventory",
    }


def build_inventory(root, batch_id=None):
    """Return a deterministic read-only inventory of *root*.

    Symlinks are never followed. Unreadable files are reported as errors.
    Exact duplicates are grouped only by SHA256; no similar-file decision is
    made here. The function does not create, update, move or delete any file.
    """
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("Папка для інвентаризації не існує")

    batch = str(batch_id or ("inventory-" + uuid.uuid4().hex))
    files = []
    skipped_symlinks = []
    errors = []

    candidates = sorted(
        root.rglob("*"),
        key=lambda item: item.relative_to(root).as_posix().casefold(),
    )
    for path in candidates:
        try:
            if path.is_symlink():
                skipped_symlinks.append(path.relative_to(root).as_posix())
                continue
            if not path.is_file():
                continue
            files.append(_file_record(root, path))
        except OSError as exc:
            errors.append({
                "source_relpath": path.relative_to(root).as_posix(),
                "error": str(exc),
            })

    by_hash = {}
    for row in files:
        by_hash.setdefault(row["sha256"], []).append(row)

    duplicate_groups = []
    duplicate_files = 0
    for digest, rows in sorted(by_hash.items()):
        if len(rows) < 2:
            continue
        rows.sort(key=lambda row: row["source_relpath"].casefold())
        canonical = rows[0]["candidate_id"]
        for row in rows[1:]:
            row["duplicate_of"] = canonical
        duplicate_files += len(rows)
        duplicate_groups.append({
            "sha256": digest,
            "canonical_candidate_id": canonical,
            "candidate_ids": [row["candidate_id"] for row in rows],
            "source_relpaths": [row["source_relpath"] for row in rows],
        })

    return {
        "format": INVENTORY_FORMAT,
        "read_only": True,
        "root": str(root),
        "import_batch_id": batch,
        "files": files,
        "exact_duplicate_groups": duplicate_groups,
        "skipped_symlinks": skipped_symlinks,
        "errors": errors,
        "summary": {
            "files": len(files),
            "bytes": sum(row["file_size"] for row in files),
            "exact_duplicate_groups": len(duplicate_groups),
            "exact_duplicate_files": duplicate_files,
            "skipped_symlinks": len(skipped_symlinks),
            "errors": len(errors),
        },
    }


def inventory_json(report):
    """Return machine-readable JSON without writing it to disk."""
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
