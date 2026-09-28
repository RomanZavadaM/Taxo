# -*- coding: utf-8 -*-
"""Taxo 10.5-r2 — per-field reconciliation for «Шлях» vehicle registry data.

The registry is an external official snapshot, not a replacement for the Taxo
working database. Empty/absent incoming values never clear local data. Decisions
about discrepancies are persisted field-by-field between quarterly extracts.
"""
from __future__ import annotations

from datetime import datetime

import vehicle_registry as registry

APP_VERSION = "10.5-r2"

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

# These values participate in vehicle identity. A mismatch must be visible as a
# critical conflict and never silently downgraded to an ordinary description diff.
CRITICAL_FIELDS = {"vin", "plate"}


def _text(value):
    return str(value or "").strip()


def _norm(field_name, value):
    if field_name == "vin":
        return registry.normalize_vin(value)
    if field_name == "plate":
        return registry.normalize_plate(value)
    if field_name == "gross_mass_kg":
        return registry._number_text(value)
    return _text(value).casefold()


def ensure_schema_on_connection(con):
    registry.ensure_schema_on_connection(con)
    con.executescript("""
        CREATE TABLE IF NOT EXISTS vehicle_registry_field_state (
            vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
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
            PRIMARY KEY(vehicle_id,field_name)
        );
        CREATE INDEX IF NOT EXISTS idx_vehicle_registry_field_state_state
            ON vehicle_registry_field_state(state,decision_active,vehicle_id);

        CREATE TABLE IF NOT EXISTS vehicle_registry_field_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
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
        CREATE INDEX IF NOT EXISTS idx_vehicle_registry_field_history_vehicle
            ON vehicle_registry_field_history(vehicle_id,created_at DESC,id DESC);
    """)


def ensure_schema(core):
    con = core.db()
    try:
        ensure_schema_on_connection(con)
        con.commit()
    finally:
        con.close()


def field_state(field_name, local_value, registry_value):
    """Classify one registry field without mutating Taxo."""
    local = _text(local_value)
    incoming = _text(registry_value)
    if not incoming:
        return STATE_UNAVAILABLE
    if not local:
        return STATE_FILL
    if _norm(field_name, local) == _norm(field_name, incoming):
        return STATE_MATCH
    if field_name in CRITICAL_FIELDS:
        return STATE_CRITICAL
    return STATE_DIFFERENCE


def _vehicle_row(con, vehicle_id):
    return con.execute("SELECT * FROM vehicles WHERE id=?", (int(vehicle_id),)).fetchone()


def reconciliation_fields(con, row_plan, source_kind="", source_name="", file_sha256=""):
    """Return field states for one already matched vehicle preview row."""
    vehicle_id = row_plan.get("vehicle_id")
    if vehicle_id is None or row_plan.get("status") == "critical":
        return []
    ensure_schema_on_connection(con)
    vehicle = _vehicle_row(con, vehicle_id)
    if vehicle is None:
        return []
    local = {key: vehicle[key] for key in vehicle.keys()}
    item = row_plan.get("item") or {}
    result = []
    for field_name, label in registry.FIELD_LABELS.items():
        incoming = _text(item.get(field_name, ""))
        current = _text(local.get(field_name, ""))
        result.append({
            "vehicle_id": int(vehicle_id),
            "field": field_name,
            "label": label,
            "local": current,
            "registry": incoming,
            "state": field_state(field_name, current, incoming),
            "source_kind": source_kind,
            "source_name": source_name,
            "file_sha256": file_sha256,
            "source_row": item.get("source_row"),
        })
    return result


