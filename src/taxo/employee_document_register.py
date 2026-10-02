# -*- coding: utf-8 -*-
"""Taxo 10.5-r3 — unified employee document register.

This module is a read/index layer over the existing ``employee_documents`` table.
It does not duplicate employee documents and it does not infer deletion from state
registry extracts. Documents imported from a registry and documents entered locally
remain in the same working register with visible provenance.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

import personnel_registry as personnel

APP_VERSION = "10.5-r3"
EXPIRING_SOON_DAYS = 30

STATE_VALID = "valid"
STATE_EXPIRING = "expiring"
STATE_EXPIRED = "expired"
STATE_NO_EXPIRY = "no_expiry"
STATE_DATE_REVIEW = "date_review"
STATE_ARCHIVED = "archived"

STATE_LABELS = {
    STATE_VALID: "Чинний",
    STATE_EXPIRING: "Закінчується ≤30 днів",
    STATE_EXPIRED: "Прострочений",
    STATE_NO_EXPIRY: "Строк не вказано / безстроковий",
    STATE_DATE_REVIEW: "Перевірити дату строку",
    STATE_ARCHIVED: "Архів",
}

SOURCE_ALL = "all"
SOURCE_MANUAL = "manual"
SOURCE_REGISTRY = "registry"
SOURCE_LABELS = {
    SOURCE_ALL: "Усі джерела",
    SOURCE_MANUAL: "Ручне введення",
    SOURCE_REGISTRY: "Державний реєстр",
}


def _text(value):
    return str(value or "").strip()


def _norm(value):
    return " ".join(_text(value).casefold().split())


def _date_value(value):
    text = _text(value)
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return False


def document_state(row, today=None, soon_days=EXPIRING_SOON_DAYS):
    """Return an informational document state without changing the document."""
    if not int(row["active"] or 0):
        return STATE_ARCHIVED
    today = today or date.today()
    expiry = _date_value(row["expiry_date"])
    if expiry is None:
        return STATE_NO_EXPIRY
    if expiry is False:
        return STATE_DATE_REVIEW
    if expiry < today:
        return STATE_EXPIRED
    if expiry <= today + timedelta(days=int(soon_days)):
        return STATE_EXPIRING
    return STATE_VALID


def source_class(row):
    kind = _norm(row["source_kind"])
    if not kind or kind == "manual":
        return SOURCE_MANUAL
    return SOURCE_REGISTRY


def source_display(row):
    if source_class(row) == SOURCE_MANUAL:
        return "Ручне введення"
    return _text(row["source_name"]) or _text(row["source_kind"]) or "Державний реєстр"


def _employee_name(row):
    return " ".join(x for x in (_text(row["last_name"]), _text(row["first_name"]), _text(row["middle_name"])) if x)


def _row_dict(row, today=None):
    data = {key: row[key] for key in row.keys()}
    data["employee_name"] = _employee_name(row)
    data["state"] = document_state(row, today=today)
    data["state_label"] = STATE_LABELS[data["state"]]
    data["source_class"] = source_class(row)
    data["source_display"] = source_display(row)
    return data


def list_documents(con, *, query="", doc_type="", state="", source=SOURCE_ALL,
                   include_archived=False, today=None):
    """Return the unified register across all employees.

    Filtering is intentionally non-destructive. A missing person/document in a later
    registry extract never archives or removes a local record.
    """
    personnel.ensure_schema_on_connection(con)
    rows = con.execute(
        """SELECT d.*, e.last_name, e.first_name, e.middle_name, e.personnel_no,
                  e.active AS employee_active
             FROM employee_documents d
             JOIN employees e ON e.id=d.employee_id
         ORDER BY d.active DESC, e.last_name, e.first_name, e.middle_name,
                  d.doc_type, d.expiry_date, d.id"""
    ).fetchall()
    wanted = _norm(query)
    result = []
    for row in rows:
        data = _row_dict(row, today=today)
        if not include_archived and data["state"] == STATE_ARCHIVED:
            continue
        if doc_type and _text(data["doc_type"]) != _text(doc_type):
            continue
        if state and data["state"] != state:
            continue
        if source not in ("", SOURCE_ALL) and data["source_class"] != source:
            continue
        if wanted:
            haystack = _norm(" ".join((
                data["employee_name"], _text(data["personnel_no"]), _text(data["doc_type"]),
                _text(data["series"]), _text(data["number"]), _text(data["issuer"]),
                data["source_display"], _text(data["notes"]),
            )))
            if wanted not in haystack:
                continue
        result.append(data)
    return result


def distinct_document_types(con):
    personnel.ensure_schema_on_connection(con)
    return [row[0] for row in con.execute(
        """SELECT DISTINCT doc_type FROM employee_documents
           WHERE TRIM(COALESCE(doc_type,''))<>'' ORDER BY doc_type"""
    ).fetchall()]


def summary(rows):
    result = {key: 0 for key in STATE_LABELS}
    for row in rows:
        state = row.get("state") if isinstance(row, dict) else document_state(row)
        if state in result:
            result[state] += 1
    result["total"] = len(rows)
    return result


def get_document(con, document_id):
    personnel.ensure_schema_on_connection(con)
    row = con.execute(
        """SELECT d.*, e.last_name, e.first_name, e.middle_name, e.personnel_no,
                  e.active AS employee_active
             FROM employee_documents d
             JOIN employees e ON e.id=d.employee_id
            WHERE d.id=?""",
        (int(document_id),),
    ).fetchone()
    return _row_dict(row) if row is not None else None
