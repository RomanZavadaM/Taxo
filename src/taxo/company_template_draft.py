# -*- coding: utf-8 -*-
"""Typed in-memory draft rendering for user-owned CompanyTemplates revisions.

This module is deliberately pure with respect to Taxo business state. It reads
one integrity-checked company template, validates a caller-supplied fact set,
renders a deep copy of the template structure, and returns a preview snapshot.
It never writes CompanyTemplates, orders, briefings, document archives or the
main database.

Rendering is structural rather than a blind whole-document replace: only
schema-defined text-bearing fields are traversed. Dynamic tables consume typed
structured facts. Unknown or unresolved placeholders are rejected visibly.
"""
from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

from company_template_store import load_company_template
from template_library_preview import _render

_PLACEHOLDER = re.compile(
    r"{{\s*([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*)\s*}}"
)
_ALLOWED_TYPES = frozenset((
    "text", "date", "integer", "person_ref", "vehicle_ref",
    "pairs", "participants", "sections", "table_rows",
))
_MAX_FACTS = 500
_MAX_LIST_ITEMS = 5000
_MAX_RENDERED_FIELD_CHARS = 750000


@dataclass(frozen=True)
class DraftVariable:
    """Declared template variable exposed to a future fact-collection UI."""

    name: str
    label: str
    variable_type: str
    required: bool
    description: str = ""


@dataclass(frozen=True)
class CompanyTemplateDraft:
    """Read-only in-memory result with exact source provenance."""

    company_template_id: str
    source_sha256: str
    edit_revision: int
    title: str
    content: str
    variables: Tuple[DraftVariable, ...]
    normalized_facts: Dict[str, Any]
    rendered_template: Dict[str, Any]


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _declarations(template: Mapping[str, Any]) -> Tuple[DraftVariable, ...]:
    raw = template.get("variables")
    if not isinstance(raw, list) or len(raw) > _MAX_FACTS:
        raise ValueError("Некоректний перелік полів шаблону")
    seen = set()
    rows = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("Некоректний опис поля шаблону")
        name = item.get("name")
        typ = item.get("type")
        required = item.get("required")
        if (
            not isinstance(name, str)
            or not _PLACEHOLDER.fullmatch("{{%s}}" % name)
            or typ not in _ALLOWED_TYPES
            or not isinstance(required, bool)
            or name in seen
        ):
            raise ValueError("Некоректне поле шаблону")
        seen.add(name)
        rows.append(DraftVariable(
            name=name,
            label=_text(item.get("label")).strip() or name,
            variable_type=typ,
            required=required,
            description=_text(item.get("description")).strip(),
        ))
    return tuple(rows)


def _is_missing(value: object, typ: str) -> bool:
    if value is None:
        return True
    if typ == "text":
        return not isinstance(value, str) or not value.strip()
    if typ in ("pairs", "participants", "sections", "table_rows"):
        return not isinstance(value, (list, tuple)) or len(value) == 0
    if typ in ("person_ref", "vehicle_ref"):
        return not isinstance(value, dict) or not value
    return False


def _normalise_date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            pass
    raise ValueError("Дата повинна мати формат YYYY-MM-DD")


def _normalise_person(value: object) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("Працівник має бути структурованим записом")
    identity = value.get("id")
    entity_type = str(value.get("entity_type") or "employee")
    if type(identity) is not int or identity < 1:
        raise ValueError("Працівник не має стабільного ID")
    if entity_type not in ("employee", "driver", "person"):
        raise ValueError("Некоректний тип працівника")
    name = str(value.get("name") or value.get("label") or "").strip()
    if not name:
        raise ValueError("Працівник не має імені")
    result = {
        "entity_type": entity_type,
        "id": identity,
        "name": name,
    }
    for key in (
        "position", "personnel_no", "rnokpp", "registry_person_id", "label"
    ):
        if key in value and value.get(key) is not None:
            result[key] = str(value.get(key))
    return result


