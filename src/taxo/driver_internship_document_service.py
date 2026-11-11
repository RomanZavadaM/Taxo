# -*- coding: utf-8 -*-
"""Document production boundary for driver internship and control-drive sheets.

The Tk UI collects and validates user input. This module owns the document-side
operation: build the existing editable DOCX, save it in the existing
PaperDocuments catalog, and open the saved file. Creating the document does not
record completed hours, signatures, or a decision to admit the driver to work.
"""
from __future__ import annotations

from datetime import date

import paper_documents as paperwork
import paper_document_store as document_store


def save_internship_document(workspace_root, data):
    """Build and persist one internship sheet without changing catalog rules."""
    driver_name = str(data.get("driver") or "")
    training_kind = str(data.get("training_kind") or "")

    return document_store.save_document(
        workspace_root,
        paperwork.build_training_docx(data),
        "Стажування",
        training_kind + ": " + driver_name,
        date.today().isoformat(),
        driver_name,
    )


def open_internship_document(path):
    """Open a saved internship sheet through the cross-platform document handler."""
    return document_store.open_file(path)
