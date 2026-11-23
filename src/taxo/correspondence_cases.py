# -*- coding: utf-8 -*-
"""Logical correspondence cases/threads.

A case groups existing registered correspondence without copying document bytes,
renumbering letters, or changing delivery/business state.  Membership is
explicit and reversible; one correspondence record belongs to at most one case
in this first bounded slice.
"""
from __future__ import annotations

import json
import os
import re
import threading
import uuid
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from correspondence_registry import (
    CorrespondenceRecord,
    read_registry,
)

STORE_NAME = "Correspondence"
FILE_NAME = "cases.json"
FORMAT = "taxo.correspondence-cases.v1"
MAX_BYTES = 4 * 1024 * 1024
MAX_TEXT = 500
MAX_NOTES = 4000

_CASE_ID = re.compile(r"^cc-[a-f0-9]{32}$")
_CORRESPONDENCE_ID = re.compile(r"^cr-[a-f0-9]{32}$")
_TEMP_FILE = re.compile(r"^\.cases\.json\.[a-f0-9]{32}\.tmp$")
_WRITE_LOCK = threading.RLock()


@dataclass(frozen=True)
class CorrespondenceCase:
    case_id: str
    title: str
    notes: str
    correspondence_ids: Tuple[str, ...]
    archived: bool
    created_at: str
    updated_at: str


def cases_root(workspace_root: Path) -> Path:
    return Path(workspace_root) / "Data" / STORE_NAME


def cases_path(workspace_root: Path) -> Path:
    return cases_root(workspace_root) / FILE_NAME


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _timestamp(value, label) -> str:
    clean = str(value or "").strip()
    try:
        parsed = datetime.fromisoformat(clean.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("%s має бути ISO timestamp" % label) from exc
    if parsed.tzinfo is None:
        raise ValueError("%s має містити timezone" % label)
    return parsed.isoformat()


def _clean_text(value, label, *, allow_empty=False, max_length=MAX_TEXT) -> str:
    clean = str(value or "").strip()
    if not clean and not allow_empty:
        raise ValueError("%s не може бути порожнім" % label)
    if len(clean) > max_length:
        raise ValueError("%s задовгий" % label)
    if any(ord(ch) < 32 and ch not in "\t\n\r" for ch in clean):
        raise ValueError("%s містить службові символи" % label)
    return clean


def _case_id(value) -> str:
    clean = str(value or "").strip()
    if _CASE_ID.fullmatch(clean) is None:
        raise ValueError("Некоректний ID справи")
    return clean


def _correspondence_id(value) -> str:
    clean = str(value or "").strip()
    if _CORRESPONDENCE_ID.fullmatch(clean) is None:
        raise ValueError("Некоректний ID кореспонденції")
    return clean


def _id_list(values) -> Tuple[str, ...]:
    if values is None:
        values = ()
    if isinstance(values, (str, bytes)) or not isinstance(values, (list, tuple)):
        raise ValueError("correspondence_ids має бути списком")
    result = tuple(_correspondence_id(value) for value in values)
    if len(result) != len(set(result)):
        raise ValueError("Справу не можна дубльовано пов'язати з одним листом")
    return result


def _json_object_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON містить дубльований ключ")
        result[key] = value
    return result


def _read_json(path: Path):
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError("Некоректний файл справ кореспонденції")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("Файл справ кореспонденції завеликий")
    try:
        return json.loads(
            path.read_text("utf-8"),
            object_pairs_hook=_json_object_no_duplicates,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Не вдалося прочитати справи кореспонденції") from exc


def _canonical_json_bytes(data) -> bytes:
    return (
        json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2)
        + "\n"
    ).encode("utf-8")


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink():
        raise ValueError("Сховище справ не може бути symlink")
    temp = path.parent / (".cases.json." + uuid.uuid4().hex + ".tmp")
    if not _TEMP_FILE.fullmatch(temp.name):
        raise ValueError("Некоректний тимчасовий файл справ")
    try:
        with temp.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(temp), str(path))
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def _case(entry) -> CorrespondenceCase:
    required = {
        "case_id",
        "title",
        "notes",
        "correspondence_ids",
        "archived",
        "created_at",
        "updated_at",
    }
    if not isinstance(entry, dict) or set(entry) != required:
        raise ValueError("Некоректний запис справи кореспонденції")
    if not isinstance(entry.get("archived"), bool):
        raise ValueError("archived має бути boolean")
    return CorrespondenceCase(
        case_id=_case_id(entry.get("case_id")),
        title=_clean_text(entry.get("title"), "Назва справи"),
        notes=_clean_text(
            entry.get("notes"),
            "Примітки справи",
            allow_empty=True,
            max_length=MAX_NOTES,
        ),
        correspondence_ids=_id_list(entry.get("correspondence_ids")),
        archived=entry["archived"],
        created_at=_timestamp(entry.get("created_at"), "created_at"),
        updated_at=_timestamp(entry.get("updated_at"), "updated_at"),
    )


