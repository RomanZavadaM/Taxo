# -*- coding: utf-8 -*-
"""Prepared-output bridge for the 10.25 briefing planning line.

The r1/r2 planning store stays unchanged. r3 links one planning session to the
exact immutable DOCX stored in Data/PaperDocuments through a separate
Data/BriefingPreparedOutputs registry. Preparing a document may move a session
to "prepared"; it never records "conducted" or a signature.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

import briefing_planner as planner
import briefing_quarter_view as quarter_view
from briefing_preparation import prepare_list
import paper_document_store as document_store
import safety_instruction_document_service as instruction_documents


STORE_NAME = "BriefingPreparedOutputs"
FILE_NAME = "index.json"
FORMAT = "taxo.briefing-prepared-outputs.v1"
MAX_BYTES = 2 * 1024 * 1024

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_DOCUMENT_ID = re.compile(r"^[0-9a-f]{32}$")
_TEMP_FILE = re.compile(r"^\.index\.json\.[0-9a-f]{32}\.tmp$")
_WRITE_LOCK = threading.RLock()


@dataclass(frozen=True)
class PreparedOutputLink:
    session_id: str
    document_id: str
    filename: str
    content_sha256: str
    created_at: str


def output_root(workspace_root: Path) -> Path:
    return Path(workspace_root) / "Data" / STORE_NAME


def output_path(workspace_root: Path) -> Path:
    return output_root(workspace_root) / FILE_NAME


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _timestamp(value: str) -> str:
    clean = str(value or "").strip()
    try:
        parsed = datetime.fromisoformat(clean.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Некоректний час prepared output") from exc
    if parsed.tzinfo is None:
        raise ValueError("Час prepared output має містити timezone")
    return parsed.isoformat(timespec="seconds")


def _link(value) -> PreparedOutputLink:
    required = {
        "session_id", "document_id", "filename",
        "content_sha256", "created_at",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("Некоректний запис prepared output")
    session_id = str(value.get("session_id") or "").strip()
    document_id = str(value.get("document_id") or "").strip()
    filename = str(value.get("filename") or "").strip()
    digest = str(value.get("content_sha256") or "").strip().lower()
    if not session_id.startswith("bs-"):
        raise ValueError("Некоректний session ID prepared output")
    if _DOCUMENT_ID.fullmatch(document_id) is None:
        raise ValueError("Некоректний document ID prepared output")
    if (
        not filename
        or Path(filename).name != filename
        or not filename.lower().endswith(".docx")
    ):
        raise ValueError("Некоректне ім'я prepared DOCX")
    if _SHA256.fullmatch(digest) is None:
        raise ValueError("Некоректний SHA-256 prepared DOCX")
    return PreparedOutputLink(
        session_id=session_id,
        document_id=document_id,
        filename=filename,
        content_sha256=digest,
        created_at=_timestamp(value.get("created_at")),
    )


def _link_dict(row: PreparedOutputLink):
    return {
        "session_id": row.session_id,
        "document_id": row.document_id,
        "filename": row.filename,
        "content_sha256": row.content_sha256,
        "created_at": row.created_at,
    }


def _json_object_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON prepared outputs містить дубльований ключ")
        result[key] = value
    return result


def _validate_links(values) -> Tuple[PreparedOutputLink, ...]:
    rows = tuple(values)
    sessions = set()
    documents = set()
    for row in rows:
        if row.session_id in sessions:
            raise ValueError("Session має більше одного prepared output")
        if row.document_id in documents:
            raise ValueError("Prepared DOCX прив'язаний до двох sessions")
        sessions.add(row.session_id)
        documents.add(row.document_id)
    return tuple(sorted(rows, key=lambda row: (row.created_at, row.session_id)))


def read_links(workspace_root: Path) -> Tuple[PreparedOutputLink, ...]:
    root = output_root(workspace_root)
    if not root.exists():
        return ()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Некоректне сховище prepared outputs")
    unexpected = [
        child.name for child in root.iterdir()
        if child.name != FILE_NAME and _TEMP_FILE.fullmatch(child.name) is None
    ]
    if unexpected:
        raise ValueError(
            "Prepared outputs містить невідомий об'єкт: %s"
            % ", ".join(sorted(unexpected))
        )
    path = output_path(workspace_root)
    if not path.exists():
        return ()
    if path.is_symlink() or not path.is_file():
        raise ValueError("Некоректний index prepared outputs")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("Prepared outputs index завеликий")
    try:
        data = json.loads(
            path.read_text("utf-8"),
            object_pairs_hook=_json_object_no_duplicates,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Не вдалося прочитати prepared outputs") from exc
    if (
        not isinstance(data, dict)
        or set(data) != {"format", "links"}
        or data.get("format") != FORMAT
        or not isinstance(data.get("links"), list)
    ):
        raise ValueError("Несумісний формат prepared outputs")
    return _validate_links(_link(row) for row in data["links"])


def _write_links(
    workspace_root: Path, links: Tuple[PreparedOutputLink, ...]
) -> Tuple[PreparedOutputLink, ...]:
    rows = _validate_links(links)
    root = output_root(workspace_root)
    data_dir = root.parent
    if data_dir.exists() and (data_dir.is_symlink() or not data_dir.is_dir()):
        raise ValueError("Некоректна папка Data у робочому сховищі")
    data_dir.mkdir(parents=True, exist_ok=True)
    if root.exists() and (root.is_symlink() or not root.is_dir()):
        raise ValueError("Некоректне сховище prepared outputs")
    root.mkdir(parents=False, exist_ok=True)

    raw = (
        json.dumps(
            {
                "format": FORMAT,
                "links": [_link_dict(row) for row in rows],
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ) + "\n"
    ).encode("utf-8")
    if len(raw) > MAX_BYTES:
        raise ValueError("Prepared outputs index завеликий")

    temp = root / (".index.json.%s.tmp" % os.urandom(16).hex())
    target = root / FILE_NAME
    try:
        with temp.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temp), str(target))
    finally:
        try:
            if temp.exists():
                temp.unlink()
        except OSError:
            pass
    return read_links(workspace_root)


def get_link(workspace_root: Path, session_id: str):
    clean = str(session_id or "").strip()
    for row in read_links(workspace_root):
        if row.session_id == clean:
            return row
    return None


def resolve_output(workspace_root: Path, link: PreparedOutputLink) -> Path:
    if not isinstance(link, PreparedOutputLink):
        raise TypeError("Потрібне посилання на prepared output")
    records = document_store.list_documents(workspace_root)
    record = next(
        (
            row for row in records
            if row.get("id") == link.document_id
            and row.get("file") == link.filename
        ),
        None,
    )
    if record is None:
        raise ValueError("Prepared DOCX відсутній у каталозі документів")
    path = document_store.document_path(workspace_root, record)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Prepared DOCX фізично відсутній")
    if _sha256_file(path) != link.content_sha256:
        raise ValueError("Prepared DOCX змінений або пошкоджений")
    return path


def build_planning_key(
    program_id: str,
    revision: int,
    scheduled_for: str,
    participants,
) -> str:
    people = tuple(planner.participant_snapshot(value) for value in participants)
    if not people:
        raise ValueError("Виберіть хоча б одного працівника")
    ids = sorted(row.employee_id for row in people)
    return "briefing:%s:r%d:%s:%s" % (
        str(program_id).strip(),
        int(revision),
        str(scheduled_for).strip(),
        ",".join(str(value) for value in ids),
    )


def ensure_planned_session(
    workspace_root: Path,
    *,
    program_id: str,
    program_revision: int,
    scheduled_for: str,
    participants,
):
    people = tuple(sorted(
        (planner.participant_snapshot(value) for value in participants),
        key=lambda row: row.employee_id,
    ))
    key = build_planning_key(
        program_id, program_revision, scheduled_for, people
    )
    return quarter_view.ensure_planned_session(
        workspace_root,
        planning_key=key,
        program_id=program_id,
        program_revision=program_revision,
        scheduled_for=scheduled_for,
        participants=people,
    )


def _prepared_payload(workspace_root: Path, session):
    program = planner.program_for_session(workspace_root, session)
    people_records = tuple({
        "id": person.employee_id,
        "name": person.name,
        "personnel_no": person.personnel_no,
        "position": person.position,
    } for person in session.participants)
    return prepare_list(
        program.direction,
        program.kind,
        datetime.strptime(
            session.scheduled_for, "%Y-%m-%d"
        ).strftime("%d.%m.%Y"),
        program.title,
        (person.name for person in session.participants),
        session.reason,
        people_records=people_records,
        program_text=program.program_text,
        template_id="%s:r%d" % (
            program.program_id, program.revision
        ),
        source_note=program.source_note,
        approved_by=program.approved_by,
    )


def _paper_record_for_target(workspace_root: Path, target: Path):
    target = Path(target)
    matches = [
        row for row in document_store.list_documents(workspace_root)
        if row.get("file") == target.name
    ]
    if len(matches) != 1:
        raise ValueError(
            "Не вдалося однозначно знайти prepared DOCX у каталозі"
        )
    return matches[0]


def prepare_session_document(workspace_root: Path, session_id: str):
    """Prepare or recover exactly one linked DOCX for a non-conducted session."""
    with _WRITE_LOCK:
        session = planner.get_session(workspace_root, session_id)
        if session.status == planner.STATUS_CONDUCTED:
            raise ValueError(
                "Проведений інструктаж не можна повторно позначати підготовленим"
            )

        existing = get_link(workspace_root, session.session_id)
        if existing is not None:
            path = resolve_output(workspace_root, existing)
            if session.status == planner.STATUS_PLANNED:
                session = planner.mark_prepared(
                    workspace_root, session.session_id
                )
            return session, existing, path

        payload = _prepared_payload(workspace_root, session)
        target = instruction_documents.save_briefing_document(
            workspace_root, payload
        )
        record = _paper_record_for_target(workspace_root, target)
        document_id = str(record.get("id") or "").strip()
        if _DOCUMENT_ID.fullmatch(document_id) is None:
            raise ValueError("Каталог повернув некоректний ID prepared DOCX")

        link = PreparedOutputLink(
            session_id=session.session_id,
            document_id=document_id,
            filename=Path(target).name,
            content_sha256=_sha256_file(target),
            created_at=_iso_now(),
        )
        links = read_links(workspace_root)
        _write_links(workspace_root, links + (link,))
        session = planner.mark_prepared(workspace_root, session.session_id)
        return session, link, resolve_output(workspace_root, link)


def ensure_planned_and_prepare(
    workspace_root: Path,
    *,
    program_id: str,
    program_revision: int,
    scheduled_for: str,
    participants,
):
    session = ensure_planned_session(
        workspace_root,
        program_id=program_id,
        program_revision=program_revision,
        scheduled_for=scheduled_for,
        participants=participants,
    )
    return prepare_session_document(workspace_root, session.session_id)
