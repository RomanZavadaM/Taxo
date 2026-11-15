# -*- coding: utf-8 -*-
"""PDF copy of one exact controlled prepared DOCX revision.

The PDF is an output copy for preview/printing. It does not alter the DOCX,
revision history, document status, signature state or any business facts.
Only existing permissive Taxo dependencies are used: python-docx + ReportLab.
"""
from __future__ import annotations

import hashlib
import io
import os
import re
import uuid
from pathlib import Path
from xml.sax.saxutils import escape

from docx import Document
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxParagraph

from prepared_document_revision import load_controlled_prepared_revision
from prepared_document_pdf_images import (
    apply_paragraph_image_alignment,
    ensure_supported_drawing_scope,
    paragraph_fragments,
)

_BAD_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(("COM%d" % i) for i in range(1, 10)),
    *(("LPT%d" % i) for i in range(1, 10)),
}
MAX_PDF_BLOCKS = 12000
MAX_TABLE_CELLS = 150000
MAX_TEXT_CHARS = 2_000_000


def suggested_prepared_pdf_name(record):
    """Portable, human-readable PDF name for one catalog revision."""
    if not isinstance(record, dict):
        raise ValueError("Некоректний запис prepared-документа")
    value = _BAD_FILENAME.sub("_", str(record.get("title") or "")).strip(" .")
    value = re.sub(r"\s+", " ", value) or "Підготовлений документ"
    if value.upper() in _RESERVED_NAMES:
        value = "_" + value
    value = value[:105].rstrip(" .") or "Підготовлений документ"
    revision = record.get("document_revision")
    if type(revision) is not int or revision < 1:
        revision = 1
    suffix = str(record.get("id") or "")[-8:] or "prepared"
    return "%s_r%d_%s.pdf" % (value, revision, suffix)


def _font(font_path):
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    if font_path is None:
        raise ValueError(
            "Не знайдено шрифт з підтримкою українського тексту для PDF"
        )
    path = Path(font_path)
    if not path.is_file():
        raise ValueError("Не знайдено шрифт для PDF")
    name = "TaxoPrepared_" + hashlib.sha256(
        str(path.resolve()).encode("utf-8")
    ).hexdigest()[:12]
    if name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(name, str(path)))
        pdfmetrics.registerFontFamily(
            name,
            normal=name,
            bold=name,
            italic=name,
            boldItalic=name,
        )
    return name


def _iter_blocks(document):
    for child in document.element.body.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            yield DocxParagraph(child, document)
        elif tag == "tbl":
            yield DocxTable(child, document)


def _paragraph_style(paragraph, styles):
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT

    name = str(getattr(paragraph.style, "name", "") or "")
    if name.lower().startswith("heading"):
        digits = "".join(ch for ch in name if ch.isdigit())
        level = int(digits) if digits else 2
        return styles["heading%d" % max(1, min(level, 3))]

    style = styles["normal"].clone("TaxoParagraph")
    alignment = paragraph.alignment
    mapping = {
        WD_ALIGN_PARAGRAPH.LEFT: TA_LEFT,
        WD_ALIGN_PARAGRAPH.CENTER: TA_CENTER,
        WD_ALIGN_PARAGRAPH.RIGHT: TA_RIGHT,
        WD_ALIGN_PARAGRAPH.JUSTIFY: TA_JUSTIFY,
    }
    if alignment is not None:
        style.alignment = mapping.get(alignment, TA_LEFT)
    if name.startswith("List Bullet"):
        style.leftIndent = 14
        style.firstLineIndent = -8
    elif name.startswith("List Number"):
        style.leftIndent = 14
        style.firstLineIndent = -8
    return style


def _paragraph_story(
    paragraph,
    styles,
    budget,
    image_budget,
    *,
    max_image_width,
    max_image_height,
    allow_page_break=True,
):
    from reportlab.platypus import PageBreak, Paragraph, Spacer

    page_break = 'w:type="page"' in paragraph._p.xml
    if page_break and not allow_page_break:
        raise ValueError(
            "DOCX містить розрив сторінки всередині таблиці; "
            "цей layout Taxo поки не переносить у PDF."
        )

    fragments = paragraph_fragments(
        paragraph,
        image_budget,
        max_width_pt=max_image_width,
        max_height_pt=max_image_height,
    )
    result = []
    style_name = str(getattr(paragraph.style, "name", "") or "")
    prefix = ""
    if style_name.startswith("List Bullet"):
        prefix = "• "
    elif style_name.startswith("List Number"):
        prefix = "• "

    text_seen = False
    content_seen = False
    for fragment in fragments:
        if fragment.kind == "text":
            text = str(fragment.value or "")
            if not text:
                continue
            if not text_seen and prefix:
                text = prefix + text
            text_seen = True
            budget["chars"] += len(text)
            if budget["chars"] > MAX_TEXT_CHARS:
                raise ValueError("DOCX містить забагато тексту для PDF")
            safe = escape(text).replace("\n", "<br/>")
            result.append(
                Paragraph(safe, _paragraph_style(paragraph, styles))
            )
            content_seen = True
        elif fragment.kind == "image":
            result.append(
                apply_paragraph_image_alignment(
                    fragment.value, paragraph
                )
            )
            content_seen = True
        else:
            raise ValueError("Невідомий фрагмент DOCX під час PDF-export")

    if not content_seen and not page_break:
        result.append(Spacer(1, 5))
    if page_break:
        result.append(PageBreak())
    return result


