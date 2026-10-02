# -*- coding: utf-8 -*-
"""Taxo 10.4-r9 — per-field reconciliation for employee state-registry data.

This layer is deliberately separate from the XLSX parser.  The registry is an
external official snapshot, not a replacement for the Taxo working database.
Empty or absent incoming values never clear local data.
"""
from __future__ import annotations

from datetime import datetime

import personnel_registry as registry

APP_VERSION = "10.4-r9"
LEGAL_BASIS = "Порядок №1487, редакція 27.06.2026"

STATE_MATCH = "match"
STATE_FILL = "fill"
STATE_DIFFERENCE = "difference"
STATE_CRITICAL = "critical"
STATE_UNAVAILABLE = "registry_unavailable"

STATE_LABELS = {
    STATE_MATCH: "Відповідає",
    STATE_FILL: "Можна доповнити",
    STATE_DIFFERENCE: "Розбіжність",
    STATE_CRITICAL: "Критичний конфлікт",
    STATE_UNAVAILABLE: "Немає у витягу",
}

DECISION_ACCEPT_REGISTRY = "accept_registry"
DECISION_KEEP_TAXO = "keep_taxo"
DECISION_FIX_REGISTRY = "fix_registry"
DECISION_DEFER = "defer"
DECISION_RESOLVED = "resolved"

DECISION_LABELS = {
    DECISION_ACCEPT_REGISTRY: "Прийняти дані реєстру",
    DECISION_KEEP_TAXO: "Залишити Taxo",
    DECISION_FIX_REGISTRY: "Потрібно виправити у реєстрі",
    DECISION_DEFER: "Відкласти рішення",
    DECISION_RESOLVED: "Розбіжність усунена",
}

ALLOWED_DECISIONS = {
    DECISION_ACCEPT_REGISTRY,
    DECISION_KEEP_TAXO,
    DECISION_FIX_REGISTRY,
    DECISION_DEFER,
}

# A mismatch in these identifiers must never be silently accepted as an ordinary
# descriptive difference.
CRITICAL_FIELDS = {
    ("employee", "rnokpp"),
    ("military", "registry_person_id"),
}


def _text(value):
    return str(value or "").strip()


def ensure_schema_on_connection(con):
    registry.ensure_schema_on_connection(con)
    con.executescript("""
        CREATE TABLE IF NOT EXISTS employee_registry_field_state (
            employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            scope TEXT NOT NULL,
            field_name TEXT NOT NULL,
            local_value TEXT DEFAULT '',
            registry_value TEXT DEFAULT '',
            state TEXT NOT NULL,
            decision TEXT DEFAULT '',
            decision_note TEXT DEFAULT '',
            decision_active INTEGER NOT NULL DEFAULT 0,
            source_kind TEXT DEFAULT '',
            source_name TEXT DEFAULT '',
            file_sha256 TEXT DEFAULT '',
            source_row INTEGER,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            decided_at TEXT DEFAULT '',
            resolved_at TEXT DEFAULT '',
            PRIMARY KEY(employee_id,scope,field_name)
        );
        CREATE INDEX IF NOT EXISTS idx_employee_registry_field_state_state
            ON employee_registry_field_state(state,decision_active,employee_id);

        CREATE TABLE IF NOT EXISTS employee_registry_field_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            scope TEXT NOT NULL,
            field_name TEXT NOT NULL,
            local_value TEXT DEFAULT '',
            registry_value TEXT DEFAULT '',
            state TEXT NOT NULL,
            decision TEXT NOT NULL,
            note TEXT DEFAULT '',
            source_kind TEXT DEFAULT '',
            source_name TEXT DEFAULT '',
            file_sha256 TEXT DEFAULT '',
            source_row INTEGER,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_employee_registry_field_history_employee
            ON employee_registry_field_history(employee_id,created_at DESC,id DESC);
    """)


def ensure_schema(core):
    con = core.db()
    try:
        ensure_schema_on_connection(con)
        con.commit()
    finally:
        con.close()


def field_state(scope, field_name, local_value, registry_value):
    """Classify one field without mutating anything.

    Empty registry value means only that this extract does not confirm the field;
    it is not a request to clear the Taxo value and not an automatic violation.
    """
    local = _text(local_value)
    incoming = _text(registry_value)
    if not incoming:
        return STATE_UNAVAILABLE
    if not local:
        return STATE_FILL
    if local == incoming:
        return STATE_MATCH
    if (scope, field_name) in CRITICAL_FIELDS:
        return STATE_CRITICAL
    return STATE_DIFFERENCE


def _employee_values(con, employee_id):
    employee = con.execute("SELECT * FROM employees WHERE id=?", (int(employee_id),)).fetchone()
    military = con.execute(
        "SELECT * FROM employee_military_profile WHERE employee_id=?", (int(employee_id),)
    ).fetchone()
    return employee, military


def _row_dict(row):
    return {key: row[key] for key in row.keys()} if row is not None else {}


