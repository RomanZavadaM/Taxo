# -*- coding: utf-8 -*-
"""Human-readable briefing program lines and reusable text sources.

This module connects the 10.25 briefing workflow with the existing Taxo
TemplateLibrary / CompanyTemplates without changing either storage format.
A selected source is copied into a new immutable briefing-program revision;
later library/template edits never rewrite an existing program revision.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import safety_templates
from company_template_store import list_company_templates, load_company_template
from template_library_preview import _render, load_template_preview
from template_library_reader import default_library_root
from template_library_service import inspect_workspace_library


LINE_ANNUAL = "Планові / річний цикл"
LINE_INITIAL = "Початкові / вступні"
LINE_TARGET = "Цільові / перед роботою"
LINE_EVENT = "Позапланові / за подією"
LINE_OTHER = "Інші"
LINE_ALL = (LINE_ANNUAL, LINE_INITIAL, LINE_TARGET, LINE_EVENT, LINE_OTHER)


@dataclass(frozen=True)
class ProgramSource:
    source_id: str
    caption: str
    origin: str
    title: str
    topic: str
    program: str
    source_note: str


def program_line(direction: str, kind: str) -> str:
    """Return a display-only line; no new persisted business field is created."""
    text = ("%s %s" % (direction or "", kind or "")).casefold()
    if "позаплан" in text or "спеціаль" in text:
        return LINE_EVENT
    if "вступ" in text or "первин" in text:
        return LINE_INITIAL
    if "передрейс" in text or "цільов" in text:
        return LINE_TARGET
    if "період" in text or "повтор" in text:
        return LINE_ANNUAL
    return LINE_OTHER


def _built_in_sources(direction: str, kind: str):
    rows = []
    for item in safety_templates.templates_for(direction, kind):
        rows.append(ProgramSource(
            source_id="builtin:" + str(item["id"]),
            caption="Taxo · " + str(item["title"]),
            origin="Taxo",
            title=str(item["title"]),
            topic=str(item["topic"]),
            program=str(item["program"]),
            source_note=str(item.get("source_note") or ""),
        ))
    return rows


def _library_sources(workspace_root: Path, app_version: str):
    rows = []
    view = inspect_workspace_library(Path(workspace_root), str(app_version))
    if view.status != "AVAILABLE":
        return rows, (view.summary,)
    root = default_library_root(Path(workspace_root))
    for item in view.rows:
        if item.category_id not in ("briefings", "training-programs"):
            continue
        preview = load_template_preview(
            root,
            str(app_version),
            item.template_id,
            item.revision_id,
        )
        program = str(preview.content or "").strip()
        if not program:
            continue
        note_parts = [
            "Бібліотека шаблонів Taxo: %s, редакція %s"
            % (preview.template_id, preview.revision_id)
        ]
        if preview.source_notes:
            note_parts.append(preview.source_notes)
        rows.append(ProgramSource(
            source_id="library:%s:%s" % (
                item.template_id, item.revision_id
            ),
            caption="Бібліотека · " + preview.title,
            origin="Бібліотека",
            title=preview.title,
            topic=preview.title,
            program=program,
            source_note="; ".join(note_parts),
        ))
    return rows, ()


def _company_sources(workspace_root: Path):
    rows = []
    for summary in list_company_templates(Path(workspace_root)):
        if not summary.enabled:
            continue
        document = load_company_template(
            Path(workspace_root), summary.company_template_id
        )
        program = str(_render(document.template) or "").strip()
        if not program:
            continue
        rows.append(ProgramSource(
            source_id="company:" + summary.company_template_id,
            caption="Власний · " + document.title,
            origin="Власний",
            title=document.title,
            topic=document.title,
            program=program,
            source_note=(
                "Власний шаблон Taxo: %s, редакція %d"
                % (summary.company_template_id, document.edit_revision)
            ),
        ))
    return rows


def source_options(
    workspace_root: Path,
    app_version: str,
    direction: str,
    kind: str,
) -> Tuple[Tuple[ProgramSource, ...], Tuple[str, ...]]:
    """Return usable bases plus non-fatal library diagnostics.

    Built-in bases are always available. Installed/vendor and user-owned
    templates are added only after the existing integrity checks succeed.
    """
    rows = list(_built_in_sources(direction, kind))
    messages = []
    try:
        extra, notes = _library_sources(workspace_root, app_version)
        rows.extend(extra)
        messages.extend(note for note in notes if note)
    except Exception as exc:
        messages.append("Бібліотека шаблонів недоступна: %s" % exc)
    try:
        rows.extend(_company_sources(workspace_root))
    except Exception as exc:
        messages.append("Власні шаблони недоступні: %s" % exc)

    deduped = []
    seen = set()
    for row in rows:
        key = row.source_id
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    deduped.sort(key=lambda row: (
        {"Taxo": 0, "Бібліотека": 1, "Власний": 2}.get(row.origin, 9),
        row.caption.casefold(),
        row.source_id,
    ))
    return tuple(deduped), tuple(messages)
