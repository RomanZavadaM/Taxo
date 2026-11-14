# -*- coding: utf-8 -*-
"""Editable DOCX export from one verified immutable PreparedDocuments snapshot.

The exporter deliberately renders the persisted snapshot. It never reloads a
CompanyTemplates revision and never creates a business fact, PDF, print job,
final archive entry, scan or signature state.
"""
from __future__ import annotations

import os
import re
import uuid
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

from prepared_document_codec import validate_snapshot_payload
from prepared_document_store import PreparedDocumentSnapshot, load_prepared_snapshot

MAX_DOCX_BLOCKS = 8000
MAX_DOCX_DEPTH = 18
MAX_DOCX_TABLE_CELLS = 120000
MAX_DOCX_TEXT_CHARS = 2_000_000
_BAD_XML = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_BAD_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(("COM%d" % i) for i in range(1, 10)),
    *(("LPT%d" % i) for i in range(1, 10)),
}


def _text(value: object, label: str = "текст") -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float, bool)):
        value = str(value)
    if not isinstance(value, str):
        raise ValueError("%s має бути текстом" % label)
    if len(value) > MAX_DOCX_TEXT_CHARS:
        raise ValueError("%s перевищує допустимий розмір" % label)
    if _BAD_XML.search(value):
        raise ValueError("%s містить недопустимий керуючий символ" % label)
    return value


def suggested_docx_name(title: str, snapshot_id: str) -> str:
    """Return a portable filename suggestion; never a path."""
    value = _BAD_FILENAME.sub("_", str(title or "")).strip(" .")
    value = re.sub(r"\s+", " ", value) or "Підготовлений документ"
    if value.upper() in _RESERVED_NAMES:
        value = "_" + value
    value = value[:110].rstrip(" .") or "Підготовлений документ"
    suffix = str(snapshot_id or "")[-8:] or "snapshot"
    return "%s_%s.docx" % (value, suffix)


def _provenance(snapshot: PreparedDocumentSnapshot) -> str:
    source = snapshot.data["source"]
    return (
        "Taxo prepared snapshot %s; company template %s; "
        "edit revision %s; source SHA-256 %s"
        % (
            snapshot.summary.snapshot_id,
            source["company_template_id"],
            source["edit_revision"],
            source["source_sha256"],
        )
    )


def _add_note(doc, value: object) -> None:
    note = _text(value, "Примітка")
    if not note:
        return
    paragraph = doc.add_paragraph()
    run = paragraph.add_run("Примітка: " + note)
    run.italic = True
    run.font.size = Pt(9)


def _table(doc, columns: object, rows: object, budget: dict) -> None:
    if not isinstance(columns, list) or not isinstance(rows, list):
        raise ValueError("Некоректна таблиця prepared snapshot-а")
    width = len(columns)
    if width == 0 and rows:
        first = rows[0]
        if not isinstance(first, list) or not first:
            raise ValueError("Некоректний рядок таблиці")
        width = len(first)
    if width < 1:
        raise ValueError("Таблиця prepared snapshot-а не має колонок")
    if width > 100:
        raise ValueError("Таблиця prepared snapshot-а має забагато колонок")
    budget["cells"] += width * (len(rows) + (1 if columns else 0))
    if budget["cells"] > MAX_DOCX_TABLE_CELLS:
        raise ValueError("Prepared snapshot містить завелику таблицю")

    table = doc.add_table(rows=1 if columns else 0, cols=width)
    table.style = "Table Grid"
    if columns:
        for index, value in enumerate(columns):
            table.rows[0].cells[index].text = _text(value, "Назва колонки")
    for row in rows:
        if not isinstance(row, list) or len(row) != width:
            raise ValueError("Кількість клітинок таблиці не збігається з колонками")
        cells = table.add_row().cells
        for index, value in enumerate(row):
            cells[index].text = _text(value, "Клітинка таблиці")


