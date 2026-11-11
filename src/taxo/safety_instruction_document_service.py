# -*- coding: utf-8 -*-
"""Document production boundary for safety briefing preparation.

The Tk UI collects user input. This module owns the document-side operation:
build the existing editable DOCX, save it in the existing PaperDocuments
catalog, and open the saved file. It never records a signature or infers that
an instruction was actually conducted.
"""
from __future__ import annotations

import paper_documents as paperwork
import paper_document_store as document_store


def save_briefing_document(workspace_root, prepared):
    """Build and persist one prepared briefing without changing catalog rules."""
    if not str(prepared.get("program_text") or "").strip():
        raise ValueError(
            "Текст програми порожній. Відкрийте «Текст програми…» та перевірте його."
        )
    return document_store.save_document(
        workspace_root,
        paperwork.build_briefing_docx(prepared),
        "Інструктаж",
        prepared["topic"],
        prepared["day"].isoformat(),
        ", ".join(prepared["people"]),
    )


def open_briefing_document(path):
    """Open a saved briefing through the existing cross-platform document handler."""
    return document_store.open_file(path)
