# -*- coding: utf-8 -*-
"""Typed, side-effect-free draft preparation for CompanyTemplates.

A draft is an in-memory rendering of one integrity-checked company-template
revision. Preparing a draft never edits TemplateLibrary/CompanyTemplates, never
writes a document record, and never creates order/briefing business facts.

Only declared {{ variable.name }} placeholders are substituted. Structured
blocks remain structured; dynamic tables receive rows from typed source facts
instead of flattening the whole template into one string.
"""
from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from company_template_store import load_company_template
from template_library_preview import render_template_text

_PLACEHOLDER = re.compile(
    r"\{\{\s*([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*)\s*\}\}"
)
_ALLOWED_TYPES = frozenset((
    "text", "date", "integer", "person_ref", "vehicle_ref", "pairs",
    "participants", "sections", "table_rows",
))
_MAX_TEXT = 750000
_MAX_COLLECTION = 5000
_MISSING_MARK = "⟦не заповнено: %s⟧"


@dataclass(frozen=True)
class DraftVariable:
    """Declared input expected by a company template."""

    name: str
    variable_type: str
    required: bool
    label: str
    description: str = ""


@dataclass(frozen=True)
class DraftFact:
    """Normalized typed fact retained with an in-memory draft."""

    name: str
    variable_type: str
    display_value: str
    snapshot: Any


@dataclass(frozen=True)
class CompanyTemplateDraft:
    """Non-persistent draft tied to an exact company-template revision."""

    company_template_id: str
    edit_revision: int
    template_sha256: str
    title: str
    template: Dict[str, Any]
    preview_text: str
    variables: Tuple[DraftVariable, ...]
    facts: Tuple[DraftFact, ...]
    warnings: Tuple[str, ...]


def _plain(value: object) -> str:
    return value if isinstance(value, str) else ""


def _variable_specs(template: Mapping[str, Any]) -> Tuple[DraftVariable, ...]:
    rows = []
    seen = set()
    for raw in template.get("variables", ()):
        if not isinstance(raw, dict):
            raise ValueError("Некоректний опис поля шаблону")
        name = raw.get("name")
        kind = raw.get("type")
        required = raw.get("required")
        if (
            not isinstance(name, str)
            or not _PLACEHOLDER.fullmatch("{{%s}}" % name)
            or kind not in _ALLOWED_TYPES
            or not isinstance(required, bool)
            or name in seen
        ):
            raise ValueError("Некоректний опис поля шаблону")
        seen.add(name)
        label = raw.get("label")
        if not isinstance(label, str) or not label.strip():
            label = name
        description = raw.get("description")
        if not isinstance(description, str):
            description = ""
        rows.append(DraftVariable(
            name=name,
            variable_type=kind,
            required=required,
            label=label.strip(),
            description=description.strip(),
        ))
    return tuple(rows)


def list_draft_variables(
    workspace_root: Path, company_template_id: str
) -> Tuple[DraftVariable, ...]:
    """Return declared variables without changing the template."""
    document = load_company_template(Path(workspace_root), company_template_id)
    return _variable_specs(document.template)


def _missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, dict)):
        return len(value) == 0
    return False


def _bounded_text(value: object, description: str) -> str:
    if not isinstance(value, str):
        raise ValueError("%s має бути текстом" % description)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    if "\x00" in value or len(value) > _MAX_TEXT:
        raise ValueError("%s має недопустимий розмір або символ" % description)
    return value


def _date_value(value: object, description: str) -> Tuple[str, str]:
    if isinstance(value, datetime):
        parsed = value.date()
    elif isinstance(value, date):
        parsed = value
    elif isinstance(value, str):
        text = value.strip()
        parsed = None
        for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
            try:
                parsed = datetime.strptime(text, fmt).date()
                break
            except ValueError:
                pass
        if parsed is None:
            raise ValueError("%s має бути датою YYYY-MM-DD або DD.MM.YYYY" % description)
    else:
        raise ValueError("%s має бути датою" % description)
    return parsed.strftime("%d.%m.%Y"), parsed.isoformat()


def _integer_value(value: object, description: str) -> Tuple[str, int]:
    if isinstance(value, bool):
        raise ValueError("%s має бути цілим числом" % description)
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str) and re.fullmatch(r"[+-]?\d+", value.strip()):
        parsed = int(value.strip())
    else:
        raise ValueError("%s має бути цілим числом" % description)
    return str(parsed), parsed


