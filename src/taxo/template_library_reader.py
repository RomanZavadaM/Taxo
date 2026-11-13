# -*- coding: utf-8 -*-
"""Read-only installed template catalog for Taxo.

This module belongs to the template-library feature, not the application
bootstrap. It never creates directories, changes SQLite or executes content
from a template. All paths are relative to the selected library root.

Contract:
    inspect_library(root, taxo_version) -> LibrarySnapshot
    default_library_root(workspace_root) -> Path

An installed vendor package contains manifest.json, data-only JSON templates
and optional referenced resources. Installation, editing and rendering belong
to separate future services. The caller owns error presentation in the UI.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

MANIFEST_FORMAT = "taxo.template-catalog.v1"
TEMPLATE_FORMAT = "taxo.template.v1"
MAX_MANIFEST_BYTES = 1024 * 1024
MAX_TEMPLATE_BYTES = 16 * 1024 * 1024
MAX_FILES = 2000
MAX_TOTAL_BYTES = 512 * 1024 * 1024
_PATH = re.compile(r"^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{4,95}$")
_VERSION = re.compile(r"^(\d+)\.(\d+)-r(10|[1-9])$")
_PACKAGE_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
_ALLOWED_CATEGORIES = frozenset((
    "orders", "briefings", "instructions", "training-programs", "acts", "forms"
))
_ALLOWED_BLOCKS = frozenset((
    "heading", "paragraph", "numbered_list", "bullet_list", "table",
    "dynamic_table", "page_break", "signature_placeholder",
    "attachment_reference", "figure",
))
_ALLOWED_VARIABLE_TYPES = frozenset((
    "text", "date", "integer", "person_ref", "vehicle_ref", "pairs",
    "participants", "sections", "table_rows",
))


@dataclass(frozen=True)
class TemplateSummary:
    """Stable item identity and presentation; content is not executed."""

    template_id: str
    revision_id: str
    category_id: str
    title: str
    document_kind: str
    scenario: str
    path: str


@dataclass(frozen=True)
class LibrarySnapshot:
    """Immutable result for a single read of an installed catalog."""

    status: str
    message: str
    root: Path
    package_id: str = ""
    package_version: str = ""
    templates: Tuple[TemplateSummary, ...] = ()


def default_library_root(workspace_root: Path) -> Path:
    """Return the workspace-relative default, never the executable directory."""
    return Path(workspace_root) / "TemplateLibrary"


def _safe_path(root: Path, relative: object) -> Path:
    """Reject traversal, symlinks and any file resolving outside the library."""
    if not isinstance(relative, str) or len(relative) > 512 or not _PATH.fullmatch(relative):
        raise ValueError("Небезпечний шлях у бібліотеці")
    parts = relative.split("/")
    if any(part in (".", "..") for part in parts):
        raise ValueError("Небезпечний шлях у бібліотеці")
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Символічне посилання у бібліотеці")
    try:
        current.resolve(strict=False).relative_to(root.resolve(strict=True))
    except (ValueError, OSError, RuntimeError):
        raise ValueError("Шлях поза бібліотекою")
    return current


def _read_bytes(path: Path, size_limit: int) -> bytes:
    """Read a bounded file and fail on changed/missing/unreadable content."""
    if not path.is_file():
        raise ValueError("Файл бібліотеки відсутній")
    size = path.stat().st_size
    if size > size_limit:
        raise ValueError("Файл бібліотеки перевищує дозволений розмір")
    with path.open("rb") as stream:
        data = stream.read(size_limit + 1)
    if len(data) > size_limit:
        raise ValueError("Файл бібліотеки перевищує дозволений розмір")
    return data


def _object(raw: bytes, description: str) -> Dict[str, Any]:
    """Decode strict JSON; duplicate keys may hide malicious substitutions."""
    def object_pairs(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("Повторене поле JSON у " + description)
            value[key] = item
        return value

    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=object_pairs)
    except (ValueError, UnicodeError) as exc:
        raise ValueError("Помилка JSON у " + description + ": " + str(exc))
    if not isinstance(result, dict):
        raise ValueError("Об'єкт JSON очікується у " + description)
    return result


def _parse_version(value: object) -> Tuple[int, int, int]:
    match = _VERSION.fullmatch(str(value or ""))
    if not match:
        raise ValueError("Некоректна версія Taxo у пакеті")
    return tuple(map(int, match.groups()))


def _validate_blocks(blocks: object) -> None:
    """A strict, nonexecuting subset of the existing template v1 schema."""
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("Шаблон повинен містити структурні блоки")
    for block in blocks:
        if not isinstance(block, dict) or block.get("type") not in _ALLOWED_BLOCKS:
            raise ValueError("Невідомий блок шаблону")
        if not isinstance(block.get("id"), str) or not re.fullmatch(r"[a-z0-9_-]+", block["id"]):
            raise ValueError("Неправильний ID блоку")
        if block.get("visible_when") is not None:
            # Conditions need a separately specified declarative evaluator.
            raise ValueError("Умови visible_when поки не підтримуються")
        if "children" in block:
            _validate_blocks(block["children"])


def _validate_template(template: Dict[str, Any], item: Dict[str, Any]) -> TemplateSummary:
    if template.get("format") != TEMPLATE_FORMAT or template.get("language") != "uk":
        raise ValueError("Непідтримуваний формат шаблону")
    if template.get("status") != "proposed":
        raise ValueError("Непідтримуваний стан шаблону")
    if template.get("template_id") != item["template_id"]:
        raise ValueError("ID шаблону не збігається з маніфестом")
    for key in ("title", "document_kind", "scenario"):
        if not isinstance(template.get(key), str) or not template[key].strip():
            raise ValueError("Не заповнено реквізит шаблону: " + key)
    if not isinstance(template.get("source_refs"), list):
        raise ValueError("Некоректні джерела шаблону")
    variables = template.get("variables")
    if not isinstance(variables, list):
        raise ValueError("Некоректні змінні шаблону")
    seen = set()
    for var in variables:
        if not isinstance(var, dict) or var.get("type") not in _ALLOWED_VARIABLE_TYPES:
            raise ValueError("Невідомий тип змінної шаблону")
        name = var.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*", name):
            raise ValueError("Некоректне ім'я змінної")
        if name in seen or not isinstance(var.get("required"), bool):
            raise ValueError("Повторена або неправильно описана змінна")
        seen.add(name)
    _validate_blocks(template.get("blocks"))
    for appendix in template.get("appendices", ()):
        if not isinstance(appendix, dict):
            raise ValueError("Некоректний додаток")
        _validate_blocks(appendix.get("blocks"))
    return TemplateSummary(
        template_id=item["template_id"],
        revision_id=item["revision_id"],
        category_id=item["category_id"],
        title=template["title"],
        document_kind=template["document_kind"],
        scenario=template["scenario"],
        path=item["path"],
    )


def _inspect(root: Path, taxo_version: str) -> LibrarySnapshot:
    manifest_path = _safe_path(root, "manifest.json")
    manifest = _object(_read_bytes(manifest_path, MAX_MANIFEST_BYTES), "manifest.json")
    required = ("format", "package_id", "package_version", "publisher",
                "minimum_taxo_version", "language", "items", "files")
    if any(field not in manifest for field in required):
        raise ValueError("Відсутні обов'язкові поля маніфесту")
    if manifest["format"] != MANIFEST_FORMAT or manifest["language"] != "uk":
        return LibrarySnapshot("INCOMPATIBLE", "Непідтримуваний формат бібліотеки", root)
    if not isinstance(manifest["package_id"], str) or not _ID.fullmatch(manifest["package_id"]):
        raise ValueError("Некоректний ID пакета")
    if not isinstance(manifest["package_version"], str) or not _PACKAGE_VERSION.fullmatch(manifest["package_version"]):
        raise ValueError("Некоректна версія бібліотеки")
    if not isinstance(manifest["publisher"], str) or not manifest["publisher"].strip():
        raise ValueError("Не вказано видавця бібліотеки")
    try:
        required_version = _parse_version(manifest["minimum_taxo_version"])
        installed_version = _parse_version(taxo_version)
    except ValueError:
        raise ValueError("Невірна версія сумісності")
    if installed_version < required_version:
        return LibrarySnapshot("INCOMPATIBLE", "Бібліотека потребує новішу версію Taxo", root)
    items, files = manifest["items"], manifest["files"]
    if not isinstance(items, list) or not isinstance(files, list) or not items or not files:
        raise ValueError("Порожній або неправильний перелік файлів бібліотеки")
    if len(files) > MAX_FILES or len(items) > MAX_FILES:
        raise ValueError("Забагато файлів бібліотеки")
    paths = {}
    total = 0
    for entry in files:
        if not isinstance(entry, dict):
            raise ValueError("Некоректний опис файла")
        path, size, digest = entry.get("path"), entry.get("size_bytes"), entry.get("sha256")
        if not isinstance(path, str) or path.casefold() in paths:
            raise ValueError("Повторений шлях у маніфесті")
        _safe_path(root, path)
        if type(size) is not int or size < 0 or size > MAX_TOTAL_BYTES:
            raise ValueError("Некоректний розмір файла")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise ValueError("Некоректна контрольна сума")
        total += size
        if total > MAX_TOTAL_BYTES:
            raise ValueError("Каталог перевищує обмеження розміру")
        paths[path.casefold()] = (path, size, digest)
    for path, size, digest in paths.values():
        content = _read_bytes(_safe_path(root, path), MAX_TOTAL_BYTES)
        if len(content) != size or hashlib.sha256(content).hexdigest() != digest:
            raise ValueError("Порушено цілісність файла: " + path)

    templates = []
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Некоректний опис шаблону")
        key = (item.get("template_id"), item.get("revision_id"))
        if any(not isinstance(value, str) for value in key) or key in seen:
            raise ValueError("Повторена редакція шаблону")
        seen.add(key)
        if not _ID.fullmatch(item["template_id"]):
            raise ValueError("Некоректний ID шаблону")
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,95}", item["revision_id"]):
            raise ValueError("Некоректний ID редакції")
        if item.get("category_id") not in _ALLOWED_CATEGORIES:
            raise ValueError("Невідома категорія шаблону")
        path = item.get("path")
        if not isinstance(path, str) or path.casefold() not in paths:
            raise ValueError("Немає файла шаблону в списку ресурсів")
        if not path.endswith(".json"):
            raise ValueError("Шаблон має бути JSON")
        raw = _read_bytes(_safe_path(root, path), MAX_TEMPLATE_BYTES)
        templates.append(_validate_template(_object(raw, path), item))
    return LibrarySnapshot(
        "AVAILABLE", "Бібліотеку перевірено", root,
        manifest["package_id"], manifest["package_version"], tuple(templates),
    )


def inspect_library(root: Path, taxo_version: str) -> LibrarySnapshot:
    """Safely inspect an installed catalog without any write side effect.

    NOT_INSTALLED means the configured directory does not exist or has no
    manifest. UNAVAILABLE is reserved for access failures, DAMAGED for invalid
    local data, and INCOMPATIBLE for an unsupported version/format.
    """
    root = Path(root)
    if not root.exists():
        return LibrarySnapshot("NOT_INSTALLED", "Картотеку шаблонів не встановлено", root)
    try:
        if not root.is_dir():
            return LibrarySnapshot("DAMAGED", "Шлях бібліотеки не є каталогом", root)
        if root.is_symlink():
            return LibrarySnapshot("DAMAGED", "Каталог бібліотеки не може бути посиланням", root)
        if not (root / "manifest.json").exists():
            return LibrarySnapshot("NOT_INSTALLED", "Картотеку шаблонів не встановлено", root)
        return _inspect(root, taxo_version)
    except (PermissionError, OSError) as exc:
        return LibrarySnapshot("UNAVAILABLE", "Немає доступу до бібліотеки: " + str(exc), root)
    except (ValueError, TypeError, KeyError, UnicodeError) as exc:
        return LibrarySnapshot("DAMAGED", "Некоректна бібліотека: " + str(exc), root)
