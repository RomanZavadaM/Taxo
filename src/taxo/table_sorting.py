# -*- coding: utf-8 -*-
"""Reusable type-aware sorting for Taxo ttk.Treeview registers.

This module only reorders visible rows; it does not change database records,
document validity, filters, or the meaning of status labels.
"""
from __future__ import annotations

import re

NUMERIC_COLUMNS = frozenset(("id", "year"))
DOCUMENTS_COLUMN = "documents"


def _document_priority(text):
    """Group valid documents before warnings, without claiming trip clearance."""
    value = str(text or "").strip().casefold()
    if not value:
        return 3
    if value.startswith("актуально"):
        return 0
    if value.startswith("проблема"):
        return 2
    return 1


def _natural_text(value):
    parts = re.split(r"(\d+)", str(value or "").strip().casefold())
    return tuple((1, int(part)) if part.isdigit() else (0, part) for part in parts)


def _value_key(column, value):
    text = str(value or "").strip()
    if not text:
        return (1,)
    if column in NUMERIC_COLUMNS:
        try:
            return (0, int(text))
        except ValueError:
            return (0, 0, _natural_text(text))
    if column == DOCUMENTS_COLUMN:
        return (0, _document_priority(text), _natural_text(text))
    return (0, _natural_text(text))


def sorted_row_ids(rows, column, descending=False):
    """Return iid order, keeping blanks last in either direction.

    rows: iterable of (iid, displayed_value) pairs. The original order is
    preserved for ties to avoid surprising changes after reload.
    """
    present = []
    missing = []
    for iid, value in rows:
        pair = (iid, _value_key(column, value))
        (missing if pair[1][0] else present).append(pair)
    present.sort(key=lambda pair: pair[1][1:], reverse=bool(descending))
    return [iid for iid, _ in present + missing]


def sort_treeview(tree, column, descending=False):
    """Reorder only the already-visible Treeview items, preserving selection."""
    rows = [(iid, tree.set(iid, column)) for iid in tree.get_children("")]
    order = sorted_row_ids(rows, column, descending)
    selected = tuple(tree.selection())
    focus = tree.focus()
    for position, iid in enumerate(order):
        tree.move(iid, "", position)
    retained = [iid for iid in selected if iid in order]
    if retained:
        tree.selection_set(retained)
    if focus in order:
        tree.focus(focus)
    return order