def _validate_cases(workspace_root: Path, cases) -> Tuple[CorrespondenceCase, ...]:
    cases = tuple(cases)
    registry = read_registry(workspace_root)
    known = {record.correspondence_id for record in registry.records}

    seen_case_ids = set()
    seen_titles = set()
    membership = {}
    for case in cases:
        if case.case_id in seen_case_ids:
            raise ValueError("Дубльований ID справи")
        seen_case_ids.add(case.case_id)
        title_key = case.title.casefold()
        if title_key in seen_titles:
            raise ValueError("Справи повинні мати різні назви")
        seen_titles.add(title_key)

        for correspondence_id in case.correspondence_ids:
            if correspondence_id not in known:
                raise ValueError("Справа посилається на відсутню кореспонденцію")
            owner = membership.get(correspondence_id)
            if owner is not None and owner != case.case_id:
                raise ValueError("Один лист не може одночасно належати двом справам")
            membership[correspondence_id] = case.case_id

    return tuple(sorted(cases, key=lambda row: (row.archived, row.title.casefold(), row.case_id)))


def read_cases(workspace_root: Path) -> Tuple[CorrespondenceCase, ...]:
    path = cases_path(workspace_root)
    data = _read_json(path)
    if data is None:
        return ()
    if (
        not isinstance(data, dict)
        or set(data) != {"format", "cases"}
        or data.get("format") != FORMAT
        or not isinstance(data.get("cases"), list)
    ):
        raise ValueError("Несумісний формат справ кореспонденції")
    return _validate_cases(
        workspace_root,
        tuple(_case(entry) for entry in data["cases"]),
    )


def _payload(workspace_root: Path, cases) -> bytes:
    checked = _validate_cases(workspace_root, cases)
    return _canonical_json_bytes({
        "format": FORMAT,
        "cases": [
            {
                "case_id": case.case_id,
                "title": case.title,
                "notes": case.notes,
                "correspondence_ids": list(case.correspondence_ids),
                "archived": case.archived,
                "created_at": case.created_at,
                "updated_at": case.updated_at,
            }
            for case in checked
        ],
    })


def _write_cases(workspace_root: Path, cases) -> Tuple[CorrespondenceCase, ...]:
    payload = _payload(workspace_root, cases)
    if len(payload) > MAX_BYTES:
        raise ValueError("Файл справ кореспонденції завеликий")
    _atomic_write(cases_path(workspace_root), payload)
    return read_cases(workspace_root)


def list_cases(
    workspace_root: Path, *, include_archived=False
) -> Tuple[CorrespondenceCase, ...]:
    cases = read_cases(workspace_root)
    if include_archived:
        return cases
    return tuple(case for case in cases if not case.archived)


def get_case(workspace_root: Path, case_id: str) -> CorrespondenceCase:
    case_id = _case_id(case_id)
    for case in read_cases(workspace_root):
        if case.case_id == case_id:
            return case
    raise ValueError("Справу кореспонденції не знайдено")


def create_case(
    workspace_root: Path, title: str, *, notes: str = ""
) -> CorrespondenceCase:
    title = _clean_text(title, "Назва справи")
    notes = _clean_text(
        notes, "Примітки справи", allow_empty=True, max_length=MAX_NOTES
    )
    with _WRITE_LOCK:
        cases = read_cases(workspace_root)
        if any(case.title.casefold() == title.casefold() for case in cases):
            raise ValueError("Справа з такою назвою вже існує")
        timestamp = _iso_now()
        case = CorrespondenceCase(
            case_id="cc-" + uuid.uuid4().hex,
            title=title,
            notes=notes,
            correspondence_ids=(),
            archived=False,
            created_at=timestamp,
            updated_at=timestamp,
        )
        saved = _write_cases(workspace_root, cases + (case,))
        return next(row for row in saved if row.case_id == case.case_id)


