# -*- coding: utf-8 -*-
"""Immutable storage for filled CompanyTemplates draft snapshots.

PreparedDocuments is an intermediate workspace store. Each snapshot is written
once, addressed by a random stable ID and verified against the authoritative
index SHA-256. The store deliberately has no update/delete operation in r6.

It is not DocumentArchive and does not create orders, briefings, DOCX/PDF,
scans or signature state.
"""
from __future__ import annotations

import hashlib
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from prepared_document_codec import (
    build_snapshot_payload,
    canonical_json_bytes,
    strict_json_object,
    validate_snapshot_payload,
)

INDEX_FORMAT = "taxo.prepared-document-index.v1"
STORE_NAME = "PreparedDocuments"
MAX_INDEX_BYTES = 4 * 1024 * 1024
MAX_SNAPSHOT_BYTES = 32 * 1024 * 1024
_FILE = re.compile(r"^(pd-[a-f0-9]{32})\.json$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


@dataclass(frozen=True)
class PreparedDocumentSummary:
    """Verified immutable snapshot metadata from index.json."""

    snapshot_id: str
    title: str
    created_at: str
    company_template_id: str
    source_sha256: str
    edit_revision: int
    file_name: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class PreparedDocumentSnapshot:
    """Verified stored snapshot plus its integrity metadata."""

    summary: PreparedDocumentSummary
    data: dict


def prepared_documents_root(workspace_root: Path) -> Path:
    """Workspace-relative root; never an application/install directory."""
    return Path(workspace_root) / "Data" / STORE_NAME


def _validate_base(workspace_root: Path, *, create: bool) -> Path:
    root = prepared_documents_root(workspace_root)
    data = root.parent

    if data.exists() and (not data.is_dir() or data.is_symlink()):
        raise ValueError("Некоректна папка Data у робочому сховищі")
    if create and not data.exists():
        data.mkdir(parents=True, exist_ok=True)
    if not data.exists():
        return root

    if root.exists() and (not root.is_dir() or root.is_symlink()):
        raise ValueError("Некоректне сховище PreparedDocuments")
    if create and not root.exists():
        root.mkdir(parents=False, exist_ok=False)
    return root


def _ensure_items(root: Path) -> Path:
    items = root / "items"
    if items.exists() and (not items.is_dir() or items.is_symlink()):
        raise ValueError("Некоректна папка prepared snapshot-ів")
    if not items.exists():
        items.mkdir(parents=False, exist_ok=False)
    return items


def _read_bytes(path: Path, limit: int, description: str) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise ValueError("%s відсутній або небезпечний" % description)
    size = path.stat().st_size
    if size < 0 or size > limit:
        raise ValueError("%s перевищує допустимий розмір" % description)
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("%s перевищує допустимий розмір" % description)
    return raw


def _atomic_write(path: Path, payload: bytes) -> None:
    """Write bytes in the target directory then atomically replace target."""
    if path.parent.is_symlink() or not path.parent.is_dir():
        raise ValueError("Некоректна папка для prepared snapshot-а")
    temp = path.with_name(
        ".%s.%s.tmp" % (path.name, uuid.uuid4().hex)
    )
    try:
        with temp.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        try:
            if temp.exists():
                temp.unlink()
        except OSError:
            pass


def _summary(entry: object) -> PreparedDocumentSummary:
    if not isinstance(entry, dict):
        raise ValueError("Некоректний запис prepared snapshot-а")
    snapshot_id = entry.get("snapshot_id")
    file_name = entry.get("file")
    match = _FILE.fullmatch(str(file_name or ""))
    if (
        not isinstance(snapshot_id, str)
        or match is None
        or match.group(1) != snapshot_id
    ):
        raise ValueError("Некоректний ID/файл prepared snapshot-а")

    title = entry.get("title")
    created_at = entry.get("created_at")
    company_template_id = entry.get("company_template_id")
    source_sha256 = entry.get("source_sha256")
    edit_revision = entry.get("edit_revision")
    size_bytes = entry.get("size_bytes")
    digest = entry.get("sha256")

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Prepared snapshot не має назви")
    if not isinstance(created_at, str) or not created_at:
        raise ValueError("Prepared snapshot не має часу створення")
    if not isinstance(company_template_id, str) or not company_template_id:
        raise ValueError("Prepared snapshot не має source template ID")
    if not isinstance(source_sha256, str) or not _SHA256.fullmatch(source_sha256):
        raise ValueError("Prepared snapshot не має source SHA-256")
    if type(edit_revision) is not int or edit_revision < 1:
        raise ValueError("Prepared snapshot не має source edit revision")
    if type(size_bytes) is not int or size_bytes < 1 or size_bytes > MAX_SNAPSHOT_BYTES:
        raise ValueError("Некоректний розмір prepared snapshot-а")
    if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
        raise ValueError("Некоректний SHA-256 prepared snapshot-а")

    return PreparedDocumentSummary(
        snapshot_id=snapshot_id,
        title=title,
        created_at=created_at,
        company_template_id=company_template_id,
        source_sha256=source_sha256,
        edit_revision=edit_revision,
        file_name=file_name,
        size_bytes=size_bytes,
        sha256=digest,
    )


def _verified_payload(items: Path, summary: PreparedDocumentSummary) -> dict:
    path = items / summary.file_name
    raw = _read_bytes(
        path, MAX_SNAPSHOT_BYTES,
        "Prepared snapshot %s" % summary.snapshot_id,
    )
    if len(raw) != summary.size_bytes:
        raise ValueError("Змінено розмір prepared snapshot-а")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != summary.sha256:
        raise ValueError("Порушено цілісність prepared snapshot-а")
    data = strict_json_object(raw, summary.file_name)
    validate_snapshot_payload(data, expected_id=summary.snapshot_id)
    source = data["source"]
    if (
        data["title"] != summary.title
        or data["created_at"] != summary.created_at
        or source["company_template_id"] != summary.company_template_id
        or source["source_sha256"] != summary.source_sha256
        or source["edit_revision"] != summary.edit_revision
    ):
        raise ValueError("Prepared snapshot не збігається з індексом")
    return data


def _load_index(root: Path) -> Tuple[PreparedDocumentSummary, ...]:
    items = root / "items"
    index = root / "index.json"

    if not index.exists():
        if items.exists():
            if not items.is_dir() or items.is_symlink():
                raise ValueError("Некоректна папка prepared snapshot-ів")
            if any(items.iterdir()):
                raise ValueError(
                    "PreparedDocuments містить файли без індексу"
                )
        return ()

    raw = _read_bytes(index, MAX_INDEX_BYTES, "Індекс PreparedDocuments")
    data = strict_json_object(raw, "PreparedDocuments/index.json")
    if data.get("format") != INDEX_FORMAT or not isinstance(data.get("items"), list):
        raise ValueError("Некоректний індекс PreparedDocuments")

    if not items.is_dir() or items.is_symlink():
        raise ValueError("Немає коректної папки prepared snapshot-ів")

    summaries = tuple(_summary(entry) for entry in data["items"])
    ids = [item.snapshot_id for item in summaries]
    files = [item.file_name for item in summaries]
    if len(ids) != len(set(ids)) or len(files) != len(set(files)):
        raise ValueError("Індекс PreparedDocuments містить дублікати")

    actual = set()
    for path in items.iterdir():
        if path.is_symlink() or not path.is_file():
            raise ValueError(
                "PreparedDocuments містить небезпечний або невідомий об'єкт"
            )
        if path.name.startswith(".") and path.name.endswith(".tmp"):
            raise ValueError("PreparedDocuments містить незавершений temp-файл")
        if _FILE.fullmatch(path.name) is None:
            raise ValueError("PreparedDocuments містить невідомий файл")
        actual.add(path.name)

    expected = set(files)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        detail = []
        if missing:
            detail.append("відсутні: " + ", ".join(missing))
        if extra:
            detail.append("без індексу: " + ", ".join(extra))
        raise ValueError(
            "Порушено індекс PreparedDocuments (%s)" % "; ".join(detail)
        )

    for item in summaries:
        _verified_payload(items, item)

    return tuple(sorted(
        summaries,
        key=lambda item: (item.created_at, item.snapshot_id),
        reverse=True,
    ))


def list_prepared_snapshots(
    workspace_root: Path,
) -> Tuple[PreparedDocumentSummary, ...]:
    """List verified snapshots without creating missing storage."""
    root = _validate_base(Path(workspace_root), create=False)
    if not root.exists():
        return ()
    return _load_index(root)


def create_prepared_snapshot(
    workspace_root: Path,
    draft,
) -> PreparedDocumentSummary:
    """Persist one new immutable snapshot and atomically publish its index entry."""
    root = _validate_base(Path(workspace_root), create=True)
    items = _ensure_items(root)
    existing = list(_load_index(root))

    snapshot_id = "pd-" + uuid.uuid4().hex
    file_name = snapshot_id + ".json"
    target = items / file_name
    if target.exists():
        raise ValueError("Колізія ID prepared snapshot-а")

    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    data = build_snapshot_payload(draft, snapshot_id, created_at)
    payload = canonical_json_bytes(data)
    if len(payload) > MAX_SNAPSHOT_BYTES:
        raise ValueError("Prepared snapshot перевищує допустимий розмір")
    digest = hashlib.sha256(payload).hexdigest()

    summary = PreparedDocumentSummary(
        snapshot_id=snapshot_id,
        title=data["title"],
        created_at=created_at,
        company_template_id=data["source"]["company_template_id"],
        source_sha256=data["source"]["source_sha256"],
        edit_revision=data["source"]["edit_revision"],
        file_name=file_name,
        size_bytes=len(payload),
        sha256=digest,
    )

    _atomic_write(target, payload)
    try:
        index_payload = canonical_json_bytes({
            "format": INDEX_FORMAT,
            "items": [
                {
                    "snapshot_id": item.snapshot_id,
                    "title": item.title,
                    "created_at": item.created_at,
                    "company_template_id": item.company_template_id,
                    "source_sha256": item.source_sha256,
                    "edit_revision": item.edit_revision,
                    "file": item.file_name,
                    "size_bytes": item.size_bytes,
                    "sha256": item.sha256,
                }
                for item in (existing + [summary])
            ],
        })
        if len(index_payload) > MAX_INDEX_BYTES:
            raise ValueError("Індекс PreparedDocuments завеликий")
        _atomic_write(root / "index.json", index_payload)
    except Exception:
        try:
            target.unlink()
        except OSError:
            pass
        raise

    # Re-read from disk before returning; the committed bytes are the truth.
    committed = {
        item.snapshot_id: item
        for item in _load_index(root)
    }
    return committed[snapshot_id]


def load_prepared_snapshot(
    workspace_root: Path,
    snapshot_id: str,
) -> PreparedDocumentSnapshot:
    """Load one exact immutable snapshot after full index/hash validation."""
    root = _validate_base(Path(workspace_root), create=False)
    if not root.exists():
        raise ValueError("PreparedDocuments ще не створено")
    summaries = _load_index(root)
    matches = [item for item in summaries if item.snapshot_id == snapshot_id]
    if len(matches) != 1:
        raise ValueError("Prepared snapshot не знайдено")
    summary = matches[0]
    data = _verified_payload(root / "items", summary)
    return PreparedDocumentSnapshot(summary=summary, data=data)
