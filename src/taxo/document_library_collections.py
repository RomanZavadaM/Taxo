# -*- coding: utf-8 -*-
"""User-managed logical folders for the ready-document library.

The store contains only folder metadata and stable document references. It never
moves, renames, copies or deletes DocumentVault/PaperDocuments/order bytes.

Persistence lives under workspace/Data/DocumentLibrary, so the existing full
workspace backup/restore and workspace cloning include it automatically.
"""
from __future__ import annotations

import json
import os
import re
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Tuple

STORE_NAME = "DocumentLibrary"
FILE_NAME = "collections.json"
FORMAT = "taxo.document-library-collections.v1"
MAX_BYTES = 4 * 1024 * 1024
MAX_NAME = 120
_COLLECTION_ID = re.compile(r"^dc-[a-f0-9]{32}$")
_DOCUMENT_KEY = re.compile(r"^(?:vault|paper|order):[A-Za-z0-9._-]{1,200}$")
_TEMP_FILE = re.compile(r"^\.collections\.json\.[a-f0-9]{32}\.tmp$")
_WRITE_LOCK = threading.RLock()


@dataclass(frozen=True)
class CollectionRecord:
    collection_id: str
    parent_id: str
    name: str
    sort_order: int
    archived_at: str
    created_at: str


@dataclass(frozen=True)
class MembershipRecord:
    collection_id: str
    document_key: str
    added_at: str


@dataclass(frozen=True)
class CollectionState:
    collections: Tuple[CollectionRecord, ...]
    memberships: Tuple[MembershipRecord, ...]


def collection_store_root(workspace_root: Path) -> Path:
    return Path(workspace_root) / "Data" / STORE_NAME


def collection_store_path(workspace_root: Path) -> Path:
    return collection_store_root(workspace_root) / FILE_NAME


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_timestamp(value, description, *, allow_empty=False):
    if allow_empty and value == "":
        return ""
    if not isinstance(value, str) or not value:
        raise ValueError("Некоректне поле %s у папках документів" % description)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Некоректне поле %s у папках документів" % description) from exc
    if parsed.tzinfo is None:
        raise ValueError("Поле %s не містить timezone" % description)
    return value


def _name(value) -> str:
    if not isinstance(value, str):
        raise ValueError("Назва папки має бути текстом")
    clean = " ".join(value.strip().split())
    if not clean or len(clean) > MAX_NAME:
        raise ValueError("Назва папки має містити від 1 до %d символів" % MAX_NAME)
    if clean in {".", ".."} or "/" in clean or "\\" in clean:
        raise ValueError("Назва папки містить недопустимий символ")
    if any(ord(ch) < 32 for ch in clean):
        raise ValueError("Назва папки містить службовий символ")
    return clean


def _document_ref(value) -> str:
    value = str(value or "").strip()
    if _DOCUMENT_KEY.fullmatch(value) is None:
        raise ValueError("Некоректне посилання на документ")
    return value


def catalog_document_key(row) -> str:
    """Return a stable logical-library key for one normalized catalog row.

    A prepared PaperDocuments revision keeps the same logical key after it is
    registered in DocumentVault. A standalone vault row uses its stored source
    PaperDocuments ID when available, so adding/removing the merged catalog view
    cannot silently remove a document from a user's folder.
    """
    row = row or {}
    source = str(row.get("source") or "").strip()
    source_id = str(row.get("source_id") or "").strip()
    if source == "paper":
        return _document_ref("paper:" + source_id)
    if source == "order":
        return _document_ref("order:" + source_id)
    if source == "vault":
        source_document_id = str(row.get("source_document_id") or "").strip()
        if source_document_id:
            return _document_ref("paper:" + source_document_id)
        vault_id = str(row.get("vault_id") or source_id).strip()
        return _document_ref("vault:" + vault_id)
    raise ValueError("Цей запис каталогу не має стабільного ключа для папок")


def _json_object_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Дубльоване поле у файлі папок документів")
        result[key] = value
    return result


