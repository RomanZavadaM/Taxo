# -*- coding: utf-8 -*-
"""Structural in-memory draft rendering for user-owned CompanyTemplates.

The renderer reads one integrity-checked company revision, normalizes the
caller-supplied facts through company_template_facts, deep-copies the template
structure and substitutes only schema-defined text-bearing fields. It never
writes a template, business record, database row, archive entry or output file.
"""
from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple

from company_template_facts import (
    DraftVariable,
    MAX_RENDERED_FIELD_CHARS,
    declared_variables,
    display_fact,
    dynamic_rows,
    normalize_facts,
)
from company_template_store import load_company_template
from template_library_preview import _render

_PLACEHOLDER = re.compile(
    r"{{\s*([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*)\s*}}"
)


@dataclass(frozen=True)
class CompanyTemplateDraft:
    """Read-only in-memory result with exact company-revision provenance."""

    company_template_id: str
    source_sha256: str
    edit_revision: int
    title: str
    content: str
    variables: Tuple[DraftVariable, ...]
    normalized_facts: Dict[str, Any]
    rendered_template: Dict[str, Any]


def _placeholder_value(
    token: str,
    declarations: Mapping[str, DraftVariable],
    facts: Mapping[str, object],
) -> str:
    if token in declarations:
        declaration = declarations[token]
        return display_fact(facts[token], declaration.variable_type)

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
        (
            "id", "name", "position", "personnel_no", "rnokpp",
            "registry_person_id", "label",
        )
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
    """Resolve approved placeholders inside one schema-defined text value."""
    if not isinstance(value, str):
        return value

    def replace(match):
        return _placeholder_value(match.group(1), declarations, facts)

    result = _PLACEHOLDER.sub(replace, value)
    if "{{" in result or "}}" in result:
        raise ValueError("Шаблон містить непідтримуваний placeholder")
    if len(result) > MAX_RENDERED_FIELD_CHARS:
        raise ValueError("Заповнене текстове поле перевищує допустимий розмір")
    return result


def _render_static_rows(
    rows: object,
    declarations: Mapping[str, DraftVariable],
    facts: Mapping[str, object],
):
    if not isinstance(rows, list):
        raise ValueError("Некоректні рядки таблиці")
    rendered = []
    for row in rows:
        if not isinstance(row, list):
            raise ValueError("Некоректний рядок таблиці")
        rendered.append([
            _substitute_text(cell, declarations, facts)
            for cell in row
        ])
    return rendered


def _render_blocks(
    blocks: object,
    declarations: Mapping[str, DraftVariable],
    facts: Mapping[str, object],
) -> None:
    """Mutate only the deep-copied block tree used for this draft."""
    if not isinstance(blocks, list):
        raise ValueError("Некоректна структура блоків")

    for block in blocks:
        if not isinstance(block, dict):
            raise ValueError("Некоректний блок шаблону")

        for key in ("text", "notes"):
            if key in block:
                block[key] = _substitute_text(
                    block[key], declarations, facts
                )

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
                for row in dynamic_rows(
                    variable, facts[source], len(columns)
                )
            ]
        elif "rows" in block:
            block["rows"] = _render_static_rows(
                block["rows"], declarations, facts
            )

        if "children" in block:
            _render_blocks(block["children"], declarations, facts)


def _render_appendices(
    appendices: object,
    declarations: Mapping[str, DraftVariable],
    facts: Mapping[str, object],
) -> None:
    if not isinstance(appendices, list):
        raise ValueError("Некоректні додатки шаблону")
    for appendix in appendices:
        if not isinstance(appendix, dict):
            raise ValueError("Некоректний додаток шаблону")
        appendix["title"] = _substitute_text(
            appendix.get("title", ""), declarations, facts
        )
        _render_blocks(
            appendix.get("blocks"), declarations, facts
        )


def prepare_company_template_draft(
    workspace_root: Path,
    company_template_id: str,
    facts: Mapping[str, object],
) -> CompanyTemplateDraft:
    """Build a typed, non-persistent preview from one company-owned revision."""
    document = load_company_template(
        Path(workspace_root), company_template_id
    )
    variables = declared_variables(document.template)
    normalized = normalize_facts(variables, facts)
    declarations = {item.name: item for item in variables}

    rendered = copy.deepcopy(document.template)
    rendered["title"] = _substitute_text(
        rendered.get("title", ""), declarations, normalized
    )
    if "description" in rendered:
        rendered["description"] = _substitute_text(
            rendered["description"], declarations, normalized
        )

    _render_blocks(
        rendered.get("blocks"), declarations, normalized
    )
    _render_appendices(
        rendered.get("appendices", []), declarations, normalized
    )

    return CompanyTemplateDraft(
        company_template_id=company_template_id,
        source_sha256=document.content_sha256,
        edit_revision=document.edit_revision,
        title=rendered.get("title", document.title),
        content=_render(rendered),
        variables=variables,
        normalized_facts=copy.deepcopy(normalized),
        rendered_template=rendered,
    )


def list_draft_variables(
    workspace_root: Path, company_template_id: str
) -> Tuple[DraftVariable, ...]:
    """Read declared variables without rendering or writing anything."""
    document = load_company_template(
        Path(workspace_root), company_template_id
    )
    return declared_variables(document.template)
