# -*- coding: utf-8 -*-
"""Shared Taxo entity choices for orders, briefings and other documents.

The UI must never identify an employee or vehicle only by a free-form label.
Every choice carries a stable database id plus identity fields that can be used
for search, validation and a future immutable document snapshot.
"""
from __future__ import annotations


def _table_exists(con, table):
    return con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (str(table),),
    ).fetchone() is not None


def _columns(con, table):
    if not _table_exists(con, table):
        return set()
    return {str(row[1]) for row in con.execute("PRAGMA table_info(%s)" % str(table)).fetchall()}


def _text(value):
    return str(value or "").strip()


def _deduplicate_labels(rows):
    counts = {}
    for row in rows:
        label = _text(row.get("label"))
        counts[label] = counts.get(label, 0) + 1
    for row in rows:
        label = _text(row.get("label"))
        if counts.get(label, 0) > 1:
            row["label"] = "%s · ID %s" % (label or row.get("entity_type", "Запис"), row["id"])
    return rows


def _masked_person_identifier(value):
    text = _text(value)
    if not text:
        return ""
    if len(text) <= 4:
        return text
    return "••••••" + text[-4:]


def _employee_registry_ids(con):
    result = {}
    if not _table_exists(con, "employee_military_profile"):
        return result
    cols = _columns(con, "employee_military_profile")
    if "employee_id" not in cols or "registry_person_id" not in cols:
        return result
    for row in con.execute(
        "SELECT employee_id,registry_person_id FROM employee_military_profile"
    ).fetchall():
        value = _text(row["registry_person_id"])
        if value:
            result[int(row["employee_id"])] = value
    return result


def list_employee_choices(con, active_only=True):
    """Return stable employee choices with identity metadata.

    The normal label avoids exposing the full RNOKPP unless it is needed to
    distinguish a record. Full identifiers remain available in the structured
    row/search text so consumers never have to match by PІB alone.
    """
    cols = _columns(con, "employees")
    if "id" not in cols:
        return []
    wanted = [
        "id", "last_name", "first_name", "middle_name", "position", "active",
        "personnel_no", "rnokpp", "driver_id",
    ]
    selected = [name for name in wanted if name in cols]
    sql = "SELECT %s FROM employees" % ",".join(selected)
    if active_only and "active" in cols:
        sql += " WHERE COALESCE(active,1)=1"
    sql += " ORDER BY %s" % ",".join(
        name for name in ("last_name", "first_name", "middle_name", "id") if name in cols
    )
    registry_ids = _employee_registry_ids(con)
    result = []
    for row in con.execute(sql).fetchall():
        employee_id = int(row["id"])
        name = " ".join(
            _text(row[key]) for key in ("last_name", "first_name", "middle_name")
            if key in cols and _text(row[key])
        )
        position = _text(row["position"]) if "position" in cols else ""
        personnel_no = _text(row["personnel_no"]) if "personnel_no" in cols else ""
        rnokpp = _text(row["rnokpp"]) if "rnokpp" in cols else ""
        registry_person_id = registry_ids.get(employee_id, "")
        parts = [name or ("Працівник #%d" % employee_id)]
        if personnel_no:
            parts.append("таб. № %s" % personnel_no)
        elif rnokpp:
            parts.append("РНОКПП %s" % _masked_person_identifier(rnokpp))
        label = " · ".join(parts)
        if position:
            label += " — " + position
        snapshot = {
            "entity_type": "employee",
            "id": employee_id,
            "name": name,
            "position": position,
            "personnel_no": personnel_no,
            "rnokpp": rnokpp,
            "registry_person_id": registry_person_id,
        }
        result.append({
            **snapshot,
            "label": label,
            "search_text": " ".join(
                value for value in (
                    name, position, personnel_no, rnokpp, registry_person_id, str(employee_id)
                ) if value
            ).lower(),
            "snapshot": dict(snapshot),
        })
    return _deduplicate_labels(result)