def _load_json(path: Path):
    if not path.is_file() or path.is_symlink():
        raise ValueError("Некоректний файл папок документів")
    size = path.stat().st_size
    if size < 1 or size > MAX_BYTES:
        raise ValueError("Файл папок документів має некоректний розмір")
    try:
        raw = path.read_text("utf-8")
        return json.loads(raw, object_pairs_hook=_json_object_no_duplicates)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Пошкоджений файл папок документів") from exc


def _collection(entry) -> CollectionRecord:
    required = {
        "id", "parent_id", "name", "sort_order", "archived_at", "created_at",
    }
    if not isinstance(entry, dict) or set(entry) != required:
        raise ValueError("Некоректний запис папки документів")
    identity = entry.get("id")
    parent_id = entry.get("parent_id")
    if not isinstance(identity, str) or _COLLECTION_ID.fullmatch(identity) is None:
        raise ValueError("Некоректний ID папки документів")
    if not isinstance(parent_id, str) or (
        parent_id and _COLLECTION_ID.fullmatch(parent_id) is None
    ):
        raise ValueError("Некоректна батьківська папка документів")
    sort_order = entry.get("sort_order")
    if type(sort_order) is not int or sort_order < 0:
        raise ValueError("Некоректний порядок папки документів")
    return CollectionRecord(
        collection_id=identity,
        parent_id=parent_id,
        name=_name(entry.get("name")),
        sort_order=sort_order,
        archived_at=_parse_timestamp(
            entry.get("archived_at"), "archived_at", allow_empty=True
        ),
        created_at=_parse_timestamp(entry.get("created_at"), "created_at"),
    )


def _membership(entry) -> MembershipRecord:
    required = {"collection_id", "document_key", "added_at"}
    if not isinstance(entry, dict) or set(entry) != required:
        raise ValueError("Некоректний запис розміщення документа")
    collection_id = entry.get("collection_id")
    if not isinstance(collection_id, str) or _COLLECTION_ID.fullmatch(collection_id) is None:
        raise ValueError("Некоректна папка у розміщенні документа")
    return MembershipRecord(
        collection_id=collection_id,
        document_key=_document_ref(entry.get("document_key")),
        added_at=_parse_timestamp(entry.get("added_at"), "added_at"),
    )


def _validate_state(state: CollectionState) -> CollectionState:
    collections = tuple(state.collections)
    memberships = tuple(state.memberships)
    by_id = {}
    for record in collections:
        if record.collection_id in by_id:
            raise ValueError("Дубльований ID папки документів")
        by_id[record.collection_id] = record

    for record in collections:
        if record.parent_id and record.parent_id not in by_id:
            raise ValueError("Папка посилається на відсутню батьківську папку")
        seen = {record.collection_id}
        parent_id = record.parent_id
        while parent_id:
            if parent_id in seen:
                raise ValueError("Виявлено цикл у дереві папок документів")
            seen.add(parent_id)
            parent_id = by_id[parent_id].parent_id

    sibling_names = set()
    for record in collections:
        key = (record.parent_id, record.name.casefold())
        if key in sibling_names:
            raise ValueError("Дві папки одного рівня мають однакову назву")
        sibling_names.add(key)

    membership_keys = set()
    for record in memberships:
        if record.collection_id not in by_id:
            raise ValueError("Розміщення посилається на відсутню папку")
        key = (record.collection_id, record.document_key)
        if key in membership_keys:
            raise ValueError("Дубльоване розміщення документа")
        membership_keys.add(key)

    return CollectionState(
        collections=tuple(sorted(
            collections,
            key=lambda row: (
                row.parent_id, row.sort_order, row.name.casefold(), row.collection_id
            ),
        )),
        memberships=tuple(sorted(
            memberships,
            key=lambda row: (row.collection_id, row.document_key),
        )),
    )


