# -*- coding: utf-8 -*-
"""Immutable core storage for ready and archived Taxo documents.

DocumentVault is a separate workspace-relative store. An entry is created only
by an explicit call for one exact controlled PreparedDocument DOCX revision.
The source PaperDocuments record is never moved or changed.

This core intentionally has no legacy auto-migration, scan/original upload,
signature evidence or automatic "signed" state.
"""
from __future__ import annotations

import hashlib
import os
import re
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Tuple

from prepared_document_codec import canonical_json_bytes, strict_json_object
from prepared_document_revision import load_controlled_prepared_revision

STORE_NAME = "DocumentVault"
INDEX_NAME = "index.json"
INDEX_FORMAT = "taxo.document-vault-index.v1"
MAX_INDEX_BYTES = 8 * 1024 * 1024
MAX_OBJECT_BYTES = 64 * 1024 * 1024
_ALLOWED_STATUS = frozenset(("ready", "archived"))
_VAULT_ID = re.compile(r"^vd-[a-f0-9]{32}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_STORAGE_KEY = re.compile(
    r"^objects/([a-f0-9]{2})/(vd-[a-f0-9]{32})\.docx$"
)
_WRITE_LOCK = threading.RLock()


@dataclass(frozen=True)
class DocumentVaultRecord:
    """Verified metadata for one immutable DOCX object in DocumentVault."""

    vault_id: str
    title: str
    kind: str
    document_date: str
    status: str
    created_at: str
    source_document_id: str
    prepared_snapshot_id: str
    document_family_id: str
    document_revision: int
    company_template_id: str
    template_revision: int
    template_source_sha256: str
    content_sha256: str
    original_name: str
    storage_key: str
    size_bytes: int


@dataclass(frozen=True)
class DocumentVaultObject:
    """One verified vault record together with its exact stored bytes."""

    record: DocumentVaultRecord
    path: Path
    payload: bytes


def document_vault_root(workspace_root: Path) -> Path:
    """Return the workspace-relative vault root, never an install directory."""

    return Path(workspace_root) / "Data" / STORE_NAME


def _validate_root(workspace_root: Path, *, create: bool) -> Path:
    root = document_vault_root(workspace_root)
    data = root.parent
    if data.exists() and (not data.is_dir() or data.is_symlink()):
        raise ValueError("Некоректна папка Data у робочому сховищі")
    if create and not data.exists():
        data.mkdir(parents=True, exist_ok=False)
    if not data.exists():
        return root
    if root.exists() and (not root.is_dir() or root.is_symlink()):
        raise ValueError("Некоректне сховище DocumentVault")
    if create and not root.exists():
        root.mkdir(parents=False, exist_ok=False)
    return root


def _read_bytes(path: Path, limit: int, description: str) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise ValueError("%s відсутній або небезпечний" % description)
    size = path.stat().st_size
    if size < 1 or size > limit:
        raise ValueError("%s має некоректний розмір" % description)
    with path.open("rb") as stream:
        payload = stream.read(limit + 1)
    if len(payload) > limit:
        raise ValueError("%s перевищує допустимий розмір" % description)
    return payload


def _atomic_write(path: Path, payload: bytes) -> None:
    parent = path.parent
    if not parent.is_dir() or parent.is_symlink():
        raise ValueError("Некоректна папка DocumentVault")
    temporary = parent / (".%s.%s.tmp" % (path.name, uuid.uuid4().hex))
    try:
        with temporary.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temporary), str(path))
    finally:
        try:
            if temporary.exists():
                temporary.unlink()
        except OSError:
            pass


def _required_text(container, key, description):
    value = container.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError("Некоректне поле %s у DocumentVault" % description)
    return value


def _parse_created_at(value):
    if not isinstance(value, str) or not value:
        raise ValueError("Некоректний час запису DocumentVault")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Некоректний час запису DocumentVault") from exc
    if parsed.tzinfo is None:
        raise ValueError("Час запису DocumentVault не містить timezone")
    return value


