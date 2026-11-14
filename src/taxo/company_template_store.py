# -*- coding: utf-8 -*-
"""User-owned template copies stored separately from the installed library.

The installed TemplateLibrary is read-only source material. A user who wants
to adapt a template first creates a copy under CompanyTemplates. Future editors
work only on those copies, so library updates cannot overwrite company wording.

This module owns filesystem writes for company templates. It does not use Tk,
SQLite, subprocesses or machine-specific paths. Missing company storage is a
normal state and listing it never creates directories.
"""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from template_library_reader import (
    MAX_TEMPLATE_BYTES,
    _object,
    _read_bytes,
    _safe_path,
    _validate_template,
    default_library_root,
    inspect_library,
)

INDEX_FORMAT = "taxo.company-template-index.v1"
COPY_FORMAT = "taxo.company-template-copy.v1"
MAX_INDEX_BYTES = 4 * 1024 * 1024
MAX_COPY_BYTES = 20 * 1024 * 1024


@dataclass(frozen=True)
class CompanyTemplateSummary:
    """Stable metadata for one user-owned copy."""

    company_template_id: str
    title: str
    based_on_template_id: str
    based_on_revision_id: str
    created_at: str
    file_name: str
    enabled: bool = True
    updated_at: str = ""
    edit_revision: int = 1


def default_company_template_root(workspace_root: Path) -> Path:
    """Return user-owned template storage inside the active workspace."""
    return Path(workspace_root) / "CompanyTemplates"


def _workspace_root(workspace_root: Path) -> Path:
    root = Path(workspace_root)
    if not root.is_dir():
        raise ValueError("Робоча папка Taxo недоступна")
    return root.resolve()


def _company_root(workspace_root: Path, *, allow_missing: bool) -> Path:
    workspace = _workspace_root(workspace_root)
    root = Path(workspace_root) / "CompanyTemplates"
    if root.exists():
        if not root.is_dir() or root.is_symlink():
            raise ValueError("Сховище власних шаблонів має бути звичайною папкою")
        try:
            root.resolve().relative_to(workspace)
        except (ValueError, OSError, RuntimeError):
            raise ValueError("Сховище власних шаблонів поза робочою папкою")
    elif not allow_missing:
        raise FileNotFoundError(str(root))
    return root


def _strict_json_bytes(data) -> bytes:
    return (json.dumps(
        data, ensure_ascii=False, indent=2, sort_keys=True
    ) + "\n").encode("utf-8")


def _atomic_write(path: Path, payload: bytes) -> None:
    """Write through a same-directory temporary file and atomic replace."""
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with tmp.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass


def _load_index(root: Path):
    index_path = root / "index.json"
    if index_path.is_symlink():
        raise ValueError("Індекс власних шаблонів не може бути посиланням")
    if not index_path.exists():
        return []
    raw = _read_bytes(index_path, MAX_INDEX_BYTES)
    data = _object(raw, "CompanyTemplates/index.json")
    if data.get("format") != INDEX_FORMAT or not isinstance(data.get("items"), list):
        raise ValueError("Пошкоджений індекс власних шаблонів")
    return data["items"]


