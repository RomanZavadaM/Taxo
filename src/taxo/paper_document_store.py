# -*- coding: utf-8 -*-
"""Persist and open generated paper documents in the workspace."""
from __future__ import annotations

import json
import os
import re
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

CATALOG_NAME = "index.json"


def catalog_dir(workspace_root):
    """Everything including files and catalog is inside full-workspace backup."""
    return Path(workspace_root) / "Data" / "PaperDocuments"


def _safe(value, limit=45):
    return re.sub(r"[^\w\-]+", "_", str(value or "").strip(), flags=re.UNICODE).strip("_")[:limit] or "документ"


def _index(root):
    path = catalog_dir(root) / CATALOG_NAME
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Невірний формат реєстру документів")
    return data


def list_documents(root, text_filter=""):
    records = _index(root)
    needle = str(text_filter or "").casefold().strip()
    if needle:
        records = [row for row in records if needle in " ".join(
            str(row.get(k, "")) for k in ("title", "kind", "date", "person")
        ).casefold()]
    # created_at can collide on filesystems/runtimes with coarser clock precision.
    # The catalog is append-only, so a later record is the newer one on an exact tie.
    indexed_records = list(enumerate(records))
    indexed_records.sort(
        key=lambda item: (item[1]["created_at"], item[0]),
        reverse=True,
    )
    return [row for _index_value, row in indexed_records]


def save_document(root, doc, kind, title, day, person="", *, metadata=None):
    """Never overwrite earlier documents; index is atomically replaced."""
    folder = catalog_dir(root)
    folder.mkdir(parents=True, exist_ok=True)
    records = _index(root)
    doc_id = uuid.uuid4().hex
    filename = "%s_%s_%s.docx" % (_safe(kind), _safe(day), doc_id[:12])
    target = folder / filename
    with tempfile.NamedTemporaryFile(suffix=".docx", dir=str(folder), delete=False) as f:
        pending = Path(f.name)
    try:
        doc.save(str(pending))
        os.replace(str(pending), str(target))
    finally:
        if pending.exists():
            pending.unlink()
    record = {
        "id": doc_id, "kind": str(kind), "title": str(title),
        "date": str(day), "person": str(person),
        "file": filename, "created_at": datetime.now(timezone.utc).isoformat(),
        "paper_signed": False,
    }
    if metadata is not None:
        allowed = {
            "origin", "document_status", "prepared_snapshot_id",
            "company_template_id", "template_revision", "template_source_sha256",
        }
        if not isinstance(metadata, dict) or set(metadata) != allowed:
            raise ValueError("Некоректні відомості джерела документа")
        if metadata["origin"] != "prepared_snapshot" or metadata["document_status"] != "prepared":
            raise ValueError("Некоректний стан підготовленого документа")
        if not isinstance(metadata["template_revision"], int) or isinstance(metadata["template_revision"], bool) or metadata["template_revision"] < 1:
            raise ValueError("Некоректна редакція шаблону")
        for field in ("prepared_snapshot_id", "company_template_id", "template_source_sha256"):
            if not isinstance(metadata[field], str) or not metadata[field]:
                raise ValueError("Неповні відомості джерела документа")
        record.update(metadata)
    records.append(record)
    fd, temp_path = tempfile.mkstemp(dir=str(folder), suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(records, stream, ensure_ascii=False, indent=2)
        os.replace(temp_path, str(folder / CATALOG_NAME))
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    return target


def document_path(root, record):
    filename = record.get("file", "")
    if not isinstance(filename, str) or Path(filename).name != filename or not filename.endswith(".docx"):
        raise ValueError("Небезпечне ім'я файла у реєстрі")
    return catalog_dir(root) / filename

def open_file(path):
    """Open the actual editable DOCX using the OS default document handler."""
    import subprocess
    import sys
    path = str(Path(path).resolve())
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])
