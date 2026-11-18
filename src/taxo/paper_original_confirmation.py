# -*- coding: utf-8 -*-
"""Explicit paper-original confirmation, independent of optional scans.

An acknowledgement means only that the operator marked the paper original
as signed; it is neither a cryptographic signature nor proof of authenticity.
Events are append-only in the workspace's DocumentVault and travel with full
workspace backups. An explicit correction never erases the previous event.
"""
from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from document_vault_store import document_vault_root, list_document_vault

FILE_NAME = "paper_original_events.json"
FORMAT = "taxo.paper-original-confirmations.v1"
MAX_BYTES = 4 * 1024 * 1024
_ID = re.compile(r"^vd-[0-9a-f]{32}$")


@dataclass(frozen=True)
class PaperOriginalState:
    signed: bool
    signed_date: str
    recorded_at: str


def _path(workspace_root):
    root = document_vault_root(Path(workspace_root))
    if root.is_symlink() or (root.exists() and not root.is_dir()):
        raise ValueError("Небезпечне сховище документів")
    path = root / FILE_NAME
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError("Небезпечний журнал паперових оригіналів")
    return path


def _read(path):
    if not path.exists():
        return []
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("Журнал паперових оригіналів завеликий")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("format") != FORMAT:
        raise ValueError("Невідомий формат журналу паперових оригіналів")
    events = payload.get("events")
    if not isinstance(events, list):
        raise ValueError("Некоректний журнал паперових оригіналів")
    used = set()
    for event in events:
        if not isinstance(event, dict) or set(event) != {
            "id", "vault_id", "signed", "signed_date", "recorded_at"
        }:
            raise ValueError("Некоректний запис паперового оригіналу")
        if not isinstance(event["id"], str) or not re.fullmatch(r"[0-9a-f]{32}", event["id"]):
            raise ValueError("Некоректний ідентифікатор зміни")
        if event["id"] in used:
            raise ValueError("Повторена зміна паперового оригіналу")
        used.add(event["id"])
        if not isinstance(event["vault_id"], str) or not _ID.fullmatch(event["vault_id"]):
            raise ValueError("Некоректний документ у журналі")
        if type(event["signed"]) is not bool or not isinstance(event["signed_date"], str):
            raise ValueError("Некоректний стан підпису")
        if event["signed"]:
            try:
                date.fromisoformat(event["signed_date"])
            except ValueError as exc:
                raise ValueError("Некоректна дата підписання") from exc
        elif event["signed_date"]:
            raise ValueError("Дата підпису без підтвердження")
        if not isinstance(event["recorded_at"], str):
            raise ValueError("Некоректний час зміни")
        try:
            datetime.fromisoformat(event["recorded_at"])
        except ValueError as exc:
            raise ValueError("Некоректний час зміни") from exc
    return events


def list_paper_original_states(workspace_root):
    """Return explicit latest marks only. Absence means 'not marked'."""
    records = list_document_vault(Path(workspace_root))
    known = {record.vault_id for record in records}
    events = _read(_path(workspace_root))
    states = {}
    for event in events:
        if event["vault_id"] not in known:
            raise ValueError("Позначка посилається на відсутній документ")
        states[event["vault_id"]] = PaperOriginalState(
            event["signed"], event["signed_date"], event["recorded_at"]
        )
    return states


def set_paper_original_state(workspace_root, vault_id, signed, signed_date=""):
    """Explicitly mark or correct paper-original confirmation with history."""
    if type(signed) is not bool or not isinstance(vault_id, str) or not _ID.fullmatch(vault_id):
        raise ValueError("Некоректна дія з паперовим оригіналом")
    if signed:
        if not isinstance(signed_date, str):
            raise ValueError("Вкажіть дату підписання")
        try:
            parsed = date.fromisoformat(signed_date)
        except ValueError as exc:
            raise ValueError("Дата підписання має формат РРРР-ММ-ДД") from exc
        if parsed > date.today():
            raise ValueError("Дата підписання не може бути у майбутньому")
        signed_date = parsed.isoformat()
    else:
        signed_date = ""
    # Validate the immutable document and all existing references before writing.
    states = list_paper_original_states(workspace_root)
    if vault_id not in {r.vault_id for r in list_document_vault(Path(workspace_root))}:
        raise ValueError("Документ не знайдено у сховищі")
    previous = states.get(vault_id)
    if previous is not None and (previous.signed, previous.signed_date) == (signed, signed_date):
        return previous
    path = _path(workspace_root)
    events = _read(path)
    events.append({
        "id": uuid.uuid4().hex,
        "vault_id": vault_id,
        "signed": signed,
        "signed_date": signed_date,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    })
    data = json.dumps({"format": FORMAT, "events": events}, ensure_ascii=False, indent=2).encode("utf-8")
    if len(data) > MAX_BYTES:
        raise ValueError("Журнал паперових оригіналів завеликий")
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise ValueError("Сховище документів недоступне")
    temporary = path.parent / ("." + FILE_NAME + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temporary), str(path))
    finally:
        if temporary.exists():
            temporary.unlink()
    return PaperOriginalState(signed, signed_date, events[-1]["recorded_at"])
