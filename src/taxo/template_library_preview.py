# -*- coding: utf-8 -*-
"""Safe, read-only preview of an installed Taxo template revision.

A preview is *not* a finished document and never substitutes company/employee
data or evaluates placeholder/visibility expressions. We require a freshly
verified manifest on each open, then bind the requested ID/revision to a
validated file path and checksum. The renderer emits plain text for Tk rather
than HTML, a command, DOCX or executable template content.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

from template_library_reader import (
    MAX_TEMPLATE_BYTES, _object, _read_bytes, _safe_path,
    _validate_template, inspect_library,
)

MAX_PREVIEW_CHARS = 750000
MAX_RENDER_BLOCKS = 8000
MAX_BLOCK_DEPTH = 18


@dataclass(frozen=True)
class PreviewVariable:
    name: str
    label: str
    variable_type: str
    required: bool


@dataclass(frozen=True)
class TemplatePreview:
    """Human-readable non-executable snapshot; no write operations."""

    title: str
    template_id: str
    revision_id: str
    package_version: str
    category_id: str
    description: str
    legal_review: str
    content: str
    variables: Tuple[PreviewVariable, ...]
    source_notes: str = ""


def _plain(value: object) -> str:
    return value if isinstance(value, str) else ""


def _format_blocks(blocks, *, budget: Dict[str, int], level: int = 0):
    """Convert schema-defined blocks into legible literal text, with quotas."""
    if level > MAX_BLOCK_DEPTH:
        raise ValueError("Шаблон містить занадто глибоку структуру")
    if not isinstance(blocks, list):
        raise ValueError("Неправильна структура блоків")
    parts = []
    for block in blocks:
        budget["blocks"] += 1
        if budget["blocks"] > MAX_RENDER_BLOCKS:
            raise ValueError("Шаблон перевищує допустиму кількість блоків")
        if not isinstance(block, dict):
            raise ValueError("Пошкоджений блок шаблону")
        typ = block.get("type")
        text = _plain(block.get("text"))
        if typ == "heading":
            heading_level = block.get("level", 2)
            prefix = "#" * min(6, heading_level) if type(heading_level) is int and heading_level > 0 else "##"
            parts.append(prefix + " " + text)
        elif typ == "paragraph":
            parts.append(text)
        elif typ in ("numbered_list", "bullet_list"):
            items = block.get("items", [])
            if not isinstance(items, list):
                raise ValueError("Некоректний список")
            parts.extend(("%d. " % (i + 1) if typ == "numbered_list" else "• ") + _plain(item)
                         for i, item in enumerate(items))
        elif typ in ("table", "dynamic_table"):
            columns = block.get("columns", [])
            rows = block.get("rows", [])
            if not isinstance(columns, list) or not isinstance(rows, list):
                raise ValueError("Некоректна таблиця")
            if columns:
                parts.append(" | ".join(_plain(col) for col in columns))
                parts.append("—" * 35)
            for row in rows:
                if not isinstance(row, list):
                    raise ValueError("Некоректний рядок таблиці")
                parts.append(" | ".join(_plain(cell) for cell in row))
            if typ == "dynamic_table":
                data_source = _plain(block.get("data_source"))
                parts.append("[Таблиця заповнюється з даних: %s]" %
                             (data_source or "не вказано"))
        elif typ == "page_break":
            parts.append("\n" + "─" * 40 + "  Нова сторінка  " + "─" * 8)
        elif typ in ("signature_placeholder", "attachment_reference", "figure"):
            captions = {
                "signature_placeholder": "Місце для підпису",
                "attachment_reference": "Посилання на додаток",
                "figure": "Ілюстрація",
            }
            parts.append("[%s] %s" % (captions[typ], text))
        else:
            raise ValueError("Непідтримуваний тип блоку")
        if "notes" in block and block["notes"]:
            parts.append("Примітка: " + _plain(block["notes"]))
        if "children" in block:
            parts.extend(_format_blocks(block["children"], budget=budget, level=level + 1))
    return parts


def _render(template: dict) -> str:
    budget = {"blocks": 0}
    parts = _format_blocks(template["blocks"], budget=budget)
    for appendix in template.get("appendices", []):
        if not isinstance(appendix, dict):
            raise ValueError("Некоректний додаток шаблону")
        parts.append("\n" + "=" * 30)
        parts.append("ДОДАТОК: " + _plain(appendix.get("title")))
        parts.extend(_format_blocks(appendix.get("blocks", []), budget=budget))
    content = "\n\n".join(piece for piece in parts if piece.strip())
    if len(content) > MAX_PREVIEW_CHARS:
        raise ValueError("Документ завеликий для перегляду")
    return content


def load_template_preview(root: Path, app_version: str, template_id: str,
                          revision_id: str) -> TemplatePreview:
    """Load one verified revision without writing or executing its contents.

    The catalog is revalidated before dereferencing the requested ID. Any
    changed bytes after the catalog scan fail the second SHA-256 check. Neither
    paths from UI inputs nor unlisted files are opened. For offline tests this
    works against a temporary package, not real user documents.
    """
    root = Path(root)
    snapshot = inspect_library(root, app_version)
    if snapshot.status != "AVAILABLE":
        raise ValueError(snapshot.message)

    matches = [item for item in snapshot.templates
               if item.template_id == template_id and item.revision_id == revision_id]
    if len(matches) != 1:
        raise ValueError("Редакцію шаблону не знайдено в перевіреній бібліотеці")
    selected = matches[0]

    manifest = _object(_read_bytes(_safe_path(root, "manifest.json"), 1024 * 1024), "manifest")
    items = [item for item in manifest["items"]
             if item.get("template_id") == template_id
             and item.get("revision_id") == revision_id
             and item.get("path") == selected.path]
    files = [entry for entry in manifest["files"] if entry.get("path") == selected.path]
    if len(items) != 1 or len(files) != 1:
        raise ValueError("Неоднозначна редакція або файл шаблону")

    raw = _read_bytes(_safe_path(root, selected.path), MAX_TEMPLATE_BYTES)
    expected = files[0]
    if len(raw) != expected["size_bytes"] or hashlib.sha256(raw).hexdigest() != expected["sha256"]:
        raise ValueError("Файл шаблону змінено після перевірки")
    data = _object(raw, selected.path)
    _validate_template(data, items[0])

    vars_ = tuple(
        PreviewVariable(
            name=v["name"],
            label=_plain(v.get("label")) or v["name"],
            variable_type=v["type"],
            required=v["required"],
        )
        for v in data["variables"]
    )
    return TemplatePreview(
        title=selected.title,
        template_id=selected.template_id,
        revision_id=selected.revision_id,
        package_version=snapshot.package_version,
        category_id=selected.category_id,
        description=_plain(data.get("description")),
        legal_review=_plain(data.get("legal_review")) or "not_checked",
        content=_render(data),
        variables=vars_,
        source_notes=_plain(data.get("source_notes")),
    )