def _table_story(table, font_name, budget, image_budget):
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph, Table, TableStyle

    source_rows = [list(row.cells) for row in table.rows]
    width = max((len(row) for row in source_rows), default=0)
    if not source_rows or width < 1:
        return []
    if width > 40:
        raise ValueError("DOCX містить таблицю з надмірною кількістю колонок")
    if any(len(row) != width for row in source_rows):
        raise ValueError("DOCX містить нерівну таблицю")

    cell_style = ParagraphStyle(
        "TaxoPreparedCell",
        fontName=font_name,
        fontSize=8.5,
        leading=10.5,
    )
    cell_styles = {
        "normal": cell_style,
        "heading1": cell_style,
        "heading2": cell_style,
        "heading3": cell_style,
    }
    max_cell_image_width = max(45.0, min(150.0, 470.0 / width))
    rows = []
    for source_row in source_rows:
        values = []
        for cell in source_row:
            budget["cells"] += 1
            if budget["cells"] > MAX_TABLE_CELLS:
                raise ValueError("DOCX містить завелику таблицю для PDF")
            if cell.tables:
                raise ValueError(
                    "DOCX містить вкладену таблицю; "
                    "цей layout Taxo поки не переносить у PDF."
                )
            story = []
            for paragraph in cell.paragraphs:
                story.extend(
                    _paragraph_story(
                        paragraph,
                        cell_styles,
                        budget,
                        image_budget,
                        max_image_width=max_cell_image_width,
                        max_image_height=180.0,
                        allow_page_break=False,
                    )
                )
            values.append(
                story or [Paragraph(" ", cell_style)]
            )
        rows.append(values)
    result = Table(rows, repeatRows=1 if len(rows) > 1 else 0, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return [result]


def build_prepared_revision_pdf(
    workspace_root,
    document_id,
    target,
    *,
    font_path=None,
    overwrite=False,
):
    """Render the selected controlled DOCX revision into a separate PDF copy."""
    controlled = load_controlled_prepared_revision(
        workspace_root, document_id
    )
    try:
        document = Document(io.BytesIO(controlled.payload))
    except Exception as exc:
        raise ValueError("Не вдалося прочитати контрольований DOCX") from exc

    ensure_supported_drawing_scope(document)

    target = Path(target)
    if target.suffix.lower() != ".pdf":
        raise ValueError("Файл для перегляду/друку має мати розширення .pdf")
    if not target.parent.is_dir() or target.parent.is_symlink():
        raise ValueError("Некоректна папка для PDF")
    if target.exists():
        if target.is_symlink() or not target.is_file():
            raise ValueError("Некоректний цільовий PDF")
        if not overwrite:
            raise FileExistsError("PDF уже існує")

    font_name = _font(font_path)
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate

    styles = {
        "normal": ParagraphStyle(
            "TaxoPreparedNormal",
            fontName=font_name,
            fontSize=10.5,
            leading=13.2,
            spaceAfter=4,
        ),
        "heading1": ParagraphStyle(
            "TaxoPreparedHeading1",
            fontName=font_name,
            fontSize=15,
            leading=18,
            spaceBefore=7,
            spaceAfter=7,
        ),
        "heading2": ParagraphStyle(
            "TaxoPreparedHeading2",
            fontName=font_name,
            fontSize=13,
            leading=16,
            spaceBefore=6,
            spaceAfter=6,
        ),
        "heading3": ParagraphStyle(
            "TaxoPreparedHeading3",
            fontName=font_name,
            fontSize=11.5,
            leading=14,
            spaceBefore=5,
            spaceAfter=5,
        ),
    }

    budget = {"blocks": 0, "cells": 0, "chars": 0}
    image_budget = {"count": 0}
    story = []
    for block in _iter_blocks(document):
        budget["blocks"] += 1
        if budget["blocks"] > MAX_PDF_BLOCKS:
            raise ValueError("DOCX містить забагато блоків для PDF")
        if isinstance(block, DocxParagraph):
            story.extend(
                _paragraph_story(
                    block,
                    styles,
                    budget,
                    image_budget,
                    max_image_width=470.0,
                    max_image_height=650.0,
                )
            )
        else:
            story.extend(
                _table_story(
                    block, font_name, budget, image_budget
                )
            )

    if not story:
        from reportlab.platypus import Paragraph
        empty = styles["normal"].clone("TaxoEmpty")
        empty.alignment = TA_CENTER
        story.append(Paragraph("(Документ не містить тексту для PDF.)", empty))

    temp = target.with_name(".%s.%s.tmp" % (target.name, uuid.uuid4().hex))
    try:
        pdf = SimpleDocTemplate(
            str(temp),
            pagesize=A4,
            leftMargin=20 * mm,
            rightMargin=17 * mm,
            topMargin=17 * mm,
            bottomMargin=17 * mm,
            title=str(controlled.record.get("title") or ""),
            author="Taxo",
        )
        pdf.build(story)
        with temp.open("rb+") as stream:
            if stream.read(5) != b"%PDF-":
                raise ValueError("PDF не був створений коректно")
            stream.flush()
            os.fsync(stream.fileno())
        if target.exists() and not overwrite:
            raise FileExistsError("PDF уже існує")
        os.replace(temp, target)
    finally:
        try:
            if temp.exists():
                temp.unlink()
        except OSError:
            pass
    return target