def read_collection_state(workspace_root: Path) -> CollectionState:
    """Read and fully validate saved logical folders without creating storage."""
    root = collection_store_root(workspace_root)
    if not root.exists():
        return CollectionState((), ())
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Некоректне сховище папок документів")
    unexpected = [
        child.name for child in root.iterdir()
        if child.name != FILE_NAME and _TEMP_FILE.fullmatch(child.name) is None
    ]
    if unexpected:
        raise ValueError(
            "Сховище папок документів містить невідомий об'єкт: %s"
            % ", ".join(sorted(unexpected))
        )
    path = root / FILE_NAME
    if not path.exists():
        return CollectionState((), ())
    data = _load_json(path)
    if (
        not isinstance(data, dict)
        or set(data) != {"format", "collections", "memberships"}
        or data.get("format") != FORMAT
        or not isinstance(data.get("collections"), list)
        or not isinstance(data.get("memberships"), list)
    ):
        raise ValueError("Несумісний формат папок документів")
    return _validate_state(CollectionState(
        tuple(_collection(item) for item in data["collections"]),
        tuple(_membership(item) for item in data["memberships"]),
    ))


def _payload(state: CollectionState) -> bytes:
    checked = _validate_state(state)
    data = {
        "format": FORMAT,
        "collections": [
            {
                "id": row.collection_id,
                "parent_id": row.parent_id,
                "name": row.name,
                "sort_order": row.sort_order,
                "archived_at": row.archived_at,
                "created_at": row.created_at,
            }
            for row in checked.collections
        ],
        "memberships": [
            {
                "collection_id": row.collection_id,
                "document_key": row.document_key,
                "added_at": row.added_at,
            }
            for row in checked.memberships
        ],
    }
    raw = (json.dumps(
        data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ) + "\n").encode("utf-8")
    if len(raw) > MAX_BYTES:
        raise ValueError("Файл папок документів перевищує допустимий розмір")
    return raw


def _atomic_write(workspace_root: Path, state: CollectionState) -> CollectionState:
    root = collection_store_root(workspace_root)
    data_dir = root.parent
    if data_dir.exists() and (not data_dir.is_dir() or data_dir.is_symlink()):
        raise ValueError("Некоректна папка Data у робочому сховищі")
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=False)
    if root.exists() and (not root.is_dir() or root.is_symlink()):
        raise ValueError("Некоректне сховище папок документів")
    if not root.exists():
        root.mkdir(parents=False, exist_ok=False)

    checked = _validate_state(state)
    payload = _payload(checked)
    target = root / FILE_NAME
    temporary = root / (".%s.%s.tmp" % (FILE_NAME, uuid.uuid4().hex))
    try:
        with temporary.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temporary), str(target))
    finally:
        try:
            if temporary.exists():
                temporary.unlink()
        except OSError:
            pass
    return checked


def create_collection(workspace_root: Path, name: str, parent_id: str = "") -> CollectionRecord:
    """Create one folder. Duplicate sibling names are rejected."""
    name = _name(name)
    parent_id = str(parent_id or "").strip()
    with _WRITE_LOCK:
        state = read_collection_state(workspace_root)
        by_id = {row.collection_id: row for row in state.collections}
        if parent_id and parent_id not in by_id:
            raise ValueError("Батьківську папку не знайдено")
        if parent_id and by_id[parent_id].archived_at:
            raise ValueError("Не можна створити папку всередині архівної")
        if any(
            row.parent_id == parent_id and row.name.casefold() == name.casefold()
            for row in state.collections
        ):
            raise ValueError("Папка з такою назвою вже є на цьому рівні")
        peers = [
            row.sort_order for row in state.collections
            if row.parent_id == parent_id
        ]
        record = CollectionRecord(
            collection_id="dc-" + uuid.uuid4().hex,
            parent_id=parent_id,
            name=name,
            sort_order=(max(peers) + 10) if peers else 10,
            archived_at="",
            created_at=_iso_now(),
        )
        saved = _atomic_write(
            workspace_root,
            CollectionState(state.collections + (record,), state.memberships),
        )
        return next(
            row for row in saved.collections
            if row.collection_id == record.collection_id
        )


