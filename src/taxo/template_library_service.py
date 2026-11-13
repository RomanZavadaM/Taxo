# -*- coding: utf-8 -*-
"""Read-only application-facing view of the offline template library.

No Tk, database, archive installation or private template content is embedded
here. The selected Taxo workspace is supplied by ApplicationServices rather
than guessed from a machine-specific Windows path.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from template_library_reader import LibrarySnapshot, default_library_root, inspect_library


CATEGORY_LABELS = {
    "orders": "Накази",
    "briefings": "Інструктажі",
    "instructions": "Інструкції",
    "training-programs": "Навчальні програми",
    "acts": "Акти",
    "forms": "Форми та плани",
}
STATUS_LABELS = {
    "NOT_INSTALLED": "Бібліотеку шаблонів не встановлено.",
    "AVAILABLE": "Бібліотеку прочитано. Шаблони доступні лише для перегляду.",
    "INCOMPATIBLE": "Версія бібліотеки не сумісна із Taxo.",
    "DAMAGED": "Бібліотека містить пошкоджені або непідтримувані дані.",
    "UNAVAILABLE": "Немає доступу до бібліотеки.",
}


@dataclass(frozen=True)
class LibraryRow:
    """One safe, human-readable catalog item, not a generated document."""

    template_id: str
    revision_id: str
    category_id: str
    category: str
    title: str
    kind: str


@dataclass(frozen=True)
class LibraryView:
    """Read-only view-model for rendering independently from business rules."""

    status: str
    summary: str
    detail: str
    root: Path
    package_version: str
    rows: Tuple[LibraryRow, ...]


def view_from_snapshot(snapshot: LibrarySnapshot) -> LibraryView:
    """Format immutable reader results without mutating source packages."""
    rows = tuple(
        LibraryRow(
            template_id=entry.template_id,
            revision_id=entry.revision_id,
            category_id=entry.category_id,
            category=CATEGORY_LABELS.get(entry.category_id, entry.category_id),
            title=entry.title,
            kind=entry.document_kind,
        )
        for entry in snapshot.templates
    )
    status = snapshot.status
    return LibraryView(
        status=status,
        summary=STATUS_LABELS.get(status, "Невідомий стан бібліотеки."),
        detail=snapshot.message,
        root=snapshot.root,
        package_version=snapshot.package_version,
        rows=rows,
    )


def inspect_workspace_library(workspace_root: Path, app_version: str) -> LibraryView:
    """Inspect the default library directory in the currently selected workspace.

    No directory is created. A custom location can be passed through a future
    configuration adapter; no literal username or local drive is embedded.
    """
    return view_from_snapshot(
        inspect_library(default_library_root(Path(workspace_root)), app_version)
    )
