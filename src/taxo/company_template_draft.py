# -*- coding: utf-8 -*-
"""Typed in-memory draft rendering for user-owned Taxo templates.

This module never writes templates, databases or document archives. It loads an
integrity-checked CompanyTemplates revision, validates declared facts by type,
substitutes only schema-defined text fields, optionally materialises
dynamic-table rows from structured data, and returns an in-memory preview.

No Python/JS expressions, eval/exec, macros or arbitrary object stringification
are supported. Missing required facts and unknown placeholders fail visibly.
"""
from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Mapping, Tuple

from company_template_store import load_company_template
from template_library_preview import render_template_text

_PLACEHOLDER = re.compile(
    r"\{\{\s*([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*)\s*\}\}"
)
_SCALAR_TYPES = frozenset(("text", "date", "integer", "person_ref", "vehicle_ref"))
_COMPLEX_TYPES = frozenset(("pairs", "participants", "sections", "table_rows"))
MAX_FACT_TEXT_CHARS = 750000
MAX_TABLE_ROWS = 5000
MAX_TABLE_COLUMNS = 80


@dataclass(frozen=True)
class DraftFactField:
    """Declared input expected by a company template."""

    name: str
    label: str
    variable_type: str
    required: bool


@dataclass(frozen=True)
class CompanyTemplateDraft:
    """Read-only result of one draft render; no business fact is recorded."""

    company_template_id: str
    company_revision: int
    title: str
    content: str
    facts: Tuple[DraftFactField, ...]
    source_sha256: str
    resolved_template: dict


def _fact_fields(template: dict) -> Tuple[DraftFactField, ...]:
    rows = []
    for variable in template.get("variables", ()):
        if not isinstance(variable, dict):
            raise ValueError("Некоректний опис змінної шаблону")
        name = variable.get("name")
        typ = variable.get("type")
        required = variable.get("required")
        if not isinstance(name, str) or typ not in _SCALAR_TYPES | _COMPLEX_TYPES:
            raise ValueError("Некоректна змінна шаблону")
        if not isinstance(required, bool):
            raise ValueError("Некоректна ознака обов'язкового поля")
        label = variable.get("label")
        rows.append(DraftFactField(
            name=name,
            label=label.strip() if isinstance(label, str) and label.strip() else name,
            variable_type=typ,
            required=required,
        ))
    return tuple(rows)


def list_draft_facts(
    workspace_root: Path, company_template_id: str
) -> Tuple[DraftFactField, ...]:
    """Return declared fact inputs without changing the company template."""
    document = load_company_template(Path(workspace_root), company_template_id)
    return _fact_fields(document.template)


