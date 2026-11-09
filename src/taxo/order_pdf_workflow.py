# -*- coding: utf-8 -*-
"""Shared, safe PDF-save and in-app preview workflow for operations orders.

The document layout remains owned by operations_orders.export_order_pdf.
This module only coordinates file identity, atomic saving, and viewing.
"""
from pathlib import Path
import re

from output_files import next_output_copy_path


def order_pdf_path(output_dir, order):
    """Choose a readable filename without overwriting an earlier print."""
    number = re.sub(r'[^\w.-]+', '-', str(order["order_no"] or ""), flags=re.UNICODE).strip(".-_") or "без-номера"
    day = re.sub(r'[^0-9.-]+', '-', str(order["order_date"] or "")).strip(".-_") or "без-дати"
    target = Path(output_dir) / ("Наказ_%s_%s.pdf" % (number, day))
    return next_output_copy_path(target) if target.exists() else target


def save_and_preview_order(core, ops, order, assignments, company, control, parent):
    """Save via Taxo's shared safe writer, then open the actual PDF in Taxo.

    A cancelled/failed save never opens a stale previous PDF. The writer
    leaves any earlier file intact and can offer a new copy on file locks.
    """
    target = order_pdf_path(core.OUTPUT_DIR, order)
    font = next((p for p in core.report_font_candidates() if core.Path(p).exists()), None)
    actual = core.write_output_file(
        lambda out: ops.export_order_pdf(
            out, order, assignments, company, control, font_path=font
        ),
        target,
        parent=parent,
        kind="PDF наказу",
        error_title="Наказ PDF",
    )
    if actual is None:
        return None
    try:
        core.open_document(parent, actual, external_opener=core.open_external)
    except Exception as exc:
        core.messagebox.showwarning(
            "Наказ PDF",
            "PDF збережено, але автоматичний перегляд не відкрився:\n%s\n\n%s"
            % (actual, exc),
            parent=parent,
        )
    return actual