def _record(entry) -> DocumentVaultRecord:
    if not isinstance(entry, dict) or set(entry) != {
        "id", "title", "kind", "document_date", "status", "created_at",
        "source", "file",
    }:
        raise ValueError("Некоректний запис DocumentVault")

    vault_id = _required_text(entry, "id", "id")
    if _VAULT_ID.fullmatch(vault_id) is None:
        raise ValueError("Некоректний ID DocumentVault")
    title = _required_text(entry, "title", "title")
    kind = _required_text(entry, "kind", "kind")
    document_date = entry.get("document_date")
    if not isinstance(document_date, str):
        raise ValueError("Некоректна дата документа у DocumentVault")
    status = entry.get("status")
    if status not in _ALLOWED_STATUS:
        raise ValueError("Некоректний стан документа у DocumentVault")
    created_at = _parse_created_at(entry.get("created_at"))

    source = entry.get("source")
    if not isinstance(source, dict) or set(source) != {
        "type", "paper_document_id", "prepared_snapshot_id",
        "document_family_id", "document_revision", "company_template_id",
        "template_revision", "template_source_sha256", "content_sha256",
    }:
        raise ValueError("Некоректне походження документа у DocumentVault")
    if source.get("type") != "prepared_document_revision":
        raise ValueError("Непідтримане походження документа у DocumentVault")
    source_document_id = _required_text(
        source, "paper_document_id", "paper document id"
    )
    prepared_snapshot_id = _required_text(
        source, "prepared_snapshot_id", "prepared snapshot id"
    )
    document_family_id = _required_text(
        source, "document_family_id", "document family id"
    )
    company_template_id = _required_text(
        source, "company_template_id", "company template id"
    )
    document_revision = source.get("document_revision")
    template_revision = source.get("template_revision")
    if type(document_revision) is not int or document_revision < 1:
        raise ValueError("Некоректна редакція документа у DocumentVault")
    if type(template_revision) is not int or template_revision < 1:
        raise ValueError("Некоректна редакція шаблону у DocumentVault")
    template_source_sha256 = source.get("template_source_sha256")
    content_sha256 = source.get("content_sha256")
    if (
        not isinstance(template_source_sha256, str)
        or _SHA256.fullmatch(template_source_sha256) is None
        or not isinstance(content_sha256, str)
        or _SHA256.fullmatch(content_sha256) is None
    ):
        raise ValueError("Некоректний SHA-256 походження у DocumentVault")

    file_data = entry.get("file")
    if not isinstance(file_data, dict) or set(file_data) != {
        "role", "original_name", "storage_key", "size_bytes", "sha256",
    }:
        raise ValueError("Некоректний файл DocumentVault")
    if file_data.get("role") != "generated_editable":
        raise ValueError("Непідтримана роль файла DocumentVault")
    original_name = _required_text(file_data, "original_name", "original name")
    if Path(original_name).name != original_name or not original_name.lower().endswith(
        ".docx"
    ):
        raise ValueError("Небезпечне початкове ім'я файла DocumentVault")
    storage_key = _required_text(file_data, "storage_key", "storage key")
    match = _STORAGE_KEY.fullmatch(storage_key)
    if match is None or match.group(2) != vault_id or match.group(1) != vault_id[3:5]:
        raise ValueError("Некоректний storage key DocumentVault")
    size_bytes = file_data.get("size_bytes")
    digest = file_data.get("sha256")
    if type(size_bytes) is not int or not 1 <= size_bytes <= MAX_OBJECT_BYTES:
        raise ValueError("Некоректний розмір файла DocumentVault")
    if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
        raise ValueError("Некоректний SHA-256 файла DocumentVault")
    if digest != content_sha256:
        raise ValueError("Файл DocumentVault не збігається з редакцією-джерелом")

    return DocumentVaultRecord(
        vault_id=vault_id,
        title=title,
        kind=kind,
        document_date=document_date,
        status=status,
        created_at=created_at,
        source_document_id=source_document_id,
        prepared_snapshot_id=prepared_snapshot_id,
        document_family_id=document_family_id,
        document_revision=document_revision,
        company_template_id=company_template_id,
        template_revision=template_revision,
        template_source_sha256=template_source_sha256,
        content_sha256=content_sha256,
        original_name=original_name,
        storage_key=storage_key,
        size_bytes=size_bytes,
    )


def _object_path(root: Path, storage_key: str) -> Path:
    match = _STORAGE_KEY.fullmatch(str(storage_key or ""))
    if match is None:
        raise ValueError("Некоректний storage key DocumentVault")
    pure = PurePosixPath(storage_key)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError("Небезпечний storage key DocumentVault")
    path = root.joinpath(*pure.parts)
    if path.parent.is_symlink():
        raise ValueError("Небезпечна папка об'єкта DocumentVault")
    return path