def _text(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Очікується текстове значення")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    if "\x00" in value or len(value) > MAX_FACT_TEXT_CHARS:
        raise ValueError("Текстове значення має недопустимий розмір або символ")
    return value


def _scalar(typ: str, value: object):
    if typ == "text":
        return _text(value), _text(value)
    if typ == "integer":
        if type(value) is not int:
            raise ValueError("Очікується ціле число")
        return value, str(value)
    if typ == "date":
        if isinstance(value, datetime):
            value = value.date()
        elif isinstance(value, str):
            try:
                value = date.fromisoformat(value)
            except ValueError:
                raise ValueError("Дата має бути у форматі YYYY-MM-DD")
        if not isinstance(value, date):
            raise ValueError("Очікується дата")
        return value.isoformat(), value.strftime("%d.%m.%Y")
    if typ in ("person_ref", "vehicle_ref"):
        if not isinstance(value, Mapping):
            raise ValueError("Очікується посилання на запис Taxo")
        identity = value.get("id")
        label = value.get("label")
        if isinstance(identity, bool) or not isinstance(identity, (int, str)):
            raise ValueError("Посилання Taxo не має коректного ID")
        label = _text(label).strip()
        if not label:
            raise ValueError("Посилання Taxo не має видимої назви")
        return {"id": identity, "label": label}, label
    raise ValueError("Непідтримуваний скалярний тип")


def _complex(typ: str, value: object):
    if not isinstance(value, (list, tuple)):
        raise ValueError("Очікується структурований список даних")
    if len(value) > MAX_TABLE_ROWS:
        raise ValueError("Забагато рядків даних для чернетки")
    if typ == "table_rows":
        result = []
        for row in value:
            if not isinstance(row, (list, tuple)) or len(row) > MAX_TABLE_COLUMNS:
                raise ValueError("Некоректний рядок таблиці")
            result.append(tuple(_text(cell) for cell in row))
        return tuple(result)
    if typ in ("pairs", "participants", "sections"):
        result = []
        for row in value:
            if not isinstance(row, Mapping):
                raise ValueError("Структурований запис має бути об'єктом")
            clean = {}
            for key, cell in row.items():
                if not isinstance(key, str) or not key:
                    raise ValueError("Некоректне поле структурованого запису")
                clean[key] = _text(cell)
            result.append(clean)
        return tuple(result)
    raise ValueError("Непідтримуваний структурований тип")


def _normalise_facts(fields: Tuple[DraftFactField, ...], facts: Mapping[str, object]):
    if not isinstance(facts, Mapping):
        raise ValueError("Фактичні дані мають бути словником")
    definitions = {field.name: field for field in fields}
    unknown = set(facts) - set(definitions)
    if unknown:
        raise ValueError("Передано поле, якого немає у шаблоні: " + sorted(unknown)[0])

    normalized = {}
    display = {}
    missing = []
    for field in fields:
        if field.name not in facts or facts[field.name] is None:
            if field.required:
                missing.append(field.label)
            continue
        value = facts[field.name]
        try:
            if field.variable_type in _SCALAR_TYPES:
                normalized[field.name], display[field.name] = _scalar(
                    field.variable_type, value
                )
            else:
                normalized[field.name] = _complex(field.variable_type, value)
        except ValueError as exc:
            raise ValueError("%s: %s" % (field.label, exc))
    if missing:
        raise ValueError("Не заповнено обов'язкове поле: " + missing[0])
    return normalized, display, definitions


def _replace_text(value: object, display: Dict[str, str], definitions) -> object:
    if not isinstance(value, str):
        return value

    def replace(match):
        name = match.group(1)
        field = definitions.get(name)
        if field is None:
            raise ValueError("Шаблон містить невідоме поле: " + name)
        if field.variable_type not in _SCALAR_TYPES:
            raise ValueError(
                "Структуроване поле не можна вставляти як звичайний текст: " + name
            )
        if name not in display:
            return ""
        return display[name]

    return _PLACEHOLDER.sub(replace, value)


def _resolve_blocks(blocks, display, definitions, normalized):
    for block in blocks:
        if not isinstance(block, dict):
            raise ValueError("Некоректний блок шаблону")
        for key in ("text", "notes"):
            if key in block:
                block[key] = _replace_text(block[key], display, definitions)
        for key in ("items", "columns"):
            if key in block:
                if not isinstance(block[key], list):
                    raise ValueError("Некоректний список у шаблоні")
                block[key] = [
                    _replace_text(item, display, definitions) for item in block[key]
                ]
        if "rows" in block:
            if not isinstance(block["rows"], list):
                raise ValueError("Некоректні рядки таблиці")
            clean_rows = []
            for row in block["rows"]:
                if not isinstance(row, list):
                    raise ValueError("Некоректний рядок таблиці")
                clean_rows.append([
                    _replace_text(cell, display, definitions) for cell in row
                ])
            block["rows"] = clean_rows

        if block.get("type") == "dynamic_table":
            source = block.get("data_source")
            if isinstance(source, str) and source:
                field = definitions.get(source)
                if field is None:
                    raise ValueError("Невідоме джерело динамічної таблиці: " + source)
                if field.variable_type not in _COMPLEX_TYPES:
                    raise ValueError("Джерело динамічної таблиці має бути структурованим")
            if isinstance(source, str) and source in normalized:
                field = definitions[source]
                value = normalized[source]
                columns = block.get("columns", [])
                if field.variable_type == "table_rows":
                    rows = [list(row) for row in value]
                else:
                    if not isinstance(columns, list) or not columns:
                        raise ValueError("Динамічна таблиця не має колонок")
                    rows = []
                    for item in value:
                        missing = [column for column in columns if column not in item]
                        if missing:
                            raise ValueError(
                                "У структурованих даних немає колонки: " + missing[0]
                            )
                        rows.append([item[column] for column in columns])
                if columns and any(len(row) != len(columns) for row in rows):
                    raise ValueError("Кількість клітинок не збігається з колонками")
                block["rows"] = rows

        children = block.get("children")
        if children is not None:
            if not isinstance(children, list):
                raise ValueError("Некоректні дочірні блоки")
            _resolve_blocks(children, display, definitions, normalized)


def render_company_template_draft(
    workspace_root: Path,
    company_template_id: str,
    facts: Mapping[str, object],
) -> CompanyTemplateDraft:
    """Render a validated in-memory draft without persisting any result."""
    document = load_company_template(Path(workspace_root), company_template_id)
    fields = _fact_fields(document.template)
    normalized, display, definitions = _normalise_facts(fields, facts)

    resolved = copy.deepcopy(document.template)
    for key in ("title", "description"):
        if key in resolved:
            resolved[key] = _replace_text(resolved[key], display, definitions)
    _resolve_blocks(resolved["blocks"], display, definitions, normalized)
    for appendix in resolved.get("appendices", ()):
        if not isinstance(appendix, dict):
            raise ValueError("Некоректний додаток шаблону")
        if "title" in appendix:
            appendix["title"] = _replace_text(
                appendix["title"], display, definitions
            )
        blocks = appendix.get("blocks")
        if not isinstance(blocks, list):
            raise ValueError("Некоректні блоки додатка")
        _resolve_blocks(blocks, display, definitions, normalized)

    content = render_template_text(resolved)
    return CompanyTemplateDraft(
        company_template_id=company_template_id,
        company_revision=document.edit_revision,
        title=resolved["title"],
        content=content,
        facts=fields,
        source_sha256=document.content_sha256,
        resolved_template=resolved,
    )