def rename_case(
    workspace_root: Path, case_id: str, title: str, *, notes=None
) -> CorrespondenceCase:
    case_id = _case_id(case_id)
    title = _clean_text(title, "Назва справи")
    with _WRITE_LOCK:
        cases = read_cases(workspace_root)
        current = get_case(workspace_root, case_id)
        if current.archived:
            raise ValueError("Спочатку відновіть архівовану справу")
        if any(
            case.case_id != case_id and case.title.casefold() == title.casefold()
            for case in cases
        ):
            raise ValueError("Справа з такою назвою вже існує")
        clean_notes = current.notes if notes is None else _clean_text(
            notes,
            "Примітки справи",
            allow_empty=True,
            max_length=MAX_NOTES,
        )
        updated = replace(
            current,
            title=title,
            notes=clean_notes,
            updated_at=_iso_now(),
        )
        saved = _write_cases(
            workspace_root,
            tuple(updated if case.case_id == case_id else case for case in cases),
        )
        return next(row for row in saved if row.case_id == case_id)


def set_case_archived(
    workspace_root: Path, case_id: str, archived: bool
) -> CorrespondenceCase:
    case_id = _case_id(case_id)
    if not isinstance(archived, bool):
        raise ValueError("archived має бути boolean")
    with _WRITE_LOCK:
        cases = read_cases(workspace_root)
        current = get_case(workspace_root, case_id)
        if current.archived == archived:
            return current
        updated = replace(
            current,
            archived=archived,
            updated_at=_iso_now(),
        )
        saved = _write_cases(
            workspace_root,
            tuple(updated if case.case_id == case_id else case for case in cases),
        )
        return next(row for row in saved if row.case_id == case_id)


def case_for_correspondence(
    workspace_root: Path, correspondence_id: str
):
    correspondence_id = _correspondence_id(correspondence_id)
    for case in read_cases(workspace_root):
        if correspondence_id in case.correspondence_ids:
            return case
    return None


def add_correspondence_to_case(
    workspace_root: Path, case_id: str, correspondence_id: str
) -> CorrespondenceCase:
    case_id = _case_id(case_id)
    correspondence_id = _correspondence_id(correspondence_id)
    with _WRITE_LOCK:
        cases = read_cases(workspace_root)
        current = get_case(workspace_root, case_id)
        if current.archived:
            raise ValueError("Не можна додавати листи до архівованої справи")

        owner = case_for_correspondence(workspace_root, correspondence_id)
        if owner is not None:
            if owner.case_id == case_id:
                return current
            raise ValueError("Цей лист уже належить іншій справі")

        updated = replace(
            current,
            correspondence_ids=current.correspondence_ids + (correspondence_id,),
            updated_at=_iso_now(),
        )
        saved = _write_cases(
            workspace_root,
            tuple(updated if case.case_id == case_id else case for case in cases),
        )
        return next(row for row in saved if row.case_id == case_id)


def remove_correspondence_from_case(
    workspace_root: Path, case_id: str, correspondence_id: str
) -> CorrespondenceCase:
    case_id = _case_id(case_id)
    correspondence_id = _correspondence_id(correspondence_id)
    with _WRITE_LOCK:
        cases = read_cases(workspace_root)
        current = get_case(workspace_root, case_id)
        if current.archived:
            raise ValueError("Спочатку відновіть архівовану справу")
        if correspondence_id not in current.correspondence_ids:
            return current
        updated = replace(
            current,
            correspondence_ids=tuple(
                value for value in current.correspondence_ids
                if value != correspondence_id
            ),
            updated_at=_iso_now(),
        )
        saved = _write_cases(
            workspace_root,
            tuple(updated if case.case_id == case_id else case for case in cases),
        )
        return next(row for row in saved if row.case_id == case_id)