def _append_history(con, field, decision, note, now):
    con.execute(
        """INSERT INTO vehicle_registry_field_history(
               vehicle_id,field_name,local_value,registry_value,state,decision,note,
               source_kind,source_name,file_sha256,source_row,created_at
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (field["vehicle_id"], field["field"], field["local"], field["registry"],
         field["state"], decision, _text(note), field.get("source_kind", ""),
         field.get("source_name", ""), field.get("file_sha256", ""),
         field.get("source_row"), now),
    )


def _upsert_current_state(con, field, now):
    existing = con.execute(
        "SELECT * FROM vehicle_registry_field_state WHERE vehicle_id=? AND field_name=?",
        (field["vehicle_id"], field["field"]),
    ).fetchone()
    decision = _text(existing["decision"]) if existing is not None else ""
    note = _text(existing["decision_note"]) if existing is not None else ""
    active = int(existing["decision_active"] or 0) if existing is not None else 0
    decided_at = _text(existing["decided_at"]) if existing is not None else ""
    resolved_at = _text(existing["resolved_at"]) if existing is not None else ""

    if active and decision == DECISION_FIX_REGISTRY and field["state"] == STATE_MATCH:
        _append_history(
            con, field, DECISION_RESOLVED,
            "Дані свіжого витягу «Шлях» тепер відповідають Taxo.", now,
        )
        decision = DECISION_RESOLVED
        note = "Дані свіжого витягу «Шлях» тепер відповідають Taxo."
        active = 0
        resolved_at = now

    first_seen = _text(existing["first_seen_at"]) if existing is not None else now
    con.execute(
        """INSERT INTO vehicle_registry_field_state(
               vehicle_id,field_name,local_value,registry_value,state,decision,
               decision_note,decision_active,source_kind,source_name,file_sha256,
               source_row,first_seen_at,last_seen_at,decided_at,resolved_at
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(vehicle_id,field_name) DO UPDATE SET
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
        (field["vehicle_id"], field["field"], field["local"], field["registry"],
         field["state"], decision, note, active, field.get("source_kind", ""),
         field.get("source_name", ""), field.get("file_sha256", ""),
         field.get("source_row"), first_seen, now, decided_at, resolved_at),
    )


def sync_preview_state(con, preview):
    """Refresh persisted per-field state without applying registry values."""
    ensure_schema_on_connection(con)
    parsed = preview.get("parsed") or {}
    now = datetime.now().isoformat(timespec="seconds")
    count = 0
    for row_plan in preview.get("plan") or []:
        for field in reconciliation_fields(
            con, row_plan,
            source_kind=parsed.get("source_kind", registry.SOURCE_KIND),
            source_name=parsed.get("source_name", ""),
            file_sha256=preview.get("file_sha256", ""),
        ):
            _upsert_current_state(con, field, now)
            count += 1
    return count


def set_decision(con, vehicle_id, field_name, decision, note=""):
    if decision not in ALLOWED_DECISIONS:
        raise ValueError("Невідоме рішення звіряння: %s" % decision)
    ensure_schema_on_connection(con)
    row = con.execute(
        "SELECT * FROM vehicle_registry_field_state WHERE vehicle_id=? AND field_name=?",
        (int(vehicle_id), field_name),
    ).fetchone()
    if row is None:
        raise ValueError("Спочатку виконайте покомпонентну звірку цього ТЗ.")
    if decision == DECISION_ACCEPT_REGISTRY and not _text(row["registry_value"]):
        raise ValueError("У витягу «Шлях» немає значення, яке можна прийняти.")
    now = datetime.now().isoformat(timespec="seconds")
    active = 1 if decision in (DECISION_FIX_REGISTRY, DECISION_DEFER) else 0
    con.execute(
        """UPDATE vehicle_registry_field_state
           SET decision=?,decision_note=?,decision_active=?,decided_at=?,resolved_at=''
           WHERE vehicle_id=? AND field_name=?""",
        (decision, _text(note), active, now, int(vehicle_id), field_name),
    )
    field = {
        "vehicle_id": int(vehicle_id), "field": field_name,
        "local": row["local_value"], "registry": row["registry_value"],
        "state": row["state"], "source_kind": row["source_kind"],
        "source_name": row["source_name"], "file_sha256": row["file_sha256"],
        "source_row": row["source_row"],
    }
    _append_history(con, field, decision, note, now)


def accept_registry_value(con, vehicle_id, field_name, note=""):
    """Apply exactly one non-empty registry field and record the decision."""
    ensure_schema_on_connection(con)
    if field_name not in registry.FIELD_LABELS:
        raise ValueError("Поле ТЗ не дозволене для реєстрового оновлення.")
    row = con.execute(
        "SELECT * FROM vehicle_registry_field_state WHERE vehicle_id=? AND field_name=?",
        (int(vehicle_id), field_name),
    ).fetchone()
    if row is None or not _text(row["registry_value"]):
        raise ValueError("У витягу «Шлях» немає значення, яке можна прийняти.")
    value = _text(row["registry_value"])
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        "UPDATE vehicles SET %s=?,registry_last_source_name=?,registry_last_verified_at=? WHERE id=?" % field_name,
        (value, row["source_name"], now, int(vehicle_id)),
    )
    con.execute(
        """UPDATE vehicle_registry_field_state
           SET local_value=?,state=?,last_seen_at=?
           WHERE vehicle_id=? AND field_name=?""",
        (value, STATE_MATCH, now, int(vehicle_id), field_name),
    )
    set_decision(con, vehicle_id, field_name, DECISION_ACCEPT_REGISTRY, note)


def current_fields(con, vehicle_id=None, states=None, active_decisions_only=False):
    ensure_schema_on_connection(con)
    where = []
    params = []
    if vehicle_id is not None:
        where.append("vehicle_id=?")
        params.append(int(vehicle_id))
    states = list(states or [])
    if states:
        where.append("state IN (%s)" % ",".join("?" for _ in states))
        params.extend(states)
    if active_decisions_only:
        where.append("decision_active=1")
    sql = "SELECT * FROM vehicle_registry_field_state"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY vehicle_id,CASE state WHEN 'critical' THEN 0 WHEN 'difference' THEN 1 WHEN 'fill' THEN 2 WHEN 'match' THEN 3 ELSE 4 END,field_name"
    return con.execute(sql, params).fetchall()


def history(con, vehicle_id, field_name=None, limit=200):
    ensure_schema_on_connection(con)
    where = ["vehicle_id=?"]
    params = [int(vehicle_id)]
    if field_name:
        where.append("field_name=?")
        params.append(field_name)
    sql = "SELECT * FROM vehicle_registry_field_history WHERE " + " AND ".join(where)
    sql += " ORDER BY created_at DESC,id DESC LIMIT ?"
    params.append(int(limit))
    return con.execute(sql, params).fetchall()


def state_counts(con, vehicle_id=None):
    rows = current_fields(con, vehicle_id=vehicle_id)
    result = {key: 0 for key in STATE_LABELS}
    for row in rows:
        if row["state"] in result:
            result[row["state"]] += 1
    return result