def _entity_snapshot(
    value: object, expected: str, description: str
) -> Tuple[str, Dict[str, Any]]:
    if not isinstance(value, dict):
        raise ValueError("%s має бути вибраним записом Taxo" % description)
    identity = value.get("id")
    if isinstance(identity, bool) or not isinstance(identity, int) or identity <= 0:
        raise ValueError("%s не має стабільного ID" % description)

    entity_type = _plain(value.get("entity_type")).strip()
    if expected == "person":
        if entity_type and entity_type not in ("employee", "person", "driver"):
            raise ValueError("%s посилається не на працівника" % description)
        name = _plain(value.get("name")).strip()
        if not name:
            raise ValueError("%s не має ПІБ" % description)
        snapshot = {
            "entity_type": entity_type or "employee",
            "id": identity,
            "name": name,
        }
        for key in (
            "position", "personnel_no", "rnokpp", "registry_person_id",
        ):
            item = _plain(value.get(key)).strip()
            if item:
                snapshot[key] = item
        label = _plain(value.get("label")).strip() or name
        return label, snapshot

    if entity_type and entity_type != "vehicle":
        raise ValueError("%s посилається не на транспортний засіб" % description)
    name = _plain(value.get("name")).strip()
    plate = _plain(value.get("plate")).strip()
    vin = _plain(value.get("vin")).strip()
    garage_no = _plain(value.get("garage_no")).strip()
    if not any((name, plate, vin, garage_no)):
        raise ValueError("%s не має реквізитів транспортного засобу" % description)
    snapshot = {
        "entity_type": "vehicle",
        "id": identity,
        "name": name,
        "plate": plate,
        "vin": vin,
        "garage_no": garage_no,
    }
    label = _plain(value.get("label")).strip()
    if not label:
        label = " · ".join(part for part in (plate, name) if part)
        if not label:
            label = vin or garage_no
    return label, snapshot


def _collection(value: object, description: str) -> Sequence[Any]:
    if not isinstance(value, (list, tuple)):
        raise ValueError("%s має бути списком" % description)
    if len(value) > _MAX_COLLECTION:
        raise ValueError("%s містить забагато записів" % description)
    return value


def _scalar_cell(value: object, description: str) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Так" if value else "Ні"
    if isinstance(value, (date, datetime)):
        return _date_value(value, description)[0]
    if isinstance(value, (int, float)):
        return str(value)
    return _bounded_text(value, description)


def _normalize_fact(spec: DraftVariable, raw: object):
    description = "Поле «%s»" % spec.label
    kind = spec.variable_type
    if kind == "text":
        text = _bounded_text(raw, description)
        return text, text, None
    if kind == "date":
        display, snapshot = _date_value(raw, description)
        return display, snapshot, None
    if kind == "integer":
        display, snapshot = _integer_value(raw, description)
        return display, snapshot, None
    if kind == "person_ref":
        display, snapshot = _entity_snapshot(raw, "person", description)
        return display, snapshot, None
    if kind == "vehicle_ref":
        display, snapshot = _entity_snapshot(raw, "vehicle", description)
        return display, snapshot, None

    items = _collection(raw, description)
    if kind == "participants":
        snapshots, labels = [], []
        for item in items:
            label, snapshot = _entity_snapshot(item, "person", description)
            labels.append(label)
            snapshots.append(snapshot)
        rows = [[label] for label in labels]
        return "\n".join(labels), snapshots, rows

    if kind == "pairs":
        snapshots, labels, rows = [], [], []
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("%s містить некоректну пару" % description)
            person = item.get("person", item.get("driver", item.get("employee")))
            vehicle = item.get("vehicle")
            person_label, person_snapshot = _entity_snapshot(
                person, "person", description
            )
            vehicle_label, vehicle_snapshot = _entity_snapshot(
                vehicle, "vehicle", description
            )
            labels.append("%s — %s" % (person_label, vehicle_label))
            rows.append([person_label, vehicle_label])
            snapshots.append({
                "person": person_snapshot,
                "vehicle": vehicle_snapshot,
            })
        return "\n".join(labels), snapshots, rows

    if kind == "sections":
        snapshots, lines, rows = [], [], []
        for item in items:
            if isinstance(item, str):
                text = _bounded_text(item, description)
                snapshot = {"title": text, "text": ""}
            elif isinstance(item, dict):
                title = _bounded_text(item.get("title", ""), description).strip()
                text = _bounded_text(item.get("text", ""), description)
                if not title and not text:
                    raise ValueError("%s містить порожній розділ" % description)
                snapshot = {"title": title, "text": text}
            else:
                raise ValueError("%s містить некоректний розділ" % description)
            display = snapshot["title"]
            if snapshot["text"]:
                display = (display + ": " if display else "") + snapshot["text"]
            lines.append(display)
            rows.append([snapshot["title"], snapshot["text"]])
            snapshots.append(snapshot)
        return "\n".join(lines), snapshots, rows

    if kind == "table_rows":
        snapshots = []
        width = None
        for row in items:
            if not isinstance(row, (list, tuple)):
                raise ValueError("%s має містити рядки таблиці" % description)
            if width is None:
                width = len(row)
            elif len(row) != width:
                raise ValueError("%s має рядки різної ширини" % description)
            snapshots.append([
                _scalar_cell(cell, description) for cell in row
            ])
        display = "\n".join(" | ".join(row) for row in snapshots)
        return display, snapshots, snapshots

    raise ValueError("Непідтримуваний тип поля: " + kind)


