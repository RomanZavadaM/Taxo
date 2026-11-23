# -*- coding: utf-8 -*-
"""Persistent incoming/outgoing business correspondence registry.

The registry stores metadata and stable links only. It does not copy document
bytes, send e-mail, change DocumentVault, or treat registration as delivery.
Persistence lives under workspace/Data/Correspondence, so full workspace backup
and restore include it automatically.
"""
from __future__ import annotations

import json
import os
import re
import threading
import uuid
from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable, Tuple


STORE_NAME = "Correspondence"
FILE_NAME = "registry.json"
FORMAT_V1 = "taxo.correspondence-registry.v1"
FORMAT = "taxo.correspondence-registry.v2"
MAX_BYTES = 8 * 1024 * 1024
MAX_TEXT = 500
MAX_SUMMARY = 4000

DIRECTION_INCOMING = "incoming"
DIRECTION_OUTGOING = "outgoing"
DIRECTIONS = (DIRECTION_INCOMING, DIRECTION_OUTGOING)

DEFAULT_STATUS = {
    DIRECTION_INCOMING: "new",
    DIRECTION_OUTGOING: "registered",
}
ALLOWED_STATUS = {
    DIRECTION_INCOMING: {
        "new",
        "received",
        "in_progress",
        "awaiting_response",
        "response_prepared",
        "response_sent",
        "closed",
        "cancelled",
    },
    DIRECTION_OUTGOING: {
        "registered",
        "sent",
        "closed",
        "cancelled",
    },
}
ALLOWED_TRANSITIONS = {
    DIRECTION_INCOMING: {
        "new": ("received", "cancelled"),
        "received": (
            "in_progress",
            "awaiting_response",
            "response_prepared",
            "closed",
            "cancelled",
        ),
        "in_progress": (
            "awaiting_response",
            "response_prepared",
            "closed",
            "cancelled",
        ),
        "awaiting_response": ("response_prepared", "closed", "cancelled"),
        "response_prepared": ("response_sent", "closed", "cancelled"),
        "response_sent": ("closed",),
        "closed": (),
        "cancelled": (),
    },
    DIRECTION_OUTGOING: {
        "registered": ("sent", "cancelled"),
        "sent": ("closed",),
        "closed": (),
        "cancelled": (),
    },
}

DELIVERY_METHODS = {
    "",
    "mail",
    "email",
    "personal",
    "courier",
    "other",
}

_ID = re.compile(r"^cr-[a-f0-9]{32}$")
_EVENT_ID = re.compile(r"^ce-[a-f0-9]{32}$")
_DOCUMENT_REF = re.compile(r"^(?:vault|paper|order):[A-Za-z0-9._-]{1,200}$")
_TEMP_FILE = re.compile(r"^\.registry\.json\.[a-f0-9]{32}\.tmp$")
_WRITE_LOCK = threading.RLock()


@dataclass(frozen=True)
class SequenceRecord:
    direction: str
    year: int
    next_number: int


@dataclass(frozen=True)
class CorrespondenceRecord:
    correspondence_id: str
    direction: str
    registration_number: str
    sequence_number: int
    registration_year: int
    registration_date: str
    document_date: str
    received_date: str
    sent_date: str
    external_number: str
    correspondent: str
    subject: str
    summary: str
    delivery_method: str
    responsible_id: str
    due_date: str
    status: str
    document_ref: str
    response_to_ids: Tuple[str, ...]
    related_ids: Tuple[str, ...]
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class CorrespondenceStateEvent:
    event_id: str
    correspondence_id: str
    direction: str
    from_status: str
    to_status: str
    action_date: str
    changed_at: str


@dataclass(frozen=True)
class RegistryState:
    sequences: Tuple[SequenceRecord, ...]
    records: Tuple[CorrespondenceRecord, ...]
    state_events: Tuple[CorrespondenceStateEvent, ...] = ()


def registry_root(workspace_root: Path) -> Path:
    return Path(workspace_root) / "Data" / STORE_NAME


def registry_path(workspace_root: Path) -> Path:
    return registry_root(workspace_root) / FILE_NAME


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _direction(value) -> str:
    clean = str(value or "").strip().casefold()
    if clean not in DIRECTIONS:
        raise ValueError("Некоректний напрям кореспонденції")
    return clean


