# -*- coding: utf-8 -*-
"""Canonical serialization for immutable prepared-document snapshots.

A prepared snapshot is an intermediate document state: it captures the exact
CompanyTemplates revision, normalized facts and rendered structured content
that the user previewed. It is not an order/briefing business fact, a generated
DOCX/PDF, DocumentArchive entry, scan or signature record.

This module has no filesystem, database or Tk dependencies.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime
from typing import Any, Mapping

SNAPSHOT_FORMAT = "taxo.prepared-document-snapshot.v1"
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_SNAPSHOT_ID = re.compile(r"^pd-[a-f0-9]{32}$")
MAX_TITLE_CHARS = 250
MAX_CONTENT_CHARS = 2_000_000
MAX_DEPTH = 32
MAX_COLLECTION_ITEMS = 20_000


def _plain_text(value: object, label: str, *, maximum: int) -> str:
    if not isinstance(value, str):
        raise ValueError("%s має бути текстом" % label)
    if "\x00" in value:
        raise ValueError("%s містить недопустимий символ" % label)
    if len(value) > maximum:
        raise ValueError("%s перевищує допустимий розмір" % label)
    return value


def _json_safe(value: object, *, depth: int = 0) -> object:
    """Convert typed draft values to deterministic JSON-safe values."""
    if depth > MAX_DEPTH:
        raise ValueError("Snapshot містить занадто глибоку структуру")
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, str) and "\x00" in value:
            raise ValueError("Snapshot містить недопустимий символ")
        return value
    if isinstance(value, datetime):
        return {
            "$taxo_type": "datetime",
            "value": value.isoformat(timespec="seconds"),
        }
    if isinstance(value, date):
        return {
            "$taxo_type": "date",
            "value": value.isoformat(),
        }
    if isinstance(value, (list, tuple)):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise ValueError("Snapshot містить забагато елементів")
        return [_json_safe(item, depth=depth + 1) for item in value]
    if isinstance(value, Mapping):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise ValueError("Snapshot містить забагато полів")
        result = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key or "\x00" in key:
                raise ValueError("Snapshot містить некоректний ключ")
            result[key] = _json_safe(item, depth=depth + 1)
        return result
    raise ValueError(
        "Snapshot містить непідтримуваний тип: %s"
        % type(value).__name__
    )


def _variable_payload(variable) -> dict:
    name = getattr(variable, "name", None)
    label = getattr(variable, "label", None)
    variable_type = getattr(variable, "variable_type", None)
    required = getattr(variable, "required", None)
    description = getattr(variable, "description", "")
    if not isinstance(name, str) or not name:
        raise ValueError("Некоректне ім'я поля snapshot-а")
    if not isinstance(label, str) or not label:
        raise ValueError("Некоректна назва поля snapshot-а")
    if not isinstance(variable_type, str) or not variable_type:
        raise ValueError("Некоректний тип поля snapshot-а")
    if not isinstance(required, bool):
        raise ValueError("Некоректна обов'язковість поля snapshot-а")
    return {
        "name": name,
        "label": label,
        "type": variable_type,
        "required": required,
        "description": str(description or ""),
    }


def build_snapshot_payload(draft, snapshot_id: str, created_at: str) -> dict:
    """Create validated canonical snapshot content from CompanyTemplateDraft."""
    if not isinstance(snapshot_id, str) or not _SNAPSHOT_ID.fullmatch(snapshot_id):
        raise ValueError("Некоректний ID prepared snapshot-а")
    if not isinstance(created_at, str) or not created_at:
        raise ValueError("Не вказано час створення prepared snapshot-а")

    company_template_id = getattr(draft, "company_template_id", None)
    source_sha256 = getattr(draft, "source_sha256", None)
    edit_revision = getattr(draft, "edit_revision", None)
    title = getattr(draft, "title", None)
    content = getattr(draft, "content", None)
    variables = getattr(draft, "variables", None)
    normalized_facts = getattr(draft, "normalized_facts", None)
    rendered_template = getattr(draft, "rendered_template", None)

    if not isinstance(company_template_id, str) or not company_template_id:
        raise ValueError("Чернетка не має ID власного шаблону")
    if not isinstance(source_sha256, str) or not _SHA256.fullmatch(source_sha256):
        raise ValueError("Чернетка не має коректного SHA-256 джерела")
    if type(edit_revision) is not int or edit_revision < 1:
        raise ValueError("Чернетка не має коректної редакції джерела")
    title = _plain_text(title, "Назва чернетки", maximum=MAX_TITLE_CHARS).strip()
    if not title:
        raise ValueError("Назва чернетки не може бути порожньою")
    content = _plain_text(
        content, "Текст чернетки", maximum=MAX_CONTENT_CHARS
    )
    if not isinstance(variables, (list, tuple)):
        raise ValueError("Чернетка не містить опису полів")
    if len(variables) > MAX_COLLECTION_ITEMS:
        raise ValueError("Чернетка містить забагато полів")
    if not isinstance(normalized_facts, Mapping):
        raise ValueError("Чернетка не містить normalized facts")
    if not isinstance(rendered_template, Mapping):
        raise ValueError("Чернетка не містить rendered structure")

    return {
        "format": SNAPSHOT_FORMAT,
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "title": title,
        "source": {
            "company_template_id": company_template_id,
            "source_sha256": source_sha256,
            "edit_revision": edit_revision,
        },
        "variables": [_variable_payload(item) for item in variables],
        "normalized_facts": _json_safe(normalized_facts),
        "rendered_template": _json_safe(rendered_template),
        "rendered_content": content,
    }


def validate_snapshot_payload(data: object, expected_id: str = "") -> dict:
    """Validate persisted snapshot shape without executing its content."""
    if not isinstance(data, dict) or data.get("format") != SNAPSHOT_FORMAT:
        raise ValueError("Непідтримуваний формат prepared snapshot-а")
    snapshot_id = data.get("snapshot_id")
    if not isinstance(snapshot_id, str) or not _SNAPSHOT_ID.fullmatch(snapshot_id):
        raise ValueError("Некоректний ID prepared snapshot-а")
    if expected_id and snapshot_id != expected_id:
        raise ValueError("ID prepared snapshot-а не збігається з індексом")
    if not isinstance(data.get("created_at"), str) or not data["created_at"]:
        raise ValueError("Prepared snapshot не має часу створення")
    title = data.get("title")
    if (
        not isinstance(title, str)
        or not title.strip()
        or len(title) > MAX_TITLE_CHARS
        or "\x00" in title
    ):
        raise ValueError("Prepared snapshot має некоректну назву")
    source = data.get("source")
    if not isinstance(source, dict):
        raise ValueError("Prepared snapshot не має джерела")
    if (
        not isinstance(source.get("company_template_id"), str)
        or not source["company_template_id"]
        or not isinstance(source.get("source_sha256"), str)
        or not _SHA256.fullmatch(source["source_sha256"])
        or type(source.get("edit_revision")) is not int
        or source["edit_revision"] < 1
    ):
        raise ValueError("Prepared snapshot має некоректне джерело")
    if not isinstance(data.get("variables"), list):
        raise ValueError("Prepared snapshot не має опису полів")
    if not isinstance(data.get("normalized_facts"), dict):
        raise ValueError("Prepared snapshot не має normalized facts")
    if not isinstance(data.get("rendered_template"), dict):
        raise ValueError("Prepared snapshot не має rendered structure")
    content = data.get("rendered_content")
    if (
        not isinstance(content, str)
        or len(content) > MAX_CONTENT_CHARS
        or "\x00" in content
    ):
        raise ValueError("Prepared snapshot має некоректний rendered content")
    return data


def canonical_json_bytes(data: object) -> bytes:
    """Stable UTF-8 JSON bytes used for hashing and immutable storage."""
    return (
        json.dumps(
            data,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def strict_json_object(raw: bytes, description: str) -> dict:
    """Decode JSON while rejecting duplicate keys and non-object roots."""
    def pairs_hook(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Повторене поле JSON у " + description)
            result[key] = value
        return result

    try:
        data = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=pairs_hook,
        )
    except (UnicodeError, ValueError, TypeError) as exc:
        raise ValueError("Помилка JSON у %s: %s" % (description, exc))
    if not isinstance(data, dict):
        raise ValueError("Очікується JSON-об'єкт у " + description)
    return data