def _summary_from_entry(root: Path, entry: dict) -> CompanyTemplateSummary:
    required = (
        "company_template_id", "title", "based_on_template_id",
        "based_on_revision_id", "created_at", "file", "size_bytes", "sha256",
    )
    if not isinstance(entry, dict) or any(key not in entry for key in required):
        raise ValueError("Неповний запис власного шаблону")
    identity = entry["company_template_id"]
    if not isinstance(identity, str) or not identity.startswith("company.") or len(identity) > 80:
        raise ValueError("Некоректний ID власного шаблону")
    file_name = entry["file"]
    if not isinstance(file_name, str) or "/" in file_name or "\\" in file_name:
        raise ValueError("Некоректний файл власного шаблону")
    items_root = root / "items"
    path = items_root / file_name
    if path.is_symlink() or items_root.is_symlink():
        raise ValueError("Посилання у сховищі власних шаблонів заборонені")
    try:
        path.resolve().relative_to(items_root.resolve())
    except (ValueError, OSError, RuntimeError):
        raise ValueError("Файл власного шаблону поза сховищем")
    raw = _read_bytes(path, MAX_COPY_BYTES)
    if (
        type(entry["size_bytes"]) is not int
        or len(raw) != entry["size_bytes"]
        or not isinstance(entry["sha256"], str)
        or hashlib.sha256(raw).hexdigest() != entry["sha256"]
    ):
        raise ValueError("Порушено цілісність власного шаблону")
    data = _object(raw, file_name)
    if data.get("format") != COPY_FORMAT or data.get("company_template_id") != identity:
        raise ValueError("Пошкоджена власна копія шаблону")
    based = data.get("based_on")
    if not isinstance(based, dict):
        raise ValueError("Власна копія не містить походження")
    if (
        based.get("template_id") != entry["based_on_template_id"]
        or based.get("revision_id") != entry["based_on_revision_id"]
    ):
        raise ValueError("Походження власної копії не збігається з індексом")
    updated_at = entry.get("updated_at", entry["created_at"])
    edit_revision = entry.get("edit_revision", 1)
    if not isinstance(updated_at, str) or not updated_at:
        raise ValueError("Некоректний час зміни власного шаблону")
    if type(edit_revision) is not int or edit_revision < 1:
        raise ValueError("Некоректний номер власної редакції")
    return CompanyTemplateSummary(
        company_template_id=identity,
        title=str(entry["title"]),
        based_on_template_id=str(entry["based_on_template_id"]),
        based_on_revision_id=str(entry["based_on_revision_id"]),
        created_at=str(entry["created_at"]),
        file_name=file_name,
        enabled=bool(entry.get("enabled", True)),
        updated_at=updated_at,
        edit_revision=edit_revision,
    )


def list_company_templates(workspace_root: Path) -> Tuple[CompanyTemplateSummary, ...]:
    """Read and integrity-check user copies; missing storage means no copies."""
    root = default_company_template_root(workspace_root)
    if not root.exists():
        return ()
    root = _company_root(workspace_root, allow_missing=False)
    entries = _load_index(root)
    seen = set()
    rows = []
    for entry in entries:
        summary = _summary_from_entry(root, entry)
        if summary.company_template_id in seen:
            raise ValueError("Повторений ID власного шаблону")
        seen.add(summary.company_template_id)
        rows.append(summary)
    rows.sort(key=lambda item: (
        item.title.casefold(), item.created_at, item.company_template_id
    ))
    return tuple(rows)