def _clean_text(value, label, *, allow_empty=False, max_length=MAX_TEXT) -> str:
    if not isinstance(value, str):
        raise ValueError("%s має бути текстом" % label)
    clean = " ".join(value.strip().split())
    if not clean and not allow_empty:
        raise ValueError("%s не може бути порожнім" % label)
    if len(clean) > max_length:
        raise ValueError("%s перевищує допустиму довжину" % label)
    if any(ord(ch) < 32 for ch in clean):
        raise ValueError("%s містить службовий символ" % label)
    return clean


def _date(value, label, *, allow_empty=False) -> str:
    if allow_empty and value == "":
        return ""
    if not isinstance(value, str) or not value:
        raise ValueError("%s має бути датою РРРР-ММ-ДД" % label)
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("%s має бути датою РРРР-ММ-ДД" % label) from exc
    return parsed.isoformat()


def _timestamp(value, label) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("Некоректне поле %s у реєстрі кореспонденції" % label)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Некоректне поле %s у реєстрі кореспонденції" % label) from exc
    if parsed.tzinfo is None:
        raise ValueError("Поле %s не містить timezone" % label)
    return value


def _status(direction, value) -> str:
    direction = _direction(direction)
    clean = str(value or "").strip().casefold()
    if clean not in ALLOWED_STATUS[direction]:
        raise ValueError("Некоректний стан кореспонденції")
    return clean


def _delivery_method(value) -> str:
    clean = str(value or "").strip().casefold()
    if clean not in DELIVERY_METHODS:
        raise ValueError("Некоректний спосіб отримання/відправлення")
    return clean


def _document_ref(value) -> str:
    clean = str(value or "").strip()
    if not clean:
        return ""
    if _DOCUMENT_REF.fullmatch(clean) is None:
        raise ValueError("Некоректне посилання на готовий документ")
    return clean


def _id(value, label="ID кореспонденції") -> str:
    clean = str(value or "").strip()
    if _ID.fullmatch(clean) is None:
        raise ValueError("Некоректний %s" % label)
    return clean


def _id_list(values, label) -> Tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, str):
        raise ValueError("%s має бути списком ID" % label)
    result = []
    seen = set()
    for value in values:
        identity = _id(value)
        if identity in seen:
            raise ValueError("Дубльований ID у полі %s" % label)
        seen.add(identity)
        result.append(identity)
    return tuple(sorted(result))


def _number_prefix(direction) -> str:
    return "Вх." if _direction(direction) == DIRECTION_INCOMING else "Вих."


def format_registration_number(direction, sequence_number, year) -> str:
    direction = _direction(direction)
    if type(sequence_number) is not int or sequence_number < 1:
        raise ValueError("Некоректний порядковий номер кореспонденції")
    if type(year) is not int or year < 2000 or year > 9999:
        raise ValueError("Некоректний рік журналу кореспонденції")
    return "%s № %04d/%04d" % (
        _number_prefix(direction),
        sequence_number,
        year,
    )


def empty_state() -> RegistryState:
    return RegistryState((), ())


def _json_object_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Дубльоване поле у реєстрі кореспонденції")
        result[key] = value
    return result


