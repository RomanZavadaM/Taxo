# -*- coding: utf-8 -*-
"""Read-only view of orders, prepared Word documents and DocumentVault.

Each source is read independently. A damaged source never hides valid records
from the other sources. Exact PaperDocuments/DocumentVault identities are shown
as one logical row; names and dates are never used for automatic merging.
"""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import date
from pathlib import Path

from document_vault_store import list_document_vault
from document_vault_paper_scans import list_paper_scans


CATEGORY_PERSONNEL = "Кадрові"
CATEGORY_OPERATIONAL = "Експлуатаційні"
CATEGORY_OCCUPATIONAL_SAFETY = "Охорона праці"
CATEGORY_ROAD_SAFETY = "БДР"
CATEGORY_FIRE_SAFETY = "Пожежна безпека"
CATEGORY_UNCLASSIFIED = "Не визначено"
DOCUMENT_CATEGORIES = (
    CATEGORY_PERSONNEL,
    CATEGORY_OPERATIONAL,
    CATEGORY_OCCUPATIONAL_SAFETY,
    CATEGORY_ROAD_SAFETY,
    CATEGORY_FIRE_SAFETY,
    CATEGORY_UNCLASSIFIED,
)

_ROAD_SAFETY_ORDER_TYPES = {"road_safety", "accident_commission"}
_OCCUPATIONAL_SAFETY_ORDER_TYPES = {"occupational_safety", "safety_training"}
_FIRE_SAFETY_ORDER_TYPES = {"fire_safety"}


def _order_category(order_series, order_type):
    """Classify only structured order metadata; never infer from free text."""
    if str(order_series or "").strip() == "personnel":
        return CATEGORY_PERSONNEL
    order_type = str(order_type or "").strip()
    if order_type in _ROAD_SAFETY_ORDER_TYPES:
        return CATEGORY_ROAD_SAFETY
    if order_type in _OCCUPATIONAL_SAFETY_ORDER_TYPES:
        return CATEGORY_OCCUPATIONAL_SAFETY
    if order_type in _FIRE_SAFETY_ORDER_TYPES:
        return CATEGORY_FIRE_SAFETY
    return CATEGORY_OPERATIONAL


def _paper_file(folder, value):
    """Accept only a DOCX inside PaperDocuments, including after symlink resolution."""
    if not isinstance(value, str) or not value or "/" in value or "\\" in value:
        raise ValueError("Небезпечна адреса документа")
    if value in (".", "..") or not value.endswith(".docx") or Path(value).name != value:
        raise ValueError("Небезпечна адреса документа")
    path = folder / value
    if path.resolve().parent != folder.resolve():
        raise ValueError("Файл документа поза робочим сховищем")
    return path


def paper_file(root, value):
    """Resolve a catalog file only inside the currently selected workspace."""
    folder = Path(root) / "Data" / "PaperDocuments"
    try:
        folder.resolve().relative_to(Path(root).resolve())
    except (ValueError, OSError, RuntimeError):
        raise ValueError("Каталог документів поза робочим сховищем")
    return _paper_file(folder, value)


def _paper_revision(item):
    value = item.get("document_revision")
    if type(value) is int and value >= 1:
        return value
    return 1 if item.get("prepared_snapshot_id") else 0


