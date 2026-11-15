# -*- coding: utf-8 -*-
"""Controlled history for editable DOCX derived from PreparedDocuments.

Taxo never overwrites an earlier catalog file in this workflow. A user edits an
explicit external copy and imports it back as the next prepared revision.
No import changes business facts, signature state or the immutable snapshot.
"""
from __future__ import annotations

import hashlib
import io
import os
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from docx import Document

from paper_document_store import (
    MAX_STORED_DOCX_BYTES,
    catalog_dir,
    document_path,
    list_documents,
    save_docx_bytes,
)

MAX_DOCX_ZIP_ENTRIES = 5000
MAX_DOCX_UNCOMPRESSED_BYTES = 256 * 1024 * 1024


@dataclass(frozen=True)
class ControlledPreparedRevision:
    path: Path
    payload: bytes
    sha256: str
    record: dict


@dataclass(frozen=True)
class PreparedDocumentRevisionResult:
    path: Path
    document_id: str
    family_id: str
    revision: int
    previous_document_id: str


def _record_by_id(workspace_root, document_id):
    matches = [
        row for row in list_documents(workspace_root)
        if row.get("id") == document_id
    ]
    if len(matches) != 1:
        raise ValueError("Документ не знайдено у каталозі Taxo")
    return matches[0]


def _prepared_record(row):
    if (
        row.get("document_status") != "prepared"
        or not row.get("prepared_snapshot_id")
        or not row.get("company_template_id")
        or not row.get("template_source_sha256")
        or type(row.get("template_revision")) is not int
    ):
        raise ValueError(
            "Нову Word-редакцію можна додати лише до prepared-документа."
        )
    return row


def _revision(row):
    value = row.get("document_revision")
    if type(value) is int and value >= 1:
        return value
    return 1 if row.get("prepared_snapshot_id") else 0


def _family_id(row):
    value = row.get("document_family_id")
    return value if isinstance(value, str) and value else row["id"]


def _family_rows(workspace_root, selected):
    family_id = _family_id(selected)
    rows = []
    for row in list_documents(workspace_root):
        if row.get("id") == family_id or row.get("document_family_id") == family_id:
            if row.get("prepared_snapshot_id") == selected.get("prepared_snapshot_id"):
                rows.append(row)
    if not rows:
        rows = [selected]
    return family_id, rows


def _latest_row(workspace_root, selected):
    family_id, rows = _family_rows(workspace_root, selected)
    latest = max(
        rows,
        key=lambda row: (
            _revision(row),
            str(row.get("created_at") or ""),
            str(row.get("id") or ""),
        ),
    )
    return family_id, latest


def _catalog_bytes(workspace_root, row):
    folder = catalog_dir(workspace_root)
    path = document_path(workspace_root, row)
    if (
        not path.is_file()
        or path.is_symlink()
        or path.resolve().parent != folder.resolve()
    ):
        raise ValueError("Файл каталогу відсутній або небезпечний")
    size = path.stat().st_size
    if size < 1 or size > MAX_STORED_DOCX_BYTES:
        raise ValueError("Некоректний розмір файла каталогу")
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    expected = row.get("content_sha256")
    if expected and expected != digest:
        raise ValueError(
            "Файл попередньої редакції змінено поза контрольованою історією Taxo."
        )
    return path, payload, digest


def _validate_zip(payload):
    try:
        with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
            infos = archive.infolist()
            if not infos or len(infos) > MAX_DOCX_ZIP_ENTRIES:
                raise ValueError("DOCX має некоректну кількість внутрішніх файлів")
            total = 0
            names = set()
            for info in infos:
                name = info.filename
                pure = PurePosixPath(name)
                if (
                    not name
                    or "\\" in name
                    or pure.is_absolute()
                    or ".." in pure.parts
                    or (info.flag_bits & 0x1)
                ):
                    raise ValueError("DOCX містить небезпечний внутрішній шлях")
                if name in names:
                    raise ValueError("DOCX містить дубльований внутрішній файл")
                names.add(name)
                total += int(info.file_size)
                if total > MAX_DOCX_UNCOMPRESSED_BYTES:
                    raise ValueError("DOCX після розпакування завеликий")
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise ValueError("Вибраний файл не є коректним Word DOCX")
    except zipfile.BadZipFile as exc:
        raise ValueError("Вибраний файл не є коректним Word DOCX") from exc


