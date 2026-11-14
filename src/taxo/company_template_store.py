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
    return CompanyTemplateSummary(
        company_template_id=identity,
        title=str(entry["title"]),
        based_on_template_id=str(entry["based_on_template_id"]),
        based_on_revision_id=str(entry["based_on_revision_id"]),
        created_at=str(entry["created_at"]),
        file_name=file_name,
        enabled=bool(entry.get("enabled", True)),
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