def _normalize_facts(
    variables: Tuple[DraftVariable, ...], facts: Mapping[str, object]
):
    if not isinstance(facts, Mapping):
        raise ValueError("Некоректний набір даних для чернетки")
    specs = {item.name: item for item in variables}
    unknown = sorted(set(facts) - set(specs))
    if unknown:
        raise ValueError("Невідомі поля чернетки: " + ", ".join(unknown))

    missing_required = [
        item.label for item in variables
        if item.required and (item.name not in facts or _missing(facts[item.name]))
    ]
    if missing_required:
        raise ValueError(
            "Не заповнено обов'язкові поля: " + ", ".join(missing_required)
        )

    normalized = {}
    facts_out = []
    for item in variables:
        raw = facts.get(item.name)
        if _missing(raw):
            continue
        display, snapshot, rows = _normalize_fact(item, raw)
        normalized[item.name] = {
            "display": display,
            "snapshot": snapshot,
            "rows": rows,
            "type": item.variable_type,
        }
        facts_out.append(DraftFact(
            name=item.name,
            variable_type=item.variable_type,
            display_value=display,
            snapshot=copy.deepcopy(snapshot),
        ))
    return normalized, tuple(facts_out)


def _substitute(
    value: object,
    specs: Mapping[str, DraftVariable],
    normalized: Mapping[str, Dict[str, Any]],
    warnings: List[str],
) -> object:
    if not isinstance(value, str) or "{{" not in value:
        return value

    def replace(match):
        name = match.group(1)
        spec = specs.get(name)
        if spec is None:
            raise ValueError(
                "Шаблон містить неоголошене поле: " + name
            )
        fact = normalized.get(name)
        if fact is not None:
            return fact["display"]
        marker = _MISSING_MARK % spec.label
        warning = "Не заповнено необов'язкове поле: " + spec.label
        if warning not in warnings:
            warnings.append(warning)
        return marker

    result = _PLACEHOLDER.sub(replace, value)
    if "{{" in result or "}}" in result:
        raise ValueError("Шаблон містить некоректний placeholder")
    return result


def _render_blocks(
    blocks: object,
    specs: Mapping[str, DraftVariable],
    normalized: Mapping[str, Dict[str, Any]],
    warnings: List[str],
) -> None:
    if not isinstance(blocks, list):
        raise ValueError("Некоректна структура блоків чернетки")
    for block in blocks:
        if not isinstance(block, dict):
            raise ValueError("Некоректний блок чернетки")
        for key in ("text", "notes"):
            if key in block:
                block[key] = _substitute(
                    block[key], specs, normalized, warnings
                )
        for key in ("items", "columns"):
            if key in block and isinstance(block[key], list):
                block[key] = [
                    _substitute(item, specs, normalized, warnings)
                    for item in block[key]
                ]
        if "rows" in block and isinstance(block["rows"], list):
            block["rows"] = [
                [
                    _substitute(cell, specs, normalized, warnings)
                    for cell in row
                ]
                if isinstance(row, list) else row
                for row in block["rows"]
            ]

        if block.get("type") == "dynamic_table":
            source = block.get("data_source")
            if not isinstance(source, str) or source not in specs:
                raise ValueError(
                    "Динамічна таблиця не має оголошеного джерела даних"
                )
            fact = normalized.get(source)
            if fact is None:
                spec = specs[source]
                warning = "Не заповнено необов'язкове поле: " + spec.label
                if warning not in warnings:
                    warnings.append(warning)
                block["rows"] = []
            elif fact["rows"] is None:
                block["rows"] = [[fact["display"]]]
            else:
                block["rows"] = copy.deepcopy(fact["rows"])

        if "children" in block:
            _render_blocks(block["children"], specs, normalized, warnings)


def prepare_company_template_draft(
    workspace_root: Path,
    company_template_id: str,
    facts: Mapping[str, object],
) -> CompanyTemplateDraft:
    """Render one non-persistent draft from an exact company-template revision."""
    document = load_company_template(Path(workspace_root), company_template_id)
    variables = _variable_specs(document.template)
    normalized, facts_out = _normalize_facts(variables, facts)
    specs = {item.name: item for item in variables}
    warnings = []

    rendered = copy.deepcopy(document.template)
    rendered["title"] = _substitute(
        rendered.get("title", ""), specs, normalized, warnings
    )
    if "description" in rendered:
        rendered["description"] = _substitute(
            rendered["description"], specs, normalized, warnings
        )
    _render_blocks(rendered.get("blocks"), specs, normalized, warnings)
    for appendix in rendered.get("appendices", ()):
        if not isinstance(appendix, dict):
            raise ValueError("Некоректний додаток чернетки")
        appendix["title"] = _substitute(
            appendix.get("title", ""), specs, normalized, warnings
        )
        _render_blocks(
            appendix.get("blocks"), specs, normalized, warnings
        )

    return CompanyTemplateDraft(
        company_template_id=document.summary.company_template_id,
        edit_revision=document.edit_revision,
        template_sha256=document.content_sha256,
        title=str(rendered.get("title") or document.title),
        template=rendered,
        preview_text=render_template_text(rendered),
        variables=variables,
        facts=facts_out,
        warnings=tuple(warnings),
    )
