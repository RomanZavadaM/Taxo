# -*- coding: utf-8 -*-
"""Business-facing operations for the correspondence registry.

This service intentionally has no Tk/UI, e-mail transport, attachment copying
or document-import APPLY. It coordinates the two journals and derives simple
read-only control views from registry metadata.
"""
from __future__ import annotations

from datetime import date
from typing import Iterable, Tuple

from correspondence_registry import (
    DIRECTION_INCOMING,
    DIRECTION_OUTGOING,
    CorrespondenceRecord,
    get_correspondence,
    list_correspondence,
    next_registration_number,
    register_correspondence,
)


def register_incoming(
    workspace_root,
    *,
    registration_date,
    correspondent,
    subject,
    document_date="",
    received_date="",
    external_number="",
    summary="",
    delivery_method="",
    responsible_id="",
    due_date="",
    document_ref="",
    related_ids=(),
) -> CorrespondenceRecord:
    """Register one incoming letter; a scan/file is never mandatory."""
    return register_correspondence(
        workspace_root,
        direction=DIRECTION_INCOMING,
        registration_date=registration_date,
        correspondent=correspondent,
        subject=subject,
        document_date=document_date,
        received_date=received_date,
        external_number=external_number,
        summary=summary,
        delivery_method=delivery_method,
        responsible_id=responsible_id,
        due_date=due_date,
        status="new",
        document_ref=document_ref,
        related_ids=related_ids,
    )


def register_outgoing(
    workspace_root,
    *,
    registration_date,
    correspondent,
    subject,
    document_date="",
    sent_date="",
    external_number="",
    summary="",
    delivery_method="",
    responsible_id="",
    due_date="",
    document_ref="",
    response_to_ids=(),
    related_ids=(),
) -> CorrespondenceRecord:
    """Register one outgoing letter; registration does not imply delivery."""
    status = "sent" if sent_date else "registered"
    return register_correspondence(
        workspace_root,
        direction=DIRECTION_OUTGOING,
        registration_date=registration_date,
        correspondent=correspondent,
        subject=subject,
        document_date=document_date,
        sent_date=sent_date,
        external_number=external_number,
        summary=summary,
        delivery_method=delivery_method,
        responsible_id=responsible_id,
        due_date=due_date,
        status=status,
        document_ref=document_ref,
        response_to_ids=response_to_ids,
        related_ids=related_ids,
    )


def register_response(
    workspace_root,
    incoming_id,
    *,
    registration_date,
    subject="",
    document_date="",
    sent_date="",
    summary="",
    delivery_method="",
    responsible_id="",
    due_date="",
    document_ref="",
) -> CorrespondenceRecord:
    """Create an outgoing registered response linked to an incoming letter."""
    source = get_correspondence(workspace_root, incoming_id)
    if source.direction != DIRECTION_INCOMING:
        raise ValueError("Відповідь можна створити лише на вхідний лист")
    return register_outgoing(
        workspace_root,
        registration_date=registration_date,
        correspondent=source.correspondent,
        subject=subject or source.subject,
        document_date=document_date,
        sent_date=sent_date,
        summary=summary,
        delivery_method=delivery_method,
        responsible_id=responsible_id,
        due_date=due_date,
        document_ref=document_ref,
        response_to_ids=(source.correspondence_id,),
    )


def incoming_journal(workspace_root) -> Tuple[CorrespondenceRecord, ...]:
    return list_correspondence(workspace_root, DIRECTION_INCOMING)


def outgoing_journal(workspace_root) -> Tuple[CorrespondenceRecord, ...]:
    return list_correspondence(workspace_root, DIRECTION_OUTGOING)


def next_incoming_number(workspace_root, registration_date) -> str:
    return next_registration_number(
        workspace_root, DIRECTION_INCOMING, registration_date
    )


def next_outgoing_number(workspace_root, registration_date) -> str:
    return next_registration_number(
        workspace_root, DIRECTION_OUTGOING, registration_date
    )


def responses_for(
    workspace_root, incoming_id
) -> Tuple[CorrespondenceRecord, ...]:
    source = get_correspondence(workspace_root, incoming_id)
    if source.direction != DIRECTION_INCOMING:
        raise ValueError("Запис не є вхідним листом")
    return tuple(
        row
        for row in outgoing_journal(workspace_root)
        if source.correspondence_id in row.response_to_ids
    )


def is_overdue(record: CorrespondenceRecord, on_date=None) -> bool:
    """Compute overdue state only from an explicit due date and open status."""
    if not record.due_date:
        return False
    if record.status in {"closed", "cancelled", "sent"}:
        return False
    if on_date is None:
        current = date.today()
    elif isinstance(on_date, date):
        current = on_date
    elif isinstance(on_date, str):
        try:
            current = date.fromisoformat(on_date)
        except ValueError as exc:
            raise ValueError("Дата контролю має бути РРРР-ММ-ДД") from exc
    else:
        raise ValueError("Некоректна дата контролю")
    return date.fromisoformat(record.due_date) < current


def overdue_incoming(
    workspace_root, on_date=None
) -> Tuple[CorrespondenceRecord, ...]:
    return tuple(
        row for row in incoming_journal(workspace_root)
        if is_overdue(row, on_date)
    )