def _actual_objects(root: Path):
    objects = root / "objects"
    if not objects.exists():
        return set()
    if not objects.is_dir() or objects.is_symlink():
        raise ValueError("Некоректна папка objects у DocumentVault")
    actual = set()
    for shard in objects.iterdir():
        if (
            shard.is_symlink()
            or not shard.is_dir()
            or re.fullmatch(r"[a-f0-9]{2}", shard.name) is None
        ):
            raise ValueError("DocumentVault містить невідому папку objects")
        for path in shard.iterdir():
            if path.is_symlink() or not path.is_file():
                raise ValueError("DocumentVault містить небезпечний об'єкт")
            key = "objects/%s/%s" % (shard.name, path.name)
            if _STORAGE_KEY.fullmatch(key) is None:
                raise ValueError("DocumentVault містить невідомий файл")
            actual.add(key)
    return actual


def _verified_payload(root: Path, record: DocumentVaultRecord) -> bytes:
    path = _object_path(root, record.storage_key)
    payload = _read_bytes(
        path, MAX_OBJECT_BYTES, "Об'єкт %s" % record.vault_id
    )
    if len(payload) != record.size_bytes:
        raise ValueError("Змінено розмір об'єкта DocumentVault")
    if hashlib.sha256(payload).hexdigest() != record.content_sha256:
        raise ValueError("Порушено цілісність об'єкта DocumentVault")
    return payload


def _load_index(root: Path) -> Tuple[DocumentVaultRecord, ...]:
    allowed_root_names = {INDEX_NAME, "objects"}
    for child in root.iterdir():
        if child.name not in allowed_root_names:
            raise ValueError("DocumentVault містить невідомий об'єкт")

    index_path = root / INDEX_NAME
    actual = _actual_objects(root)
    if not index_path.exists():
        if actual:
            raise ValueError("DocumentVault містить файли без індексу")
        return ()

    raw = _read_bytes(index_path, MAX_INDEX_BYTES, "Індекс DocumentVault")
    data = strict_json_object(raw, "DocumentVault/index.json")
    if data.get("format") != INDEX_FORMAT or set(data) != {"format", "items"}:
        raise ValueError("Некоректний індекс DocumentVault")
    if not isinstance(data.get("items"), list):
        raise ValueError("Індекс DocumentVault не містить списку документів")

    records = tuple(_record(entry) for entry in data["items"])
    ids = [item.vault_id for item in records]
    source_ids = [item.source_document_id for item in records]
    storage_keys = [item.storage_key for item in records]
    if (
        len(ids) != len(set(ids))
        or len(source_ids) != len(set(source_ids))
        or len(storage_keys) != len(set(storage_keys))
    ):
        raise ValueError("Індекс DocumentVault містить дублікати")

    expected = set(storage_keys)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        details = []
        if missing:
            details.append("відсутні: " + ", ".join(missing))
        if extra:
            details.append("без індексу: " + ", ".join(extra))
        raise ValueError(
            "Порушено індекс DocumentVault (%s)" % "; ".join(details)
        )

    for item in records:
        _verified_payload(root, item)

    return tuple(sorted(
        records,
        key=lambda item: (item.created_at, item.vault_id),
        reverse=True,
    ))


def list_document_vault(
    workspace_root: Path,
) -> Tuple[DocumentVaultRecord, ...]:
    """List all verified vault records without creating missing storage."""

    root = _validate_root(Path(workspace_root), create=False)
    if not root.exists():
        return ()
    return _load_index(root)


def _entry(record: DocumentVaultRecord):
    return {
        "id": record.vault_id,
        "title": record.title,
        "kind": record.kind,
        "document_date": record.document_date,
        "status": record.status,
        "created_at": record.created_at,
        "source": {
            "type": "prepared_document_revision",
            "paper_document_id": record.source_document_id,
            "prepared_snapshot_id": record.prepared_snapshot_id,
            "document_family_id": record.document_family_id,
            "document_revision": record.document_revision,
            "company_template_id": record.company_template_id,
            "template_revision": record.template_revision,
            "template_source_sha256": record.template_source_sha256,
            "content_sha256": record.content_sha256,
        },
        "file": {
            "role": "generated_editable",
            "original_name": record.original_name,
            "storage_key": record.storage_key,
            "size_bytes": record.size_bytes,
            "sha256": record.content_sha256,
        },
    }


