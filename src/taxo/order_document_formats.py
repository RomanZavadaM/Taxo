# -*- coding: utf-8 -*-
"""DOCX and multipage JPG for orders, using Taxo's existing permissive libraries.

DOCX is an editable text rendition of the same frozen order preview;
JPG pages are rendered directly from the printable PDF via PDFium.
No office application is required to *create* any output format.
"""
from pathlib import Path


def build_order_docx(path, ops, order, assignments=(), entities=(),
                     company=None, control_name=""):
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Mm, Pt

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
    base = doc.styles["Normal"]
    base.font.name = "Times New Roman"
    base.font.size = Pt(11)
    text = ops.order_preview_text(
        order, assignments=assignments, entities=entities,
        company=company, control_name=control_name,
    )
    for index, line in enumerate(text.splitlines()):
        paragraph = doc.add_paragraph()
        if index in (0, 1) or line == "Н А К А З У Ю:":
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run(line)
        if index == 0 or line == "Н А К А З У Ю:":
            run.bold = True
        if index == 0:
            run.font.size = Pt(15)
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