def _normalise_vehicle(value: object) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("Транспортний засіб має бути структурованим записом")
    identity = value.get("id")
    entity_type = str(value.get("entity_type") or "vehicle")
    if type(identity) is not int or identity < 1 or entity_type != "vehicle":
        raise ValueError("Транспортний засіб не має коректного стабільного ID")
    result = {
        "entity_type": "vehicle",
        "id": identity,
        "name": str(value.get("name") or "").strip(),
        "plate": str(value.get("plate") or "").strip(),
        "vin": str(value.get("vin") or "").strip(),
        "garage_no": str(value.get("garage_no") or "").strip(),
    }
    if value.get("label") is not None:
        result["label"] = str(value.get("label"))
    if not any(result[key] for key in ("name", "plate", "vin", "garage_no")):
        raise ValueError("Транспортний засіб не має реквізитів для документа")
    return result


def _normalise_rows(value: object) -> Tuple[Tuple[str, ...], ...]:
    if not isinstance(value, (list, tuple)) or len(value) > _MAX_LIST_ITEMS:
        raise ValueError("Некоректні рядки таблиці")
    result = []
    for row in value:
        if not isinstance(row, (list, tuple)):
            raise ValueError("Рядок таблиці має бути списком значень")
        cells = []
        for cell in row:
            if isinstance(cell, datetime):
                cells.append(cell.date().strftime("%d.%m.%Y"))
            elif isinstance(cell, date):
                cells.append(cell.strftime("%d.%m.%Y"))
            elif isinstance(cell, bool) or not isinstance(cell, (str, int)):
                raise ValueError("Непідтримуване значення клітинки таблиці")
            else:
                cells.append(str(cell))
        result.append(tuple(cells))
    return tuple(result)


def _normalise_value(value: object, typ: str) -> object:
    if typ == "text":
        if not isinstance(value, str):
            raise ValueError("Текстове поле має бути рядком")
        if "\x00" in value or len(value) > _MAX_RENDERED_FIELD_CHARS:
            raise ValueError("Некоректне або завелике текстове поле")
        return value
    if typ == "date":
        return _normalise_date(value)
    if typ == "integer":
        if type(value) is not int:
            raise ValueError("Числове поле має бути цілим числом")
        return value
    if typ == "person_ref":
        return _normalise_person(value)
    if typ == "vehicle_ref":
        return _normalise_vehicle(value)
    if typ == "participants":
        if not isinstance(value, (list, tuple)) or len(value) > _MAX_LIST_ITEMS:
            raise ValueError("Некоректний список учасників")
        return tuple(_normalise_person(item) for item in value)
    if typ == "pairs":
        if not isinstance(value, (list, tuple)) or len(value) > _MAX_LIST_ITEMS:
            raise ValueError("Некоректний список пар водій–ТЗ")
        pairs = []
        for item in value:
            if isinstance(item, dict):
                person = item.get("person", item.get("employee"))
                vehicle = item.get("vehicle")
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                person, vehicle = item
            else:
                raise ValueError("Пара водій–ТЗ має містити два структуровані записи")
            pairs.append({
                "person": _normalise_person(person),
                "vehicle": _normalise_vehicle(vehicle),
            })
        return tuple(pairs)
    if typ == "sections":
        if not isinstance(value, (list, tuple)) or len(value) > _MAX_LIST_ITEMS:
            raise ValueError("Некоректний список розділів")
        sections = []
        for item in value:
            if not isinstance(item, str) or "\x00" in item:
                raise ValueError("Розділ має бути текстом")
            sections.append(item)
        return tuple(sections)
    if typ == "table_rows":
        return _normalise_rows(value)
    raise ValueError("Непідтримуваний тип поля шаблону")


def _normalise_facts(
    variables: Tuple[DraftVariable, ...], facts: Mapping[str, object]
) -> Dict[str, object]:
    if not isinstance(facts, Mapping):
        raise ValueError("Фактичні дані мають бути словником")
    declarations = {item.name: item for item in variables}
    unknown = set(facts) - set(declarations)
    if unknown:
        raise ValueError(
            "Передано невідомі поля шаблону: " + ", ".join(sorted(unknown))
        )
    result = {}
    for name, declaration in declarations.items():
        raw = facts.get(name)
        if _is_missing(raw, declaration.variable_type):
            if declaration.required:
                raise ValueError(
                    "Не заповнено обов'язкове поле: %s" % declaration.label
                )
            result[name] = None
            continue
        try:
            result[name] = _normalise_value(raw, declaration.variable_type)
        except ValueError as exc:
            raise ValueError("%s: %s" % (declaration.label, exc))
    return result


