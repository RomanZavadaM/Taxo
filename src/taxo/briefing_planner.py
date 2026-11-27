# -*- coding: utf-8 -*-
"""Safe planning core for BDR / occupational-safety briefings.

The store is paper-first. Preparing or printing material never means that a
briefing was actually conducted or signed. A conducted fact is written only by
an explicit call with a factual date and an evidence note referring to the
paper record controlled by the responsible employee.

Persistence lives under workspace/Data/BriefingPlanning and is therefore part
of the normal full workspace backup/restore. Program revisions and participant
snapshots are immutable history: later registry/template edits never rewrite
older sessions.
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
from typing import Tuple


STORE_NAME = "BriefingPlanning"
FILE_NAME = "planning.json"
FORMAT = "taxo.briefing-planning.v1"
MAX_BYTES = 8 * 1024 * 1024
MAX_TEXT = 500
MAX_PROGRAM_TEXT = 200000
MAX_EVIDENCE = 4000

MODE_PLANNED = "planned"
MODE_EVENT = "event"
MODES = (MODE_PLANNED, MODE_EVENT)

STATUS_PLANNED = "planned"
STATUS_PREPARED = "prepared"
STATUS_CONDUCTED = "conducted"
STATUSES = (STATUS_PLANNED, STATUS_PREPARED, STATUS_CONDUCTED)

_PROGRAM_ID = re.compile(r"^bp-[a-f0-9]{32}$")
_SESSION_ID = re.compile(r"^bs-[a-f0-9]{32}$")
_TEMP_FILE = re.compile(r"^\.planning\.json\.[a-f0-9]{32}\.tmp$")
_WRITE_LOCK = threading.RLock()


@dataclass(frozen=True)
class ProgramRevision:
    program_id: str
    revision: int
    direction: str
    kind: str
    title: str
    program_text: str
    source_note: str
    approved_by: str
    valid_from: str
    valid_until: str
    created_at: str


@dataclass(frozen=True)
class ParticipantSnapshot:
    employee_id: int
    name: str
    personnel_no: str
    position: str


@dataclass(frozen=True)
class BriefingSession:
    session_id: str
    mode: str
    planning_key: str
    program_id: str
    program_revision: int
    scheduled_for: str
    reason: str
    participants: Tuple[ParticipantSnapshot, ...]
    status: str
    prepared_at: str
    conducted_on: str
    evidence_note: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class PlanningState:
    programs: Tuple[ProgramRevision, ...]
    sessions: Tuple[BriefingSession, ...]


def planning_root(workspace_root: Path) -> Path:
    return Path(workspace_root) / "Data" / STORE_NAME


def planning_path(workspace_root: Path) -> Path:
    return planning_root(workspace_root) / FILE_NAME


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _text(value, label, *, allow_empty=False, limit=MAX_TEXT) -> str:
    clean = str(value or "").strip()
    if not clean and not allow_empty:
        raise ValueError("%s не може бути порожнім" % label)
    if len(clean) > int(limit):
        raise ValueError("%s задовгий" % label)
    if any(ord(ch) < 32 and ch not in "\t\n\r" for ch in clean):
        raise ValueError("%s містить службові символи" % label)
    return clean


def _date(value, label, *, allow_empty=False) -> str:
    clean = str(value or "").strip()
    if allow_empty and not clean:
        return ""
    try:
        parsed = date.fromisoformat(clean)
    except ValueError as exc:
        raise ValueError("%s має бути датою YYYY-MM-DD" % label) from exc
    return parsed.isoformat()


def _timestamp(value, label, *, allow_empty=False) -> str:
    clean = str(value or "").strip()
    if allow_empty and not clean:
        return ""
    try:
        parsed = datetime.fromisoformat(clean.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("%s має бути ISO timestamp" % label) from exc
    if parsed.tzinfo is None:
        raise ValueError("%s має містити timezone" % label)
    return parsed.isoformat(timespec="seconds")


def _program_id(value) -> str:
    clean = str(value or "").strip()
    if _PROGRAM_ID.fullmatch(clean) is None:
        raise ValueError("Некоректний ID програми інструктажу")
    return clean


def _session_id(value) -> str:
    clean = str(value or "").strip()
    if _SESSION_ID.fullmatch(clean) is None:
        raise ValueError("Некоректний ID запланованого інструктажу")
    return clean


def _revision(value) -> int:
    if type(value) is not int or value < 1:
        raise ValueError("Некоректна редакція програми")
    return value


def _participant(value) -> ParticipantSnapshot:
    if not isinstance(value, dict):
        raise ValueError("Некоректний знімок працівника")
    required = {"employee_id", "name", "personnel_no", "position"}
    if set(value) != required:
        raise ValueError("Неповний знімок працівника")
    employee_id = value.get("employee_id")
    if type(employee_id) is not int or employee_id < 1:
        raise ValueError("Некоректний Taxo ID працівника")
    return ParticipantSnapshot(
        employee_id=employee_id,
        name=_text(value.get("name"), "ПІБ працівника", limit=250),
        personnel_no=_text(
            value.get("personnel_no"), "Табельний номер",
            allow_empty=True, limit=100,
        ),
        position=_text(
            value.get("position"), "Посада",
            allow_empty=True, limit=250,
        ),
    )


def participant_snapshot(value) -> ParticipantSnapshot:
    """Normalize one registry choice into an immutable session snapshot."""
    if isinstance(value, ParticipantSnapshot):
        return value
    if not isinstance(value, dict):
        raise ValueError("Працівник має бути переданий структурованим записом")
    raw_id = value.get("employee_id", value.get("id"))
    raw_name = value.get("name") or value.get("label") or ""
    return _participant({
        "employee_id": raw_id,
        "name": raw_name,
        "personnel_no": value.get("personnel_no", ""),
        "position": value.get("position", ""),
    })


def _participants(values) -> Tuple[ParticipantSnapshot, ...]:
    if isinstance(values, (str, bytes)) or values is None:
        raise ValueError("Потрібен список працівників")
    result = tuple(participant_snapshot(value) for value in values)
    if not result:
        raise ValueError("Виберіть хоча б одного працівника")
    ids = [row.employee_id for row in result]
    if len(ids) != len(set(ids)):
        raise ValueError("Один працівник не може бути доданий двічі")
    return result


def _program(entry) -> ProgramRevision:
    required = {
        "program_id", "revision", "direction", "kind", "title",
        "program_text", "source_note", "approved_by",
        "valid_from", "valid_until", "created_at",
    }
    if not isinstance(entry, dict) or set(entry) != required:
        raise ValueError("Некоректний запис редакції програми")
    valid_from = _date(entry.get("valid_from"), "valid_from")
    valid_until = _date(
        entry.get("valid_until"), "valid_until", allow_empty=True
    )
    if valid_until and valid_until < valid_from:
        raise ValueError("Дата завершення чинності програми раніше початку")
    return ProgramRevision(
        program_id=_program_id(entry.get("program_id")),
        revision=_revision(entry.get("revision")),
        direction=_text(entry.get("direction"), "Напрям", limit=100),
        kind=_text(entry.get("kind"), "Вид інструктажу", limit=150),
        title=_text(entry.get("title"), "Назва програми"),
        program_text=_text(
            entry.get("program_text"), "Текст програми",
            limit=MAX_PROGRAM_TEXT,
        ),
        source_note=_text(
            entry.get("source_note"), "Підстава",
            allow_empty=True, limit=4000,
        ),
        approved_by=_text(
            entry.get("approved_by"), "Затвердив",
            allow_empty=True, limit=250,
        ),
        valid_from=valid_from,
        valid_until=valid_until,
        created_at=_timestamp(entry.get("created_at"), "created_at"),
    )


def _session(entry) -> BriefingSession:
    required = {
        "session_id", "mode", "planning_key", "program_id",
        "program_revision", "scheduled_for", "reason", "participants",
        "status", "prepared_at", "conducted_on", "evidence_note",
        "created_at", "updated_at",
    }
    if not isinstance(entry, dict) or set(entry) != required:
        raise ValueError("Некоректний запис інструктажу")
    mode = str(entry.get("mode") or "")
    if mode not in MODES:
        raise ValueError("Некоректний режим інструктажу")
    status = str(entry.get("status") or "")
    if status not in STATUSES:
        raise ValueError("Некоректний стан інструктажу")
    planning_key = _text(
        entry.get("planning_key"), "Ключ плану",
        allow_empty=(mode == MODE_EVENT), limit=250,
    )
    if mode == MODE_EVENT and planning_key:
        raise ValueError("Подієвий інструктаж не має ключа плану")
    reason = _text(
        entry.get("reason"), "Підстава події",
        allow_empty=(mode == MODE_PLANNED), limit=4000,
    )
    if mode == MODE_EVENT and not reason:
        raise ValueError("Для подієвого інструктажу потрібна підстава")
    prepared_at = _timestamp(
        entry.get("prepared_at"), "prepared_at", allow_empty=True
    )
    conducted_on = _date(
        entry.get("conducted_on"), "conducted_on", allow_empty=True
    )
    evidence_note = _text(
        entry.get("evidence_note"), "Відомості паперового запису",
        allow_empty=True, limit=MAX_EVIDENCE,
    )
    if status == STATUS_PLANNED and (prepared_at or conducted_on or evidence_note):
        raise ValueError("Плановий стан не може містити факт підготовки/проведення")
    if status == STATUS_PREPARED and not prepared_at:
        raise ValueError("Підготовлений інструктаж не має часу підготовки")
    if status == STATUS_PREPARED and (conducted_on or evidence_note):
        raise ValueError("Підготовлений інструктаж не може містити факт проведення")
    if status == STATUS_CONDUCTED and (not conducted_on or not evidence_note):
        raise ValueError(
            "Факт проведення потребує дати і посилання на паперовий запис"
        )
    raw_people = entry.get("participants")
    if not isinstance(raw_people, list):
        raise ValueError("Некоректний список працівників")
    return BriefingSession(
        session_id=_session_id(entry.get("session_id")),
        mode=mode,
        planning_key=planning_key,
        program_id=_program_id(entry.get("program_id")),
        program_revision=_revision(entry.get("program_revision")),
        scheduled_for=_date(entry.get("scheduled_for"), "scheduled_for"),
        reason=reason,
        participants=_participants(raw_people),
        status=status,
        prepared_at=prepared_at,
        conducted_on=conducted_on,
        evidence_note=evidence_note,
        created_at=_timestamp(entry.get("created_at"), "created_at"),
        updated_at=_timestamp(entry.get("updated_at"), "updated_at"),
    )


def _validate_state(state: PlanningState) -> PlanningState:
    programs = tuple(state.programs)
    sessions = tuple(state.sessions)
    program_keys = set()
    revisions_by_program = {}
    for program in programs:
        key = (program.program_id, program.revision)
        if key in program_keys:
            raise ValueError("Дубльована редакція програми")
        program_keys.add(key)
        revisions_by_program.setdefault(program.program_id, []).append(
            program.revision
        )
    for program_id, revisions in revisions_by_program.items():
        expected = list(range(1, max(revisions) + 1))
        if sorted(revisions) != expected:
            raise ValueError(
                "Редакції програми %s мають іти послідовно" % program_id
            )

    session_ids = set()
    planning_keys = set()
    for session in sessions:
        if session.session_id in session_ids:
            raise ValueError("Дубльований ID інструктажу")
        session_ids.add(session.session_id)
        if (session.program_id, session.program_revision) not in program_keys:
            raise ValueError("Інструктаж посилається на відсутню редакцію програми")
        if session.mode == MODE_PLANNED:
            key = session.planning_key.casefold()
            if key in planning_keys:
                raise ValueError("План уже містить захід із таким ключем")
            planning_keys.add(key)
        ids = [person.employee_id for person in session.participants]
        if len(ids) != len(set(ids)):
            raise ValueError("Дубльований працівник у знімку інструктажу")

    return PlanningState(
        programs=tuple(sorted(
            programs,
            key=lambda row: (row.program_id, row.revision),
        )),
        sessions=tuple(sorted(
            sessions,
            key=lambda row: (row.scheduled_for, row.created_at, row.session_id),
        )),
    )


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
        raise ValueError("Некоректний файл планування інструктажів")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("Файл планування інструктажів завеликий")
    try:
        return json.loads(
            path.read_text("utf-8"),
            object_pairs_hook=_json_object_no_duplicates,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Не вдалося прочитати планування інструктажів") from exc


def read_state(workspace_root: Path) -> PlanningState:
    root = planning_root(workspace_root)
    if not root.exists():
        return PlanningState((), ())
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Некоректне сховище планування інструктажів")
    unexpected = [
        child.name for child in root.iterdir()
        if child.name != FILE_NAME and _TEMP_FILE.fullmatch(child.name) is None
    ]
    if unexpected:
        raise ValueError(
            "Сховище планування містить невідомий об'єкт: %s"
            % ", ".join(sorted(unexpected))
        )
    data = _read_json(planning_path(workspace_root))
    if data is None:
        return PlanningState((), ())
    if (
        not isinstance(data, dict)
        or set(data) != {"format", "programs", "sessions"}
        or data.get("format") != FORMAT
        or not isinstance(data.get("programs"), list)
        or not isinstance(data.get("sessions"), list)
    ):
        raise ValueError("Несумісний формат планування інструктажів")
    return _validate_state(PlanningState(
        tuple(_program(row) for row in data["programs"]),
        tuple(_session(row) for row in data["sessions"]),
    ))


def _program_dict(row: ProgramRevision):
    return {
        "program_id": row.program_id,
        "revision": row.revision,
        "direction": row.direction,
        "kind": row.kind,
        "title": row.title,
        "program_text": row.program_text,
        "source_note": row.source_note,
        "approved_by": row.approved_by,
        "valid_from": row.valid_from,
        "valid_until": row.valid_until,
        "created_at": row.created_at,
    }


def _participant_dict(row: ParticipantSnapshot):
    return {
        "employee_id": row.employee_id,
        "name": row.name,
        "personnel_no": row.personnel_no,
        "position": row.position,
    }


def _session_dict(row: BriefingSession):
    return {
        "session_id": row.session_id,
        "mode": row.mode,
        "planning_key": row.planning_key,
        "program_id": row.program_id,
        "program_revision": row.program_revision,
        "scheduled_for": row.scheduled_for,
        "reason": row.reason,
        "participants": [_participant_dict(person) for person in row.participants],
        "status": row.status,
        "prepared_at": row.prepared_at,
        "conducted_on": row.conducted_on,
        "evidence_note": row.evidence_note,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def _payload(state: PlanningState) -> bytes:
    checked = _validate_state(state)
    data = {
        "format": FORMAT,
        "programs": [_program_dict(row) for row in checked.programs],
        "sessions": [_session_dict(row) for row in checked.sessions],
    }
    raw = (
        json.dumps(
            data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ) + "\n"
    ).encode("utf-8")
    if len(raw) > MAX_BYTES:
        raise ValueError("Планування інструктажів перевищує допустимий розмір")
    return raw


def _write_state(workspace_root: Path, state: PlanningState) -> PlanningState:
    checked = _validate_state(state)
    root = planning_root(workspace_root)
    data_dir = root.parent
    if data_dir.exists() and (data_dir.is_symlink() or not data_dir.is_dir()):
        raise ValueError("Некоректна папка Data у робочому сховищі")
    data_dir.mkdir(parents=True, exist_ok=True)
    if root.exists() and (root.is_symlink() or not root.is_dir()):
        raise ValueError("Некоректне сховище планування інструктажів")
    root.mkdir(parents=False, exist_ok=True)
    target = root / FILE_NAME
    temp = root / (".planning.json.%s.tmp" % uuid.uuid4().hex)
    payload = _payload(checked)
    try:
        with temp.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temp), str(target))
    finally:
        try:
            if temp.exists():
                temp.unlink()
        except OSError:
            pass
    return read_state(workspace_root)


def list_programs(workspace_root: Path, program_id=None) -> Tuple[ProgramRevision, ...]:
    programs = read_state(workspace_root).programs
    if program_id is None:
        return programs
    program_id = _program_id(program_id)
    return tuple(row for row in programs if row.program_id == program_id)


def get_program_revision(
    workspace_root: Path, program_id: str, revision: int
) -> ProgramRevision:
    program_id = _program_id(program_id)
    revision = _revision(revision)
    for row in read_state(workspace_root).programs:
        if row.program_id == program_id and row.revision == revision:
            return row
    raise ValueError("Редакцію програми не знайдено")


def latest_program(workspace_root: Path, program_id: str) -> ProgramRevision:
    rows = list_programs(workspace_root, program_id)
    if not rows:
        raise ValueError("Програму не знайдено")
    return max(rows, key=lambda row: row.revision)


def create_program(
    workspace_root: Path, *, direction: str, kind: str, title: str,
    program_text: str, valid_from: str, valid_until: str = "",
    source_note: str = "", approved_by: str = "",
) -> ProgramRevision:
    timestamp = _iso_now()
    row = _program({
        "program_id": "bp-" + uuid.uuid4().hex,
        "revision": 1,
        "direction": direction,
        "kind": kind,
        "title": title,
        "program_text": program_text,
        "source_note": source_note,
        "approved_by": approved_by,
        "valid_from": valid_from,
        "valid_until": valid_until,
        "created_at": timestamp,
    })
    with _WRITE_LOCK:
        state = read_state(workspace_root)
        saved = _write_state(
            workspace_root,
            PlanningState(state.programs + (row,), state.sessions),
        )
        return next(
            item for item in saved.programs
            if item.program_id == row.program_id and item.revision == 1
        )


def revise_program(
    workspace_root: Path, program_id: str, *, direction=None, kind=None,
    title=None, program_text=None, valid_from=None, valid_until=None,
    source_note=None, approved_by=None,
) -> ProgramRevision:
    program_id = _program_id(program_id)
    with _WRITE_LOCK:
        state = read_state(workspace_root)
        current_rows = [
            row for row in state.programs if row.program_id == program_id
        ]
        if not current_rows:
            raise ValueError("Програму не знайдено")
        current = max(current_rows, key=lambda row: row.revision)
        row = _program({
            "program_id": current.program_id,
            "revision": current.revision + 1,
            "direction": current.direction if direction is None else direction,
            "kind": current.kind if kind is None else kind,
            "title": current.title if title is None else title,
            "program_text": (
                current.program_text if program_text is None else program_text
            ),
            "source_note": (
                current.source_note if source_note is None else source_note
            ),
            "approved_by": (
                current.approved_by if approved_by is None else approved_by
            ),
            "valid_from": (
                current.valid_from if valid_from is None else valid_from
            ),
            "valid_until": (
                current.valid_until if valid_until is None else valid_until
            ),
            "created_at": _iso_now(),
        })
        saved = _write_state(
            workspace_root,
            PlanningState(state.programs + (row,), state.sessions),
        )
        return next(
            item for item in saved.programs
            if item.program_id == row.program_id
            and item.revision == row.revision
        )


def list_sessions(
    workspace_root: Path, *, mode=None
) -> Tuple[BriefingSession, ...]:
    sessions = read_state(workspace_root).sessions
    if mode is None:
        return sessions
    if mode not in MODES:
        raise ValueError("Некоректний режим інструктажу")
    return tuple(row for row in sessions if row.mode == mode)


def get_session(workspace_root: Path, session_id: str) -> BriefingSession:
    session_id = _session_id(session_id)
    for row in read_state(workspace_root).sessions:
        if row.session_id == session_id:
            return row
    raise ValueError("Інструктаж не знайдено")


def _create_session(
    workspace_root: Path, *, mode: str, planning_key: str,
    program_id: str, program_revision: int, scheduled_for: str,
    reason: str, participants,
) -> BriefingSession:
    program_id = _program_id(program_id)
    program_revision = _revision(program_revision)
    timestamp = _iso_now()
    row = _session({
        "session_id": "bs-" + uuid.uuid4().hex,
        "mode": mode,
        "planning_key": planning_key,
        "program_id": program_id,
        "program_revision": program_revision,
        "scheduled_for": scheduled_for,
        "reason": reason,
        "participants": [
            _participant_dict(person) for person in _participants(participants)
        ],
        "status": STATUS_PLANNED,
        "prepared_at": "",
        "conducted_on": "",
        "evidence_note": "",
        "created_at": timestamp,
        "updated_at": timestamp,
    })
    with _WRITE_LOCK:
        state = read_state(workspace_root)
        if (program_id, program_revision) not in {
            (program.program_id, program.revision)
            for program in state.programs
        }:
            raise ValueError("Редакцію програми не знайдено")
        saved = _write_state(
            workspace_root,
            PlanningState(state.programs, state.sessions + (row,)),
        )
        return next(
            item for item in saved.sessions
            if item.session_id == row.session_id
        )


def create_planned_session(
    workspace_root: Path, *, planning_key: str, program_id: str,
    program_revision: int, scheduled_for: str, participants,
) -> BriefingSession:
    return _create_session(
        workspace_root,
        mode=MODE_PLANNED,
        planning_key=planning_key,
        program_id=program_id,
        program_revision=program_revision,
        scheduled_for=scheduled_for,
        reason="",
        participants=participants,
    )


def create_event_session(
    workspace_root: Path, *, program_id: str, program_revision: int,
    scheduled_for: str, reason: str, participants,
) -> BriefingSession:
    return _create_session(
        workspace_root,
        mode=MODE_EVENT,
        planning_key="",
        program_id=program_id,
        program_revision=program_revision,
        scheduled_for=scheduled_for,
        reason=reason,
        participants=participants,
    )


def _replace_session(
    workspace_root: Path, updated: BriefingSession
) -> BriefingSession:
    state = read_state(workspace_root)
    found = False
    rows = []
    for row in state.sessions:
        if row.session_id == updated.session_id:
            rows.append(updated)
            found = True
        else:
            rows.append(row)
    if not found:
        raise ValueError("Інструктаж не знайдено")
    saved = _write_state(
        workspace_root,
        PlanningState(state.programs, tuple(rows)),
    )
    return next(
        row for row in saved.sessions if row.session_id == updated.session_id
    )


def mark_prepared(workspace_root: Path, session_id: str) -> BriefingSession:
    session_id = _session_id(session_id)
    with _WRITE_LOCK:
        current = get_session(workspace_root, session_id)
        if current.status == STATUS_CONDUCTED:
            raise ValueError("Проведений інструктаж не повертається у підготовку")
        if current.status == STATUS_PREPARED:
            return current
        updated = replace(
            current,
            status=STATUS_PREPARED,
            prepared_at=_iso_now(),
            updated_at=_iso_now(),
        )
        return _replace_session(workspace_root, updated)


def mark_conducted(
    workspace_root: Path, session_id: str, *,
    conducted_on: str, evidence_note: str,
) -> BriefingSession:
    session_id = _session_id(session_id)
    factual_day = _date(conducted_on, "Дата проведення")
    evidence = _text(
        evidence_note, "Відомості паперового запису", limit=MAX_EVIDENCE
    )
    with _WRITE_LOCK:
        current = get_session(workspace_root, session_id)
        if current.status == STATUS_CONDUCTED:
            if (
                current.conducted_on == factual_day
                and current.evidence_note == evidence
            ):
                return current
            raise ValueError(
                "Факт проведення вже зафіксовано; історію не переписувати"
            )
        updated = replace(
            current,
            status=STATUS_CONDUCTED,
            conducted_on=factual_day,
            evidence_note=evidence,
            updated_at=_iso_now(),
        )
        return _replace_session(workspace_root, updated)


def status_at(session: BriefingSession, as_of=None) -> str:
    """Return display status without writing derived overdue state to history."""
    if not isinstance(session, BriefingSession):
        raise TypeError("Потрібен запис інструктажу")
    if session.status == STATUS_CONDUCTED:
        return STATUS_CONDUCTED
    if as_of is None:
        current = date.today()
    elif isinstance(as_of, date):
        current = as_of
    else:
        current = date.fromisoformat(_date(as_of, "Контрольна дата"))
    planned = date.fromisoformat(session.scheduled_for)
    if planned < current:
        return "overdue"
    return session.status


def program_for_session(
    workspace_root: Path, session: BriefingSession
) -> ProgramRevision:
    return get_program_revision(
        workspace_root, session.program_id, session.program_revision
    )