def create_company_copy(
    workspace_root: Path,
    app_version: str,
    template_id: str,
    revision_id: str,
) -> CompanyTemplateSummary:
    """Copy one verified library revision into user-owned storage.

    The source package is revalidated immediately before reading. The original
    data-only template is embedded with provenance. An exact source revision can
    be copied only once in this first implementation; a future explicit
    Duplicate action may intentionally create additional copies.
    """
    workspace = _workspace_root(workspace_root)
    vendor_root = default_library_root(workspace)
    snapshot = inspect_library(vendor_root, app_version)
    if snapshot.status != "AVAILABLE":
        raise ValueError(snapshot.message)

    matches = [
        item for item in snapshot.templates
        if item.template_id == template_id and item.revision_id == revision_id
    ]
    if len(matches) != 1:
        raise ValueError("Редакцію шаблону не знайдено у перевіреній бібліотеці")
    selected = matches[0]

    manifest = _object(
        _read_bytes(_safe_path(vendor_root, "manifest.json"), 1024 * 1024),
        "manifest.json",
    )
    manifest_items = [
        item for item in manifest["items"]
        if item.get("template_id") == template_id
        and item.get("revision_id") == revision_id
        and item.get("path") == selected.path
    ]
    manifest_files = [
        item for item in manifest["files"] if item.get("path") == selected.path
    ]
    if len(manifest_items) != 1 or len(manifest_files) != 1:
        raise ValueError("Неоднозначна редакція шаблону")

    raw = _read_bytes(_safe_path(vendor_root, selected.path), MAX_TEMPLATE_BYTES)
    expected = manifest_files[0]
    source_sha = hashlib.sha256(raw).hexdigest()
    if len(raw) != expected["size_bytes"] or source_sha != expected["sha256"]:
        raise ValueError("Початковий шаблон змінено після перевірки")
    template = _object(raw, selected.path)
    _validate_template(template, manifest_items[0])

    root = default_company_template_root(workspace)
    if root.exists():
        root = _company_root(workspace, allow_missing=False)
        existing = list_company_templates(workspace)
    else:
        existing = ()
    for item in existing:
        if (
            item.based_on_template_id == template_id
            and item.based_on_revision_id == revision_id
        ):
            raise ValueError("Власна копія цієї редакції вже існує")

    root.mkdir(parents=False, exist_ok=True)
    root = _company_root(workspace, allow_missing=False)
    items_root = root / "items"
    if items_root.exists() and (not items_root.is_dir() or items_root.is_symlink()):
        raise ValueError("Папка власних шаблонів пошкоджена")
    items_root.mkdir(exist_ok=True)

    identity = "company." + uuid.uuid4().hex
    created = datetime.now(timezone.utc).isoformat(timespec="seconds")
    copy_data = {
        "format": COPY_FORMAT,
        "company_template_id": identity,
        "title": selected.title,
        "enabled": True,
        "created_at": created,
        "updated_at": created,
        "edit_revision": 1,
        "based_on": {
            "package_id": snapshot.package_id,
            "package_version": snapshot.package_version,
            "template_id": template_id,
            "revision_id": revision_id,
            "sha256": source_sha,
        },
        "template": template,
    }
    payload = _strict_json_bytes(copy_data)
    if len(payload) > MAX_COPY_BYTES:
        raise ValueError("Власна копія шаблону перевищує допустимий розмір")
    file_name = identity + ".json"
    target = items_root / file_name
    _atomic_write(target, payload)

    entry = {
        "company_template_id": identity,
        "title": selected.title,
        "based_on_template_id": template_id,
        "based_on_revision_id": revision_id,
        "created_at": created,
        "updated_at": created,
        "edit_revision": 1,
        "enabled": True,
        "file": file_name,
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
    try:
        index_payload = _strict_json_bytes({
            "format": INDEX_FORMAT,
            "items": list(_load_index(root)) + [entry],
        })
        _atomic_write(root / "index.json", index_payload)
    except Exception:
        try:
            target.unlink()
        except OSError:
            pass
        raise
    return _summary_from_entry(root, entry)

@dataclass(frozen=True)
class CompanyTemplateDocument:
    """Verified current revision of one user-owned template.

    content_sha256 is the optimistic-concurrency token. edit_revision starts at
    1 for r1 copies that predate explicit revision metadata.
    """

    summary: CompanyTemplateSummary
    title: str
    template: dict
    updated_at: str
    edit_revision: int
    content_sha256: str


def _current_entry(root: Path, company_template_id: str):
    entries = _load_index(root)
    matches = [
        entry for entry in entries
        if isinstance(entry, dict)
        and entry.get("company_template_id") == company_template_id
    ]
    if len(matches) != 1:
        raise ValueError("Власний шаблон не знайдено або його індекс неоднозначний")
    return entries, matches[0]


def _verified_copy_data(root: Path, entry: dict):
    summary = _summary_from_entry(root, entry)
    items_root = root / "items"
    path = items_root / summary.file_name
    if items_root.is_symlink() or path.is_symlink():
        raise ValueError("Посилання у сховищі власних шаблонів заборонені")
    raw = _read_bytes(path, MAX_COPY_BYTES)
    digest = hashlib.sha256(raw).hexdigest()
    if digest != entry["sha256"]:
        raise ValueError("Порушено цілісність власного шаблону")
    data = _object(raw, summary.file_name)
    template = data.get("template")
    if not isinstance(template, dict):
        raise ValueError("Власна копія не містить шаблону")
    revision = data.get("edit_revision", entry.get("edit_revision", 1))
    if type(revision) is not int or revision < 1:
        raise ValueError("Некоректний номер власної редакції")
    updated_at = data.get("updated_at", entry.get("updated_at", summary.created_at))
    if not isinstance(updated_at, str) or not updated_at:
        raise ValueError("Некоректний час зміни власного шаблону")
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Власна копія не має назви")
    if template.get("title") != title:
        raise ValueError("Назва власної копії не збігається з її шаблоном")
    return summary, data, raw, digest, revision, updated_at


def load_company_template(
    workspace_root: Path, company_template_id: str
) -> CompanyTemplateDocument:
    """Load one integrity-checked current company-template revision."""
    root = _company_root(workspace_root, allow_missing=False)
    _entries, entry = _current_entry(root, company_template_id)
    summary, data, _raw, digest, revision, updated_at = _verified_copy_data(
        root, entry
    )
    return CompanyTemplateDocument(
        summary=summary,
        title=data["title"],
        template=data["template"],
        updated_at=updated_at,
        edit_revision=revision,
        content_sha256=digest,
    )


def save_company_template(
    workspace_root: Path,
    company_template_id: str,
    expected_sha256: str,
    title: str,
    template: dict,
) -> CompanyTemplateDocument:
    """Commit a new immutable company revision and atomically move the index.

    The previous revision file is deliberately preserved. The index is the
    commit point: if writing it fails, the old revision remains current and the
    unreferenced new file is removed. expected_sha256 prevents last-write-wins.
    """
    if (
        not isinstance(expected_sha256, str)
        or len(expected_sha256) != 64
        or any(ch not in "0123456789abcdef" for ch in expected_sha256)
    ):
        raise ValueError("Некоректна контрольна сума редакції")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Назва шаблону не може бути порожньою")
    if len(title) > 250 or "\n" in title or "\r" in title:
        raise ValueError("Некоректна назва шаблону")
    if not isinstance(template, dict):
        raise ValueError("Некоректний вміст власного шаблону")

    root = _company_root(workspace_root, allow_missing=False)
    entries, current = _current_entry(root, company_template_id)
    (
        _summary,
        current_data,
        _current_raw,
        current_digest,
        current_revision,
        _updated_at,
    ) = _verified_copy_data(root, current)
    if current_digest != expected_sha256:
        raise ValueError(
            "Власний шаблон уже змінено. Оновіть його перед повторним збереженням."
        )

    based_on = current_data.get("based_on")
    if not isinstance(based_on, dict):
        raise ValueError("Власна копія не містить походження")
    if template.get("template_id") != based_on.get("template_id"):
        raise ValueError("Не можна змінити ID початкового шаблону")
    if template.get("title") != title:
        raise ValueError("Назва шаблону не синхронізована")

    _validate_template(
        template,
        {
            "template_id": based_on["template_id"],
            "revision_id": str(based_on.get("revision_id") or "company"),
            "category_id": "forms",
            "path": "company.json",
        },
    )

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    new_revision = current_revision + 1
    previous_file = current["file"]
    previous_sha = current["sha256"]
    copy_data = dict(current_data)
    copy_data.update({
        "title": title,
        "updated_at": now,
        "edit_revision": new_revision,
        "template": template,
        "previous_revision": {
            "file": previous_file,
            "sha256": previous_sha,
            "edit_revision": current_revision,
        },
    })
    payload = _strict_json_bytes(copy_data)
    if len(payload) > MAX_COPY_BYTES:
        raise ValueError("Власна копія шаблону перевищує допустимий розмір")

    items_root = root / "items"
    if not items_root.is_dir() or items_root.is_symlink():
        raise ValueError("Папка власних шаблонів пошкоджена")
    file_name = "%s.rev-%04d-%s.json" % (
        company_template_id,
        new_revision,
        uuid.uuid4().hex[:12],
    )
    target = items_root / file_name
    _atomic_write(target, payload)
    digest = hashlib.sha256(payload).hexdigest()

    updated_entry = dict(current)
    updated_entry.update({
        "title": title,
        "updated_at": now,
        "edit_revision": new_revision,
        "file": file_name,
        "size_bytes": len(payload),
        "sha256": digest,
    })
    new_entries = [
        updated_entry
        if entry.get("company_template_id") == company_template_id
        else entry
        for entry in entries
    ]
    try:
        index_payload = _strict_json_bytes({
            "format": INDEX_FORMAT,
            "items": new_entries,
        })
        _atomic_write(root / "index.json", index_payload)
    except Exception:
        try:
            target.unlink()
        except OSError:
            pass
        raise

    summary = _summary_from_entry(root, updated_entry)
    return CompanyTemplateDocument(
        summary=summary,
        title=title,
        template=template,
        updated_at=now,
        edit_revision=new_revision,
        content_sha256=digest,
    )