def register_prepared_revision(
    workspace_root: Path,
    paper_document_id: str,
    *,
    status: str = "ready"
) -> DocumentVaultRecord:
    """Copy one exact prepared DOCX revision into DocumentVault.

    The operation is explicit and append-only. The same PaperDocuments revision
    cannot be registered twice. Neither a signature nor an issued business fact
    is inferred from this copy.
    """

    if status not in _ALLOWED_STATUS:
        raise ValueError("Стан DocumentVault має бути ready або archived")
    workspace_root = Path(workspace_root)

    with _WRITE_LOCK:
        controlled = load_controlled_prepared_revision(
            workspace_root, paper_document_id
        )
        source = controlled.record
        root = _validate_root(workspace_root, create=True)
        existing = list(_load_index(root))
        if any(
            item.source_document_id == source["id"] for item in existing
        ):
            raise ValueError("Ця Word-редакція вже є у DocumentVault")

        payload = controlled.payload
        if not payload or len(payload) > MAX_OBJECT_BYTES:
            raise ValueError("Word-редакція перевищує межі DocumentVault")
        digest = hashlib.sha256(payload).hexdigest()
        if digest != controlled.sha256 or digest != source.get("content_sha256"):
            raise ValueError("Word-редакція не збігається з каталогом Taxo")

        vault_id = "vd-" + uuid.uuid4().hex
        shard = vault_id[3:5]
        storage_key = "objects/%s/%s.docx" % (shard, vault_id)
        objects = root / "objects"
        if objects.exists() and (not objects.is_dir() or objects.is_symlink()):
            raise ValueError("Некоректна папка objects у DocumentVault")
        if not objects.exists():
            objects.mkdir(parents=False, exist_ok=False)
        shard_dir = objects / shard
        if shard_dir.exists() and (
            not shard_dir.is_dir() or shard_dir.is_symlink()
        ):
            raise ValueError("Некоректна shard-папка DocumentVault")
        if not shard_dir.exists():
            shard_dir.mkdir(parents=False, exist_ok=False)

        target = _object_path(root, storage_key)
        if target.exists():
            raise ValueError("Колізія ID DocumentVault")

        record = DocumentVaultRecord(
            vault_id=vault_id,
            title=str(source.get("title") or "Підготовлений документ"),
            kind=str(source.get("kind") or "Підготовлений документ"),
            document_date=str(source.get("date") or ""),
            status=status,
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            source_document_id=source["id"],
            prepared_snapshot_id=source["prepared_snapshot_id"],
            document_family_id=source["document_family_id"],
            document_revision=source["document_revision"],
            company_template_id=source["company_template_id"],
            template_revision=source["template_revision"],
            template_source_sha256=source["template_source_sha256"],
            content_sha256=digest,
            original_name=controlled.path.name,
            storage_key=storage_key,
            size_bytes=len(payload),
        )

        _atomic_write(target, payload)
        try:
            index_payload = canonical_json_bytes({
                "format": INDEX_FORMAT,
                "items": [_entry(item) for item in existing + [record]],
            })
            if len(index_payload) > MAX_INDEX_BYTES:
                raise ValueError("Індекс DocumentVault завеликий")
            _atomic_write(root / INDEX_NAME, index_payload)
        except Exception:
            try:
                target.unlink()
            except OSError:
                pass
            raise

        committed = {
            item.vault_id: item for item in _load_index(root)
        }
        return committed[vault_id]


def load_document_vault_object(
    workspace_root: Path,
    vault_id: str,
) -> DocumentVaultObject:
    """Load one exact immutable vault object after full index/hash checks."""

    root = _validate_root(Path(workspace_root), create=False)
    if not root.exists():
        raise ValueError("DocumentVault ще не створено")
    matches = [
        item for item in _load_index(root) if item.vault_id == vault_id
    ]
    if len(matches) != 1:
        raise ValueError("Документ у DocumentVault не знайдено")
    record = matches[0]
    path = _object_path(root, record.storage_key)
    payload = _verified_payload(root, record)
    return DocumentVaultObject(record=record, path=path, payload=payload)
