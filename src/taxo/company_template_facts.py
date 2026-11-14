# -*- coding: utf-8 -*-
"""Typed fact contract for CompanyTemplates draft rendering.

This module owns validation and normalization of factual values supplied to a
company template. It has no filesystem, database or Tk dependencies. Entity
references intentionally match the stable snapshot dictionaries already used
by entity_choices.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, Mapping, Tuple

VARIABLE_NAME = re.compile(
    r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*$"
)
ALLOWED_TYPES = frozenset((
    "text", "date", "integer", "person_ref", "vehicle_ref",
    "pairs", "participants", "sections", "table_rows",
))
MAX_FACTS = 500
MAX_LIST_ITEMS = 5000
MAX_RENDERED_FIELD_CHARS = 750000


@dataclass(frozen=True)
class DraftVariable:
    """One typed variable declared by a template revision."""

    name: str
    label: str
    variable_type: str
    required: bool
    description: str = ""


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def declared_variables(template: Mapping[str, Any]) -> Tuple[DraftVariable, ...]:
    """Validate and expose the template's variable declarations."""
    raw = template.get("variables")
    if not isinstance(raw, list) or len(raw) > MAX_FACTS:
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
            or not VARIABLE_NAME.fullmatch(name)
            or typ not in ALLOWED_TYPES
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
    if not isinstance(value, (list, tuple)) or len(value) > MAX_LIST_ITEMS:
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
        if "\\x00" in value or len(value) > MAX_RENDERED_FIELD_CHARS:
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
        if not isinstance(value, (list, tuple)) or len(value) > MAX_LIST_ITEMS:
            raise ValueError("Некоректний список учасників")
        return tuple(_normalise_person(item) for item in value)
    if typ == "pairs":
        if not isinstance(value, (list, tuple)) or len(value) > MAX_LIST_ITEMS:
            raise ValueError("Некоректний список пар водій–ТЗ")
        pairs = []
        for item in value:
            if isinstance(item, dict):
                person = item.get("person", item.get("employee"))
                vehicle = item.get("vehicle")
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                person, vehicle = item
            else:
                raise ValueError(
                    "Пара водій–ТЗ має містити два структуровані записи"
                )
            pairs.append({
                "person": _normalise_person(person),
                "vehicle": _normalise_vehicle(vehicle),
            })
        return tuple(pairs)
    if typ == "sections":
        if not isinstance(value, (list, tuple)) or len(value) > MAX_LIST_ITEMS:
            raise ValueError("Некоректний список розділів")
        sections = []
        for item in value:
            if not isinstance(item, str) or "\\x00" in item:
                raise ValueError("Розділ має бути текстом")
            sections.append(item)
        return tuple(sections)
    if typ == "table_rows":
        return _normalise_rows(value)
    raise ValueError("Непідтримуваний тип поля шаблону")


def normalize_facts(
    variables: Tuple[DraftVariable, ...], facts: Mapping[str, object]
) -> Dict[str, object]:
    """Normalize exactly the facts declared by one template revision."""
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


def display_person(value: Mapping[str, object]) -> str:
    """Human-readable employee snapshot without re-querying the database."""
    label = str(value.get("label") or "").strip()
    if label:
        return label
    name = str(value.get("name") or "").strip()
    position = str(value.get("position") or "").strip()
    return name + ((" — " + position) if position else "")


def display_vehicle(value: Mapping[str, object]) -> str:
    """Human-readable vehicle snapshot without label-only identity matching."""
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


def display_fact(value: object, typ: str) -> str:
    """Render one normalized fact when a scalar placeholder requests it."""
    if value is None:
        return ""
    if typ == "text":
        return str(value)
    if typ == "date":
        return value.strftime("%d.%m.%Y")
    if typ == "integer":
        return str(value)
    if typ == "person_ref":
        return display_person(value)
    if typ == "vehicle_ref":
        return display_vehicle(value)
    if typ == "participants":
        return "\\n".join(display_person(item) for item in value)
    if typ == "pairs":
        return "\\n".join(
            "%s — %s" % (
                display_person(item["person"]),
                display_vehicle(item["vehicle"]),
            )
            for item in value
        )
    if typ == "sections":
        return "\\n\\n".join(value)
    if typ == "table_rows":
        return "\\n".join(" | ".join(row) for row in value)
    raise ValueError("Непідтримуваний тип поля")


def dynamic_rows(
    variable: DraftVariable,
    value: object,
    column_count: int,
) -> Tuple[Tuple[str, ...], ...]:
    """Turn a normalized complex fact into strict table rows."""
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
                display_person(item["person"]),
                display_vehicle(item["vehicle"]),
            )
            for item in value
        )
    elif variable.variable_type == "participants":
        if column_count != 1:
            raise ValueError(
                "Таблиця учасників у r4 повинна мати одну колонку"
            )
        rows = tuple((display_person(item),) for item in value)
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