def _read_paper(root):
    folder = Path(root) / "Data" / "PaperDocuments"
    index = folder / "index.json"
    try:
        folder.resolve().relative_to(Path(root).resolve())
        if index.exists() and index.resolve().parent != folder.resolve():
            raise ValueError("індекс поза робочим сховищем")
        data = json.loads(index.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("індекс не є списком")
    except FileNotFoundError:
        return [], "Каталог інструктажів і стажування ще не створений."
    except (OSError, ValueError, UnicodeError, RuntimeError) as exc:
        return [], "Помилка каталогу інструктажів і стажування: " + str(exc)

    rows, problems, seen = [], 0, set()
    for pos, item in enumerate(data):
        if not isinstance(item, dict):
            problems += 1
            continue
        identity = str(item.get("id") or "").strip()
        if not identity or identity in seen:
            problems += 1
        seen.add(identity)
        try:
            path = paper_file(root, item.get("file"))
            state = "Файл доступний" if path.is_file() else "Файл не знайдено"
        except (ValueError, OSError, RuntimeError):
            path = None
            state = "Небезпечний шлях"
            problems += 1

        revision = _paper_revision(item)
        rows.append({
            "key": ("paper", identity, pos),
            "source": "paper",
            "sources": ("paper",),
            "source_label": "Word",
            "source_id": identity,
            "date": str(item.get("date") or ""),
            "created_at": str(item.get("created_at") or item.get("date") or ""),
            "number": "",
            "kind": str(item.get("kind") or "Документ"),
            "title": str(item.get("title") or ""),
            "person": str(item.get("person") or ""),
            "category": CATEGORY_UNCLASSIFIED,
            "file_state": state,
            "file_path": path,
            "origin": str(item.get("origin") or ""),
            "document_status": str(item.get("document_status") or ""),
            "prepared_snapshot_id": str(item.get("prepared_snapshot_id") or ""),
            "company_template_id": str(item.get("company_template_id") or ""),
            "document_family_id": str(item.get("document_family_id") or ""),
            "document_revision": revision,
            "previous_document_id": str(item.get("previous_document_id") or ""),
            "content_sha256": str(item.get("content_sha256") or ""),
            "revision_label": ("r%d" % revision) if revision else "",
            "vault_id": "",
            "vault_status": "",
            "vault_created_at": "",
            "vault_content_sha256": "",
        })
    status = "Інструктажі й стажування: %d." % len(rows)
    if problems:
        status += " Проблемних записів або шляхів: %d." % problems
    return rows, status


def _read_vault(root):
    try:
        records = list_document_vault(Path(root))
    except (OSError, ValueError, UnicodeError, RuntimeError) as exc:
        return [], "Помилка сховища документів: " + str(exc)

    rows = []
    for record in records:
        rows.append({
            "key": ("vault", record.vault_id, 0),
            "source": "vault",
            "sources": ("vault",),
            "source_label": "Сховище",
            "source_id": record.vault_id,
            "source_document_id": record.source_document_id,
            "date": record.document_date,
            "created_at": record.created_at,
            "number": "",
            "kind": record.kind,
            "title": record.title,
            "person": "",
            "category": CATEGORY_UNCLASSIFIED,
            "file_state": "Незмінна копія у сховищі",
            "file_path": None,
            "origin": "document_vault",
            "document_status": record.status,
            "prepared_snapshot_id": record.prepared_snapshot_id,
            "company_template_id": record.company_template_id,
            "document_family_id": record.document_family_id,
            "document_revision": record.document_revision,
            "previous_document_id": "",
            "content_sha256": record.content_sha256,
            "revision_label": "r%d" % record.document_revision,
            "vault_id": record.vault_id,
            "vault_status": record.status,
            "vault_created_at": record.created_at,
            "vault_content_sha256": record.content_sha256,
        })
    return rows, "Сховище документів: %d." % len(rows)


def _read_paper_scan_counts(root, vault_rows):
    """Read active paper-scan counts without making the catalog depend on scans."""

    if not vault_rows:
        return {}, "Скани: у сховищі ще немає документів."
    try:
        records = list_paper_scans(Path(root))
    except (OSError, ValueError, UnicodeError, RuntimeError) as exc:
        return None, "Помилка перевірки сканів: " + str(exc)

    counts = {}
    for record in records:
        counts[record.vault_id] = counts.get(record.vault_id, 0) + 1
    return counts, "Активні скани: %d." % len(records)


def _attach_paper_scan_state(rows, counts):
    """Add a read-only active-scan indicator to every catalog row."""

    for row in rows:
        vault_id = str(row.get("vault_id") or "")
        if not vault_id:
            row["paper_scan_count"] = 0
            row["paper_scan_state"] = "—"
        elif counts is None:
            row["paper_scan_count"] = None
            row["paper_scan_state"] = "Помилка перевірки"
        else:
            count = int(counts.get(vault_id, 0))
            row["paper_scan_count"] = count
            row["paper_scan_state"] = "Є: %d" % count if count else "Немає"
    return rows


def _merge_paper_and_vault(paper_rows, vault_rows):
    """Merge only a vault record that points to the exact PaperDocuments ID."""
    paper_by_id = {}
    for row in paper_rows:
        identity = row.get("source_id")
        if identity and identity not in paper_by_id:
            paper_by_id[identity] = row

    standalone = []
    for vault in vault_rows:
        source_document_id = str(vault.get("source_document_id") or "")
        paper = paper_by_id.get(source_document_id)
        if paper is None:
            standalone.append(vault)
            continue
        paper["sources"] = ("paper", "vault")
        paper["source_label"] = "Word + сховище"
        paper["vault_id"] = vault["vault_id"]
        paper["vault_status"] = vault["vault_status"]
        paper["vault_created_at"] = vault["vault_created_at"]
        paper["vault_content_sha256"] = vault["vault_content_sha256"]
        paper["file_state"] = paper["file_state"] + " · копія у сховищі"
    return paper_rows + standalone


def _readonly_sqlite_uri(file_uri):
    """Allow Windows UNC paths without requiring SQLite URI authority support."""
    if file_uri.startswith("file://") and not file_uri.startswith("file:///"):
        file_uri = "file:////" + file_uri[len("file://"):]
    return file_uri + "?mode=ro"


def _read_orders(root):
    db = Path(root) / "Data" / "driver_worktime.sqlite3"
    try:
        db.stat()
    except FileNotFoundError:
        return [], "Базу наказів не знайдено."
    except OSError as exc:
        return [], "Помилка доступу до бази наказів: " + str(exc)
    try:
        con = sqlite3.connect(
            _readonly_sqlite_uri(db.resolve().as_uri()),
            uri=True,
            timeout=5,
        )
        try:
            con.execute("PRAGMA query_only=ON")
            exists = con.execute(
                "SELECT 1 FROM sqlite_master "
                "WHERE type='table' AND name='operations_orders'"
            ).fetchone()
            if not exists:
                return [], "Таблиці наказів у цій базі немає."
            columns = {
                item[1] for item in con.execute(
                    "PRAGMA table_info(operations_orders)"
                ).fetchall()
            }
            created = "created_at" if "created_at" in columns else "''"
            series = "order_series" if "order_series" in columns else "''"
            raw = con.execute(
                "SELECT id, order_date, order_no, order_type, subject, "
                + series + ", " + created + " FROM operations_orders"
            ).fetchall()
        finally:
            con.close()
    except (sqlite3.Error, OSError, ValueError, RuntimeError) as exc:
        return [], "Помилка читання наказів: " + str(exc)

    rows = [{
        "key": ("order", str(order_id), 0),
        "source": "order",
        "sources": ("order",),
        "source_label": "Наказ",
        "source_id": int(order_id),
        "date": str(day or ""),
        "created_at": str(created or day or ""),
        "number": str(number or ""),
        "kind": "Наказ",
        "title": str(subject or ""),
        "person": "",
        "order_type": str(kind or ""),
        "order_series": str(series or ""),
        "category": _order_category(series, kind),
        "file_state": "Файл не прив'язаний",
        "file_path": None,
        "revision_label": "",
        "prepared_snapshot_id": "",
        "vault_id": "",
        "vault_status": "",
        "vault_created_at": "",
        "vault_content_sha256": "",
    } for order_id, day, number, kind, subject, series, created in raw]
    return rows, "Накази: %d." % len(rows)


def _sort_key(row):
    return (
        row["date"],
        row["source"],
        row["created_at"] if row["source"] != "order" else "",
        int(row["source_id"]) if row["source"] == "order" else 0,
        str(row["source_id"]),
        row["key"][2],
    )


def read_sources(root):
    """Read all sources, merge only exact PaperDocuments/Vault identities."""
    paper, paper_status = _read_paper(root)
    vault, vault_status = _read_vault(root)
    scan_counts, paper_scan_status = _read_paper_scan_counts(root, vault)
    orders, order_status = _read_orders(root)
    rows = _merge_paper_and_vault(paper, vault) + orders
    _attach_paper_scan_state(rows, scan_counts)
    rows.sort(key=_sort_key, reverse=True)
    return {
        "rows": rows,
        "paper_status": paper_status,
        "vault_status": vault_status,
        "paper_scan_status": paper_scan_status,
        "order_status": order_status,
    }



def _date_bound(value, label):
    """Parse an optional inclusive YYYY-MM-DD catalog boundary."""
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise ValueError(
            "%s: введіть дату у форматі РРРР-ММ-ДД" % label
        )


def document_kinds(snapshot):
    """Return exact document types already present in the catalog snapshot."""
    values = {
        str(row.get("kind") or "").strip()
        for row in snapshot.get("rows", ())
    }
    values.discard("")
    return tuple(sorted(values, key=str.casefold))


def document_categories(snapshot):
    """Return known categories in a stable user-facing order."""
    present = {
        str(row.get("category") or CATEGORY_UNCLASSIFIED).strip()
        for row in snapshot.get("rows", ())
    }
    return tuple(category for category in DOCUMENT_CATEGORIES if category in present)


def paginate_sources(
    snapshot,
    text_filter="",
    page=0,
    page_size=100,
    source_filter="all",
    scan_filter="all",
    date_from="",
    date_to="",
    kind_filter="all",
    category_filter="all",
    date_sort="default",
    number_sort="default",
):
    """Filter the full snapshot before paging; preserve all source statuses."""
    needle = str(text_filter or "").strip().casefold()
    all_rows = list(snapshot["rows"])
    start_day = _date_bound(date_from, "Період від")
    end_day = _date_bound(date_to, "Період до")
    if start_day is not None and end_day is not None and start_day > end_day:
        raise ValueError("Період від не може бути пізніше за період до")
    if start_day is not None or end_day is not None:
        filtered = []
        for row in all_rows:
            raw_day = str(row.get("date") or "").strip()
            try:
                row_day = date.fromisoformat(raw_day)
            except ValueError:
                continue
            if start_day is not None and row_day < start_day:
                continue
            if end_day is not None and row_day > end_day:
                continue
            filtered.append(row)
        all_rows = filtered
    if source_filter in ("paper", "vault", "order"):
        all_rows = [
            row for row in all_rows
            if source_filter in row.get("sources", (row.get("source"),))
        ]
    selected_kind = str(kind_filter or "all").strip()
    if selected_kind and selected_kind != "all":
        all_rows = [
            row for row in all_rows
            if str(row.get("kind") or "").strip() == selected_kind
        ]
    selected_category = str(category_filter or "all").strip()
    if selected_category and selected_category != "all":
        all_rows = [
            row for row in all_rows
            if str(row.get("category") or CATEGORY_UNCLASSIFIED).strip()
            == selected_category
        ]
    if scan_filter == "present":
        all_rows = [
            row for row in all_rows
            if row.get("vault_id")
            and isinstance(row.get("paper_scan_count"), int)
            and row["paper_scan_count"] > 0
        ]
    elif scan_filter == "absent":
        all_rows = [
            row for row in all_rows
            if row.get("vault_id") and row.get("paper_scan_count") == 0
        ]
    elif scan_filter == "error":
        all_rows = [
            row for row in all_rows
            if row.get("vault_id") and row.get("paper_scan_count") is None
        ]
    if source_filter == "paper":
        all_rows.sort(
            key=lambda row: (row["created_at"], row["key"][2]),
            reverse=True,
        )
    if source_filter == "vault":
        all_rows.sort(
            key=lambda row: (
                row.get("vault_created_at") or row["created_at"],
                str(row.get("vault_id") or row["source_id"]),
            ),
            reverse=True,
        )
    if needle:
        fields = (
            "date", "number", "kind", "title", "person",
            "order_type", "order_series", "category", "revision_label",
            "source_label", "paper_scan_state",
        )
        all_rows = [
            row for row in all_rows
            if needle in " ".join(
                str(row.get(field, "")) for field in fields
            ).casefold()
        ]
    if date_sort in ("newest", "oldest"):
        def date_order_key(row):
            try:
                document_day = date.fromisoformat(
                    str(row.get("date") or "").strip()
                )
            except ValueError:
                document_day = None
            if document_day is None:
                return (1, 0)
            day_number = document_day.toordinal()
            return (0, -day_number if date_sort == "newest" else day_number)

        # Stable ties preserve the existing source-specific order.
        # Missing/invalid dates stay after dated records in both directions.
        all_rows.sort(key=date_order_key)
    if number_sort in ("ascending", "descending"):
        numbered = []
        unnumbered = []
        for row in all_rows:
            number = str(row.get("number") or "").strip()
            if number:
                numbered.append(row)
            else:
                unnumbered.append(row)

        def number_key(row):
            # Natural order: 2 comes before 10, including mixed values
            # such as 2-А, 10-А. Preserve stable order on equal keys.
            value = str(row.get("number") or "").strip().casefold()
            return tuple(
                (0, int(part)) if part.isdecimal() else (1, part)
                for part in re.split(r"(\d+)", value) if part
            )

        numbered.sort(
            key=number_key, reverse=number_sort == "descending"
        )
        all_rows = numbered + unnumbered
    page_size = max(1, min(int(page_size), 500))
    pages = max(1, (len(all_rows) + page_size - 1) // page_size)
    page = max(0, min(int(page), pages - 1))
    return {
        "rows": all_rows[page * page_size:(page + 1) * page_size],
        "total": len(all_rows),
        "page": page,
        "pages": pages,
        "available_kinds": document_kinds(snapshot),
        "available_categories": document_categories(snapshot),
        "paper_status": snapshot["paper_status"],
        "vault_status": snapshot.get("vault_status", ""),
        "paper_scan_status": snapshot.get("paper_scan_status", ""),
        "order_status": snapshot["order_status"],
    }


def read_catalog(
    root,
    text_filter="",
    page=0,
    page_size=100,
    scan_filter="all",
    date_from="",
    date_to="",
    kind_filter="all",
    category_filter="all",
    date_sort="default",
    number_sort="default",
):
    """Convenience one-shot read for callers and tests."""
    return paginate_sources(
        read_sources(root),
        text_filter,
        page,
        page_size,
        scan_filter=scan_filter,
        date_from=date_from,
        date_to=date_to,
        kind_filter=kind_filter,
        category_filter=category_filter,
        date_sort=date_sort,
        number_sort=number_sort,
    )