def _blocks(doc, blocks: object, budget: dict, depth: int = 0) -> None:
    if depth > MAX_DOCX_DEPTH:
        raise ValueError("Prepared snapshot містить занадто глибоку структуру")
    if not isinstance(blocks, list):
        raise ValueError("Prepared snapshot має некоректну структуру блоків")

    for block in blocks:
        budget["blocks"] += 1
        if budget["blocks"] > MAX_DOCX_BLOCKS:
            raise ValueError("Prepared snapshot містить забагато блоків")
        if not isinstance(block, dict):
            raise ValueError("Prepared snapshot містить некоректний блок")

        kind = block.get("type")
        value = _text(block.get("text", ""), "Текст блоку")
        if kind == "heading":
            level = block.get("level", 2)
            if type(level) is not int or level < 1:
                level = 2
            doc.add_heading(value, level=min(level, 9))
        elif kind == "paragraph":
            doc.add_paragraph(value)
        elif kind in ("numbered_list", "bullet_list"):
            items = block.get("items", [])
            if not isinstance(items, list):
                raise ValueError("Prepared snapshot містить некоректний список")
            style = "List Number" if kind == "numbered_list" else "List Bullet"
            for item in items:
                doc.add_paragraph(_text(item, "Елемент списку"), style=style)
        elif kind in ("table", "dynamic_table"):
            _table(doc, block.get("columns", []), block.get("rows", []), budget)
        elif kind == "page_break":
            doc.add_page_break()
        elif kind in ("signature_placeholder", "attachment_reference", "figure"):
            labels = {
                "signature_placeholder": "Місце для підпису",
                "attachment_reference": "Посилання на додаток",
                "figure": "Ілюстрація",
            }
            doc.add_paragraph(
                "[%s]%s" % (labels[kind], (" " + value) if value else "")
            )
        else:
            raise ValueError(
                "Непідтримуваний тип блоку prepared snapshot-а: %s" % kind
            )

        if block.get("notes"):
            _add_note(doc, block["notes"])
        if "children" in block:
            _blocks(doc, block["children"], budget, depth + 1)


def build_prepared_snapshot_docx(snapshot: PreparedDocumentSnapshot):
    """Build an editable python-docx Document from verified snapshot data."""
    if not isinstance(snapshot, PreparedDocumentSnapshot):
        raise TypeError("Очікується перевірений PreparedDocumentSnapshot")
    data = validate_snapshot_payload(
        snapshot.data,
        expected_id=snapshot.summary.snapshot_id,
    )
    rendered = data["rendered_template"]
    if not isinstance(rendered, dict):
        raise ValueError("Prepared snapshot не має rendered structure")

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(1.7)
    section.bottom_margin = Cm(1.7)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(1.7)
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(4)

    provenance = _provenance(snapshot)
    props = doc.core_properties
    props.title = _text(data["title"], "Назва документа")
    props.subject = "Taxo prepared snapshot " + snapshot.summary.snapshot_id
    props.comments = provenance

    budget = {"blocks": 0, "cells": 0}
    _blocks(doc, rendered.get("blocks"), budget)
    appendices = rendered.get("appendices", [])
    if not isinstance(appendices, list):
        raise ValueError("Prepared snapshot має некоректні додатки")
    for appendix in appendices:
        if not isinstance(appendix, dict):
            raise ValueError("Prepared snapshot має некоректний додаток")
        doc.add_page_break()
        title = _text(appendix.get("title", ""), "Назва додатка")
        if title:
            doc.add_heading(title, level=1)
        _blocks(doc, appendix.get("blocks", []), budget)

    footer = doc.sections[0].footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = footer.add_run(provenance)
    run.font.size = Pt(7)
    return doc


def export_prepared_snapshot_docx(
    workspace_root: Path,
    snapshot_id: str,
    target: Path,
    *,
    overwrite: bool = False,
) -> Path:
    """Load one exact snapshot, render it and atomically publish a DOCX file."""
    snapshot = load_prepared_snapshot(Path(workspace_root), snapshot_id)
    document = build_prepared_snapshot_docx(snapshot)
    target = Path(target)
    if target.suffix.lower() != ".docx":
        raise ValueError("Файл підготовленого документа має мати розширення .docx")
    parent = target.parent
    if not parent.is_dir() or parent.is_symlink():
        raise ValueError("Некоректна папка для DOCX")
    if target.exists():
        if target.is_symlink() or not target.is_file():
            raise ValueError("Некоректний цільовий файл DOCX")
        if not overwrite:
            raise FileExistsError("DOCX уже існує")

    temp = target.with_name(".%s.%s.tmp" % (target.name, uuid.uuid4().hex))
    try:
        document.save(str(temp))
        with temp.open("rb+") as stream:
            os.fsync(stream.fileno())
        if target.exists() and not overwrite:
            raise FileExistsError("DOCX уже існує")
        os.replace(temp, target)
    finally:
        try:
            if temp.exists():
                temp.unlink()
        except OSError:
            pass
    return target