def _read_external_docx(source_path):
    path = Path(source_path)
    if path.suffix.lower() != ".docx":
        raise ValueError("Для нової редакції виберіть файл .docx")
    if not path.is_file() or path.is_symlink():
        raise ValueError("Вибраний DOCX відсутній або небезпечний")
    size = path.stat().st_size
    if size < 1 or size > MAX_STORED_DOCX_BYTES:
        raise ValueError("DOCX перевищує допустимий розмір")
    payload = path.read_bytes()
    _validate_zip(payload)
    try:
        Document(io.BytesIO(payload))
    except Exception as exc:
        raise ValueError("Word DOCX не вдалося перевірити") from exc
    return path, payload, hashlib.sha256(payload).hexdigest()


def load_controlled_prepared_revision(workspace_root, document_id):
    """Return one exact immutable prepared DOCX revision after integrity checks."""
    selected = _prepared_record(_record_by_id(workspace_root, document_id))
    path, payload, digest = _catalog_bytes(workspace_root, selected)
    return ControlledPreparedRevision(
        path=path,
        payload=payload,
        sha256=digest,
        record=dict(selected),
    )


def copy_prepared_document_for_editing(
    workspace_root, document_id, target, *, overwrite=False
):
    """Export an exact catalog revision to an external file for editing."""
    selected = _prepared_record(_record_by_id(workspace_root, document_id))
    source, payload, _digest = _catalog_bytes(workspace_root, selected)
    target = Path(target)
    if target.suffix.lower() != ".docx":
        raise ValueError("Копія для редагування має мати розширення .docx")
    if not target.parent.is_dir() or target.parent.is_symlink():
        raise ValueError("Некоректна папка для копії DOCX")
    if target.parent.resolve() == catalog_dir(workspace_root).resolve():
        raise ValueError(
            "Копію для редагування не можна створювати всередині каталогу Taxo."
        )
    if target.exists():
        if target.is_symlink() or not target.is_file():
            raise ValueError("Некоректний цільовий DOCX")
        if not overwrite:
            raise FileExistsError("DOCX уже існує")

    temp = target.with_name(".%s.%s.tmp" % (target.name, uuid.uuid4().hex))
    try:
        with temp.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if target.exists() and not overwrite:
            raise FileExistsError("DOCX уже існує")
        os.replace(temp, target)
    finally:
        try:
            if temp.exists():
                temp.unlink()
        except OSError:
            pass
    if source.resolve() == target.resolve():
        raise ValueError("Не можна редагувати файл каталогу напряму")
    return target


def import_prepared_document_revision(
    workspace_root, document_id, source_path
):
    """Append a validated external DOCX as the next immutable prepared revision."""
    selected = _prepared_record(_record_by_id(workspace_root, document_id))
    family_id, latest = _latest_row(workspace_root, selected)
    if latest.get("id") != selected.get("id"):
        raise ValueError(
            "Виберіть найновішу редакцію документа перед додаванням наступної."
        )

    catalog = catalog_dir(workspace_root).resolve()
    source = Path(source_path)
    if source.parent.resolve() == catalog:
        raise ValueError(
            "Файл із каталогу Taxo не можна імпортувати як нову редакцію. "
            "Спочатку створіть зовнішню копію для редагування."
        )

    _old_path, old_payload, old_digest = _catalog_bytes(workspace_root, latest)
    _source_path, payload, digest = _read_external_docx(source)
    if digest == old_digest or payload == old_payload:
        raise ValueError("Вибраний DOCX не містить змін відносно поточної редакції.")

    next_revision = _revision(latest) + 1
    metadata = {
        "origin": "edited_docx",
        "document_status": "prepared",
        "prepared_snapshot_id": latest["prepared_snapshot_id"],
        "company_template_id": latest["company_template_id"],
        "template_revision": latest["template_revision"],
        "template_source_sha256": latest["template_source_sha256"],
        "document_family_id": family_id,
        "document_revision": next_revision,
        "previous_document_id": latest["id"],
        "content_sha256": digest,
    }
    path = save_docx_bytes(
        workspace_root,
        payload,
        latest.get("kind") or "Підготовлений документ",
        latest.get("title") or "Підготовлений документ",
        latest.get("date") or "",
        latest.get("person") or "",
        metadata=metadata,
    )
    created = next(
        (
            row for row in list_documents(workspace_root)
            if row.get("file") == path.name
        ),
        None,
    )
    if created is None:
        raise ValueError("Нову редакцію записано, але її не знайдено в індексі")
    return PreparedDocumentRevisionResult(
        path=path,
        document_id=created["id"],
        family_id=family_id,
        revision=next_revision,
        previous_document_id=latest["id"],
    )
