# -*- coding: utf-8 -*-
"""Quarter working view over the immutable briefing-planning store.

This layer never marks a briefing as conducted. It only derives a quarter view,
filters it, resolves the exact saved program revision, and provides an
idempotent helper for explicit planned-session generation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Tuple

import briefing_planner as planner


DIRECTION_ALL = "Усі"
DIRECTIONS = (DIRECTION_ALL, "БДР", "Охорона праці")

STATUS_CAPTIONS = {
    planner.STATUS_PLANNED: "Заплановано",
    planner.STATUS_PREPARED: "Підготовлено",
    planner.STATUS_CONDUCTED: "Проведено",
    "overdue": "Прострочено",
}
MODE_CAPTIONS = {
    planner.MODE_PLANNED: "Плановий",
    planner.MODE_EVENT: "За подією",
}


@dataclass(frozen=True)
class QuarterRow:
    session_id: str
    scheduled_for: str
    direction: str
    kind: str
    title: str
    mode: str
    people_count: int
    status: str
    program_id: str
    program_revision: int


def quarter_bounds(year: int, quarter: int):
    year = int(year)
    quarter = int(quarter)
    if quarter not in (1, 2, 3, 4):
        raise ValueError("Квартал має бути від 1 до 4")
    start_month = 1 + (quarter - 1) * 3
    start = date(year, start_month, 1)
    if quarter == 4:
        next_start = date(year + 1, 1, 1)
    else:
        next_start = date(year, start_month + 3, 1)
    return start, next_start


def _direction(value: str) -> str:
    clean = str(value or DIRECTION_ALL).strip() or DIRECTION_ALL
    if clean not in DIRECTIONS:
        raise ValueError("Некоректний фільтр напряму")
    return clean


def rows_for_quarter(
    workspace_root,
    year: int,
    quarter: int,
    *,
    direction: str = DIRECTION_ALL,
    as_of=None,
) -> Tuple[QuarterRow, ...]:
    direction = _direction(direction)
    start, next_start = quarter_bounds(year, quarter)
    state = planner.read_state(workspace_root)
    programs = {
        (row.program_id, row.revision): row
        for row in state.programs
    }
    result = []
    for session in state.sessions:
        scheduled = date.fromisoformat(session.scheduled_for)
        if not (start <= scheduled < next_start):
            continue
        program = programs[(session.program_id, session.program_revision)]
        if direction != DIRECTION_ALL and program.direction != direction:
            continue
        result.append(QuarterRow(
            session_id=session.session_id,
            scheduled_for=session.scheduled_for,
            direction=program.direction,
            kind=program.kind,
            title=program.title,
            mode=session.mode,
            people_count=len(session.participants),
            status=planner.status_at(session, as_of),
            program_id=program.program_id,
            program_revision=program.revision,
        ))
    return tuple(sorted(
        result,
        key=lambda row: (
            row.scheduled_for,
            row.direction.casefold(),
            row.kind.casefold(),
            row.title.casefold(),
            row.session_id,
        ),
    ))


def get_exact_program(workspace_root, row: QuarterRow):
    if not isinstance(row, QuarterRow):
        raise TypeError("Потрібен рядок квартального плану")
    return planner.get_program_revision(
        workspace_root, row.program_id, row.program_revision
    )


def ensure_planned_session(
    workspace_root,
    *,
    planning_key: str,
    program_id: str,
    program_revision: int,
    scheduled_for: str,
    participants,
):
    """Create one explicit planned session or return its exact existing twin.

    Same planning_key with different program/date/participants is a conflict,
    never an implicit rewrite.
    """
    clean_key = str(planning_key or "").strip()
    if not clean_key:
        raise ValueError("Ключ плану не може бути порожнім")
    wanted_people = tuple(
        planner.participant_snapshot(value) for value in participants
    )
    wanted_ids = tuple(row.employee_id for row in wanted_people)
    for existing in planner.list_sessions(
        workspace_root, mode=planner.MODE_PLANNED
    ):
        if existing.planning_key.casefold() != clean_key.casefold():
            continue
        existing_ids = tuple(row.employee_id for row in existing.participants)
        if (
            existing.program_id == str(program_id).strip()
            and existing.program_revision == int(program_revision)
            and existing.scheduled_for == str(scheduled_for).strip()
            and existing_ids == wanted_ids
        ):
            return existing
        raise ValueError(
            "Ключ плану вже використано іншим заходом; "
            "існуючий запис не переписано"
        )
    return planner.create_planned_session(
        workspace_root,
        planning_key=clean_key,
        program_id=program_id,
        program_revision=program_revision,
        scheduled_for=scheduled_for,
        participants=wanted_people,
    )


def status_caption(value: str) -> str:
    return STATUS_CAPTIONS.get(str(value), str(value))


def mode_caption(value: str) -> str:
    return MODE_CAPTIONS.get(str(value), str(value))
