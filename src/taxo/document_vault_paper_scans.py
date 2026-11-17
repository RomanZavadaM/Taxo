# -*- coding: utf-8 -*-
"""Safe immutable paper-scan attachments for DocumentVault.

A paper scan is an optional copy attached to one existing vault document.
Adding a scan never changes the document's business state and never means that
the signature is valid. The original external file is copied into the Taxo
workspace; it is never opened or executed by this module.
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

from document_vault_store import document_vault_root, list_document_vault
from prepared_document_codec import canonical_json_bytes, strict_json_object

ATTACHMENTS_NAME = "attachments"
INDEX_NAME = "index.json"
INDEX_FORMAT = "taxo.document-vault-paper-scan-index.v1"
HISTORY_NAME = "history.json"
HISTORY_FORMAT = "taxo.document-vault-paper-scan-history.v1"
MAX_INDEX_BYTES = 8 * 1024 * 1024
MAX_HISTORY_BYTES = 8 * 1024 * 1024
MAX_SCAN_BYTES = 256 * 1024 * 1024
_CHUNK_BYTES = 1024 * 1024
_ATTACHMENT_ID = re.compile(r"^va-[a-f0-9]{32}$")
_HISTORY_ID = re.compile(r"^vh-[a-f0-9]{32}$")
_VAULT_ID = re.compile(r"^vd-[a-f0-9]{32}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_STORAGE_KEY = re.compile(
    r"^objects/([a-f0-9]{2})/(va-[a-f0-9]{32})\.(pdf|jpg|png|tiff)$"
)
_WRITE_LOCK = threading.RLock()

_SOURCE_SUFFIXES = {
    ".pdf": ("pdf", "application/pdf"),
    ".jpg": ("jpg", "image/jpeg"),
    ".jpeg": ("jpg", "image/jpeg"),
    ".png": ("png", "image/png"),
    ".tif": ("tiff", "image/tiff"),
    ".tiff": ("tiff", "image/tiff"),
}


@dataclass(frozen=True)
class PaperScanRecord:
    """Verified metadata for one immutable paper scan."""

    attachment_id: str
    vault_id: str
    created_at: str
    role: str
    original_name: str
    media_type: str
    storage_key: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class PaperScanObject:
    """Verified scan metadata and its local immutable path."""

    record: PaperScanRecord
    path: Path


@dataclass(frozen=True)
class PaperScanHistoryRecord:
    """One append-only user action affecting an immutable scan."""

    action_id: str
    attachment_id: str
    vault_id: str
    created_at: str
    action: str


@dataclass(frozen=True)
class RemovedPaperScan:
    """Inactive scan metadata paired with its preserved immutable record."""

    history: PaperScanHistoryRecord
    record: PaperScanRecord


@dataclass(frozen=True)
class ReplacedPaperScan:
    """One completed user-requested replacement of an active scan."""

    previous: RemovedPaperScan
    current: PaperScanRecord


def paper_scan_root(workspace_root: Path) -> Path:
    """Return the attachment area inside the selected workspace vault."""

    return document_vault_root(Path(workspace_root)) / ATTACHMENTS_NAME


def _atomic_write(path: Path, payload: bytes) -> None:
    parent = path.parent
    if not parent.is_dir() or parent.is_symlink():
        raise ValueError("Некоректна папка вкладень DocumentVault")
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


def _read_limited_bytes(path: Path, limit: int, description: str) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise ValueError("%s відсутній або небезпечний" % description)
    size = path.stat().st_size
    if size < 1 or size > limit:
        raise ValueError("%s має некоректний розмір" % description)
    with path.open("rb") as stream:
        payload = stream.read(limit + 1)
    if len(payload) > limit:
        raise ValueError("%s завеликий" % description)
    return payload


def _parse_created_at(value, description="додавання скана"):
    if not isinstance(value, str) or not value:
        raise ValueError("Некоректний час %s" % description)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Некоректний час %s" % description) from exc
    if parsed.tzinfo is None:
        raise ValueError("Час %s не містить timezone" % description)
    return value


def _required_text(container, key, description):
    value = container.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError("Некоректне поле %s у скані" % description)
    return value


def _record(entry) -> PaperScanRecord:
    if not isinstance(entry, dict) or set(entry) != {
        "id", "vault_id", "created_at", "role", "file",
    }:
        raise ValueError("Некоректний запис скана DocumentVault")

    attachment_id = _required_text(entry, "id", "id")
    vault_id = _required_text(entry, "vault_id", "vault id")
    if _ATTACHMENT_ID.fullmatch(attachment_id) is None:
        raise ValueError("Некоректний ID скана")
    if _VAULT_ID.fullmatch(vault_id) is None:
        raise ValueError("Некоректний ID документа для скана")
    created_at = _parse_created_at(entry.get("created_at"))
    if entry.get("role") != "paper_scan":
        raise ValueError("Непідтримана роль вкладення")

    file_data = entry.get("file")
    if not isinstance(file_data, dict) or set(file_data) != {
        "original_name", "media_type", "storage_key", "size_bytes", "sha256",
    }:
        raise ValueError("Некоректний файл скана")
    original_name = _required_text(file_data, "original_name", "original name")
    if Path(original_name).name != original_name:
        raise ValueError("Небезпечне початкове ім'я скана")
    media_type = _required_text(file_data, "media_type", "media type")
    storage_key = _required_text(file_data, "storage_key", "storage key")
    match = _STORAGE_KEY.fullmatch(storage_key)
    if (
        match is None
        or match.group(2) != attachment_id
        or match.group(1) != attachment_id[3:5]
    ):
        raise ValueError("Некоректний шлях скана у сховищі")
    expected_media = {
        "pdf": "application/pdf",
        "jpg": "image/jpeg",
        "png": "image/png",
        "tiff": "image/tiff",
    }[match.group(3)]
    if media_type != expected_media:
        raise ValueError("Тип файла скана не збігається зі сховищем")
    size_bytes = file_data.get("size_bytes")
    digest = file_data.get("sha256")
    if type(size_bytes) is not int or not 1 <= size_bytes <= MAX_SCAN_BYTES:
        raise ValueError("Некоректний розмір скана")
    if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
        raise ValueError("Некоректний SHA-256 скана")

    return PaperScanRecord(
        attachment_id=attachment_id,
        vault_id=vault_id,
        created_at=created_at,
        role="paper_scan",
        original_name=original_name,
        media_type=media_type,
        storage_key=storage_key,
        size_bytes=size_bytes,
        sha256=digest,
    )


def _history_record(entry) -> PaperScanHistoryRecord:
    if not isinstance(entry, dict) or set(entry) != {
        "id", "attachment_id", "vault_id", "created_at", "action",
    }:
        raise ValueError("Некоректний запис історії скана")

    action_id = _required_text(entry, "id", "history id")
    attachment_id = _required_text(entry, "attachment_id", "attachment id")
    vault_id = _required_text(entry, "vault_id", "vault id")
    if _HISTORY_ID.fullmatch(action_id) is None:
        raise ValueError("Некоректний ID історії скана")
    if _ATTACHMENT_ID.fullmatch(attachment_id) is None:
        raise ValueError("Некоректний ID скана в історії")
    if _VAULT_ID.fullmatch(vault_id) is None:
        raise ValueError("Некоректний ID документа в історії скана")
    created_at = _parse_created_at(
        entry.get("created_at"),
        "дії зі сканом",
    )
    action = entry.get("action")
    if action not in {"removed", "replaced"}:
        raise ValueError("Непідтримана дія в історії скана")

    return PaperScanHistoryRecord(
        action_id=action_id,
        attachment_id=attachment_id,
        vault_id=vault_id,
        created_at=created_at,
        action=action,
    )


def _detect_scan(header: bytes):
    if header.startswith(b"%PDF-"):
        return "pdf", "application/pdf"
    if header.startswith(b"\xff\xd8\xff"):
        return "jpg", "image/jpeg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png", "image/png"
    if header.startswith((b"II*\x00", b"MM\x00*")):
        return "tiff", "image/tiff"
    raise ValueError("Файл не схожий на підтримуваний PDF/JPG/PNG/TIFF")


def _attachment_root(workspace_root: Path, *, create: bool) -> Path:
    vault_root = document_vault_root(Path(workspace_root))
    if not vault_root.exists():
        raise ValueError("Спочатку збережіть документ у сховищі")
    if not vault_root.is_dir() or vault_root.is_symlink():
        raise ValueError("Некоректне сховище DocumentVault")
    root = vault_root / ATTACHMENTS_NAME
    if root.exists() and (not root.is_dir() or root.is_symlink()):
        raise ValueError("Некоректна папка вкладень DocumentVault")
    if create and not root.exists():
        root.mkdir(parents=False, exist_ok=False)
    return root


def _object_path(root: Path, storage_key: str) -> Path:
    match = _STORAGE_KEY.fullmatch(str(storage_key or ""))
    if match is None:
        raise ValueError("Некоректний шлях скана у сховищі")
    pure = PurePosixPath(storage_key)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError("Небезпечний шлях скана у сховищі")
    path = root.joinpath(*pure.parts)
    if path.parent.is_symlink():
        raise ValueError("Небезпечна папка скана")
    return path


def _actual_objects(root: Path):
    objects = root / "objects"
    if not objects.exists():
        return set()
    if not objects.is_dir() or objects.is_symlink():
        raise ValueError("Некоректна папка сканів")
    actual = set()
    for shard in objects.iterdir():
        if (
            shard.is_symlink()
            or not shard.is_dir()
            or re.fullmatch(r"[a-f0-9]{2}", shard.name) is None
        ):
            raise ValueError("Сховище сканів містить невідому папку")
        for path in shard.iterdir():
            if path.is_symlink() or not path.is_file():
                raise ValueError("Сховище сканів містить небезпечний об'єкт")
            key = "objects/%s/%s" % (shard.name, path.name)
            if _STORAGE_KEY.fullmatch(key) is None:
                raise ValueError("Сховище сканів містить невідомий файл")
            actual.add(key)
    return actual


def _verify_object(root: Path, record: PaperScanRecord) -> Path:
    path = _object_path(root, record.storage_key)
    if not path.is_file() or path.is_symlink():
        raise ValueError("Скан відсутній або небезпечний")
    digest = hashlib.sha256()
    total = 0
    header = b""
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(_CHUNK_BYTES)
            if not chunk:
                break
            if not header:
                header = chunk[:16]
            total += len(chunk)
            if total > MAX_SCAN_BYTES:
                raise ValueError("Скан перевищує допустимий розмір")
            digest.update(chunk)
    detected_ext, detected_media = _detect_scan(header)
    expected_ext = _STORAGE_KEY.fullmatch(record.storage_key).group(3)
    if detected_ext != expected_ext or detected_media != record.media_type:
        raise ValueError("Змінено тип файла скана")
    if total != record.size_bytes:
        raise ValueError("Змінено розмір скана")
    if digest.hexdigest() != record.sha256:
        raise ValueError("Порушено цілісність скана")
    return path


def _entry(record: PaperScanRecord):
    return {
        "id": record.attachment_id,
        "vault_id": record.vault_id,
        "created_at": record.created_at,
        "role": "paper_scan",
        "file": {
            "original_name": record.original_name,
            "media_type": record.media_type,
            "storage_key": record.storage_key,
            "size_bytes": record.size_bytes,
            "sha256": record.sha256,
        },
    }


def _history_entry(record: PaperScanHistoryRecord):
    return {
        "id": record.action_id,
        "attachment_id": record.attachment_id,
        "vault_id": record.vault_id,
        "created_at": record.created_at,
        "action": record.action,
    }


def _load_index(
    root: Path,
    valid_vault_ids,
) -> Tuple[PaperScanRecord, ...]:
    allowed = {INDEX_NAME, HISTORY_NAME, "objects"}
    for child in root.iterdir():
        if child.name not in allowed:
            raise ValueError("Сховище сканів містить невідомий об'єкт")

    actual = _actual_objects(root)
    index_path = root / INDEX_NAME
    if not index_path.exists():
        if actual:
            raise ValueError("Сховище сканів містить файли без індексу")
        return ()

    data = strict_json_object(
        _read_limited_bytes(
            index_path,
            MAX_INDEX_BYTES,
            "Індекс сканів",
        ),
        "DocumentVault/attachments/index.json",
    )
    if data.get("format") != INDEX_FORMAT or set(data) != {"format", "items"}:
        raise ValueError("Некоректний індекс сканів")
    if not isinstance(data.get("items"), list):
        raise ValueError("Індекс сканів не містить списку")

    records = tuple(_record(item) for item in data["items"])
    ids = [item.attachment_id for item in records]
    keys = [item.storage_key for item in records]
    if len(ids) != len(set(ids)) or len(keys) != len(set(keys)):
        raise ValueError("Індекс сканів містить дублікати")
    if any(item.vault_id not in valid_vault_ids for item in records):
        raise ValueError("Скан посилається на відсутній документ")

    expected = set(keys)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        details = []
        if missing:
            details.append("відсутні: " + ", ".join(missing))
        if extra:
            details.append("без індексу: " + ", ".join(extra))
        raise ValueError("Порушено індекс сканів (%s)" % "; ".join(details))

    for record in records:
        _verify_object(root, record)

    return tuple(sorted(
        records,
        key=lambda item: (item.created_at, item.attachment_id),
        reverse=True,
    ))


def _load_history(
    root: Path,
    records: Tuple[PaperScanRecord, ...],
) -> Tuple[PaperScanHistoryRecord, ...]:
    path = root / HISTORY_NAME
    if not path.exists():
        return ()

    data = strict_json_object(
        _read_limited_bytes(
            path,
            MAX_HISTORY_BYTES,
            "Історія сканів",
        ),
        "DocumentVault/attachments/history.json",
    )
    if data.get("format") != HISTORY_FORMAT or set(data) != {"format", "items"}:
        raise ValueError("Некоректна історія сканів")
    if not isinstance(data.get("items"), list):
        raise ValueError("Історія сканів не містить списку")

    history = tuple(_history_record(item) for item in data["items"])
    action_ids = [item.action_id for item in history]
    attachment_ids = [item.attachment_id for item in history]
    if len(action_ids) != len(set(action_ids)):
        raise ValueError("Історія сканів містить дублікати дій")
    if len(attachment_ids) != len(set(attachment_ids)):
        raise ValueError("Скан не може бути деактивований двічі")

    by_id = {item.attachment_id: item for item in records}
    for item in history:
        scan = by_id.get(item.attachment_id)
        if scan is None:
            raise ValueError("Історія посилається на відсутній скан")
        if scan.vault_id != item.vault_id:
            raise ValueError("Історія скана посилається на інший документ")

    return tuple(sorted(
        history,
        key=lambda item: (item.created_at, item.action_id),
        reverse=True,
    ))


def list_paper_scans(
    workspace_root: Path,
    vault_id: str = "",
) -> Tuple[PaperScanRecord, ...]:
    """List fully verified scans without creating storage."""

    vault_records = list_document_vault(Path(workspace_root))
    valid_ids = {item.vault_id for item in vault_records}
    if vault_id and vault_id not in valid_ids:
        raise ValueError("Документ у сховищі не знайдено")
    root = _attachment_root(Path(workspace_root), create=False)
    if not root.exists():
        return ()
    records = _load_index(root, valid_ids)
    history = _load_history(root, records)
    removed_ids = {item.attachment_id for item in history}
    records = tuple(
        item for item in records
        if item.attachment_id not in removed_ids
    )
    if vault_id:
        records = tuple(item for item in records if item.vault_id == vault_id)
    return records


def list_removed_paper_scans(
    workspace_root: Path,
    vault_id: str = "",
) -> Tuple[RemovedPaperScan, ...]:
    """List verified inactive scans, newest action first."""

    vault_records = list_document_vault(Path(workspace_root))
    valid_ids = {item.vault_id for item in vault_records}
    if vault_id and vault_id not in valid_ids:
        raise ValueError("Документ у сховищі не знайдено")
    root = _attachment_root(Path(workspace_root), create=False)
    if not root.exists():
        return ()

    records = _load_index(root, valid_ids)
    by_id = {item.attachment_id: item for item in records}
    history = _load_history(root, records)
    removed = tuple(
        RemovedPaperScan(history=item, record=by_id[item.attachment_id])
        for item in history
        if not vault_id or item.vault_id == vault_id
    )
    return removed


def _append_inactive_history(
    root: Path,
    records: Tuple[PaperScanRecord, ...],
    history,
    scan: PaperScanRecord,
    action_name: str,
) -> PaperScanHistoryRecord:
    """Persist one append-only deactivation action for an immutable scan."""

    if action_name not in {"removed", "replaced"}:
        raise ValueError("Непідтримана дія зі сканом")
    if any(item.attachment_id == scan.attachment_id for item in history):
        raise ValueError("Скан уже неактивний")

    action = PaperScanHistoryRecord(
        action_id="vh-" + uuid.uuid4().hex,
        attachment_id=scan.attachment_id,
        vault_id=scan.vault_id,
        created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        action=action_name,
    )
    payload = canonical_json_bytes({
        "format": HISTORY_FORMAT,
        "items": [_history_entry(item) for item in list(history) + [action]],
    })
    if len(payload) > MAX_HISTORY_BYTES:
        raise ValueError("Історія сканів завелика")
    _atomic_write(root / HISTORY_NAME, payload)
    return action


def remove_paper_scan(
    workspace_root: Path,
    attachment_id: str,
) -> RemovedPaperScan:
    """Remove a scan from the active list without deleting immutable bytes."""

    if (
        not isinstance(attachment_id, str)
        or _ATTACHMENT_ID.fullmatch(attachment_id) is None
    ):
        raise ValueError("Некоректний ID скана")
    workspace_root = Path(workspace_root)

    with _WRITE_LOCK:
        vault_records = list_document_vault(workspace_root)
        valid_ids = {item.vault_id for item in vault_records}
        root = _attachment_root(workspace_root, create=False)
        if not root.exists():
            raise ValueError("Скан не знайдено")

        records = _load_index(root, valid_ids)
        by_id = {item.attachment_id: item for item in records}
        scan = by_id.get(attachment_id)
        if scan is None:
            raise ValueError("Скан не знайдено")

        history = list(_load_history(root, records))
        if any(item.attachment_id == attachment_id for item in history):
            raise ValueError("Скан уже прибрано з активного списку")

        action = _append_inactive_history(
            root,
            records,
            history,
            scan,
            "removed",
        )
        return RemovedPaperScan(history=action, record=scan)


def register_paper_scan(
    workspace_root: Path,
    vault_id: str,
    source_path: Path,
) -> PaperScanRecord:
    """Copy one explicit paper scan into the workspace as an immutable object."""

    if not isinstance(vault_id, str) or _VAULT_ID.fullmatch(vault_id) is None:
        raise ValueError("Некоректний ID документа для скана")
    workspace_root = Path(workspace_root)
    source_path = Path(source_path)

    with _WRITE_LOCK:
        vault_records = list_document_vault(workspace_root)
        valid_ids = {item.vault_id for item in vault_records}
        if vault_id not in valid_ids:
            raise ValueError("Документ у сховищі не знайдено")
        if (
            not source_path.is_file()
            or source_path.is_symlink()
            or source_path.stat().st_size < 1
        ):
            raise ValueError("Файл скана відсутній або небезпечний")
        if source_path.stat().st_size > MAX_SCAN_BYTES:
            raise ValueError("Скан перевищує допустимий розмір")

        suffix = source_path.suffix.casefold()
        if suffix not in _SOURCE_SUFFIXES:
            raise ValueError("Підтримуються лише PDF/JPG/PNG/TIFF")

        root = _attachment_root(workspace_root, create=True)
        existing = list(_load_index(root, valid_ids))
        _load_history(root, tuple(existing))

        attachment_id = "va-" + uuid.uuid4().hex
        shard = attachment_id[3:5]

        objects = root / "objects"
        if objects.exists() and (not objects.is_dir() or objects.is_symlink()):
            raise ValueError("Некоректна папка сканів")
        if not objects.exists():
            objects.mkdir(parents=False, exist_ok=False)
        shard_dir = objects / shard
        if shard_dir.exists() and (
            not shard_dir.is_dir() or shard_dir.is_symlink()
        ):
            raise ValueError("Некоректна папка сканів")
        if not shard_dir.exists():
            shard_dir.mkdir(parents=False, exist_ok=False)

        digest = hashlib.sha256()
        total = 0
        target = None
        temporary = None
        detected_ext = ""
        media_type = ""
        try:
            with source_path.open("rb") as source:
                first = source.read(16)
                detected_ext, media_type = _detect_scan(first)
                allowed_ext, allowed_media = _SOURCE_SUFFIXES[suffix]
                if detected_ext != allowed_ext or media_type != allowed_media:
                    raise ValueError("Розширення файла не відповідає його вмісту")

                storage_key = "objects/%s/%s.%s" % (
                    shard, attachment_id, detected_ext
                )
                target = _object_path(root, storage_key)
                if target.exists():
                    raise ValueError("Колізія ID скана")
                temporary = target.with_name(
                    ".%s.%s.tmp" % (target.name, uuid.uuid4().hex)
                )
                with temporary.open("xb") as output:
                    if first:
                        output.write(first)
                        digest.update(first)
                        total += len(first)
                    while True:
                        chunk = source.read(_CHUNK_BYTES)
                        if not chunk:
                            break
                        total += len(chunk)
                        if total > MAX_SCAN_BYTES:
                            raise ValueError("Скан перевищує допустимий розмір")
                        output.write(chunk)
                        digest.update(chunk)
                    output.flush()
                    os.fsync(output.fileno())
                if total < 1:
                    raise ValueError("Порожній файл скана")
                os.replace(str(temporary), str(target))
                temporary = None

            scan_hash = digest.hexdigest()
            if any(
                item.vault_id == vault_id and item.sha256 == scan_hash
                for item in existing
            ):
                raise ValueError("Цей скан уже додано до документа")

            record = PaperScanRecord(
                attachment_id=attachment_id,
                vault_id=vault_id,
                created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                role="paper_scan",
                original_name=source_path.name,
                media_type=media_type,
                storage_key=storage_key,
                size_bytes=total,
                sha256=scan_hash,
            )
            index_payload = canonical_json_bytes({
                "format": INDEX_FORMAT,
                "items": [_entry(item) for item in existing + [record]],
            })
            if len(index_payload) > MAX_INDEX_BYTES:
                raise ValueError("Індекс сканів завеликий")
            _atomic_write(root / INDEX_NAME, index_payload)
        except Exception:
            for path in (temporary, target):
                if path is None:
                    continue
                try:
                    if path.exists():
                        path.unlink()
                except OSError:
                    pass
            raise

        committed = {
            item.attachment_id: item
            for item in _load_index(root, valid_ids)
        }
        return committed[attachment_id]


def replace_paper_scan(
    workspace_root: Path,
    attachment_id: str,
    source_path: Path,
) -> ReplacedPaperScan:
    """Replace one active scan while preserving the previous immutable bytes.

    The new immutable object is committed first. Only after that succeeds is
    the previous scan marked inactive as replaced. If writing replacement
    history fails normally, the just-created object/index entry is rolled back.
    A hard process interruption therefore favours duplicate active copies over
    silent loss of the previous scan.
    """

    if (
        not isinstance(attachment_id, str)
        or _ATTACHMENT_ID.fullmatch(attachment_id) is None
    ):
        raise ValueError("Некоректний ID скана")
    workspace_root = Path(workspace_root)
    source_path = Path(source_path)

    with _WRITE_LOCK:
        vault_records = list_document_vault(workspace_root)
        valid_ids = {item.vault_id for item in vault_records}
        root = _attachment_root(workspace_root, create=False)
        if not root.exists():
            raise ValueError("Скан не знайдено")

        before_records = _load_index(root, valid_ids)
        before_by_id = {item.attachment_id: item for item in before_records}
        previous = before_by_id.get(attachment_id)
        if previous is None:
            raise ValueError("Скан не знайдено")
        before_history = list(_load_history(root, before_records))
        if any(item.attachment_id == attachment_id for item in before_history):
            raise ValueError("Скан уже неактивний")

        current = register_paper_scan(
            workspace_root,
            previous.vault_id,
            source_path,
        )

        records = _load_index(root, valid_ids)
        history = list(_load_history(root, records))
        try:
            action = _append_inactive_history(
                root,
                records,
                history,
                previous,
                "replaced",
            )
        except Exception as original_error:
            rollback_records = tuple(
                item for item in records
                if item.attachment_id != current.attachment_id
            )
            rollback_payload = canonical_json_bytes({
                "format": INDEX_FORMAT,
                "items": [_entry(item) for item in rollback_records],
            })
            rollback_ok = False
            try:
                _atomic_write(root / INDEX_NAME, rollback_payload)
                rollback_ok = True
            except Exception:
                rollback_ok = False

            if rollback_ok:
                current_path = _object_path(root, current.storage_key)
                try:
                    if current_path.exists():
                        current_path.unlink()
                except OSError as cleanup_error:
                    raise RuntimeError(
                        "Заміну не завершено; новий файл не вдалося "
                        "прибрати після відкату"
                    ) from cleanup_error
                _load_index(root, valid_ids)
                _load_history(root, rollback_records)
                raise original_error

            raise RuntimeError(
                "Не вдалося завершити або безпечно відкотити заміну скана; "
                "потрібна перевірка сховища"
            ) from original_error

        committed_records = _load_index(root, valid_ids)
        committed_history = _load_history(root, committed_records)
        committed_actions = {
            item.attachment_id: item for item in committed_history
        }
        committed_new = {
            item.attachment_id: item for item in committed_records
        }[current.attachment_id]
        return ReplacedPaperScan(
            previous=RemovedPaperScan(
                history=committed_actions[previous.attachment_id],
                record=previous,
            ),
            current=committed_new,
        )


def load_paper_scan(
    workspace_root: Path,
    attachment_id: str,
) -> PaperScanObject:
    """Return one fully verified scan path without opening the file."""

    if (
        not isinstance(attachment_id, str)
        or _ATTACHMENT_ID.fullmatch(attachment_id) is None
    ):
        raise ValueError("Некоректний ID скана")
    records = list_paper_scans(Path(workspace_root))
    matches = [item for item in records if item.attachment_id == attachment_id]
    if len(matches) != 1:
        raise ValueError("Скан не знайдено")
    record = matches[0]
    root = _attachment_root(Path(workspace_root), create=False)
    path = _verify_object(root, record)
    return PaperScanObject(record=record, path=path)
