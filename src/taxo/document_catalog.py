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


def _read_paper(root):
    folder = Path(root) / "Data" / "PaperDocuments"
    index = folder / "index.json"
    try:
        data = json.loads(index.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("індекс не є списком")
    except FileNotFoundError:
        return [], "Каталог інструктажів і стажування ще не створений."
    except (OSError, ValueError, UnicodeError) as exc:
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
            path = _paper_file(folder, item.get("file"))
            state = "Файл доступний" if path.is_file() else "Файл не знайдено"
        except (ValueError, OSError, RuntimeError):
            path = None
            state = "Небезпечний шлях"
            problems += 1
        rows.append({
            "key": ("paper", identity, pos),
            "source": "paper", "source_id": identity,
            "date": str(item.get("date") or ""),
            "number": "", "kind": str(item.get("kind") or "Документ"),
            "title": str(item.get("title") or ""),
            "person": str(item.get("person") or ""),
            "file_state": state, "file_path": path,
        })
    status = "Інструктажі й стажування: %d." % len(rows)
    if problems:
        status += " Проблемних записів або шляхів: %d." % problems
    return rows, status


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
        con = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
        try:
            con.execute("PRAGMA query_only=ON")
            exists = con.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='operations_orders'"
            ).fetchone()
            if not exists:
                return [], "Таблиці наказів у цій базі немає."
            raw = con.execute(
                "SELECT id, order_date, order_no, order_type, subject "
                "FROM operations_orders ORDER BY order_date DESC, id DESC"
            ).fetchall()
        finally:
            con.close()
    except (sqlite3.Error, OSError, ValueError, RuntimeError) as exc:
        return [], "Помилка читання наказів: " + str(exc)
    rows = [{
        "key": ("order", str(order_id), 0),
        "source": "order", "source_id": int(order_id),
        "date": str(day or ""), "number": str(number or ""),
        "kind": "Наказ", "title": str(subject or ""),
        "person": "", "order_type": str(kind or ""),
        "file_state": "Файл не прив'язаний", "file_path": None,
    } for order_id, day, number, kind, subject in raw]
    return rows, "Накази: %d." % len(rows)


def read_sources(root):
    """Read both sources once; keep their errors independent."""
    paper, paper_status = _read_paper(root)
    orders, order_status = _read_orders(root)
    return {"rows": paper + orders, "paper_status": paper_status,
            "order_status": order_status}


def paginate_sources(snapshot, text_filter="", page=0, page_size=100):
    """Filter the full snapshot before paging; preserve all source statuses."""
    needle = str(text_filter or "").strip().casefold()
    all_rows = list(snapshot["rows"])
    if needle:
        fields = ("date", "number", "kind", "title", "person", "order_type")
        all_rows = [row for row in all_rows if needle in " ".join(
            str(row.get(field, "")) for field in fields).casefold()]
    # Invalid or blank legacy dates remain visible as text rather than disappearing.
    all_rows.sort(key=lambda row: (row["date"], row["source"], str(row["source_id"]),
                                  row["key"][2]), reverse=True)
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
