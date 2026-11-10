# -*- coding: utf-8 -*-
"""Read-only view of existing orders and prepared paper documents.

The catalog does not create or migrate a database or an index. The two sources
are read independently, so a damaged source never hides records from the other.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path


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


def _read_paper(root):
    folder = Path(root) / "Data" / "PaperDocuments"
    index = folder / "index.json"
    try:
        # A redirected folder or index must not escape this workspace.
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
        rows.append({
            "key": ("paper", identity, pos),
            "source": "paper", "source_id": identity,
            "date": str(item.get("date") or ""),
            "created_at": str(item.get("created_at") or item.get("date") or ""),
            "number": "", "kind": str(item.get("kind") or "Документ"),
            "title": str(item.get("title") or ""),
            "person": str(item.get("person") or ""),
            "file_state": state, "file_path": path,
        })
    status = "Інструктажі й стажування: %d." % len(rows)
    if problems:
        status += " Проблемних записів або шляхів: %d." % problems
    return rows, status


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
        # mode=ro prevents SQLite from silently creating a missing database.
        con = sqlite3.connect(_readonly_sqlite_uri(db.resolve().as_uri()), uri=True, timeout=5)
        try:
            con.execute("PRAGMA query_only=ON")
            exists = con.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='operations_orders'"
            ).fetchone()
            if not exists:
                return [], "Таблиці наказів у цій базі немає."
            columns = {item[1] for item in con.execute(
                "PRAGMA table_info(operations_orders)").fetchall()}
            created = "created_at" if "created_at" in columns else "''"
            raw = con.execute(
                "SELECT id, order_date, order_no, order_type, subject, "
                + created + " FROM operations_orders"
            ).fetchall()
        finally:
            con.close()
    except (sqlite3.Error, OSError, ValueError, RuntimeError) as exc:
        return [], "Помилка читання наказів: " + str(exc)
    rows = [{
        "key": ("order", str(order_id), 0),
        "source": "order", "source_id": int(order_id),
        "date": str(day or ""), "created_at": str(created or day or ""),
        "number": str(number or ""),
        "kind": "Наказ", "title": str(subject or ""),
        "person": "", "order_type": str(kind or ""),
        "file_state": "Файл не прив'язаний", "file_path": None,
    } for order_id, day, number, kind, subject, created in raw]
    return rows, "Накази: %d." % len(rows)


def _sort_key(row):
    # Document date is the shared ordering key. Legacy order timestamps are
    # local and paper timestamps are UTC; comparing them globally is misleading.
    # Within paper documents retain their original creation-time ordering.
    return (
        row["date"], row["source"],
        row["created_at"] if row["source"] == "paper" else "",
        int(row["source_id"]) if row["source"] == "order" else 0,
        str(row["source_id"]), row["key"][2],
    )


def read_sources(root):
    """Read both sources and sort by document date; keep errors independent."""
    paper, paper_status = _read_paper(root)
    orders, order_status = _read_orders(root)
    rows = paper + orders
    rows.sort(key=_sort_key, reverse=True)
    return {"rows": rows, "paper_status": paper_status,
            "order_status": order_status}


def paginate_sources(snapshot, text_filter="", page=0, page_size=100):
    """Filter the full snapshot before paging; preserve all source statuses."""
    needle = str(text_filter or "").strip().casefold()
    all_rows = list(snapshot["rows"])
    if needle:
        fields = ("date", "number", "kind", "title", "person", "order_type")
        all_rows = [row for row in all_rows if needle in " ".join(
            str(row.get(field, "")) for field in fields).casefold()]
    # Rows are already sorted by document date in the background reader.
    page_size = max(1, min(int(page_size), 500))
    pages = max(1, (len(all_rows) + page_size - 1) // page_size)
    page = max(0, min(int(page), pages - 1))
    return {
        "rows": all_rows[page * page_size:(page + 1) * page_size],
        "total": len(all_rows), "page": page, "pages": pages,
        "paper_status": snapshot["paper_status"], "order_status": snapshot["order_status"],
    }


def read_catalog(root, text_filter="", page=0, page_size=100):
    """Convenience one-shot read for callers and tests."""
    return paginate_sources(read_sources(root), text_filter, page, page_size)
