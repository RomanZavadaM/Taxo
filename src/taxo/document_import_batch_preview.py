# -*- coding: utf-8 -*-
"""Verified read-only preview for persisted document inventory batches.

The preview works only with a managed r7 batch. It never opens source files and
never writes to the batch or source archive.
"""
from __future__ import annotations

import re
from copy import deepcopy
from datetime import datetime

from document_import_inventory import INVENTORY_FORMAT
from document_import_batch_store import BATCH_FORMAT, read_inventory_batch


PREVIEW_FORMAT = "taxo.document-batch-preview.v1"
_UNKNOWN = {"", "не визначено", "невідомо", "undefined", "unknown"}
_NATURAL_PART = re.compile(r"(\d+)")


def _text(value):
    return str(value or "").strip()


def _fold(value):
    return _text(value).casefold()


def _parse_date(value):
    raw = _text(value)
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(raw[:19], fmt).date()
        except ValueError:
            continue
    return None


def _natural_key(value):
    raw = _fold(value)
    return tuple(
        (0, int(part)) if part.isdigit() else (1, part)
        for part in _NATURAL_PART.split(raw)
        if part != ""
    )


def _identity(row):
    value = _text(row.get("candidate_id") or row.get("document_id"))
    if not value:
        raise ValueError("Inventory record не має стабільного identity")
    return value


def _source_fallback(row):
    return (
        _fold(row.get("source_relpath")),
        _fold(row.get("source_name")),
        _identity(row),
    )


def _date_components(row):
    document_date = _parse_date(row.get("document_date"))
    registration_date = _parse_date(row.get("registration_date"))
    return (
        1 if document_date is None else 0,
        -(document_date.toordinal()) if document_date else 0,
        1 if registration_date is None else 0,
        -(registration_date.toordinal()) if registration_date else 0,
    )


def _date_desc_key(row):
    return _date_components(row) + _source_fallback(row)


def _number_asc_key(row):
    number = _text(row.get("document_number"))
    return (
        1 if not number else 0,
        _natural_key(number),
        *_date_components(row),
        _identity(row),
    )


def _category_asc_key(row):
    category = _fold(row.get("category"))
    kind = _fold(row.get("document_kind"))
    unknown = category in _UNKNOWN
    return (
        1 if unknown else 0,
        category,
        1 if kind in _UNKNOWN else 0,
        kind,
        *_date_components(row),
        _natural_key(row.get("document_number")),
        _identity(row),
    )


def _source_asc_key(row):
    return _source_fallback(row)


_SORTS = {
    "date_desc": _date_desc_key,
    "number_asc": _number_asc_key,
    "category_asc": _category_asc_key,
    "source_asc": _source_asc_key,
}


def _validate_loaded_batch(batch_id, loaded):
    inventory = loaded.get("inventory")
    report = loaded.get("report")
    if not isinstance(inventory, dict) or not isinstance(report, dict):
        raise ValueError("Некоректний import batch")
    if inventory.get("format") != INVENTORY_FORMAT:
        raise ValueError("Несумісний формат inventory manifest")
    if inventory.get("read_only") is not True:
        raise ValueError("Inventory manifest не позначено read-only")
    if report.get("format") != BATCH_FORMAT:
        raise ValueError("Несумісний формат import batch")
    if report.get("inventory_format") != INVENTORY_FORMAT:
        raise ValueError("Report посилається на несумісний inventory format")
    if _text(inventory.get("import_batch_id")) != _text(batch_id):
        raise ValueError("Inventory manifest має невірний batch ID")
    if _text(report.get("import_batch_id")) != _text(batch_id):
        raise ValueError("Import report має невірний batch ID")
    if _text(report.get("source_root")) != _text(inventory.get("root")):
        raise ValueError("Inventory/report мають різний source root")
    files = inventory.get("files")
    if not isinstance(files, list):
        raise ValueError("Inventory не містить списку файлів")
    for row in files:
        if not isinstance(row, dict):
            raise ValueError("Некоректний inventory record")
        _identity(row)
    return inventory, report


def build_batch_preview(workspace_root, batch_id, sort_mode="date_desc"):
    """Load, verify and return a deterministic read-only batch preview."""
    if sort_mode not in _SORTS:
        raise ValueError("Невідомий режим сортування preview")
    loaded = read_inventory_batch(workspace_root, batch_id)
    inventory, report = _validate_loaded_batch(batch_id, loaded)

    rows = [deepcopy(row) for row in inventory["files"]]
    rows.sort(key=_SORTS[sort_mode])

    return {
        "format": PREVIEW_FORMAT,
        "read_only": True,
        "import_batch_id": _text(batch_id),
        "source_root": inventory["root"],
        "sort_mode": sort_mode,
        "records": rows,
        "summary": deepcopy(report.get("summary") or {}),
        "exact_duplicate_groups": deepcopy(
            report.get("exact_duplicate_groups") or []
        ),
        "errors": deepcopy(report.get("errors") or []),
        "skipped_symlinks": deepcopy(
            report.get("skipped_symlinks") or []
        ),
    }