def _load_json(path: Path):
    if not path.is_file() or path.is_symlink():
        raise ValueError("Некоректний файл реєстру кореспонденції")
    size = path.stat().st_size
    if size < 1 or size > MAX_BYTES:
        raise ValueError("Файл реєстру кореспонденції має некоректний розмір")
    try:
        return json.loads(
            path.read_text("utf-8"),
            object_pairs_hook=_json_object_no_duplicates,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Пошкоджений файл реєстру кореспонденції") from exc


def _sequence(entry) -> SequenceRecord:
    required = {"direction", "year", "next_number"}
    if not isinstance(entry, dict) or set(entry) != required:
        raise ValueError("Некоректний запис номерної послідовності")
    direction = _direction(entry.get("direction"))
    year = entry.get("year")
    next_number = entry.get("next_number")
    if type(year) is not int or year < 2000 or year > 9999:
        raise ValueError("Некоректний рік номерної послідовності")
    if type(next_number) is not int or next_number < 1:
        raise ValueError("Некоректний наступний номер кореспонденції")
    return SequenceRecord(direction, year, next_number)


def _record(entry) -> CorrespondenceRecord:
    required = {
        "id",
        "direction",
        "registration_number",
        "sequence_number",
        "registration_year",
        "registration_date",
        "document_date",
        "received_date",
        "sent_date",
        "external_number",
        "correspondent",
        "subject",
        "summary",
        "delivery_method",
        "responsible_id",
        "due_date",
        "status",
        "document_ref",
        "response_to_ids",
        "related_ids",
        "created_at",
        "updated_at",
    }
    if not isinstance(entry, dict) or set(entry) != required:
        raise ValueError("Некоректний запис кореспонденції")

    direction = _direction(entry.get("direction"))
    sequence_number = entry.get("sequence_number")
    registration_year = entry.get("registration_year")
    if type(sequence_number) is not int or sequence_number < 1:
        raise ValueError("Некоректний порядковий номер кореспонденції")
    if type(registration_year) is not int:
        raise ValueError("Некоректний рік реєстрації")

    registration_date = _date(
        entry.get("registration_date"), "Дата реєстрації"
    )
    if date.fromisoformat(registration_date).year != registration_year:
        raise ValueError("Рік журналу не відповідає даті реєстрації")

    expected_number = format_registration_number(
        direction, sequence_number, registration_year
    )
    if entry.get("registration_number") != expected_number:
        raise ValueError("Реєстраційний номер не відповідає послідовності")

    received_date = _date(
        entry.get("received_date"), "Дата отримання", allow_empty=True
    )
    sent_date = _date(
        entry.get("sent_date"), "Дата відправлення", allow_empty=True
    )
    if direction == DIRECTION_INCOMING and sent_date:
        raise ValueError("Вхідний лист не може мати дату відправлення як власну дію")
    if direction == DIRECTION_OUTGOING and received_date:
        raise ValueError("Вихідний лист не може мати дату отримання як власну дію")

    return CorrespondenceRecord(
        correspondence_id=_id(entry.get("id")),
        direction=direction,
        registration_number=expected_number,
        sequence_number=sequence_number,
        registration_year=registration_year,
        registration_date=registration_date,
        document_date=_date(
            entry.get("document_date"), "Дата документа", allow_empty=True
        ),
        received_date=received_date,
        sent_date=sent_date,
        external_number=_clean_text(
            entry.get("external_number"),
            "Зовнішній номер",
            allow_empty=True,
        ),
        correspondent=_clean_text(
            entry.get("correspondent"), "Кореспондент"
        ),
        subject=_clean_text(entry.get("subject"), "Тема"),
        summary=_clean_text(
            entry.get("summary"),
            "Короткий зміст",
            allow_empty=True,
            max_length=MAX_SUMMARY,
        ),
        delivery_method=_delivery_method(entry.get("delivery_method")),
        responsible_id=_clean_text(
            entry.get("responsible_id"),
            "ID відповідального",
            allow_empty=True,
            max_length=200,
        ),
        due_date=_date(
            entry.get("due_date"), "Строк виконання", allow_empty=True
        ),
        status=_status(direction, entry.get("status")),
        document_ref=_document_ref(entry.get("document_ref")),
        response_to_ids=_id_list(
            entry.get("response_to_ids"), "response_to_ids"
        ),
        related_ids=_id_list(entry.get("related_ids"), "related_ids"),
        created_at=_timestamp(entry.get("created_at"), "created_at"),
        updated_at=_timestamp(entry.get("updated_at"), "updated_at"),
    )



def _state_event(entry) -> CorrespondenceStateEvent:
    required = {
        "event_id",
        "correspondence_id",
        "direction",
        "from_status",
        "to_status",
        "action_date",
        "changed_at",
    }
    if not isinstance(entry, dict) or set(entry) != required:
        raise ValueError("Некоректна подія стану кореспонденції")

    event_id = str(entry.get("event_id") or "").strip()
    if _EVENT_ID.fullmatch(event_id) is None:
        raise ValueError("Некоректний ID події стану")
    correspondence_id = _id(entry.get("correspondence_id"))
    direction = _direction(entry.get("direction"))
    from_status = _status(direction, entry.get("from_status"))
    to_status = _status(direction, entry.get("to_status"))
    if to_status not in ALLOWED_TRANSITIONS[direction].get(from_status, ()):
        raise ValueError("Недозволений перехід стану кореспонденції")
    action_date = _date(
        entry.get("action_date"), "Дата фактичної дії", allow_empty=True
    )
    if to_status == "received":
        if direction != DIRECTION_INCOMING or not action_date:
            raise ValueError("Стан «отримано» потребує дати отримання")
    elif to_status == "sent":
        if direction != DIRECTION_OUTGOING or not action_date:
            raise ValueError("Стан «надіслано» потребує дати відправлення")
    elif action_date:
        raise ValueError("Дата фактичної дії дозволена лише для отримання/відправлення")
    return CorrespondenceStateEvent(
        event_id=event_id,
        correspondence_id=correspondence_id,
        direction=direction,
        from_status=from_status,
        to_status=to_status,
        action_date=action_date,
        changed_at=_timestamp(entry.get("changed_at"), "changed_at"),
    )

def _validate_state(state: RegistryState) -> RegistryState:
    sequences = tuple(state.sequences)
    records = tuple(state.records)
    state_events = tuple(state.state_events)

    seq_by_key = {}
    for item in sequences:
        key = (item.direction, item.year)
        if key in seq_by_key:
            raise ValueError("Дубльована номерна послідовність")
        seq_by_key[key] = item

    by_id = {}
    number_keys = set()
    max_used = {}
    for item in records:
        if item.correspondence_id in by_id:
            raise ValueError("Дубльований ID кореспонденції")
        by_id[item.correspondence_id] = item
        key = (item.direction, item.registration_year, item.sequence_number)
        if key in number_keys:
            raise ValueError("Дубльований реєстраційний номер")
        number_keys.add(key)
        seq_key = (item.direction, item.registration_year)
        max_used[seq_key] = max(max_used.get(seq_key, 0), item.sequence_number)

    for key, maximum in max_used.items():
        sequence = seq_by_key.get(key)
        if sequence is None:
            raise ValueError("Відсутня номерна послідовність для журналу")
        if sequence.next_number <= maximum:
            raise ValueError("Наступний номер може повторити вже виданий")

    for key, sequence in seq_by_key.items():
        if sequence.next_number <= max_used.get(key, 0):
            raise ValueError("Пошкоджена номерна послідовність")

    for item in records:
        if item.correspondence_id in item.response_to_ids:
            raise ValueError("Лист не може бути відповіддю на самого себе")
        if item.correspondence_id in item.related_ids:
            raise ValueError("Лист не може бути пов'язаний сам із собою")
        for target_id in item.response_to_ids + item.related_ids:
            if target_id not in by_id:
                raise ValueError("Зв'язок посилається на відсутню кореспонденцію")
        if item.response_to_ids:
            if item.direction != DIRECTION_OUTGOING:
                raise ValueError("Лише вихідний лист може бути відповіддю")
            if any(
                by_id[target_id].direction != DIRECTION_INCOMING
                for target_id in item.response_to_ids
            ):
                raise ValueError("Відповідь має посилатися на вхідний лист")

    seen_event_ids = set()
    last_status_by_record = {}
    for event in state_events:
        if event.event_id in seen_event_ids:
            raise ValueError("Дубльований ID події стану")
        seen_event_ids.add(event.event_id)
        record = by_id.get(event.correspondence_id)
        if record is None:
            raise ValueError("Подія стану посилається на відсутню кореспонденцію")
        if record.direction != event.direction:
            raise ValueError("Напрям події стану не відповідає листу")
        expected_from = last_status_by_record.get(
            event.correspondence_id, event.from_status
        )
        if event.from_status != expected_from:
            raise ValueError("Порушений ланцюжок історії станів")
        last_status_by_record[event.correspondence_id] = event.to_status

    for correspondence_id, last_status in last_status_by_record.items():
        if by_id[correspondence_id].status != last_status:
            raise ValueError("Поточний стан не відповідає історії переходів")

    return RegistryState(
        sequences=tuple(sorted(
            sequences, key=lambda row: (row.direction, row.year)
        )),
        records=tuple(sorted(
            records,
            key=lambda row: (
                row.registration_date,
                row.direction,
                row.sequence_number,
                row.correspondence_id,
            ),
        )),
        state_events=state_events,
    )


def read_registry(workspace_root: Path) -> RegistryState:
    """Read and fully validate the correspondence registry without creating it."""
    root = registry_root(workspace_root)
    if not root.exists():
        return empty_state()
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Некоректне сховище кореспонденції")
    unexpected = [
        child.name
        for child in root.iterdir()
        if child.name != FILE_NAME and _TEMP_FILE.fullmatch(child.name) is None
    ]
    if unexpected:
        raise ValueError(
            "Сховище кореспонденції містить невідомий об'єкт: %s"
            % ", ".join(sorted(unexpected))
        )
    path = root / FILE_NAME
    if not path.exists():
        return empty_state()
    data = _load_json(path)
    if not isinstance(data, dict):
        raise ValueError("Несумісний формат реєстру кореспонденції")
    if data.get("format") == FORMAT_V1:
        if (
            set(data) != {"format", "sequences", "records"}
            or not isinstance(data.get("sequences"), list)
            or not isinstance(data.get("records"), list)
        ):
            raise ValueError("Несумісний формат реєстру кореспонденції")
        state_events = ()
    elif data.get("format") == FORMAT:
        if (
            set(data) != {"format", "sequences", "records", "state_events"}
            or not isinstance(data.get("sequences"), list)
            or not isinstance(data.get("records"), list)
            or not isinstance(data.get("state_events"), list)
        ):
            raise ValueError("Несумісний формат реєстру кореспонденції")
        state_events = tuple(
            _state_event(item) for item in data["state_events"]
        )
    else:
        raise ValueError("Несумісний формат реєстру кореспонденції")
    return _validate_state(RegistryState(
        tuple(_sequence(item) for item in data["sequences"]),
        tuple(_record(item) for item in data["records"]),
        state_events,
    ))


def _payload(state: RegistryState) -> bytes:
    checked = _validate_state(state)
    data = {
        "format": FORMAT,
        "sequences": [
            {
                "direction": row.direction,
                "year": row.year,
                "next_number": row.next_number,
            }
            for row in checked.sequences
        ],
        "records": [
            {
                "id": row.correspondence_id,
                "direction": row.direction,
                "registration_number": row.registration_number,
                "sequence_number": row.sequence_number,
                "registration_year": row.registration_year,
                "registration_date": row.registration_date,
                "document_date": row.document_date,
                "received_date": row.received_date,
                "sent_date": row.sent_date,
                "external_number": row.external_number,
                "correspondent": row.correspondent,
                "subject": row.subject,
                "summary": row.summary,
                "delivery_method": row.delivery_method,
                "responsible_id": row.responsible_id,
                "due_date": row.due_date,
                "status": row.status,
                "document_ref": row.document_ref,
                "response_to_ids": list(row.response_to_ids),
                "related_ids": list(row.related_ids),
                "created_at": row.created_at,
                "updated_at": row.updated_at,
            }
            for row in checked.records
        ],
        "state_events": [
            {
                "event_id": event.event_id,
                "correspondence_id": event.correspondence_id,
                "direction": event.direction,
                "from_status": event.from_status,
                "to_status": event.to_status,
                "action_date": event.action_date,
                "changed_at": event.changed_at,
            }
            for event in checked.state_events
        ],
    }
    raw = (
        json.dumps(
            data,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    if len(raw) > MAX_BYTES:
        raise ValueError("Реєстр кореспонденції перевищує допустимий розмір")
    return raw


def _atomic_write(workspace_root: Path, state: RegistryState) -> RegistryState:
    root = registry_root(workspace_root)
    data_dir = root.parent
    if data_dir.exists() and (not data_dir.is_dir() or data_dir.is_symlink()):
        raise ValueError("Некоректна папка Data у робочому сховищі")
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=False)
    if root.exists() and (not root.is_dir() or root.is_symlink()):
        raise ValueError("Некоректне сховище кореспонденції")
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


def _sequence_for(state, direction, year) -> SequenceRecord:
    for row in state.sequences:
        if row.direction == direction and row.year == year:
            return row
    return SequenceRecord(direction, year, 1)


def next_registration_number(
    workspace_root: Path,
    direction: str,
    registration_date: str,
) -> str:
    """Preview the next number without reserving it."""
    direction = _direction(direction)
    registration_date = _date(registration_date, "Дата реєстрації")
    year = date.fromisoformat(registration_date).year
    with _WRITE_LOCK:
        state = read_registry(workspace_root)
        sequence = _sequence_for(state, direction, year)
        return format_registration_number(
            direction, sequence.next_number, year
        )


def register_correspondence(
    workspace_root: Path,
    *,
    direction: str,
    registration_date: str,
    correspondent: str,
    subject: str,
    document_date: str = "",
    received_date: str = "",
    sent_date: str = "",
    external_number: str = "",
    summary: str = "",
    delivery_method: str = "",
    responsible_id: str = "",
    due_date: str = "",
    status: str = "",
    document_ref: str = "",
    response_to_ids: Iterable[str] = (),
    related_ids: Iterable[str] = (),
) -> CorrespondenceRecord:
    """Register one letter and atomically reserve the next journal number."""
    direction = _direction(direction)
    registration_date = _date(registration_date, "Дата реєстрації")
    year = date.fromisoformat(registration_date).year
    correspondent = _clean_text(correspondent, "Кореспондент")
    subject = _clean_text(subject, "Тема")
    document_date = _date(
        document_date, "Дата документа", allow_empty=True
    )
    received_date = _date(
        received_date, "Дата отримання", allow_empty=True
    )
    sent_date = _date(
        sent_date, "Дата відправлення", allow_empty=True
    )
    if direction == DIRECTION_INCOMING and sent_date:
        raise ValueError("Для вхідного листа sent_date не використовується")
    if direction == DIRECTION_OUTGOING and received_date:
        raise ValueError("Для вихідного листа received_date не використовується")
    external_number = _clean_text(
        external_number, "Зовнішній номер", allow_empty=True
    )
    summary = _clean_text(
        summary,
        "Короткий зміст",
        allow_empty=True,
        max_length=MAX_SUMMARY,
    )
    delivery_method = _delivery_method(delivery_method)
    responsible_id = _clean_text(
        responsible_id,
        "ID відповідального",
        allow_empty=True,
        max_length=200,
    )
    due_date = _date(due_date, "Строк виконання", allow_empty=True)
    status = _status(direction, status or DEFAULT_STATUS[direction])
    document_ref = _document_ref(document_ref)
    response_to_ids = _id_list(response_to_ids, "response_to_ids")
    related_ids = _id_list(related_ids, "related_ids")

    with _WRITE_LOCK:
        state = read_registry(workspace_root)
        by_id = {row.correspondence_id: row for row in state.records}
        for target_id in response_to_ids + related_ids:
            if target_id not in by_id:
                raise ValueError("Пов'язаний лист не знайдено")
        if response_to_ids:
            if direction != DIRECTION_OUTGOING:
                raise ValueError("Лише вихідний лист може бути відповіддю")
            if any(
                by_id[target_id].direction != DIRECTION_INCOMING
                for target_id in response_to_ids
            ):
                raise ValueError("Відповідь має посилатися на вхідний лист")

        sequence = _sequence_for(state, direction, year)
        timestamp = _iso_now()
        record = CorrespondenceRecord(
            correspondence_id="cr-" + uuid.uuid4().hex,
            direction=direction,
            registration_number=format_registration_number(
                direction, sequence.next_number, year
            ),
            sequence_number=sequence.next_number,
            registration_year=year,
            registration_date=registration_date,
            document_date=document_date,
            received_date=received_date,
            sent_date=sent_date,
            external_number=external_number,
            correspondent=correspondent,
            subject=subject,
            summary=summary,
            delivery_method=delivery_method,
            responsible_id=responsible_id,
            due_date=due_date,
            status=status,
            document_ref=document_ref,
            response_to_ids=response_to_ids,
            related_ids=related_ids,
            created_at=timestamp,
            updated_at=timestamp,
        )
        replacement = SequenceRecord(
            direction=direction,
            year=year,
            next_number=sequence.next_number + 1,
        )
        sequences = tuple(
            row
            for row in state.sequences
            if not (row.direction == direction and row.year == year)
        ) + (replacement,)
        saved = _atomic_write(
            workspace_root,
            RegistryState(sequences, state.records + (record,), state.state_events),
        )
        return next(
            row
            for row in saved.records
            if row.correspondence_id == record.correspondence_id
        )


def get_correspondence(
    workspace_root: Path, correspondence_id: str
) -> CorrespondenceRecord:
    correspondence_id = _id(correspondence_id)
    state = read_registry(workspace_root)
    for row in state.records:
        if row.correspondence_id == correspondence_id:
            return row
    raise ValueError("Запис кореспонденції не знайдено")


def list_correspondence(
    workspace_root: Path, direction: str = ""
) -> Tuple[CorrespondenceRecord, ...]:
    state = read_registry(workspace_root)
    if direction:
        direction = _direction(direction)
        rows = [row for row in state.records if row.direction == direction]
    else:
        rows = list(state.records)
    return tuple(sorted(
        rows,
        key=lambda row: (
            row.registration_date,
            row.sequence_number,
            row.correspondence_id,
        ),
        reverse=True,
    ))

def allowed_status_transitions(record: CorrespondenceRecord) -> Tuple[str, ...]:
    """Return only legal forward transitions for one validated record."""
    if not isinstance(record, CorrespondenceRecord):
        raise ValueError("Некоректний запис кореспонденції")
    return tuple(ALLOWED_TRANSITIONS[record.direction].get(record.status, ()))


def transition_correspondence(
    workspace_root: Path,
    correspondence_id: str,
    to_status: str,
    *,
    action_date: str = "",
) -> CorrespondenceRecord:
    """Atomically change one state and append an immutable transition event."""
    correspondence_id = _id(correspondence_id)
    with _WRITE_LOCK:
        state = read_registry(workspace_root)
        try:
            current = next(
                row for row in state.records
                if row.correspondence_id == correspondence_id
            )
        except StopIteration as exc:
            raise ValueError("Запис кореспонденції не знайдено") from exc

        to_status = _status(current.direction, to_status)
        if to_status not in ALLOWED_TRANSITIONS[current.direction].get(
            current.status, ()
        ):
            raise ValueError(
                "Недозволений перехід стану: %s → %s"
                % (current.status, to_status)
            )

        action_date = _date(
            action_date, "Дата фактичної дії", allow_empty=True
        )
        updates = {}
        if to_status == "received":
            if current.direction != DIRECTION_INCOMING:
                raise ValueError("Лише вхідний лист можна позначити отриманим")
            action_date = action_date or current.received_date
            if not action_date:
                raise ValueError("Вкажіть фактичну дату отримання")
            updates["received_date"] = action_date
        elif to_status == "sent":
            if current.direction != DIRECTION_OUTGOING:
                raise ValueError("Лише вихідний лист можна позначити надісланим")
            action_date = action_date or current.sent_date
            if not action_date:
                raise ValueError("Вкажіть фактичну дату відправлення")
            updates["sent_date"] = action_date
        elif action_date:
            raise ValueError(
                "Дата фактичної дії дозволена лише для отримання/відправлення"
            )

        timestamp = _iso_now()
        updated = replace(
            current,
            status=to_status,
            updated_at=timestamp,
            **updates
        )
        event = CorrespondenceStateEvent(
            event_id="ce-" + uuid.uuid4().hex,
            correspondence_id=current.correspondence_id,
            direction=current.direction,
            from_status=current.status,
            to_status=to_status,
            action_date=action_date,
            changed_at=timestamp,
        )
        records = tuple(
            updated if row.correspondence_id == correspondence_id else row
            for row in state.records
        )
        saved = _atomic_write(
            workspace_root,
            RegistryState(
                state.sequences,
                records,
                state.state_events + (event,),
            ),
        )
        return next(
            row for row in saved.records
            if row.correspondence_id == correspondence_id
        )


def list_state_events(
    workspace_root: Path, correspondence_id: str
) -> Tuple[CorrespondenceStateEvent, ...]:
    """Read append-only state history for one letter."""
    correspondence_id = _id(correspondence_id)
    state = read_registry(workspace_root)
    if not any(
        row.correspondence_id == correspondence_id for row in state.records
    ):
        raise ValueError("Запис кореспонденції не знайдено")
    return tuple(
        event for event in state.state_events
        if event.correspondence_id == correspondence_id
    )

