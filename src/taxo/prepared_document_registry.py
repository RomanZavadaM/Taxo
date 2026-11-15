# -*- coding: utf-8 -*-
"""Register a generated DOCX from an immutable prepared snapshot in Taxo.

This is a bridge to the existing PaperDocuments catalog, not a new archive.
No external/exported file is silently imported, and no business fact or
signature is inferred from the existence of an editable DOCX.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from paper_document_store import (
    catalog_dir,
    list_documents,
    save_document,
)
from prepared_document_docx import build_prepared_snapshot_docx
from prepared_document_store import load_prepared_snapshot


def register_prepared_document(workspace_root: Path, snapshot_id: str) -> Path:
    """Explicitly register one snapshot-backed editable DOCX; reject duplicates."""
    workspace_root = Path(workspace_root)
    snapshot = load_prepared_snapshot(workspace_root, snapshot_id)
    for row in list_documents(workspace_root):
        if row.get("prepared_snapshot_id") == snapshot_id:
            raise ValueError("Ця підготовлена чернетка вже є у каталозі документів.")

    data = snapshot.data
    source = data["source"]
    document = build_prepared_snapshot_docx(snapshot)
    # created_at is a technical registration date, NOT the document's
    # effective date/issue date, which has not been confirmed by a user.
    day = datetime.fromisoformat(snapshot.summary.created_at).date().isoformat()
    provenance = {
        "origin": "prepared_snapshot",
        "document_status": "prepared",
        "prepared_snapshot_id": snapshot.summary.snapshot_id,
        "company_template_id": source["company_template_id"],
        "template_revision": source["edit_revision"],
        "template_source_sha256": source["source_sha256"],
    }
    path = save_document(
        workspace_root, document,
        "Підготовлений документ", data["title"], day,
        metadata=provenance,
    )
    if path.parent != catalog_dir(workspace_root):
        raise ValueError("Файл збережено поза каталогом Taxo")
    return path