def rename_collection(workspace_root: Path, collection_id: str, name: str) -> CollectionRecord:
    """Rename only the logical folder; document bytes and metadata stay untouched."""
    name = _name(name)
    collection_id = str(collection_id or "").strip()
    with _WRITE_LOCK:
        state = read_collection_state(workspace_root)
        current = next(
            (row for row in state.collections if row.collection_id == collection_id),
            None,
        )
        if current is None:
            raise ValueError("Папку не знайдено")
        if current.archived_at:
            raise ValueError("Спочатку відновіть архівну папку")
        if any(
            row.collection_id != collection_id
            and row.parent_id == current.parent_id
            and row.name.casefold() == name.casefold()
            for row in state.collections
        ):
            raise ValueError("Папка з такою назвою вже є на цьому рівні")
        replacement = CollectionRecord(
            collection_id=current.collection_id,
            parent_id=current.parent_id,
            name=name,
            sort_order=current.sort_order,
            archived_at=current.archived_at,
            created_at=current.created_at,
        )
        saved = _atomic_write(
            workspace_root,
            CollectionState(
                tuple(
                    replacement if row.collection_id == collection_id else row
                    for row in state.collections
                ),
                state.memberships,
            ),
        )
        return next(row for row in saved.collections if row.collection_id == collection_id)


def move_collection(workspace_root: Path, collection_id: str, parent_id: str = "") -> CollectionRecord:
    """Move one logical folder, rejecting self-parenting and descendant cycles."""
    collection_id = str(collection_id or "").strip()
    parent_id = str(parent_id or "").strip()
    if collection_id == parent_id:
        raise ValueError("Папку не можна перемістити саму в себе")
    with _WRITE_LOCK:
        state = read_collection_state(workspace_root)
        by_id = {row.collection_id: row for row in state.collections}
        current = by_id.get(collection_id)
        if current is None:
            raise ValueError("Папку не знайдено")
        if current.archived_at:
            raise ValueError("Спочатку відновіть архівну папку")
        if parent_id and parent_id not in by_id:
            raise ValueError("Батьківську папку не знайдено")
        if parent_id and by_id[parent_id].archived_at:
            raise ValueError("Не можна перемістити папку всередину архівної")
        cursor = parent_id
        while cursor:
            if cursor == collection_id:
                raise ValueError("Переміщення створить цикл у дереві папок")
            cursor = by_id[cursor].parent_id
        if any(
            row.collection_id != collection_id
            and row.parent_id == parent_id
            and row.name.casefold() == current.name.casefold()
            for row in state.collections
        ):
            raise ValueError("У цій папці вже є папка з такою назвою")
        peers = [
            row.sort_order for row in state.collections
            if row.parent_id == parent_id and row.collection_id != collection_id
        ]
        replacement = CollectionRecord(
            collection_id=current.collection_id,
            parent_id=parent_id,
            name=current.name,
            sort_order=(max(peers) + 10) if peers else 10,
            archived_at=current.archived_at,
            created_at=current.created_at,
        )
        saved = _atomic_write(
            workspace_root,
            CollectionState(
                tuple(
                    replacement if row.collection_id == collection_id else row
                    for row in state.collections
                ),
                state.memberships,
            ),
        )
        return next(row for row in saved.collections if row.collection_id == collection_id)


def _descendant_ids(
    collections: Tuple[CollectionRecord, ...],
    collection_id: str,
) -> set:
    """Find one complete subtree, including its root, without touching files."""
    children = {}
    for item in collections:
        children.setdefault(item.parent_id, []).append(item.collection_id)
    result = {collection_id}
    pending = [collection_id]
    while pending:
        for child in children.get(pending.pop(), ()):
            if child not in result:
                result.add(child)
                pending.append(child)
    return result


def archive_collection(workspace_root: Path, collection_id: str) -> Tuple[str, ...]:
    """Hide one folder and descendants; retain all placements and document bytes.

    Archive is reversible. Nothing gets deleted or detached from any document.
    """
    collection_id = str(collection_id or "").strip()
    with _WRITE_LOCK:
        state = read_collection_state(workspace_root)
        by_id = {item.collection_id: item for item in state.collections}
        current = by_id.get(collection_id)
        if current is None:
            raise ValueError("Папку не знайдено")
        if current.archived_at:
            raise ValueError("Папка вже архівована")
        subtree = _descendant_ids(state.collections, collection_id)
        archived_at = _iso_now()
        changed = tuple(
            CollectionRecord(
                collection_id=item.collection_id,
                parent_id=item.parent_id,
                name=item.name,
                sort_order=item.sort_order,
                archived_at=archived_at if item.collection_id in subtree else item.archived_at,
                created_at=item.created_at,
            )
            for item in state.collections
        )
        _atomic_write(workspace_root, CollectionState(changed, state.memberships))
        return tuple(sorted(subtree))