def _driver_employee_ids(con, active_only=True):
    ids = set()
    if _table_exists(con, "employee_roles"):
        cols = _columns(con, "employee_roles")
        if "employee_id" in cols and "role" in cols:
            for row in con.execute("SELECT employee_id,role FROM employee_roles").fetchall():
                role = _text(row["role"]).lower()
                if role == "водій" or role.startswith("водій ") or "водій автотранспорт" in role:
                    ids.add(int(row["employee_id"]))

    employee_cols = _columns(con, "employees")
    if "id" not in employee_cols or "driver_id" not in employee_cols:
        return ids
    linked = con.execute(
        "SELECT id,driver_id FROM employees WHERE driver_id IS NOT NULL"
    ).fetchall()
    if not active_only or not _table_exists(con, "drivers"):
        ids.update(int(row["id"]) for row in linked)
        return ids

    driver_cols = _columns(con, "drivers")
    clauses = []
    if "active" in driver_cols:
        clauses.append("COALESCE(active,1)=1")
    if "driver_end_date" in driver_cols:
        clauses.append("COALESCE(driver_end_date,'')=''")
    sql = "SELECT id FROM drivers"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    current_driver_ids = {int(row["id"]) for row in con.execute(sql).fetchall()}
    ids.update(int(row["id"]) for row in linked if int(row["driver_id"]) in current_driver_ids)
    return ids


def list_driver_choices(con, active_only=True):
    driver_ids = _driver_employee_ids(con, active_only=active_only)
    return [
        row for row in list_employee_choices(con, active_only=active_only)
        if int(row["id"]) in driver_ids
    ]


def list_vehicle_choices(con, active_only=False):
    """Return stable vehicle choices with VIN/plate identity metadata."""
    cols = _columns(con, "vehicles")
    if "id" not in cols:
        return []
    wanted = ["id", "name", "plate", "make_model", "vin", "garage_no", "active"]
    selected = [name for name in wanted if name in cols]
    sql = "SELECT %s FROM vehicles" % ",".join(selected)
    if active_only and "active" in cols:
        sql += " WHERE COALESCE(active,1)=1"
    order_fields = [name for name in ("plate", "name", "id") if name in cols]
    if order_fields:
        sql += " ORDER BY " + ",".join("COALESCE(%s,'')" % name if name != "id" else "id" for name in order_fields)
    result = []
    for row in con.execute(sql).fetchall():
        vehicle_id = int(row["id"])
        plate = _text(row["plate"]) if "plate" in cols else ""
        name = _text(row["make_model"]) if "make_model" in cols else ""
        if not name and "name" in cols:
            name = _text(row["name"])
        vin = _text(row["vin"]) if "vin" in cols else ""
        garage_no = _text(row["garage_no"]) if "garage_no" in cols else ""
        label_parts = [value for value in (plate, name) if value]
        if vin:
            label_parts.append("VIN %s" % vin)
        elif garage_no:
            label_parts.append("гараж. № %s" % garage_no)
        label = " · ".join(label_parts) or ("ТЗ #%d" % vehicle_id)
        snapshot = {
            "entity_type": "vehicle",
            "id": vehicle_id,
            "name": name,
            "plate": plate,
            "vin": vin,
            "garage_no": garage_no,
        }
        result.append({
            **snapshot,
            "label": label,
            "search_text": " ".join(
                value for value in (plate, name, vin, garage_no, str(vehicle_id)) if value
            ).lower(),
            "snapshot": dict(snapshot),
        })
    return _deduplicate_labels(result)


def choice_snapshot(choice):
    """Return a plain immutable-ready snapshot for document storage."""
    if not choice:
        return {}
    snapshot = choice.get("snapshot") if isinstance(choice, dict) else None
    if isinstance(snapshot, dict):
        return dict(snapshot)
    keys = (
        "entity_type", "id", "name", "position", "personnel_no", "rnokpp",
        "registry_person_id", "plate", "vin", "garage_no",
    )
    return {key: choice.get(key) for key in keys if isinstance(choice, dict) and key in choice}