def move_correspondence_to_case(
    workspace_root: Path, correspondence_id: str, target_case_id=None
):
    """Atomically move one letter between logical cases or unfile it."""
    correspondence_id = _correspondence_id(correspondence_id)
    target_case_id = (
        None if target_case_id in (None, "") else _case_id(target_case_id)
    )
    with _WRITE_LOCK:
        cases = read_cases(workspace_root)
        registry = read_registry(workspace_root)
        if correspondence_id not in {
            row.correspondence_id for row in registry.records
        }:
            raise ValueError("Запис кореспонденції не знайдено")

        target = None
        if target_case_id is not None:
            target = next(
                (case for case in cases if case.case_id == target_case_id),
                None,
            )
            if target is None:
                raise ValueError("Справу кореспонденції не знайдено")
            if target.archived:
                raise ValueError("Не можна додавати листи до архівованої справи")

        current = next(
            (
                case for case in cases
                if correspondence_id in case.correspondence_ids
            ),
            None,
        )
        if current is not None and current.archived:
            raise ValueError("Спочатку відновіть архівовану справу")
        if (
            (current is None and target_case_id is None)
            or (
                current is not None
                and current.case_id == target_case_id
            )
        ):
            return current

        timestamp = _iso_now()
        updated_cases = []
        for case in cases:
            ids = tuple(
                value for value in case.correspondence_ids
                if value != correspondence_id
            )
            if case.case_id == target_case_id:
                ids = ids + (correspondence_id,)
            if ids != case.correspondence_ids:
                case = replace(
                    case,
                    correspondence_ids=ids,
                    updated_at=timestamp,
                )
            updated_cases.append(case)

        saved = _write_cases(workspace_root, tuple(updated_cases))
        if target_case_id is None:
            return None
        return next(case for case in saved if case.case_id == target_case_id)


def list_case_correspondence(
    workspace_root: Path, case_id: str
) -> Tuple[CorrespondenceRecord, ...]:
    case = get_case(workspace_root, case_id)
    registry = read_registry(workspace_root)
    by_id = {row.correspondence_id: row for row in registry.records}
    return tuple(sorted(
        (by_id[value] for value in case.correspondence_ids),
        key=lambda row: (
            row.registration_date,
            row.direction,
            row.sequence_number,
            row.correspondence_id,
        ),
    ))


def linked_correspondence_candidates(
    workspace_root: Path, case_id: str
) -> Tuple[CorrespondenceRecord, ...]:
    """Return explicitly linked records outside a case, without adding them."""
    case = get_case(workspace_root, case_id)
    registry = read_registry(workspace_root)
    records = tuple(registry.records)
    by_id = {row.correspondence_id: row for row in records}
    adjacency = {identity: set() for identity in by_id}

    for row in records:
        for target in set(row.response_to_ids) | set(row.related_ids):
            if target in by_id:
                adjacency[row.correspondence_id].add(target)
                adjacency[target].add(row.correspondence_id)

    in_case = set(case.correspondence_ids)
    seen = set(in_case)
    pending = list(in_case)
    while pending:
        identity = pending.pop()
        for target in adjacency.get(identity, ()):
            if target not in seen:
                seen.add(target)
                pending.append(target)

    linked = seen - in_case
    return tuple(sorted(
        (by_id[value] for value in linked),
        key=lambda row: (
            row.registration_date,
            row.direction,
            row.sequence_number,
            row.correspondence_id,
        ),
    ))


def add_linked_correspondence_to_case(
    workspace_root: Path, case_id: str
) -> CorrespondenceCase:
    """Atomically add all explicitly linked thread records to one case."""
    case_id = _case_id(case_id)
    with _WRITE_LOCK:
        cases = read_cases(workspace_root)
        current = next(
            (case for case in cases if case.case_id == case_id),
            None,
        )
        if current is None:
            raise ValueError("Справу кореспонденції не знайдено")
        if current.archived:
            raise ValueError("Не можна додавати листи до архівованої справи")

        candidates = linked_correspondence_candidates(workspace_root, case_id)
        ownership = {
            correspondence_id: case.case_id
            for case in cases
            for correspondence_id in case.correspondence_ids
        }
        for record in candidates:
            owner = ownership.get(record.correspondence_id)
            if owner is not None and owner != case_id:
                raise ValueError(
                    "Пов'язаний лист уже належить іншій справі: %s"
                    % record.registration_number
                )

        new_ids = current.correspondence_ids + tuple(
            record.correspondence_id
            for record in candidates
            if record.correspondence_id not in current.correspondence_ids
        )
        if new_ids == current.correspondence_ids:
            return current

        updated = replace(
            current,
            correspondence_ids=new_ids,
            updated_at=_iso_now(),
        )
        saved = _write_cases(
            workspace_root,
            tuple(updated if case.case_id == case_id else case for case in cases),
        )
        return next(case for case in saved if case.case_id == case_id)