def _display_person(value: Mapping[str, object]) -> str:
    label = str(value.get("label") or "").strip()
    if label:
        return label
    name = str(value.get("name") or "").strip()
    position = str(value.get("position") or "").strip()
    return name + ((" — " + position) if position else "")


def _display_vehicle(value: Mapping[str, object]) -> str:
    label = str(value.get("label") or "").strip()
    if label:
        return label
    parts = [
        str(value.get("plate") or "").strip(),
        str(value.get("name") or "").strip(),
    ]
    parts = [part for part in parts if part]
    if value.get("vin"):
        parts.append("VIN %s" % value["vin"])
    elif value.get("garage_no"):
        parts.append("гараж. № %s" % value["garage_no"])
    return " · ".join(parts)


def _scalar_display(value: object, typ: str) -> str:
    if value is None:
        return ""
    if typ == "text":
        return str(value)
    if typ == "date":
        return value.strftime("%d.%m.%Y")
    if typ == "integer":
        return str(value)
    if typ == "person_ref":
        return _display_person(value)
    if typ == "vehicle_ref":
        return _display_vehicle(value)
    if typ == "participants":
        return "\n".join(_display_person(item) for item in value)
    if typ == "pairs":
        return "\n".join(
            "%s — %s" % (
                _display_person(item["person"]),
                _display_vehicle(item["vehicle"]),
            )
            for item in value
        )
    if typ == "sections":
        return "\n\n".join(value)
    if typ == "table_rows":
        return "\n".join(" | ".join(row) for row in value)
    raise ValueError("Непідтримуваний тип поля")


def _placeholder_value(
    token: str,
    declarations: Mapping[str, DraftVariable],
    facts: Mapping[str, object],
) -> str:
    if token in declarations:
        declaration = declarations[token]
        return _scalar_display(facts[token], declaration.variable_type)

    matches = [
        name for name in declarations
        if token.startswith(name + ".")
    ]
    if not matches:
        raise ValueError("Шаблон містить невідоме поле: %s" % token)
    name = max(matches, key=len)
    declaration = declarations[name]
    value = facts[name]
    suffix = token[len(name) + 1:]
    if value is None:
        return ""
    if declaration.variable_type not in ("person_ref", "vehicle_ref"):
        raise ValueError(
            "Поле %s не підтримує вкладений реквізит %s" % (name, suffix)
        )
    allowed = (
        ("id", "name", "position", "personnel_no", "rnokpp",
         "registry_person_id", "label")
        if declaration.variable_type == "person_ref"
        else ("id", "name", "plate", "vin", "garage_no", "label")
    )
    if suffix not in allowed:
        raise ValueError(
            "Непідтримуваний реквізит %s.%s" % (name, suffix)
        )
    return str(value.get(suffix) or "")


def _substitute_text(
    value: object,
    declarations: Mapping[str, DraftVariable],
    facts: Mapping[str, object],
) -> object:
    if not isinstance(value, str):
        return value

    def replace(match):
        return _placeholder_value(match.group(1), declarations, facts)

    result = _PLACEHOLDER.sub(replace, value)
    if "{{" in result or "}}" in result:
        raise ValueError("Шаблон містить непідтримуваний placeholder")
    if len(result) > _MAX_RENDERED_FIELD_CHARS:
        raise ValueError("Заповнене текстове поле перевищує допустимий розмір")
    return result


