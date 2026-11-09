# -*- coding: utf-8 -*-
"""Editable Word order from Taxo's shared printable layout; PDFium JPG export.

Word and PDF use exactly the same content sections, metadata and assignment
table. Word's installed fonts/layout engine can still affect line wrapping.
No Word or LibreOffice process is required for DOCX generation.
"""
from pathlib import Path

from order_layout import order_layout


def build_order_docx(path, ops, order, assignments=(), entities=(),
                     company=None, control_name="", appendices=()):
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Mm, Pt

    layout = order_layout(ops, order, assignments, company, control_name)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    section = doc.sections[0]
    section.page_height = Mm(297)
    section.page_width = Mm(210)
    section.left_margin = Mm(20)
    section.right_margin = Mm(18)
    section.top_margin = Mm(17)
    section.bottom_margin = Mm(17)
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11.5)
    style.paragraph_format.space_after = Pt(0)
    style.paragraph_format.line_spacing = 1.15

    def para(value, *, center=False, bold=False, before=0, after=0, size=None):
        p = doc.add_paragraph()
        if center:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.space_after = Pt(after)
        run = p.add_run(str(value))
        run.bold = bold
        if size:
            run.font.size = Pt(size)
        return p

    def put_cell(cell, value, align=None, bold=False):
        p = cell.paragraphs[0]
        if align is not None:
            p.alignment = align
        run = p.add_run(str(value))
        run.bold = bool(bold)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    def border_table(table):
        tbl_pr = table._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement("w:" + edge)
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "4")
            borders.append(el)
        tbl_pr.append(borders)

    para(layout["heading"], center=True, bold=True, after=2, size=15)
    para(layout["company"], center=True, after=20)
    meta = doc.add_table(rows=1, cols=3)
    meta.autofit = False
    for cell, width in zip(meta.rows[0].cells, (55, 55, 55)):
        cell.width = Mm(width)
    for cell, value, align in zip(
        meta.rows[0].cells,
        (layout["date"], layout["number"], layout["place"]),
        (WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT),
    ):
        put_cell(cell, value, align=align, bold=value == layout["number"])
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    if layout["subject"]:
        para(layout["subject"], bold=True, after=14)
    if layout["preamble"]:
        para(layout["preamble"], after=18)
    para(layout["instruction_heading"], center=True, bold=True, after=14, size=12.5)

    if layout["is_assignment"]:
        if layout["paragraphs"]:
            para(layout["paragraphs"][0], after=9)
        table = doc.add_table(rows=1, cols=4)
        table.autofit = False
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        widths=(10,52,38,65)
        for i, value in enumerate(layout["table_headers"]):
            table.columns[i].width = Mm(widths[i])
            put_cell(table.rows[0].cells[i], value,
                     align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
        for row in layout["assignment_rows"]:
            cells=table.add_row().cells
            for i, value in enumerate(row):
                put_cell(cells[i], value)
        # Repeat the table header on subsequent pages, like ReportLab.
        header = table.rows[0]._tr.get_or_add_trPr()
        header.append(OxmlElement("w:tblHeader"))
        border_table(table)
        doc.add_paragraph().paragraph_format.space_after=Pt(10)
        for item in layout["paragraphs"][1:]:
            para(item, after=3)
    else:
        for item in layout["paragraphs"]:
            para(item, after=6)

    sig=doc.add_table(rows=1, cols=3)
    sig.autofit=False
    for cell, width in zip(sig.rows[0].cells,(60,45,55)):
        cell.width=Mm(width)
    for cell, value, align in zip(
        sig.rows[0].cells, layout["signature"],
        (WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT)
    ):
        put_cell(cell,value,align=align)

    if entities:
        doc.add_page_break()
        para("Структурований перелік працівників і транспортних засобів",
             center=True,bold=True,after=8)
        para("до наказу від %s %s" % (layout["date"],layout["number"]),
             center=True,after=18)
        entity_table=doc.add_table(rows=1,cols=5)
        entity_table.autofit=False
        for i,title in enumerate(("№","Тип","Роль / призначення","Працівник / ТЗ","Однозначний реквізит")):
            put_cell(entity_table.rows[0].cells[i],title,align=WD_ALIGN_PARAGRAPH.CENTER,bold=True)
        for index, entity in enumerate(entities,1):
            view=ops.order_entity_view(entity)
            values=(str(index),view["type_label"],view["role"],view["display"],view["identifier"])
            cells=entity_table.add_row().cells
            for i,value in enumerate(values):
                put_cell(cells[i],value)
        entity_table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
        border_table(entity_table)
        para("Перелік сформовано зі структурованих записів Taxo. "
             "Ідентифікаційні реквізити зафіксовано на момент додавання до чернетки наказу.",
             before=8)

    for index, appendix in enumerate(appendices,1):
        doc.add_page_break()
        seq = appendix["sequence_no"] or index
        p=para("Додаток %s\nдо наказу від %s %s" % (seq,layout["date"],layout["number"]),
               after=26)
        p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
        para(appendix["title"] or "Додаток",center=True,bold=True,after=20)
        for line in str(appendix["content"] or "").splitlines():
            if line.strip():
                para(line.strip(),after=7)

    doc.save(str(path))
    return path


def render_order_jpg_pages(pdf_path, targets, dpi=180, quality=92):
    """Render every page (not only the first two) and close PDFium cleanly."""
    from pdf_engine import PdfDocument
    doc = PdfDocument(Path(pdf_path))
    try:
        count = len(doc)
        if count < 1:
            raise ValueError("PDF наказу не містить сторінок.")
        if len(targets) != count:
            raise ValueError("Кількість JPG-сторінок не збігається з PDF.")
        for index, target in enumerate(targets):
            image = doc.render(index, dpi / 72.0)
            image.save(str(target), "JPEG", quality=int(quality))
    finally:
        doc.close()
    return tuple(Path(target) for target in targets)


def pdf_page_count(path):
    from pdf_engine import PdfDocument
    doc = PdfDocument(Path(path))
    try:
        return len(doc)
    finally:
        doc.close()
