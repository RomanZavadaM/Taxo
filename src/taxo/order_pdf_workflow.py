# -*- coding: utf-8 -*-
"""Safe multi-format output for Taxo operations orders.

One user-selected document can be generated as DOCX, PDF, multipage JPG,
or all three. Reuses the existing safe writer, internal viewer, and PDFium.
"""
from pathlib import Path
import re
import shutil
import tempfile

from output_files import next_output_copy_path
from order_document_formats import build_order_docx, pdf_page_count, render_order_jpg_pages

ORDER_FORMATS = ("docx", "pdf", "jpg")


def order_pdf_path(output_dir, order):
    """Choose a readable PDF filename without overwriting an earlier print."""
    number = re.sub(r'[^\w.-]+', '-', str(order["order_no"] or ""), flags=re.UNICODE).strip(".-_") or "без-номера"
    day = re.sub(r'[^0-9.-]+', '-', str(order["order_date"] or "")).strip(".-_") or "без-дати"
    target = Path(output_dir) / ("Наказ_%s_%s.pdf" % (number, day))
    return next_output_copy_path(target) if target.exists() else target


def _unique_order_base(output_dir, order):
    """Keep all formats from one generation together; preserve old copies."""
    candidate = order_pdf_path(output_dir, order)
    while (
        candidate.exists()
        or candidate.with_suffix(".docx").exists()
        or list(candidate.parent.glob(candidate.stem + "_сторінка_*.jpg"))
    ):
        candidate = next_output_copy_path(candidate)
    return candidate.with_name(candidate.name[:-4])


def generate_order_formats(core, ops, order, assignments=(), entities=(),
                           company=None, control="", formats=("pdf",), parent=None):
    """Return actual saved files grouped by format; never claim an unsaved file.

    PDF and JPG use the existing PDF renderer as their sole print source.
    JPG can have any number of pages. DOCX uses the same order preview data.
    No Word/LibreOffice binary or unapproved dependency is required.
    """
    selected = tuple(dict.fromkeys(str(fmt).lower() for fmt in formats))
    if not selected or set(selected) - set(ORDER_FORMATS):
        raise ValueError("Виберіть DOCX, PDF, JPG або всі три формати.")
    company = company or {}
    base = _unique_order_base(core.OUTPUT_DIR, order)
    base.parent.mkdir(parents=True, exist_ok=True)
    saved = {}
    if "docx" in selected:
        result = core.write_output_file(
            lambda out: build_order_docx(
                out, ops, order, assignments, entities, company, control
            ), base.with_name(base.name + ".docx"), parent=parent,
            kind="DOCX наказу", error_title="Наказ Word",
        )
        if result is None:
            return saved
        saved["docx"] = (Path(result),)

    if "pdf" not in selected and "jpg" not in selected:
        return saved

    font = next((p for p in core.report_font_candidates() if core.Path(p).exists()), None)
    with tempfile.TemporaryDirectory(prefix="taxo_order_") as scratch:
        temporary_pdf = Path(scratch) / "order.pdf"
        pdf_result = None
        if "pdf" in selected:
            pdf_result = core.write_output_file(
                lambda out: ops.export_order_pdf(
                    out, order, assignments, company, control, font_path=font
                ), base.with_name(base.name + ".pdf"), parent=parent,
                kind="PDF наказу", error_title="Наказ PDF",
            )
            if pdf_result is None:
                return saved
            saved["pdf"] = (Path(pdf_result),)
        if "jpg" in selected:
            source = Path(pdf_result) if pdf_result is not None else temporary_pdf
            if pdf_result is None:
                ops.export_order_pdf(
                    source, order, assignments, company, control, font_path=font
                )
            count = pdf_page_count(source)
            if not 1 <= count <= 100:
                raise ValueError("Недопустима кількість сторінок PDF наказу.")
            temporary_pages = [
                Path(scratch) / ("page_%03d.jpg" % index)
                for index in range(1, count + 1)
            ]
            render_order_jpg_pages(source, temporary_pages)
            jpg_paths = []
            for number, temp_file in enumerate(temporary_pages, 1):
                output = base.with_name(
                    base.name + "_сторінка_%02d.jpg" % number
                )
                actual = core.write_output_file(
                    lambda out, src=temp_file: shutil.copyfile(src, out),
                    output, parent=parent,
                    kind="JPG наказу", error_title="Наказ JPG",
                )
                if actual is None:
                    if jpg_paths:
                        saved["jpg"] = tuple(jpg_paths)
                    return saved
                jpg_paths.append(Path(actual))
            saved["jpg"] = tuple(jpg_paths)
    return saved


def open_order_format(core, paths, parent, external=False):
    """Preview with Taxo, or open the exact file in its OS-associated app."""
    if not paths:
        return None
    target = Path(paths[0])
    if external:
        core.open_external(target)
    else:
        core.open_document(parent, target, external_opener=core.open_external)
    return target


def save_and_preview_order(core, ops, order, assignments, company, control, parent):
    """Compatibility: existing one-click PDF and Taxo-preview workflow."""
    try:
        saved = generate_order_formats(
            core, ops, order, assignments, (), company, control,
            formats=("pdf",), parent=parent,
        )
        paths = saved.get("pdf", ())
        if not paths:
            return None
        try:
            return open_order_format(core, paths, parent)
        except Exception as exc:
            core.messagebox.showwarning(
                "Наказ PDF",
                "PDF збережено, але автоматичний перегляд не відкрився:\n%s\n\n%s"
                % (paths[0], exc),
                parent=parent,
            )
            return paths[0]
    except Exception as exc:
        core.messagebox.showerror("Наказ PDF", str(exc), parent=parent)
        return None