def _dynamic_rows(
    variable: DraftVariable,
    value: object,
    column_count: int,
) -> Tuple[Tuple[str, ...], ...]:
    if value is None:
        return ()
    if variable.variable_type == "table_rows":
        rows = value
    elif variable.variable_type == "pairs":
        if column_count != 2:
            raise ValueError(
                "Таблиця пар водій–ТЗ повинна мати рівно дві колонки"
            )
        rows = tuple(
            (
                _display_person(item["person"]),
                _display_vehicle(item["vehicle"]),
            )
            for item in value
        )
    elif variable.variable_type == "participants":
        if column_count != 1:
            raise ValueError(
                "Таблиця учасників у r4 повинна мати одну колонку"
            )
        rows = tuple((_display_person(item),) for item in value)
    else:
        raise ValueError(
            "Поле %s не можна використати як джерело таблиці" % variable.name
        )
    for row in rows:
        if len(row) != column_count:
            raise ValueError(
                "Кількість клітинок не збігається з колонками таблиці"
            )
    return tuple(tuple(str(cell) for cell in row) for row in rows)


def _render_blocks(
    blocks: object,
    declarations: Mapping[str, DraftVariable],
    facts: Mapping[str, object],
) -> None:
    if not isinstance(blocks, list):
        raise ValueError("Некоректна структура блоків")
    for block in blocks:
        if not isinstance(block, dict):
            raise ValueError("Некоректний блок шаблону")
        for key in ("text", "notes"):
            if key in block:
                block[key] = _substitute_text(block[key], declarations, facts)
        for key in ("items", "columns"):
            if key in block:
                values = block[key]
                if not isinstance(values, list):
                    raise ValueError("Некоректне текстове поле блоку")
                block[key] = [
                    _substitute_text(item, declarations, facts)
                    for item in values
                ]
        if block.get("type") == "dynamic_table":
            source = block.get("data_source")
            columns = block.get("columns", [])
            if not isinstance(source, str) or source not in declarations:
                raise ValueError(
                    "Динамічна таблиця не має оголошеного джерела даних"
                )
            if not isinstance(columns, list) or not columns:
                raise ValueError("Динамічна таблиця не має колонок")
            variable = declarations[source]
            block["rows"] = [
                list(row)
                for row in _dynamic_rows(
                    variable, facts[source], len(columns)
                )
            ]
        elif "rows" in block:
            rows = block["rows"]
            if not isinstance(rows, list):
                raise ValueError("Некоректні рядки таблиці")
            block["rows"] = [
                [
                    _substitute_text(cell, declarations, facts)
                    for cell in row
                ]
                if isinstance(row, list) else row
                for row in rows
            ]
        if "children" in block:
            _render_blocks(block["children"], declarations, facts)


def prepare_company_template_draft(
    workspace_root: Path,
    company_template_id: str,
    facts: Mapping[str, object],
) -> CompanyTemplateDraft:
    """Build a typed, non-persistent preview from one company-owned revision."""
    document = load_company_template(Path(workspace_root), company_template_id)
    variables = _declarations(document.template)
    normalized = _normalise_facts(variables, facts)
    declarations = {item.name: item for item in variables}

    rendered = copy.deepcopy(document.template)
    rendered["title"] = _substitute_text(
        rendered.get("title", ""), declarations, normalized
    )
    if "description" in rendered:
        rendered["description"] = _substitute_text(
            rendered["description"], declarations, normalized
        )
    _render_blocks(rendered.get("blocks"), declarations, normalized)

    appendices = rendered.get("appendices", [])
    if not isinstance(appendices, list):
        raise ValueError("Некоректні додатки шаблону")
    for appendix in appendices:
        if not isinstance(appendix, dict):
            raise ValueError("Некоректний додаток шаблону")
        appendix["title"] = _substitute_text(
            appendix.get("title", ""), declarations, normalized
        )
        _render_blocks(appendix.get("blocks"), declarations, normalized)

    content = _render(rendered)
    return CompanyTemplateDraft(
        company_template_id=company_template_id,
        source_sha256=document.content_sha256,
        edit_revision=document.edit_revision,
        title=rendered.get("title", document.title),
        content=content,
        variables=variables,
        normalized_facts=copy.deepcopy(normalized),
        rendered_template=rendered,
    )


def list_draft_variables(
    workspace_root: Path, company_template_id: str
) -> Tuple[DraftVariable, ...]:
    """Read declared variables without rendering or writing anything."""
    document = load_company_template(Path(workspace_root), company_template_id)
    return _declarations(document.template)