def restore_collection(workspace_root: Path, collection_id: str) -> Tuple[str, ...]:
    """Restore an archived subtree, refusing to unhide it under an archived parent."""
    collection_id = str(collection_id or "").strip()
    with _WRITE_LOCK:
        state = read_collection_state(workspace_root)
        by_id = {item.collection_id: item for item in state.collections}
        current = by_id.get(collection_id)
        if current is None:
            raise ValueError("Папку не знайдено")
        if not current.archived_at:
            raise ValueError("Папка не архівована")
        parent = current.parent_id
        while parent:
            ancestor = by_id[parent]
            if ancestor.archived_at:
                raise ValueError("Спочатку відновіть батьківську папку")
            parent = ancestor.parent_id
        subtree = _descendant_ids(state.collections, collection_id)
        changed = tuple(
            CollectionRecord(
                collection_id=item.collection_id,
                parent_id=item.parent_id,
                name=item.name,
                sort_order=item.sort_order,
                archived_at="" if item.collection_id in subtree else item.archived_at,
                created_at=item.created_at,
            )
            for item in state.collections
        )
        _atomic_write(workspace_root, CollectionState(changed, state.memberships))
        return tuple(sorted(subtree))


def document_collection_ids(workspace_root: Path, document_key: str) -> Tuple[str, ...]:
    key = _document_ref(document_key)
    state = read_collection_state(workspace_root)
    return tuple(
        row.collection_id for row in state.memberships
        if row.document_key == key
    )


def set_document_collections(
    workspace_root: Path,
    document_key: str,
    collection_ids: Iterable[str],
) -> Tuple[str, ...]:
    """Atomically replace a document's logical-folder placements.

    Existing unchanged placements keep their original added_at timestamp.
    Passing an empty collection list removes only logical placements; the
    document itself is never deleted or changed.
    """
    document_key = _document_ref(document_key)
    wanted = []
    seen = set()
    for value in collection_ids:
        identity = str(value or "").strip()
        if identity in seen:
            continue
        seen.add(identity)
        wanted.append(identity)

    with _WRITE_LOCK:
        state = read_collection_state(workspace_root)
        known = {row.collection_id for row in state.collections}
        missing = [identity for identity in wanted if identity not in known]
        if missing:
            raise ValueError("Вибрану папку не знайдено")
        archived_ids = {
            item.collection_id for item in state.collections if item.archived_at
        }
        if any(identity in archived_ids for identity in wanted):
            raise ValueError("Спочатку відновіть архівну папку")
        old_for_document = {
            row.collection_id: row
            for row in state.memberships
            if row.document_key == document_key
        }
        others = tuple(
            row for row in state.memberships
            if row.document_key != document_key
        )
        now = _iso_now()
        replacements = tuple(
            old_for_document.get(identity)
            or MembershipRecord(identity, document_key, now)
            for identity in wanted
        )
        _atomic_write(
            workspace_root,
            CollectionState(state.collections, others + replacements),
        )
        return tuple(wanted)


def move_document(
    workspace_root: Path,
    document_key: str,
    collection_id: str,
) -> str:
    """Place a document in exactly one logical folder."""
    result = set_document_collections(
        workspace_root, document_key, (collection_id,)
    )
    return result[0]


def collection_document_keys(
    state: CollectionState,
    collection_id: str,
    *,
    include_descendants: bool = True,
) -> Tuple[str, ...]:
    """Return unique document keys in one folder, optionally including children."""
    checked = _validate_state(state)
    collection_id = str(collection_id or "").strip()
    by_id = {row.collection_id: row for row in checked.collections}
    if collection_id not in by_id:
        raise ValueError("Папку не знайдено")
    included = {collection_id}
    if include_descendants:
        changed = True
        while changed:
            changed = False
            for row in checked.collections:
                if row.parent_id in included and row.collection_id not in included:
                    included.add(row.collection_id)
                    changed = True
    return tuple(sorted({
        row.document_key for row in checked.memberships
        if row.collection_id in included
    }))
