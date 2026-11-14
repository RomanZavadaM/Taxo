# -*- coding: utf-8 -*-
"""Structured editing service for user-owned Taxo template copies.

The service exposes only user-visible text fields from a CompanyTemplates copy.
Template IDs, block types, variable definitions, data sources and vendor
provenance are intentionally not editable here. The service has no Tk code and
never touches the read-only TemplateLibrary.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple, Union

from company_template_store import (
    CompanyTemplateSummary,
    list_company_templates,
    load_company_template,
    save_company_template,
)

MAX_EDITOR_FIELD_CHARS = 750000
MAX_TITLE_CHARS = 250
PathPart = Union[str, int]


@dataclass(frozen=True)
class EditableTemplateField:
    """One user-visible string that can be changed without altering structure."""

    key: str
    section: str
    label: str
    value: str


@dataclass(frozen=True)
class CompanyTemplateEditorModel:
    """Optimistic-concurrency snapshot used by the editor UI."""

    company_template_id: str
    title: str
    fields: Tuple[EditableTemplateField, ...]
    expected_sha256: str
    edit_revision: int
    updated_at: str


def list_editor_templates(workspace_root: Path) -> Tuple[CompanyTemplateSummary, ...]:
    """List integrity-checked company templates without creating storage."""
    return list_company_templates(Path(workspace_root))


def _normalise_text(value: object, *, title: bool = False) -> str:
    if not isinstance(value, str):
        raise ValueError("Текст шаблону має бути рядком")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    if "\x00" in value:
        raise ValueError("Текст шаблону містить недопустимий символ")
    limit = MAX_TITLE_CHARS if title else MAX_EDITOR_FIELD_CHARS
    if len(value) > limit:
        raise ValueError("Текстове поле шаблону перевищує допустимий розмір")
    if title:
        value = value.strip()
        if not value:
            raise ValueError("Назва шаблону не може бути порожньою")
        if "\n" in value:
            raise ValueError("Назва шаблону має бути в одному рядку")
    return value


def _key(path: Iterable[PathPart]) -> str:
    return "/".join(str(part) for part in path)


def _field(rows, path, section, label, value) -> None:
    if isinstance(value, str):
        rows.append((_key(path), tuple(path), section, label, value))


def _walk_blocks(blocks, prefix, section, rows) -> None:
    for index, block in enumerate(blocks):
        if not isinstance(block, dict):
            continue
        base = tuple(prefix) + (index,)
        block_id = str(block.get("id") or ("block-%d" % (index + 1)))
        block_type = str(block.get("type") or "block")
        stem = "%s · %s" % (block_type, block_id)
        _field(rows, base + ("text",), section, stem + " · текст", block.get("text"))
        _field(rows, base + ("notes",), section, stem + " · примітка", block.get("notes"))

        items = block.get("items")
        if isinstance(items, list):
            for item_index, item in enumerate(items):
                _field(
                    rows,
                    base + ("items", item_index),
                    section,
                    "%s · пункт %d" % (stem, item_index + 1),
                    item,
                )

        columns = block.get("columns")
        if isinstance(columns, list):
            for column_index, item in enumerate(columns):
                _field(
                    rows,
                    base + ("columns", column_index),
                    section,
                    "%s · колонка %d" % (stem, column_index + 1),
                    item,
                )

        table_rows = block.get("rows")
        if isinstance(table_rows, list):
            for row_index, row in enumerate(table_rows):
                if not isinstance(row, list):
                    continue
                for column_index, item in enumerate(row):
                    _field(
                        rows,
                        base + ("rows", row_index, column_index),
                        section,
                        "%s · клітинка %d:%d" % (
                            stem, row_index + 1, column_index + 1
                        ),
                        item,
                    )

        children = block.get("children")
        if isinstance(children, list):
            _walk_blocks(
                children,
                base + ("children",),
                section + " / " + block_id,
                rows,
            )


def _editable_rows(template: dict):
    rows = []
    _field(rows, ("description",), "Шаблон", "Опис", template.get("description"))
    blocks = template.get("blocks")
    if isinstance(blocks, list):
        _walk_blocks(blocks, ("blocks",), "Основний документ", rows)
    appendices = template.get("appendices")
    if isinstance(appendices, list):
        for appendix_index, appendix in enumerate(appendices):
            if not isinstance(appendix, dict):
                continue
            appendix_id = str(
                appendix.get("id") or ("appendix-%d" % (appendix_index + 1))
            )
            section = "Додаток %d · %s" % (appendix_index + 1, appendix_id)
            _field(
                rows,
                ("appendices", appendix_index, "title"),
                section,
                "Назва додатка",
                appendix.get("title"),
            )
            appendix_blocks = appendix.get("blocks")
            if isinstance(appendix_blocks, list):
                _walk_blocks(
                    appendix_blocks,
                    ("appendices", appendix_index, "blocks"),
                    section,
                    rows,
                )
    return rows


def _set_path(root: object, path: Tuple[PathPart, ...], value: str) -> None:
    current = root
    for part in path[:-1]:
        if isinstance(part, int):
            if not isinstance(current, list) or part < 0 or part >= len(current):
                raise ValueError("Структура шаблону змінилася під час редагування")
            current = current[part]
        else:
            if not isinstance(current, dict) or part not in current:
                raise ValueError("Структура шаблону змінилася під час редагування")
            current = current[part]
    leaf = path[-1]
    if isinstance(leaf, int):
        if not isinstance(current, list) or leaf < 0 or leaf >= len(current):
            raise ValueError("Структура шаблону змінилася під час редагування")
        current[leaf] = value
    else:
        if not isinstance(current, dict) or leaf not in current:
            raise ValueError("Структура шаблону змінилася під час редагування")
        current[leaf] = value


def _model_from_document(document) -> CompanyTemplateEditorModel:
    fields = tuple(
        EditableTemplateField(
            key=key, section=section, label=label, value=value
        )
        for key, _path, section, label, value in _editable_rows(document.template)
    )
    return CompanyTemplateEditorModel(
        company_template_id=document.summary.company_template_id,
        title=document.title,
        fields=fields,
        expected_sha256=document.content_sha256,
        edit_revision=document.edit_revision,
        updated_at=document.updated_at,
    )


def load_editor_model(
    workspace_root: Path, company_template_id: str
) -> CompanyTemplateEditorModel:
    """Load one verified company template for editing."""
    return _model_from_document(
        load_company_template(Path(workspace_root), company_template_id)
    )


def save_editor_model(
    workspace_root: Path,
    company_template_id: str,
    expected_sha256: str,
    title: str,
    values: Dict[str, str],
) -> CompanyTemplateEditorModel:
    """Save text-only edits using optimistic concurrency.

    Unknown keys are rejected. A changed on-disk SHA rejects the save rather
    than silently overwriting another editor's revision.
    """
    title = _normalise_text(title, title=True)
    document = load_company_template(Path(workspace_root), company_template_id)
    if document.content_sha256 != expected_sha256:
        raise ValueError(
            "Власний шаблон уже змінено в іншому вікні або процесі. "
            "Оновіть його перед повторним збереженням."
        )

    rows = _editable_rows(document.template)
    allowed = {
        key: (path, old_value)
        for key, path, _section, _label, old_value in rows
    }
    if not isinstance(values, dict):
        raise ValueError("Некоректний набір змін шаблону")
    unknown = set(values) - set(allowed)
    if unknown:
        raise ValueError("Спроба змінити службову структуру шаблону")

    updated = copy.deepcopy(document.template)
    for key, value in values.items():
        value = _normalise_text(value)
        path, _old_value = allowed[key]
        _set_path(updated, path, value)
    updated["title"] = title

    saved = save_company_template(
        Path(workspace_root),
        company_template_id,
        expected_sha256,
        title,
        updated,
    )
    return _model_from_document(saved)