def reconciliation_fields(con, row_plan, source_kind="", source_name="", file_sha256=""):
    """Return all official fields supplied/known for one matched employee row."""
    employee_id = row_plan.get("employee_id")
    if employee_id is None:
        return []
    ensure_schema_on_connection(con)
    employee, military = _employee_values(con, employee_id)
    employee_data = _row_dict(employee)
    military_data = _row_dict(military)
    item = row_plan.get("item") or {}
    result = []
    for scope, values, local_data, labels in (
        ("employee", item.get("personal") or {}, employee_data, registry.EMPLOYEE_FIELD_LABELS),
        ("military", item.get("military") or {}, military_data, registry.MILITARY_FIELD_LABELS),
    ):
        # Include fields explicitly represented by the parser even when this row is
        # blank. That distinction is useful: "no value in extract" != "delete local".
        for field_name, incoming in values.items():
            local = _text(local_data.get(field_name, ""))
            incoming = _text(incoming)
            result.append({
                "employee_id": int(employee_id),
                "scope": scope,
                "field": field_name,
                "label": labels.get(field_name, field_name),
                "local": local,
                "registry": incoming,
                "state": field_state(scope, field_name, local, incoming),
                "source_kind": source_kind,
                "source_name": source_name,
                "file_sha256": file_sha256,
                "source_row": item.get("source_row"),
            })
    return result


