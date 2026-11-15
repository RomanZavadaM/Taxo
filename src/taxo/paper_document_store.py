# -*- coding: utf-8 -*-
"""Persist and open generated paper documents in the workspace."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

CATALOG_NAME = "index.json"
MAX_STORED_DOCX_BYTES = 64 * 1024 * 1024
_CATALOG_WRITE_LOCK = threading.RLock()
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_PREPARED_CORE = {
    "origin", "document_status", "prepared_snapshot_id",
    "company_template_id", "template_revision", "template_source_sha256",
}
_PREPARED_LINEAGE = {
    "document_family_id", "document_revision", "previous_document_id",
    "content_sha256",
}


def catalog_dir(workspace_root):
    """Everything including files and catalog is inside full-workspace backup."""
    return Path(workspace_root) / "Data" / "PaperDocuments"


def _safe(value, limit=45):
    return re.sub(
        r"[^\w\-]+", "_", str(value or "").strip(), flags=re.UNICODE
    ).strip("_")[:limit] or "документ"


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
        records = [
            row for row in records
            if needle in " ".join(
                str(row.get(k, ""))
                for k in ("title", "kind", "date", "person")
            ).casefold()
        ]
    indexed_records = list(enumerate(records))
    indexed_records.sort(
        key=lambda item: (item[1]["created_at"], item[0]),
        reverse=True,
    )
    return [row for _index_value, row in indexed_records]


def _sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _prepared_metadata(metadata, doc_id, actual_sha256):
    if metadata is None:
        return {}
    if not isinstance(metadata, dict):
        raise ValueError("Некоректні відомості джерела документа")
    keys = set(metadata)
    if not _PREPARED_CORE.issubset(keys) or not keys.issubset(
        _PREPARED_CORE | _PREPARED_LINEAGE
    ):
        raise ValueError("Некоректні відомості джерела документа")

    origin = metadata["origin"]
    if origin not in ("prepared_snapshot", "edited_docx"):
        raise ValueError("Некоректне походження підготовленого документа")
    if metadata["document_status"] != "prepared":
        raise ValueError("Некоректний стан підготовленого документа")
    if (
        not isinstance(metadata["template_revision"], int)
        or isinstance(metadata["template_revision"], bool)
        or metadata["template_revision"] < 1
    ):
        raise ValueError("Некоректна редакція шаблону")
    for field in (
        "prepared_snapshot_id", "company_template_id", "template_source_sha256"
    ):
        if not isinstance(metadata[field], str) or not metadata[field]:
            raise ValueError("Неповні відомості джерела документа")
    if not _SHA256.fullmatch(metadata["template_source_sha256"]):
        raise ValueError("Некоректний SHA-256 редакції шаблону")

    family_id = metadata.get("document_family_id") or doc_id
    revision = metadata.get("document_revision", 1)
    previous_id = metadata.get("previous_document_id", "")
    supplied_digest = metadata.get("content_sha256", actual_sha256)

    if not isinstance(family_id, str) or not family_id:
        raise ValueError("Некоректна сім'я редакцій документа")
    if (
        type(revision) is not int
        or revision < 1
        or not isinstance(previous_id, str)
    ):
        raise ValueError("Некоректна редакція документа")
    if not isinstance(supplied_digest, str) or not _SHA256.fullmatch(
        supplied_digest
    ):
        raise ValueError("Некоректний SHA-256 файла документа")
    if supplied_digest != actual_sha256:
        raise ValueError("SHA-256 файла документа не збігається з записом")

    if origin == "prepared_snapshot":
        if revision != 1 or previous_id:
            raise ValueError("Початковий prepared DOCX має бути редакцією r1")
        family_id = doc_id
    else:
        if revision < 2 or not previous_id:
            raise ValueError("Нова Word-редакція не має попередньої редакції")

    result = dict(metadata)
    result.update({
        "document_family_id": family_id,
        "document_revision": revision,
        "previous_document_id": previous_id,
        "content_sha256": actual_sha256,
    })
    return result


def _write_index(folder, records):
    fd, temp_path = tempfile.mkstemp(dir=str(folder), suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(records, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, str(folder / CATALOG_NAME))
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def _record(doc_id, filename, kind, title, day, person, digest, metadata):
    record = {
        "id": doc_id,
        "kind": str(kind),
        "title": str(title),
        "date": str(day),
        "person": str(person),
        "file": filename,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "paper_signed": False,
    }
    record.update(_prepared_metadata(metadata, doc_id, digest))
    return record


def _new_target(folder, kind, day):
    doc_id = uuid.uuid4().hex
    filename = "%s_%s_%s.docx" % (
        _safe(kind), _safe(day), doc_id[:12]
    )
    return doc_id, filename, folder / filename


def _save_document_unlocked(root, doc, kind, title, day, person="", *, metadata=None):
    """Never overwrite earlier documents; index is atomically replaced."""
    folder = catalog_dir(root)
    folder.mkdir(parents=True, exist_ok=True)
    records = _index(root)
    doc_id, filename, target = _new_target(folder, kind, day)

    with tempfile.NamedTemporaryFile(
        suffix=".docx", dir=str(folder), delete=False
    ) as stream:
        pending = Path(stream.name)
    try:
        doc.save(str(pending))
        os.replace(str(pending), str(target))
        digest = _sha256_file(target)
        record = _record(
            doc_id, filename, kind, title, day, person,
            digest, metadata,
        )
        records.append(record)
        try:
            _write_index(folder, records)
        except Exception:
            try:
                target.unlink()
            except OSError:
                pass
            raise
    except Exception:
        try:
            if target.exists() and not any(
                row.get("file") == filename for row in _index(root)
            ):
                target.unlink()
        except Exception:
            pass
        raise
    finally:
        if pending.exists():
            pending.unlink()
    return target


def save_document(root, doc, kind, title, day, person="", *, metadata=None):
    """Serialize index updates so two Taxo windows cannot lose each other."""
    with _CATALOG_WRITE_LOCK:
        return _save_document_unlocked(
            root, doc, kind, title, day, person, metadata=metadata
        )


def _save_docx_bytes_unlocked(
    root, payload, kind, title, day, person="", *, metadata
):
    """Store exact validated DOCX bytes as a new immutable catalog record."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("DOCX має бути передано як bytes")
    payload = bytes(payload)
    if not payload or len(payload) > MAX_STORED_DOCX_BYTES:
        raise ValueError("Некоректний розмір DOCX")

    folder = catalog_dir(root)
    folder.mkdir(parents=True, exist_ok=True)
    records = _index(root)
    doc_id, filename, target = _new_target(folder, kind, day)
    digest = hashlib.sha256(payload).hexdigest()
    record = _record(
        doc_id, filename, kind, title, day, person,
        digest, metadata,
    )

    with tempfile.NamedTemporaryFile(
        suffix=".docx", dir=str(folder), delete=False
    ) as stream:
        pending = Path(stream.name)
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(str(pending), str(target))
        records.append(record)
        try:
            _write_index(folder, records)
        except Exception:
            try:
                target.unlink()
            except OSError:
                pass
            raise
    finally:
        if pending.exists():
            pending.unlink()
    return target


def save_docx_bytes(
    root, payload, kind, title, day, person="", *, metadata
):
    """Serialize exact-DOCX appends with all other PaperDocuments writes."""
    with _CATALOG_WRITE_LOCK:
        return _save_docx_bytes_unlocked(
            root,
            payload,
            kind,
            title,
            day,
            person,
            metadata=metadata,
        )


def document_path(root, record):
    filename = record.get("file", "")
    if (
        not isinstance(filename, str)
        or Path(filename).name != filename
        or not filename.endswith(".docx")
    ):
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
