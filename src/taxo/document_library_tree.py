# -*- coding: utf-8 -*-
"""Virtual and user-managed folders over ready documents; never copies a file."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date

from document_library_collections import (
    catalog_document_key,
    collection_document_keys,
)

MONTHS = (
    "Січень", "Лютий", "Березень", "Квітень",
    "Травень", "Червень", "Липень", "Серпень",
    "Вересень", "Жовтень", "Листопад", "Грудень",
)


def document_day(row):
    """Read the actual document date; missing/invalid dates stay unclassified."""
    try:
        return date.fromisoformat(str(row.get("date") or "").strip())
    except ValueError:
        return None


def navigation_nodes(snapshot, mode):
    """Return (id, parent_id, caption, count, filter) for a virtual tree.

    Counts describe the full snapshot, never just the visible page.
    No file, database or metadata changes occur.
    """
    rows = snapshot.get("rows", ())
    result = [("all", "", "Усі документи", len(rows), ("all",))]
    if mode == "kind":
        counts = Counter(
            str(row.get("kind") or "").strip() or "Не визначено"
            for row in rows
        )
        for kind in sorted(counts, key=str.casefold):
            result.append(("kind:" + kind, "all", kind, counts[kind], ("kind", kind)))
    elif mode == "date":
        years = Counter()
        months = defaultdict(Counter)
        missing = 0
        for row in rows:
            day = document_day(row)
            if day is None:
                missing += 1
                continue
            years[day.year] += 1
            months[day.year][day.month] += 1
        for year in sorted(years, reverse=True):
            parent = "year:" + str(year)
            result.append((parent, "all", str(year), years[year], ("year", year)))
            for month in sorted(months[year]):
                result.append((
                    "month:%d:%02d" % (year, month), parent,
                    "%02d — %s" % (month, MONTHS[month - 1]),
                    months[year][month], ("month", year, month),
                ))
        if missing:
            result.append(("undated", "all", "Без дати", missing, ("undated",)))
    else:
        raise ValueError("Невідомий режим перегляду бібліотеки")
    return tuple(result)


def collection_navigation_nodes(snapshot, collection_state):
    """Build «Мої папки» over stable catalog keys.

    A parent folder includes documents placed directly in it and in descendants.
    The same document may belong to several folders without creating copies.
    """
    rows = snapshot.get("rows", ())
    available = set()
    for row in rows:
        try:
            available.add(catalog_document_key(row))
        except ValueError:
            continue

    active = {
        row.collection_id: row
        for row in collection_state.collections
        if not row.archived_at
    }
    children = defaultdict(list)
    for row in active.values():
        parent_id = row.parent_id if row.parent_id in active else ""
        children[parent_id].append(row)
    for values in children.values():
        values.sort(key=lambda row: (
            row.sort_order, row.name.casefold(), row.collection_id
        ))

    result = [("all", "", "Мої папки", len(rows), ("all",))]

    def append_children(parent_id):
        for row in children.get(parent_id, ()):
            keys = collection_document_keys(
                collection_state, row.collection_id, include_descendants=True
            )
            result.append((
                "collection:" + row.collection_id,
                "collection:" + parent_id if parent_id else "all",
                row.name,
                len(available.intersection(keys)),
                ("collection", row.collection_id, tuple(keys)),
            ))
            append_children(row.collection_id)

    append_children("")
    return tuple(result)


def matches_navigation(row, selection):
    """Filter an existing row by a selected virtual or user-managed folder."""
    if not selection or selection == ("all",):
        return True
    field = selection[0]
    if field == "kind" and len(selection) == 2:
        return (str(row.get("kind") or "").strip() or "Не визначено") == selection[1]
    if field == "collection" and len(selection) == 3:
        try:
            key = catalog_document_key(row)
        except ValueError:
            return False
        return key in set(selection[2])
    day = document_day(row)
    if field == "undated" and len(selection) == 1:
        return day is None
    if field == "year" and len(selection) == 2:
        return day is not None and day.year == selection[1]
    if field == "month" and len(selection) == 3:
        return day is not None and (day.year, day.month) == (selection[1], selection[2])
    raise ValueError("Некоректний вузол дерева бібліотеки")
