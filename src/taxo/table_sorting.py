# -*- coding: utf-8 -*-
"""Reusable type-aware sorting for Taxo ttk.Treeview registers.

This module only reorders visible rows; it does not change database records,
document validity, filters, or the meaning of status labels.
"""
from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

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


def _number_key(text):
    normalized = str(text or "").strip().replace("\xa0", "").replace(" ", "").replace(",", ".")
    try:
        return (0, Decimal(normalized))
    except (InvalidOperation, ValueError):
        return (1, _natural_text(text))


def _date_key(text):
    value = str(text or "").strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d.%m.%y"):
        try:
            parsed = datetime.strptime(value, fmt)
            return (0, parsed.toordinal())
        except ValueError:
            pass
    return (1, _natural_text(value))


def _datetime_key(text):
    """Order displayed change-log timestamps by instant, not by text.

    SQLite change logs use ISO timestamps; also accept common local display
    forms. Mixed offsets are normalized through UTC timestamps where present,
    so sorting remains comparable with naive local values.
    """
    value = str(text or "").strip()
    normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        parsed = None
    if parsed is None:
        for fmt in ("%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M"):
            try:
                parsed = datetime.strptime(value, fmt)
                break
            except ValueError:
                pass
    if parsed is not None:
        # A numeric key avoids comparing offset-aware and naive datetime
        # objects, which Python does not allow.
        if parsed.tzinfo is not None:
            from datetime import timezone
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return (0, (parsed.toordinal(), parsed.hour, parsed.minute,
                    parsed.second, parsed.microsecond))
    return (1, _natural_text(value))


def _duration_key(text):
    value = str(text or "").strip()
    match = re.fullmatch(r"(\d+):(\d{1,2})", value)
    if match:
        hours, minutes = int(match.group(1)), int(match.group(2))
        if 0 <= minutes < 60:
            return (0, hours * 60 + minutes)
    return (1, _natural_text(value))


def _status_key(text, status_order=None):
    value = str(text or "").strip()
    if status_order:
        if isinstance(status_order, dict):
            normalized = {str(key).casefold(): rank for key, rank in status_order.items()}
        else:
            normalized = {str(key).casefold(): rank for rank, key in enumerate(status_order)}
        key = value.casefold()
        if key in normalized:
            return (0, normalized[key])
        return (1, _natural_text(value))
    return (0, _natural_text(value))


def _value_key(column, value, value_type=None, status_order=None):
    text = str(value or "").strip()
    if not text:
        return (1,)

    kind = value_type
    if kind is None:
        if column in NUMERIC_COLUMNS:
            kind = "number"
        elif column == DOCUMENTS_COLUMN:
            kind = "documents"
        else:
            kind = "text"

    if kind == "number":
        return (0,) + _number_key(text)
    if kind == "date":
        return (0,) + _date_key(text)
    if kind == "datetime":
        return (0,) + _datetime_key(text)
    if kind == "duration":
        return (0,) + _duration_key(text)
    if kind == "status":
        return (0,) + _status_key(text, status_order)
    if kind == "documents":
        return (0, _document_priority(text), _natural_text(text))
    return (0, _natural_text(text))


def sorted_row_ids(
    rows, column, descending=False, *, value_type=None, status_order=None
):
    """Return iid order, keeping blanks last in either direction.

    value_type may be text, number, date, datetime, duration, status or the legacy
    documents kind. The original order is preserved for ties to avoid
    surprising changes after reload.
    """
    present = []
    missing = []
    for iid, value in rows:
        pair = (iid, _value_key(column, value, value_type, status_order))
        (missing if pair[1][0] else present).append(pair)
    present.sort(key=lambda pair: pair[1][1:], reverse=bool(descending))
    return [iid for iid, _ in present + missing]


def sort_treeview(
    tree, column, descending=False, *, value_type=None, status_order=None
):
    """Reorder only the already-visible Treeview items, preserving selection."""
    rows = [(iid, tree.set(iid, column)) for iid in tree.get_children("")]
    order = sorted_row_ids(
        rows,
        column,
        descending,
        value_type=value_type,
        status_order=status_order,
    )
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



def restore_tree_selection(tree, item_ids):
    """Restore only still-visible stable Treeview IDs after a refresh."""
    visible = set(tree.get_children(""))
    retained = tuple(iid for iid in item_ids if iid in visible)
    if not retained:
        return ()
    tree.selection_set(retained)
    tree.focus(retained[0])
    try:
        tree.see(retained[0])
    except Exception:
        pass
    return retained


def configure_sortable_tree(tree, columns, sort_state, state_key):
    """Attach reusable type-aware click sorting to a Treeview."""
    specs = {key: (label, value_type, status_order) for key, label, value_type, status_order in columns}

    def apply_current():
        current = sort_state.get(state_key)
        if current is None:
            return ()
        column, descending = current
        _label, value_type, status_order = specs[column]
        order = sort_treeview(tree, column, descending, value_type=value_type, status_order=status_order)
        update_headings()
        return tuple(order)

    def sort_by_header(column):
        current = sort_state.get(state_key)
        descending = bool(current and current[0] == column and not current[1])
        sort_state[state_key] = (column, descending)
        return apply_current()

    def update_headings():
        current = sort_state.get(state_key)
        for key, (label, _value_type, _status_order) in specs.items():
            direction = ""
            if current and current[0] == key:
                direction = " ▼" if current[1] else " ▲"
            tree.heading(key, text=label + direction, command=lambda name=key: sort_by_header(name))

    update_headings()
    return apply_current