def _upsert_current_state(con, field, now):
    existing = con.execute(
        """SELECT * FROM employee_registry_field_state
           WHERE employee_id=? AND scope=? AND field_name=?""",
        (field["employee_id"], field["scope"], field["field"]),
    ).fetchone()

    decision = _text(existing["decision"]) if existing is not None else ""
    note = _text(existing["decision_note"]) if existing is not None else ""
    active = int(existing["decision_active"] or 0) if existing is not None else 0
    decided_at = _text(existing["decided_at"]) if existing is not None else ""
    resolved_at = _text(existing["resolved_at"]) if existing is not None else ""

    # A standing "fix in registry" task resolves automatically when a later
    # official extract finally matches the Taxo value.
    if active and decision == DECISION_FIX_REGISTRY and field["state"] == STATE_MATCH:
        con.execute(
            """INSERT INTO employee_registry_field_history(
                   employee_id,scope,field_name,local_value,registry_value,state,
                   decision,note,source_kind,source_name,file_sha256,source_row,created_at
               ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (field["employee_id"], field["scope"], field["field"], field["local"],
             field["registry"], field["state"], DECISION_RESOLVED,
             "Дані державного витягу тепер відповідають Taxo.",
             field.get("source_kind", ""), field.get("source_name", ""),
             field.get("file_sha256", ""), field.get("source_row"), now),
        )
        decision = DECISION_RESOLVED
        note = "Дані державного витягу тепер відповідають Taxo."
        active = 0
        resolved_at = now

    first_seen = _text(existing["first_seen_at"]) if existing is not None else now
    con.execute(
        """INSERT INTO employee_registry_field_state(
               employee_id,scope,field_name,local_value,registry_value,state,
               decision,decision_note,decision_active,source_kind,source_name,
               file_sha256,source_row,first_seen_at,last_seen_at,decided_at,resolved_at
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(employee_id,scope,field_name) DO UPDATE SET
               local_value=excluded.local_value,
               registry_value=excluded.registry_value,
               state=excluded.state,
               decision=excluded.decision,
               decision_note=excluded.decision_note,
               decision_active=excluded.decision_active,
               source_kind=excluded.source_kind,
               source_name=excluded.source_name,
               file_sha256=excluded.file_sha256,
               source_row=excluded.source_row,
               last_seen_at=excluded.last_seen_at,
               decided_at=excluded.decided_at,
               resolved_at=excluded.resolved_at""",
        (field["employee_id"], field["scope"], field["field"], field["local"],
         field["registry"], field["state"], decision, note, active,
         field.get("source_kind", ""), field.get("source_name", ""),
         field.get("file_sha256", ""), field.get("source_row"), first_seen, now,
         decided_at, resolved_at),
    )


def sync_preview_state(con, preview):
    """Refresh per-field state for a preview without applying registry values."""
    ensure_schema_on_connection(con)
    parsed = preview.get("parsed") or {}
    now = datetime.now().isoformat(timespec="seconds")
    count = 0
    for row_plan in preview.get("plan") or []:
        for field in reconciliation_fields(
            con, row_plan,
            source_kind=parsed.get("source_kind", ""),
            source_name=parsed.get("source_name", ""),
            file_sha256=preview.get("file_sha256", ""),
        ):
            _upsert_current_state(con, field, now)
            count += 1
    return count


def set_decision(con, employee_id, scope, field_name, decision, note=""):
    if decision not in ALLOWED_DECISIONS:
        raise ValueError("Невідоме рішення звіряння: %s" % decision)
    ensure_schema_on_connection(con)
    row = con.execute(
        """SELECT * FROM employee_registry_field_state
           WHERE employee_id=? AND scope=? AND field_name=?""",
        (int(employee_id), scope, field_name),
    ).fetchone()
    if row is None:
        raise ValueError("Спочатку виконайте звіряння цього поля з державним витягом.")
    if decision == DECISION_ACCEPT_REGISTRY and not _text(row["registry_value"]):
        raise ValueError("У державному витягу немає значення, яке можна прийняти.")
    now = datetime.now().isoformat(timespec="seconds")
    active = 1 if decision in (DECISION_FIX_REGISTRY, DECISION_DEFER) else 0
    con.execute(
        """UPDATE employee_registry_field_state
           SET decision=?,decision_note=?,decision_active=?,decided_at=?,resolved_at=''
           WHERE employee_id=? AND scope=? AND field_name=?""",
        (decision, _text(note), active, now, int(employee_id), scope, field_name),
    )
    con.execute(
        """INSERT INTO employee_registry_field_history(
               employee_id,scope,field_name,local_value,registry_value,state,
               decision,note,source_kind,source_name,file_sha256,source_row,created_at
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (int(employee_id), scope, field_name, row["local_value"], row["registry_value"],
         row["state"], decision, _text(note), row["source_kind"], row["source_name"],
         row["file_sha256"], row["source_row"], now),
    )


def accept_registry_value(con, employee_id, scope, field_name, note=""):
    """Apply exactly one non-empty registry value, then record the decision."""
    ensure_schema_on_connection(con)
    row = con.execute(
        """SELECT * FROM employee_registry_field_state
           WHERE employee_id=? AND scope=? AND field_name=?""",
        (int(employee_id), scope, field_name),
    ).fetchone()
    if row is None or not _text(row["registry_value"]):
        raise ValueError("У державному витягу немає значення, яке можна прийняти.")
    value = _text(row["registry_value"])
    if scope == "employee":
        if field_name not in registry.EMPLOYEE_FIELD_LABELS:
            raise ValueError("Поле працівника не дозволене для реєстрового оновлення.")
        con.execute("UPDATE employees SET %s=? WHERE id=?" % field_name, (value, int(employee_id)))
    elif scope == "military":
        if field_name not in registry.MILITARY_FIELD_LABELS:
            raise ValueError("Поле військового профілю не дозволене для реєстрового оновлення.")
        con.execute("INSERT OR IGNORE INTO employee_military_profile(employee_id) VALUES(?)", (int(employee_id),))
        con.execute(
            "UPDATE employee_military_profile SET %s=?,updated_at=? WHERE employee_id=?" % field_name,
            (value, datetime.now().isoformat(timespec="seconds"), int(employee_id)),
        )
    else:
        raise ValueError("Невідома група поля: %s" % scope)

    # Refresh current state to MATCH and preserve provenance before writing history.
    con.execute(
        """UPDATE employee_registry_field_state
           SET local_value=?,state=?,last_seen_at=?
           WHERE employee_id=? AND scope=? AND field_name=?""",
        (value, STATE_MATCH, datetime.now().isoformat(timespec="seconds"),
         int(employee_id), scope, field_name),
    )
    set_decision(con, employee_id, scope, field_name, DECISION_ACCEPT_REGISTRY, note)


def current_fields(con, employee_id=None, states=None, active_decisions_only=False):
    ensure_schema_on_connection(con)
    where = []
    params = []
    if employee_id is not None:
        where.append("employee_id=?")
        params.append(int(employee_id))
    states = list(states or [])
    if states:
        where.append("state IN (%s)" % ",".join("?" for _ in states))
        params.extend(states)
    if active_decisions_only:
        where.append("decision_active=1")
    sql = "SELECT * FROM employee_registry_field_state"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY employee_id,CASE state WHEN 'critical' THEN 0 WHEN 'difference' THEN 1 WHEN 'fill' THEN 2 WHEN 'match' THEN 3 ELSE 4 END,scope,field_name"
    return con.execute(sql, params).fetchall()


def history(con, employee_id, scope=None, field_name=None, limit=200):
    ensure_schema_on_connection(con)
    where = ["employee_id=?"]
    params = [int(employee_id)]
    if scope:
        where.append("scope=?")
        params.append(scope)
    if field_name:
        where.append("field_name=?")
        params.append(field_name)
    params.append(int(limit))
    return con.execute(
        "SELECT * FROM employee_registry_field_history WHERE " + " AND ".join(where)
        + " ORDER BY created_at DESC,id DESC LIMIT ?", params
    ).fetchall()


def employee_summary(con, employee_id):
    rows = current_fields(con, employee_id=employee_id)
    counts = {key: 0 for key in (STATE_MATCH, STATE_FILL, STATE_DIFFERENCE, STATE_CRITICAL, STATE_UNAVAILABLE)}
    active = 0
    for row in rows:
        counts[row["state"]] = counts.get(row["state"], 0) + 1
        active += int(row["decision_active"] or 0)
    return {"counts": counts, "active_decisions": active, "total": len(rows)}
