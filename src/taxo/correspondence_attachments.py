# -*- coding: utf-8 -*-
"""Controlled immutable attachments for business correspondence.

The attachment store is deliberately separate from the correspondence registry.
It stores either:
- immutable copied bytes with SHA256 metadata; or
- a stable reference to an already controlled ready document.

Removing an attachment is a history event. Bytes are not deleted and attachment
presence never changes sent/received/closed business state.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from correspondence_registry import read_registry


STORE_NAME = "CorrespondenceAttachments"
INDEX_NAME = "index.json"
HISTORY_NAME = "history.json"
OBJECTS_NAME = "objects"
INDEX_FORMAT = "taxo.correspondence-attachments.v1"
HISTORY_FORMAT = "taxo.correspondence-attachment-history.v1"

MAX_INDEX_BYTES = 8 * 1024 * 1024
MAX_HISTORY_BYTES = 8 * 1024 * 1024
MAX_ATTACHMENT_BYTES = 256 * 1024 * 1024
MAX_DOCX_UNCOMPRESSED_BYTES = 1024 * 1024 * 1024
MAX_DOCX_ENTRIES = 10000
_CHUNK_BYTES = 1024 * 1024

_ATTACHMENT_ID = re.compile(r"^ca-[a-f0-9]{32}$")
_ACTION_ID = re.compile(r"^ch-[a-f0-9]{32}$")
_CORRESPONDENCE_ID = re.compile(r"^cr-[a-f0-9]{32}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_DOCUMENT_REF = re.compile(
    r"^(?:vault|paper|order):[A-Za-z0-9._-]{1,200}$"
)
_STORAGE_KEY = re.compile(
    r"^objects/([a-f0-9]{2})/([a-f0-9]{64})\."
    r"(pdf|jpg|png|tiff|docx)$"
)
_TEMP_FILE = re.compile(
    r"^\.(?:index\.json|history\.json|object)\."
    r"[a-f0-9]{32}\.tmp$"
)
_SHARD = re.compile(r"^[a-f0-9]{2}$")
_OBJECT_NAME = re.compile(
    r"^[a-f0-9]{64}\.(?:pdf|jpg|png|tiff|docx)$"
)
_WRITE_LOCK = threading.RLock()

_FILE_TYPES = {
    ".pdf": ("pdf", "application/pdf"),
    ".jpg": ("jpg", "image/jpeg"),
    ".jpeg": ("jpg", "image/jpeg"),
    ".png": ("png", "image/png"),
    ".tif": ("tiff", "image/tiff"),
    ".tiff": ("tiff", "image/tiff"),
    ".docx": (
        "docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ),
}
_EXT_BY_MEDIA = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/tiff": "tiff",
    (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ): "docx",
}


@dataclass(frozen=True)
class CorrespondenceAttachmentRecord:
    attachment_id: str
    correspondence_id: str
    created_at: str
    source_kind: str
    original_name: str
    media_type: str
    storage_key: str
    size_bytes: int
    sha256: str
    document_ref: str


@dataclass(frozen=True)
class CorrespondenceAttachmentObject:
    record: CorrespondenceAttachmentRecord
    path: Path


@dataclass(frozen=True)
class CorrespondenceAttachmentHistory:
    action_id: str
    attachment_id: str
    correspondence_id: str
    created_at: str
    action: str


@dataclass(frozen=True)
class RemovedCorrespondenceAttachment:
    history: CorrespondenceAttachmentHistory
    record: CorrespondenceAttachmentRecord


def attachment_root(workspace_root: Path) -> Path:
    return Path(workspace_root) / "Data" / STORE_NAME


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _timestamp(value, label) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("Некоректний час %s" % label)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Некоректний час %s" % label) from exc
    if parsed.tzinfo is None:
        raise ValueError("Час %s не містить timezone" % label)
    return value


def _correspondence_id(value) -> str:
    clean = str(value or "").strip()
    if _CORRESPONDENCE_ID.fullmatch(clean) is None:
        raise ValueError("Некоректний ID кореспонденції")
    return clean


def _attachment_id(value) -> str:
    clean = str(value or "").strip()
    if _ATTACHMENT_ID.fullmatch(clean) is None:
        raise ValueError("Некоректний ID вкладення")
    return clean


def _document_ref(value) -> str:
    clean = str(value or "").strip()
    if _DOCUMENT_REF.fullmatch(clean) is None:
        raise ValueError("Некоректне посилання на готовий документ")
    return clean


def _safe_name(value, *, allow_empty=False) -> str:
    if not isinstance(value, str):
        raise ValueError("Назва вкладення має бути текстом")
    clean = " ".join(value.strip().split())
    if not clean and allow_empty:
        return ""
    if (
        not clean
        or len(clean) > 255
        or Path(clean).name != clean
        or clean in {".", ".."}
        or any(ord(ch) < 32 for ch in clean)
    ):
        raise ValueError("Некоректна назва вкладення")
    return clean


def _json_object_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Дубльоване поле у сховищі вкладень")
        result[key] = value
    return result


def _read_json(path: Path, limit: int, label: str):
    if not path.is_file() or path.is_symlink():
        raise ValueError("Некоректний файл %s" % label)
    size = path.stat().st_size
    if size < 1 or size > limit:
        raise ValueError("Файл %s має некоректний розмір" % label)
    try:
        return json.loads(
            path.read_text("utf-8"),
            object_pairs_hook=_json_object_no_duplicates,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Пошкоджений файл %s" % label) from exc


def _canonical_json_bytes(data) -> bytes:
    return (
        json.dumps(
            data,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _atomic_write(path: Path, payload: bytes) -> None:
    parent = path.parent
    if not parent.is_dir() or parent.is_symlink():
        raise ValueError("Некоректна папка сховища вкладень")
    temporary = parent / (
        ".%s.%s.tmp" % (path.name, uuid.uuid4().hex)
    )
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


def _ensure_root(workspace_root: Path) -> Path:
    root = attachment_root(workspace_root)
    data_dir = root.parent
    if data_dir.exists() and (not data_dir.is_dir() or data_dir.is_symlink()):
        raise ValueError("Некоректна папка Data у робочому сховищі")
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=False)
    if root.exists() and (not root.is_dir() or root.is_symlink()):
        raise ValueError("Некоректне сховище вкладень кореспонденції")
    if not root.exists():
        root.mkdir(parents=False, exist_ok=False)
    return root


def _validate_root_shape(root: Path) -> None:
    if not root.exists():
        return
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Некоректне сховище вкладень кореспонденції")
    allowed = {INDEX_NAME, HISTORY_NAME, OBJECTS_NAME}
    unexpected = [
        child.name
        for child in root.iterdir()
        if child.name not in allowed and _TEMP_FILE.fullmatch(child.name) is None
    ]
    if unexpected:
        raise ValueError(
            "Сховище вкладень містить невідомий об'єкт: %s"
            % ", ".join(sorted(unexpected))
        )
    objects = root / OBJECTS_NAME
    if objects.exists():
        if not objects.is_dir() or objects.is_symlink():
            raise ValueError("Некоректна папка об'єктів вкладень")
        for shard in objects.iterdir():
            if (
                not shard.is_dir()
                or shard.is_symlink()
                or _SHARD.fullmatch(shard.name) is None
            ):
                raise ValueError("Некоректний каталог об'єктів вкладень")
            for item in shard.iterdir():
                if (
                    not item.is_file()
                    or item.is_symlink()
                    or _OBJECT_NAME.fullmatch(item.name) is None
                ):
                    raise ValueError("Некоректний об'єкт вкладення")


def _record(entry) -> CorrespondenceAttachmentRecord:
    required = {
        "id",
        "correspondence_id",
        "created_at",
        "source_kind",
        "original_name",
        "media_type",
        "storage_key",
        "size_bytes",
        "sha256",
        "document_ref",
    }
    if not isinstance(entry, dict) or set(entry) != required:
        raise ValueError("Некоректний запис вкладення кореспонденції")
    attachment_id = _attachment_id(entry.get("id"))
    correspondence_id = _correspondence_id(entry.get("correspondence_id"))
    created_at = _timestamp(entry.get("created_at"), "додавання вкладення")
    source_kind = entry.get("source_kind")
    if source_kind not in {"stored", "document_ref"}:
        raise ValueError("Некоректне джерело вкладення")

    if source_kind == "stored":
        original_name = _safe_name(entry.get("original_name"))
        media_type = str(entry.get("media_type") or "")
        extension = _EXT_BY_MEDIA.get(media_type)
        if extension is None:
            raise ValueError("Некоректний MIME вкладення")
        storage_key = str(entry.get("storage_key") or "")
        match = _STORAGE_KEY.fullmatch(storage_key)
        sha256 = str(entry.get("sha256") or "")
        size_bytes = entry.get("size_bytes")
        if _SHA256.fullmatch(sha256) is None:
            raise ValueError("Некоректний SHA256 вкладення")
        if type(size_bytes) is not int or not (1 <= size_bytes <= MAX_ATTACHMENT_BYTES):
            raise ValueError("Некоректний розмір вкладення")
        if (
            match is None
            or match.group(1) != sha256[:2]
            or match.group(2) != sha256
            or match.group(3) != extension
        ):
            raise ValueError("Некоректний storage key вкладення")
        if entry.get("document_ref") != "":
            raise ValueError("Файлове вкладення не може мати document_ref")
        return CorrespondenceAttachmentRecord(
            attachment_id,
            correspondence_id,
            created_at,
            source_kind,
            original_name,
            media_type,
            storage_key,
            size_bytes,
            sha256,
            "",
        )

    if any((
        entry.get("media_type") != "",
        entry.get("storage_key") != "",
        entry.get("sha256") != "",
        entry.get("size_bytes") != 0,
    )):
        raise ValueError("Document-ref вкладення не повинно містити file metadata")
    return CorrespondenceAttachmentRecord(
        attachment_id,
        correspondence_id,
        created_at,
        source_kind,
        _safe_name(entry.get("original_name"), allow_empty=True),
        "",
        "",
        0,
        "",
        _document_ref(entry.get("document_ref")),
    )


def _history_record(entry) -> CorrespondenceAttachmentHistory:
    required = {
        "id",
        "attachment_id",
        "correspondence_id",
        "created_at",
        "action",
    }
    if not isinstance(entry, dict) or set(entry) != required:
        raise ValueError("Некоректний запис історії вкладень")
    action_id = str(entry.get("id") or "")
    if _ACTION_ID.fullmatch(action_id) is None:
        raise ValueError("Некоректний ID події вкладення")
    action = entry.get("action")
    if action != "removed":
        raise ValueError("Некоректна дія в історії вкладень")
    return CorrespondenceAttachmentHistory(
        action_id=action_id,
        attachment_id=_attachment_id(entry.get("attachment_id")),
        correspondence_id=_correspondence_id(entry.get("correspondence_id")),
        created_at=_timestamp(entry.get("created_at"), "події вкладення"),
        action=action,
    )


def _entry(record: CorrespondenceAttachmentRecord):
    return {
        "id": record.attachment_id,
        "correspondence_id": record.correspondence_id,
        "created_at": record.created_at,
        "source_kind": record.source_kind,
        "original_name": record.original_name,
        "media_type": record.media_type,
        "storage_key": record.storage_key,
        "size_bytes": record.size_bytes,
        "sha256": record.sha256,
        "document_ref": record.document_ref,
    }


def _history_entry(record: CorrespondenceAttachmentHistory):
    return {
        "id": record.action_id,
        "attachment_id": record.attachment_id,
        "correspondence_id": record.correspondence_id,
        "created_at": record.created_at,
        "action": record.action,
    }


def _validate_records(workspace_root: Path, records, history):
    records = tuple(records)
    history = tuple(history)
    registry = read_registry(workspace_root)
    correspondence_ids = {row.correspondence_id for row in registry.records}

    by_id = {}
    for item in records:
        if item.attachment_id in by_id:
            raise ValueError("Дубльований ID вкладення")
        if item.correspondence_id not in correspondence_ids:
            raise ValueError("Вкладення посилається на відсутню кореспонденцію")
        by_id[item.attachment_id] = item

    action_ids = set()
    removed_ids = set()
    for item in history:
        if item.action_id in action_ids:
            raise ValueError("Дубльована подія вкладення")
        action_ids.add(item.action_id)
        record = by_id.get(item.attachment_id)
        if record is None:
            raise ValueError("Історія посилається на відсутнє вкладення")
        if item.correspondence_id != record.correspondence_id:
            raise ValueError("Подія вкладення має іншу кореспонденцію")
        if item.attachment_id in removed_ids:
            raise ValueError("Вкладення прибрано більше одного разу")
        removed_ids.add(item.attachment_id)

    active_keys = set()
    for item in records:
        if item.attachment_id in removed_ids:
            continue
        identity = (
            item.correspondence_id,
            item.source_kind,
            item.sha256 if item.source_kind == "stored" else item.document_ref,
        )
        if identity in active_keys:
            raise ValueError("Дубльоване активне вкладення")
        active_keys.add(identity)

    return (
        tuple(sorted(records, key=lambda row: (row.created_at, row.attachment_id))),
        tuple(sorted(history, key=lambda row: (row.created_at, row.action_id))),
    )


def _load_state(workspace_root: Path):
    root = attachment_root(workspace_root)
    if not root.exists():
        return (), ()
    _validate_root_shape(root)

    index_path = root / INDEX_NAME
    if index_path.exists():
        data = _read_json(index_path, MAX_INDEX_BYTES, "індексу вкладень")
        if (
            not isinstance(data, dict)
            or set(data) != {"format", "items"}
            or data.get("format") != INDEX_FORMAT
            or not isinstance(data.get("items"), list)
        ):
            raise ValueError("Несумісний формат індексу вкладень")
        records = tuple(_record(item) for item in data["items"])
    else:
        records = ()

    history_path = root / HISTORY_NAME
    if history_path.exists():
        data = _read_json(history_path, MAX_HISTORY_BYTES, "історії вкладень")
        if (
            not isinstance(data, dict)
            or set(data) != {"format", "events"}
            or data.get("format") != HISTORY_FORMAT
            or not isinstance(data.get("events"), list)
        ):
            raise ValueError("Несумісний формат історії вкладень")
        history = tuple(_history_record(item) for item in data["events"])
    else:
        history = ()

    records, history = _validate_records(workspace_root, records, history)
    _verify_object_set(root, records)
    return records, history


def _index_payload(records) -> bytes:
    raw = _canonical_json_bytes({
        "format": INDEX_FORMAT,
        "items": [_entry(item) for item in records],
    })
    if len(raw) > MAX_INDEX_BYTES:
        raise ValueError("Індекс вкладень перевищує допустимий розмір")
    return raw


def _history_payload(history) -> bytes:
    raw = _canonical_json_bytes({
        "format": HISTORY_FORMAT,
        "events": [_history_entry(item) for item in history],
    })
    if len(raw) > MAX_HISTORY_BYTES:
        raise ValueError("Історія вкладень перевищує допустимий розмір")
    return raw


def _object_path(root: Path, storage_key: str) -> Path:
    match = _STORAGE_KEY.fullmatch(storage_key)
    if match is None:
        raise ValueError("Некоректний storage key вкладення")
    return root.joinpath(*storage_key.split("/"))


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(_CHUNK_BYTES)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _verify_object(root: Path, record: CorrespondenceAttachmentRecord) -> Path:
    path = _object_path(root, record.storage_key)
    if not path.is_file() or path.is_symlink():
        raise ValueError("Файл вкладення відсутній або небезпечний")
    if path.stat().st_size != record.size_bytes:
        raise ValueError("Порушено розмір вкладення")
    if _hash_file(path) != record.sha256:
        raise ValueError("Порушено цілісність вкладення")
    return path


def _verify_object_set(root: Path, records) -> None:
    referenced = {
        item.storage_key
        for item in records
        if item.source_kind == "stored"
    }
    objects = root / OBJECTS_NAME
    actual = set()
    if objects.exists():
        for shard in objects.iterdir():
            for item in shard.iterdir():
                actual.add(
                    "%s/%s/%s" % (OBJECTS_NAME, shard.name, item.name)
                )
    if actual != referenced:
        extra = sorted(actual - referenced)
        missing = sorted(referenced - actual)
        if extra:
            raise ValueError(
                "Сховище вкладень містить файл без індексу: %s" % extra[0]
            )
        raise ValueError(
            "Індекс вкладень посилається на відсутній файл: %s"
            % missing[0]
        )
    for item in records:
        if item.source_kind == "stored":
            _verify_object(root, item)


def _validate_docx(path: Path) -> None:
    try:
        with zipfile.ZipFile(str(path), "r") as archive:
            infos = archive.infolist()
            if len(infos) > MAX_DOCX_ENTRIES:
                raise ValueError("DOCX містить забагато внутрішніх файлів")
            names = {item.filename for item in infos}
            if (
                "[Content_Types].xml" not in names
                or "word/document.xml" not in names
            ):
                raise ValueError("Файл не схожий на DOCX")
            total = 0
            for item in infos:
                pure = Path(item.filename)
                if (
                    item.filename.startswith(("/", "\\"))
                    or ".." in pure.parts
                ):
                    raise ValueError("DOCX містить небезпечний шлях")
                mode = (item.external_attr >> 16) & 0o170000
                if mode == 0o120000:
                    raise ValueError("DOCX містить символічне посилання")
                total += item.file_size
                if total > MAX_DOCX_UNCOMPRESSED_BYTES:
                    raise ValueError("DOCX має надмірний розпакований розмір")
                if item.filename.casefold().endswith("vbaproject.bin"):
                    raise ValueError("DOCX з макросами не підтримується")
    except (OSError, zipfile.BadZipFile) as exc:
        raise ValueError("Файл не схожий на DOCX") from exc


def _validate_content(path: Path, extension: str) -> None:
    with path.open("rb") as stream:
        head = stream.read(16)
    valid = {
        "pdf": head.startswith(b"%PDF-"),
        "jpg": head.startswith(b"\xff\xd8\xff"),
        "png": head.startswith(b"\x89PNG\r\n\x1a\n"),
        "tiff": head.startswith(b"II*\x00") or head.startswith(b"MM\x00*"),
    }
    if extension == "docx":
        _validate_docx(path)
    elif not valid.get(extension, False):
        raise ValueError("Вміст файла не відповідає його типу")


def _source_type(path: Path):
    suffix = path.suffix.casefold()
    result = _FILE_TYPES.get(suffix)
    if result is None:
        raise ValueError("Непідтримуваний тип вкладення")
    return result


def _copy_source_to_temp(root: Path, source: Path, extension: str):
    if not source.is_file() or source.is_symlink():
        raise ValueError("Вкладення відсутнє або є небезпечним посиланням")
    before = source.stat()
    if before.st_size < 1 or before.st_size > MAX_ATTACHMENT_BYTES:
        raise ValueError("Вкладення має некоректний розмір")
    _validate_content(source, extension)

    temporary = root / (".object.%s.tmp" % uuid.uuid4().hex)
    digest = hashlib.sha256()
    copied = 0
    try:
        with source.open("rb") as input_stream, temporary.open("xb") as output:
            while True:
                chunk = input_stream.read(_CHUNK_BYTES)
                if not chunk:
                    break
                copied += len(chunk)
                if copied > MAX_ATTACHMENT_BYTES:
                    raise ValueError("Вкладення завелике")
                digest.update(chunk)
                output.write(chunk)
            output.flush()
            os.fsync(output.fileno())
        after = source.stat()
        if (
            before.st_size != after.st_size
            or before.st_mtime_ns != after.st_mtime_ns
            or copied != before.st_size
        ):
            raise ValueError("Вкладення змінилося під час копіювання")
        _validate_content(temporary, extension)
        return temporary, copied, digest.hexdigest()
    except Exception:
        try:
            if temporary.exists():
                temporary.unlink()
        except OSError:
            pass
        raise


def _store_object(
    root: Path,
    temporary: Path,
    sha256: str,
    size_bytes: int,
    extension: str,
):
    objects = root / OBJECTS_NAME
    if objects.exists() and (not objects.is_dir() or objects.is_symlink()):
        raise ValueError("Некоректна папка об'єктів вкладень")
    if not objects.exists():
        objects.mkdir(parents=False, exist_ok=False)
    shard = objects / sha256[:2]
    if shard.exists() and (not shard.is_dir() or shard.is_symlink()):
        raise ValueError("Некоректний каталог об'єктів вкладень")
    if not shard.exists():
        shard.mkdir(parents=False, exist_ok=False)
    target = shard / ("%s.%s" % (sha256, extension))
    storage_key = "%s/%s/%s" % (OBJECTS_NAME, shard.name, target.name)
    created = False
    if target.exists():
        if (
            not target.is_file()
            or target.is_symlink()
            or target.stat().st_size != size_bytes
            or _hash_file(target) != sha256
        ):
            raise ValueError("Наявний об'єкт вкладення пошкоджений")
        temporary.unlink()
    else:
        os.replace(str(temporary), str(target))
        created = True
    return storage_key, target, created


def list_correspondence_attachments(
    workspace_root: Path,
    correspondence_id: str = "",
) -> Tuple[CorrespondenceAttachmentRecord, ...]:
    records, history = _load_state(Path(workspace_root))
    removed = {item.attachment_id for item in history}
    if correspondence_id:
        correspondence_id = _correspondence_id(correspondence_id)
    return tuple(
        item
        for item in records
        if item.attachment_id not in removed
        and (
            not correspondence_id
            or item.correspondence_id == correspondence_id
        )
    )


def list_removed_correspondence_attachments(
    workspace_root: Path,
    correspondence_id: str = "",
) -> Tuple[RemovedCorrespondenceAttachment, ...]:
    records, history = _load_state(Path(workspace_root))
    by_id = {item.attachment_id: item for item in records}
    if correspondence_id:
        correspondence_id = _correspondence_id(correspondence_id)
    return tuple(
        RemovedCorrespondenceAttachment(item, by_id[item.attachment_id])
        for item in history
        if (
            not correspondence_id
            or item.correspondence_id == correspondence_id
        )
    )


def add_correspondence_file(
    workspace_root: Path,
    correspondence_id: str,
    source_path: Path,
) -> CorrespondenceAttachmentRecord:
    correspondence_id = _correspondence_id(correspondence_id)
    source = Path(source_path)
    original_name = _safe_name(source.name)
    extension, media_type = _source_type(source)

    with _WRITE_LOCK:
        # Fail before reading an external file when the parent record is absent.
        registry = read_registry(workspace_root)
        if correspondence_id not in {
            item.correspondence_id for item in registry.records
        }:
            raise ValueError("Запис кореспонденції не знайдено")

        root = _ensure_root(Path(workspace_root))
        _validate_root_shape(root)
        records, history = _load_state(Path(workspace_root))
        removed = {item.attachment_id for item in history}

        temporary, size_bytes, sha256 = _copy_source_to_temp(
            root, source, extension
        )
        try:
            if any(
                item.correspondence_id == correspondence_id
                and item.source_kind == "stored"
                and item.sha256 == sha256
                and item.attachment_id not in removed
                for item in records
            ):
                raise ValueError("Цей файл уже додано до листа")

            storage_key, target, created_object = _store_object(
                root, temporary, sha256, size_bytes, extension
            )
            record = CorrespondenceAttachmentRecord(
                attachment_id="ca-" + uuid.uuid4().hex,
                correspondence_id=correspondence_id,
                created_at=_iso_now(),
                source_kind="stored",
                original_name=original_name,
                media_type=media_type,
                storage_key=storage_key,
                size_bytes=size_bytes,
                sha256=sha256,
                document_ref="",
            )
            updated = records + (record,)
            updated, _ = _validate_records(
                Path(workspace_root), updated, history
            )
            try:
                _atomic_write(root / INDEX_NAME, _index_payload(updated))
            except Exception:
                if created_object:
                    try:
                        target.unlink()
                    except OSError as exc:
                        raise RuntimeError(
                            "Не вдалося відкотити незавершене додавання вкладення"
                        ) from exc
                raise
            _load_state(Path(workspace_root))
            return record
        finally:
            try:
                if temporary.exists():
                    temporary.unlink()
            except OSError:
                pass


def link_correspondence_document(
    workspace_root: Path,
    correspondence_id: str,
    document_ref: str,
    label: str = "",
) -> CorrespondenceAttachmentRecord:
    correspondence_id = _correspondence_id(correspondence_id)
    document_ref = _document_ref(document_ref)
    label = _safe_name(label, allow_empty=True)

    with _WRITE_LOCK:
        registry = read_registry(workspace_root)
        if correspondence_id not in {
            item.correspondence_id for item in registry.records
        }:
            raise ValueError("Запис кореспонденції не знайдено")
        root = _ensure_root(Path(workspace_root))
        _validate_root_shape(root)
        records, history = _load_state(Path(workspace_root))
        removed = {item.attachment_id for item in history}
        if any(
            item.correspondence_id == correspondence_id
            and item.source_kind == "document_ref"
            and item.document_ref == document_ref
            and item.attachment_id not in removed
            for item in records
        ):
            raise ValueError("Цей документ уже додано до листа")

        record = CorrespondenceAttachmentRecord(
            attachment_id="ca-" + uuid.uuid4().hex,
            correspondence_id=correspondence_id,
            created_at=_iso_now(),
            source_kind="document_ref",
            original_name=label,
            media_type="",
            storage_key="",
            size_bytes=0,
            sha256="",
            document_ref=document_ref,
        )
        updated = records + (record,)
        updated, _ = _validate_records(
            Path(workspace_root), updated, history
        )
        _atomic_write(root / INDEX_NAME, _index_payload(updated))
        _load_state(Path(workspace_root))
        return record


def load_correspondence_file(
    workspace_root: Path,
    attachment_id: str,
) -> CorrespondenceAttachmentObject:
    attachment_id = _attachment_id(attachment_id)
    records, history = _load_state(Path(workspace_root))
    removed = {item.attachment_id for item in history}
    if attachment_id in removed:
        raise ValueError("Вкладення прибрано з листа")
    record = next(
        (item for item in records if item.attachment_id == attachment_id),
        None,
    )
    if record is None:
        raise ValueError("Вкладення не знайдено")
    if record.source_kind != "stored":
        raise ValueError("Це посилання на готовий документ, а не окремий файл")
    path = _verify_object(attachment_root(Path(workspace_root)), record)
    return CorrespondenceAttachmentObject(record, path)


def remove_correspondence_attachment(
    workspace_root: Path,
    attachment_id: str,
) -> RemovedCorrespondenceAttachment:
    attachment_id = _attachment_id(attachment_id)
    with _WRITE_LOCK:
        root = attachment_root(Path(workspace_root))
        records, history = _load_state(Path(workspace_root))
        record = next(
            (item for item in records if item.attachment_id == attachment_id),
            None,
        )
        if record is None:
            raise ValueError("Вкладення не знайдено")
        if any(item.attachment_id == attachment_id for item in history):
            raise ValueError("Вкладення вже прибрано")
        event = CorrespondenceAttachmentHistory(
            action_id="ch-" + uuid.uuid4().hex,
            attachment_id=record.attachment_id,
            correspondence_id=record.correspondence_id,
            created_at=_iso_now(),
            action="removed",
        )
        updated = history + (event,)
        _, updated = _validate_records(
            Path(workspace_root), records, updated
        )
        _atomic_write(root / HISTORY_NAME, _history_payload(updated))
        _load_state(Path(workspace_root))
        return RemovedCorrespondenceAttachment(event, record)
